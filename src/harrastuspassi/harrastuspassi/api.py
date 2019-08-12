# -*- coding: utf-8 -*-

import datetime
import logging
from itertools import chain
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.serializers import (
    HobbySerializer, HobbyDetailSerializer, HobbyCategorySerializer, HobbyEventSerializer
)

LOG = logging.getLogger(__name__)


class ExtraDataSchema(AutoSchema):
    """ Schema describing the include parameter from ExtraDataMixin for serializers """
    def __init__(self, *args, **kwargs):
        self.include_description = kwargs.pop('include_description')
        if self.include_description is None:
            self.include_description = 'Include extra data in the response'
        super().__init__(*args, **kwargs)

    def get_operation(self, path, method, *args, **kwargs):
        operation = super().get_operation(path, method, *args, **kwargs)
        if method == 'GET':
            include_parameter = {
                'description': self.include_description,
                'in': 'query',
                'name': 'include',
                'required': False,
                'schema': {'type': 'string'},
            }
            operation['parameters'].append(include_parameter)
        return operation


class HobbyCategoryFilter(filters.FilterSet):
    parent = filters.ModelChoiceFilter(null_label='Root category', queryset=HobbyCategory.objects.all())


class HobbyCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyCategoryFilter
    queryset = HobbyCategory.objects.all()
    schema = ExtraDataSchema(
        include_description='Include extra data in the response. Possible options: child_categories')
    serializer_class = HobbyCategorySerializer


class HierarchyModelMultipleChoiceFilter(filters.ModelMultipleChoiceFilter):
    """ Filters using the given object and it's children. Use with MPTT models. """
    def filter(self, qs, value):
        # qs is the initial list of objects to be filtered
        # value is a list of objects to be used for filtering
        values_with_children = chain.from_iterable(
            [obj.get_descendants(include_self=True) if hasattr(obj, 'get_descendants') else [obj] for obj in value]
        )
        return super().filter(qs, list(values_with_children))


class HobbyFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        queryset=HobbyCategory.objects.all(),
    )

    class Meta:
        model = Hobby
        fields = ['category']


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyFilter
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer

    def retrieve(self, request, pk=None):
        queryset = Hobby.objects.all()
        hobby = get_object_or_404(queryset, pk=pk)
        serializer = HobbyDetailSerializer(hobby)
        return Response(serializer.data)


class HobbyEventFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='hobby__category', queryset=HobbyCategory.objects.all(),
    )
    hobby = filters.ModelChoiceFilter(field_name='hobby', queryset=Hobby.objects.all())
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    start_time_from = filters.TimeFilter(field_name='start_time', lookup_expr='gte')
    start_time_to = filters.TimeFilter(field_name='start_time', lookup_expr='lte')
    start_weekday = filters.MultipleChoiceFilter(choices=HobbyEvent.DAY_OF_WEEK_CHOICES)

    class Meta:
        model = HobbyEvent
        fields = ['category', 'hobby', 'start_date_from', 'start_date_to',
                  'start_time_from', 'start_time_to', 'start_weekday']


class HobbyEventViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyEventFilter
    queryset = HobbyEvent.objects.all().select_related('hobby__location')
    serializer_class = HobbyEventSerializer
