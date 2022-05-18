from django.shortcuts import render
from rest_framework import viewsets, permissions, pagination, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .permissions import IsAuthorPermission
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorPermission)

    # pagination_class = pagination.LimitOffsetPagination
    # search_fields = ('title', 'description')
    # filter_backends = (filters.SearchFilter, )


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        if q == 'available':
            queryset = queryset.filter(available=True)
        elif q:
            #поиск
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)