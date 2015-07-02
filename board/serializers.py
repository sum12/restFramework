import date
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from .models import Sprint, Task

User = get_user_model()

class SprintSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    
    def get_links(self, obj):
        request =  self.context['request']
        return { 'self':reverse("sprint-detail", request=request, kwargs={'pk':obj.pk}),
                'tasks': "{}?sprint={}".format(reverse('task-list', request=request),obj.pk)}
    
    def validate_end(self, attrs, source):
        end_date = attrs[source]
        new  = self.object
        changed = self.object and self.object.end != end_date
        if (new or changed)  and end_date < date.today() :
            msg = "End date cannot be in the past"
            raise serializers.ValidationError(msg)
        return attrs

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', "links" )


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    assigned = serializers.SlugRelatedField(
            queryset=User.objects.all(),
            slug_field=User.USERNAME_FIELD,
            required=False)
    links = serializers.SerializerMethodField()
    
    def get_links(self, obj):
        request =  self.context['request']
        links =  { 'self':reverse("task-detail", request=request, kwargs={'pk':obj.pk}),
                'sprint': None,
                'assigned':None, }

        if obj.sprint_id: links['sprint'] = reverse("sprint-detail", request=request, kwargs={'pk':obj.sprint_id})
        if obj.assigned: links['assigned'] = reverse("user-detail", request=request, kwargs={User.USERNAME_FIELD:obj.assigned})
        
        return links


    def get_status_display(self, obj):
        return obj.get_status_display()


    def validate_sprint(self, attrs, source):
        sprint = attrs[source]
        if self.object and self.object.pk:
            if sprint != self.object.sprint:
                if self.object.status == TASK.STATUS_DONE:
                    msg = "Cannot change sprint of a completed task"
                    raise serializers.ValidationError(msg)
                if sprint.end < date.today():
                    msg = "Cannot assign to an already ended sprint"
                    raise serializers.ValidationError(msg)
        else:
            if sprint.end < date.today():
                msg = "Cannot assign to an already ended sprint"
                raise serializers.ValidationError(msg)
        return attrs

    def validate(self, attrs):
        sprint = attrs.get('sprint')
        status = int(attrs.get('status'))
        started = attrs.get('started')
        completed = attrs.get('completed')
        if not sprint and status != Task.STATUS_TODO:
            msg = _('Backlog tasks must have "Not Started" status.')
            raise serializers.ValidationError(msg)
        if started and status == Task.STATUS_TODO:
            msg = _('Started date cannot be set for not started tasks.')
            raise serializers.ValidationError(msg)
        if completed and status != Task.STATUS_DONE:
            msg = _('Completed date cannot be set for uncompleted tasks.')
            raise serializers.ValidationError(msg)
        return attrs

    class Meta:
        model = Task
        fields = ('id',  'name', 'description', 'sprint', 'status', 'status_display', 'order', 'assigned', 'started', 'due', 'completed', 'links')


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    links = serializers.SerializerMethodField()

    def get_links(self, obj):
        request =  self.context['request']
        return { 'self': reverse("user-detail", request=request, kwargs={User.USERNAME_FIELD:obj.get_username()}),
                'tasks': '{}?assigned={}'.format(reverse('task-list', request=request),obj.get_username()) }

    class Meta:
        model = User
        fields = ('id', User.USERNAME_FIELD, 'full_name', 'is_active', 'links')


