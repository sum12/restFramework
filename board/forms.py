import django_filters
from django.contrib.auth import get_user_model
from .models import Task, Sprint

User = get_user_model()


class SprintFilter(django_filters.FilterSet):
    end_min = django_filters.DateTimeFilter(name='end', lookup_type='gte')
    end_max = django_filters.DateTimeFilter(name='end', lookup_type='lte')

    class Meta:
        model = Sprint
        fields = ('end_min', 'end_max', )



class NullFilter(django_filters.BooleanFilter):

    def filter(self, qs, value):
        if value is not None:
            return qs.filter(**{"%s__isnull"%self.name : value})
        return qs

class TaskFilter(django_filters.FilterSet):

    backlog = NullFilter("sprint")
    def __init__(self, *args, **kwargs):
        super(TaskFilter, self).__init__(*args, **kwargs)
        self.filters['assigned'].extra.update({
            'to_field_name':User.USERNAME_FIELD
            })
    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned', "backlog", )



