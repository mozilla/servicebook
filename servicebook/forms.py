from collections import OrderedDict
from servicebook.mappings import Project
from wtforms_alchemy import ModelForm


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


class ProjectForm(BaseForm):
    class Meta:
        model = Project
