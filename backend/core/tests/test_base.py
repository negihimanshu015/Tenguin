import pytest
from django.utils import timezone
from django.db import models

from core.models.base import BaseModel

class TestModel(BaseModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "core"

@pytest.fixture(autouse=True)
def create_testmodel_table():
    from django.db import connection

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(TestModel)

    yield

    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(TestModel)

@pytest.mark.django_db
class TestBaseModel:
    def test_uuid(self):
        obj = TestModel.objects.create(name="test")
        assert obj.id is not None
        assert obj.id is not None
    
    def test_created(self):
        obj = TestModel.objects.create(name="test")
        assert obj.created is not None
        assert obj.updated is not None

    def test_updated(self):
        obj = TestModel.objects.create(name="test")
        old = obj.updated

        obj.name = "test 1"
        obj.save()

        assert obj.updated > old
    
    def test_deleted(self):
        obj = TestModel.objects.create(name="test")
        obj.soft_delete()

        assert obj.is_active == False
        assert obj.deleted_at is not None

    def test_restored(self):
        obj = TestModel.objects.create(name="test")
        obj.restore()

        assert obj.is_active == True
        assert obj.deleted_at is None

