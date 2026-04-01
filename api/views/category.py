from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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

        offset_param = self.request.query_params.get("offset")
        limit_param = self.request.query_params.get("limit")

        # limit・offset が指定された場合、空文字とNoneを区別しintに変換できなければ400を返す。
        try:
            offset = int(offset_param) if offset_param is not None else 0
            limit = int(limit_param) if limit_param is not None else None
        except ValueError:
            raise ValidationError("limitとoffsetは数値で入力してください")

        if offset < 0 or (limit is not None and limit <= 0):
            raise ValidationError("limitとoffsetは数値で入力してください")

        if limit is not None:
            queryset = queryset[offset:offset + limit]
        else:
            queryset = queryset[offset:]

        return queryset

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    def bulk_destroy(self, request):
        ids = request.data.get("ids", [])
        # 存在するものだけ削除
        Category.objects.filter(pk__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["patch"], url_path="bulk-update")
    def bulk_update(self, request):
        updated = []
        errors = []

        for item in request.data:
            item_id = item.get("id")
            try:
                instance = Category.objects.get(pk=item_id)
            except Category.DoesNotExist:
                # 存在しないIDはスキップ
                continue

            serializer = self.get_serializer(instance, data=item, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated.append(serializer.data)
            else:
                errors.append({"id": item_id, "errors": serializer.errors})

        return Response({"updated": updated, "errors": errors}, status=status.HTTP_200_OK)
