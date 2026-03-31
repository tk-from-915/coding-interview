from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class CategorySerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True, # NULL を受け入れる（ルートカテゴリは親なし）
        required=False, # リクエストボディに含まれなくてもエラーにしない
    )

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        name = attrs.get("name", getattr(self.instance, "name", None))

        qs = Category.objects.filter(company=company, name=name)

        # 更新時に「自分自身と同じ name」は重複扱いにしないため
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({"name": "このカテゴリ名はすでに存在します。"})

        return attrs
