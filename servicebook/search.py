from whooshalchemy import IndexService
from servicebook.mappings import published


def get_indexer(config, session):
    index_service = IndexService(config=config, session=session)
    for mapping in published:
        index_service.register_class(mapping)
    return index_service
