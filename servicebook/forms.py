from collections import OrderedDict
from wtforms_alchemy import ModelForm, QuerySelectField

from servicebook.mappings import Project, Person, Group, Deployment


class BaseForm(ModelForm):
    def __iter__(self):
        field_order = getattr(self, 'field_order', None)
        if field_order:
            temp_fields = []
            for name in field_order:
                if name == '*':
                    for k, v in self._fields.items():
                        if k not in field_order:
                            temp_fields.append((k, v))
                    break
                else:
                    temp_fields.append((name, self._fields[name]))

            self._fields = OrderedDict(temp_fields)

        return super(BaseForm, self).__iter__()


def get_persons():
    # only mozqa folks can be primary/secondary/group lead
    from servicebook.db import Session
    return Session().query(Person).filter(Person.mozqa == True)   # noqa


def get_groups():
    from servicebook.db import Session
    return Session().query(Group).order_by(Group.name)


def get_projects():
    from servicebook.db import Session
    return Session().query(Project).order_by(Project.name)


class ProjectForm(BaseForm):
    class Meta:
        model = Project

    field_order = ('name', 'description', 'primary', 'secondary', 'group',
                   'bz_product', 'bz_component', 'irc')
    primary = QuerySelectField('primary', query_factory=get_persons)
    secondary = QuerySelectField('secondary', query_factory=get_persons)
    group = QuerySelectField('group', query_factory=get_groups,
                             get_label='name')


class DeploymentForm(BaseForm):
    class Meta:
        model = Deployment

    field_order = ('name', 'endpoint')
