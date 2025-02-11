# Create your tests here.
import pytest

import beanserver.backend.models


@pytest.mark.django_db
def test_budget():
    budget = beanserver.backend.models.Budget.objects.create(
        name="Test Budget",
        description="Test Description",
    )
    assert budget.name == "Test Budget"
    assert budget.description == "Test Description"
