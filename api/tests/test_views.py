import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="企業A")
        self.company_b = Company.objects.create(name="企業B")

        self.category_fashion = Category.objects.create(
            company=self.company_a,
            name="ファッション",
            parent_category=None,
        )
        self.category_ladies = Category.objects.create(
            company=self.company_a,
            name="レディース",
            parent_category=self.category_fashion,
        )
        self.category_tops = Category.objects.create(
            company=self.company_a,
            name="トップス",
            parent_category=self.category_ladies,
        )
        self.category_food = Category.objects.create(
            company=self.company_b,
            name="食品",
            parent_category=None,
        )

    # --- list ---

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_list_filter_by_company_id(self):
        url = reverse("category-list")
        response = self.client.get(url, {"company_id": self.company_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_filter_by_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"name": "トップス"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

    def test_list_filter_by_parent_category_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"parent_category_name": "レディース"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

    # --- retrieve ---

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category_fashion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ファッション")

    def test_retrieve_not_found(self):
        url = reverse("category-detail", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- create ---

    def test_create(self):
        url = reverse("category-list")
        data = {
            "company": self.company_a.id,
            "name": "メンズ",
            "parent_category": self.category_fashion.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "メンズ")

    def test_create_duplicate_name(self):
        url = reverse("category-list")
        data = {
            "company": self.company_a.id,
            "name": "ファッション",  # 企業A内で既存
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_company(self):
        url = reverse("category-list")
        data = {
            "company": uuid.uuid4(),  # 存在しないcompany_id
            "name": "メンズ",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- update (PUT) ---

    def test_update(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        data = {
            "company": self.company_a.id,
            "name": "ボトムス",
            "parent_category": self.category_ladies.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ボトムス")

    # --- partial_update (PATCH) ---

    def test_partial_update(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        data = {"name": "ボトムス"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ボトムス")

    # --- destroy ---

    def test_destroy(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category_tops.id).exists())

    def test_destroy_not_found(self):
        url = reverse("category-detail", args=[uuid.uuid4()])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
