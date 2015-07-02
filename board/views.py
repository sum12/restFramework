from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework import viewsets, authentication, permissions, filters
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, UserSerializer
from .forms import TaskFilter, SprintFilter
# Create your views here.

User = get_user_model()

class DefaultsMixin(object):
    authetication_classes = (
            authentication.BasicAuthentication,
            authentication.TokenAuthentication,
            )
    permission_classes = (
            #permissions.IsAuthenticated,
            )
    paginate_by = 25
    pagination_param = 'page_size'
    max_paginate = 100
    filter_backends=(
            filters.DjangoFilterBackend,
            filters.SearchFilter,
            filters.OrderingFilter,
            )

class SprintViewSet(DefaultsMixin, viewsets.ModelViewSet):
   queryset = Sprint.objects.all()
   serializer_class = SprintSerializer
   filter_class = SprintFilter
   search_fields = ('name',)
   ordering_fields = ('end', 'name',)

class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
   queryset = Task.objects.all()
   serializer_class = TaskSerializer
   filter_class =  TaskFilter
   search_fields = ('name', 'description', )
   ordering_fields = ('name', 'order', 'started', 'due' , 'completed', )

class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
   lookup_field = User.USERNAME_FIELD
   lookup_url_kwargs = User.USERNAME_FIELD
   queryset = User.objects.order_by(User.USERNAME_FIELD)
   serializer_class = UserSerializer
   search_fields = (User.USERNAME_FIELD, )
