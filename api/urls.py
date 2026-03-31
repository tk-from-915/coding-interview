from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()
# router.register(prefix, ViewSet, basename)
# prefix: URLの先頭部分。"categories" なら /categories/ と /categories/{id}/ が生成される
# ViewSet: 紐付けるViewSet
# basename: URL名の接頭辞。get_queryset をオーバーライドしている場合は必須。
#           例) basename="category" → "category-list", "category-detail" などのURL名が生成される
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [path("", include(router.urls))]
