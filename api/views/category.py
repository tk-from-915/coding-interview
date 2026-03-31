from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


# list, retrieve, create, update, partial_update, destroy の6つのアクションを一括で提供するため
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    # メソッドでオーバーライドすることでリクエストごとに動的にフィルタを適用
    def get_queryset(self):
        # N+1問題が発生しないように
        queryset = Category.objects.select_related("company", "parent_category")

        company_id = self.request.query_params.get("company_id")
        name = self.request.query_params.get("name")
        parent_category_name = self.request.query_params.get("parent_category_name")

        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if name:
            queryset = queryset.filter(name=name)
        if parent_category_name:
            queryset = queryset.filter(parent_category__name=parent_category_name)

        return queryset
