from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models.category import Category
from api.serializers.category import CategorySerializer


# list, retrieve, create, update, partial_update, destroy の6つのアクションを一括で提供するため
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    # メソッドでオーバーライドすることでリクエストごとに動的にフィルタを適用
    def get_queryset(self):
        # N+1問題が発生しないように
        queryset = Category.objects.select_related("company", "parent_category")

        company_ids = self.request.query_params.getlist("company_id")
        name = self.request.query_params.get("name")
        parent_category_name = self.request.query_params.get("parent_category_name")

        if company_ids:
            queryset = queryset.filter(company_id__in=company_ids)
        if name:
            queryset = queryset.filter(name=name)
        if parent_category_name:
            queryset = queryset.filter(parent_category__name=parent_category_name)

        return queryset

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    def bulk_destroy(self, request):
        ids = request.data.get("ids", [])
        # 存在するものだけ削除
        Category.objects.filter(pk__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
