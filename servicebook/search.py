import os
from six import text_type

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema
from whoosh.qparser import MultifieldParser
import whoosh.index

from servicebook.mappings import published
from sqlalchemy import event


class IndexService:
    def __init__(self, config=None, session=None, whoosh_base=None):
        self.config = config
        self.session = session
        self.mappings = []
        event.listen(session, "after_flush", self._after_flush)
        if not whoosh_base and config:
            whoosh_base = config.get("WHOOSH_BASE")
        if not whoosh_base:
            whoosh_base = "whoosh_indexes"  # Default value
        self.whoosh_base = whoosh_base
        self.indexes = {}

    def register_mapping(self, mapping):
        self.mappings.append(mapping)
        index_path = os.path.join(self.whoosh_base, mapping.__name__)

        schema, primary = self._get_whoosh_schema_and_primary(mapping)

        if whoosh.index.exists_in(index_path):
            index = whoosh.index.open_dir(index_path)
        else:
            if not os.path.exists(index_path):
                os.makedirs(index_path)
            index = whoosh.index.create_in(index_path, schema)

        self.indexes[mapping.__name__] = index
        mapping.search_query = Searcher(mapping, primary, index,
                                        self.session)
        return index

    def _after_flush(self, session, changes):
        self._flush_set(session.new)
        self._flush_set(session.dirty)
        # XXX deletes

    def _flush_set(self, _set):
        for instance in _set:
            mapping = instance.__class__
            if mapping not in self.mappings:
                continue

            index = self.indexes[mapping.__name__]
            primary_field = mapping.search_query.primary
            primary_value = text_type(getattr(instance, primary_field))

            with index.writer() as writer:
                attrs = {}
                writer.delete_by_term(primary_field, primary_value)
                attrs[primary_field] = primary_value
                attrs['body'] = instance.index()
                writer.add_document(**attrs)

    def _get_whoosh_schema_and_primary(self, mapping):
        schema = {}
        primary = None
        for field in mapping.__table__.columns:
            if field.primary_key:
                schema[field.name] = whoosh.fields.ID(stored=True, unique=True)
                primary = field.name
                break

        schema['body'] = whoosh.fields.TEXT(analyzer=StemmingAnalyzer())
        return Schema(**schema), primary


class Searcher(object):
    """
    Assigned to a Model class as ``search_query``, which enables text-querying.
    """

    def __init__(self, mapping, primary, index, session=None):
        self.mapping = mapping
        self.primary = primary
        self.index = index
        self.session = session
        self.searcher = index.searcher()
        fields = set(index.schema._fields.keys()) - set([self.primary])
        self.parser = MultifieldParser(list(fields), index.schema)

    def __call__(self, query, limit=None):
        session = self.session
        if not session:
            session = self.mapping.query.session

        results = self.index.searcher().search(
            self.parser.parse(query), limit=limit)
        keys = [x[self.primary] for x in results]
        primary_column = getattr(self.mapping, self.primary)
        return session.query(self.mapping).filter(primary_column.in_(keys))


def get_indexer(config, session):
    index_service = IndexService(config=config, session=session)
    for mapping in published:
        index_service.register_mapping(mapping)
    return index_service
