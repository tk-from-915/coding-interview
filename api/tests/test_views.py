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
    # --- retrieve ---

    # カテゴリIDで1件取得できること
    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category_fashion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ファッション")

    # 存在しないIDで404が返ること
    def test_retrieve_not_found(self):
        url = reverse("category-detail", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- list ---

    # フィルタなしで全件取得できること
    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    # 1つの企業IDで絞り込めること
    def test_list_filter_by_company_id(self):
        url = reverse("category-list")
        response = self.client.get(url, {"company_id": self.company_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    # カテゴリ名で絞り込めること
    def test_list_filter_by_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"name": "トップス"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

        # 親カテゴリ名で絞り込めること
    def test_list_filter_by_parent_category_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"parent_category_name": "レディース"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

    # 複数の企業IDで絞り込めること
    def test_list_filter_by_multiple_company_ids(self):
        url = reverse("category-list")
        response = self.client.get(url, {"company_id": [self.company_a.id, self.company_b.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    # 複数の企業ID ＋ カテゴリ名で絞り込めること
    def test_list_filter_by_multiple_company_ids_and_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"company_id": [self.company_a.id, self.company_b.id], "name": "トップス"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

    # 複数の企業ID ＋ 親カテゴリ名で絞り込めること
    def test_list_filter_by_multiple_company_ids_and_parent_category_name(self):
        url = reverse("category-list")
        response = self.client.get(url, {"company_id": [self.company_a.id, self.company_b.id], "parent_category_name": "レディース"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "トップス")

    # --- create ---

    # カテゴリを1件作成できること
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

    # 同じ企業内で重複したカテゴリ名は作成できないこと
    def test_create_duplicate_name(self):
        url = reverse("category-list")
        data = {
            "company": self.company_a.id,
            "name": "ファッション",  # 企業A内で既存
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 存在しない企業IDでは作成できないこと
    def test_create_invalid_company(self):
        url = reverse("category-list")
        data = {
            "company": uuid.uuid4(),  # 存在しないcompany_id
            "name": "メンズ",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- update (PUT) ---

    # カテゴリを全フィールド更新できること
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

    # カテゴリを部分更新できること
    def test_partial_update(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        data = {"name": "ボトムス"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ボトムス")

    # 存在しない parent_category IDを指定した場合は400が返ること
    def test_partial_update_with_nonexistent_parent_category(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        data = {"parent_category": uuid.uuid4()}  # 存在しないID
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- bulk_update ---

    # 複数のカテゴリをまとめて更新できること
    def test_bulk_update(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_ladies.id, "name": "メンズ"},
            {"id": self.category_tops.id, "name": "ボトムス"},
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated"]), 2)
        self.assertEqual(len(response.data["errors"]), 0)
        self.assertTrue(Category.objects.filter(pk=self.category_ladies.id, name="メンズ").exists())
        self.assertTrue(Category.objects.filter(pk=self.category_tops.id, name="ボトムス").exists())

    # 存在しないIDはスキップして、存在するものだけ更新されること
    def test_bulk_update_skips_nonexistent_ids(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_tops.id, "name": "ボトムス"},
            {"id": uuid.uuid4(), "name": "存在しない"},
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated"]), 1)
        self.assertTrue(Category.objects.filter(pk=self.category_tops.id, name="ボトムス").exists())

    # バリデーションエラーのものはerrorsに含まれ、有効なものは更新されること
    def test_bulk_update_returns_errors_for_invalid_records(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_ladies.id, "name": "ボトムス"},
            {"id": self.category_tops.id, "name": "ファッション"},  # 企業A内で既存
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated"]), 1)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["id"], str(self.category_tops.id))
        self.assertTrue(Category.objects.filter(pk=self.category_ladies.id, name="ボトムス").exists())

    # 存在しないcompany IDを指定したレコードはerrorsに含まれ、有効なものは更新されること
    def test_bulk_update_with_nonexistent_company(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_ladies.id, "name": "メンズ"},
            {"id": self.category_tops.id, "company": uuid.uuid4()},  # 存在しないcompany
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated"]), 1)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["id"], str(self.category_tops.id))

    # 存在しないparent_category IDを指定したレコードはerrorsに含まれ、有効なものは更新されること
    def test_bulk_update_with_nonexistent_parent_category(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_ladies.id, "name": "メンズ"},
            {"id": self.category_tops.id, "parent_category": uuid.uuid4()},  # 存在しないparent_category
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated"]), 1)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["id"], str(self.category_tops.id))

    # companyにnullを指定した場合はerrorsに含まれること（companyは必須ForeignKey）
    def test_bulk_update_with_null_company(self):
        url = reverse("category-bulk-update")
        data = [
            {"id": self.category_tops.id, "company": None},
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["id"], str(self.category_tops.id))

    # --- destroy ---

    # カテゴリを1件削除できること
    def test_destroy(self):
        url = reverse("category-detail", args=[self.category_tops.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category_tops.id).exists())

    # 存在しないIDで404が返ること
    def test_destroy_not_found(self):
        url = reverse("category-detail", args=[uuid.uuid4()])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- bulk_destroy ---

    # 複数のカテゴリをまとめて削除できること
    def test_bulk_destroy(self):
        url = reverse("category-bulk-destroy")
        data = {"ids": [self.category_ladies.id, self.category_tops.id]}
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category_ladies.id).exists())
        self.assertFalse(Category.objects.filter(pk=self.category_tops.id).exists())

    # 存在しないIDが混じっていても、存在するものだけ削除されること
    def test_bulk_destroy_skips_nonexistent_ids(self):
        url = reverse("category-bulk-destroy")
        data = {"ids": [self.category_tops.id, uuid.uuid4()]}
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category_tops.id).exists())
