from datetime import datetime, timedelta, timezone

import pytest

from domain.cache import ReportCache
from domain.enums.report import ReportType
from domain.schemas.report import SupplierEvaluationFilters


@pytest.fixture(autouse=True)
def clear_cache():
    ReportCache.clear_all()
    yield


def test_cachegenerate_key():
    filters1 = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION,
        evaluation_year=2024,
        period_type="A",
    )
    filters2 = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION,
        period_type="A",
        evaluation_year=2024,
    )
    filters3 = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION,
        evaluation_year=2023,
        period_type="A",
    )

    key1 = ReportCache.generate_key("supplier", filters1)
    key2 = ReportCache.generate_key("supplier", filters2)
    key3 = ReportCache.generate_key("supplier", filters3)

    assert key1 == key2  # A ordem dos dicionários não deve importar
    assert key1 != key3  # Valores diferentes devem gerar hashes diferentes


def test_cache_set_and_get():
    filters = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION, evaluation_year=2024
    )
    data = [{"id": 1, "name": "Supplier A"}]

    cache_key = ReportCache.set("supplier", filters, data)
    assert cache_key is not None

    cached_data = ReportCache.get("supplier", filters)
    assert cached_data == data


def test_cache_get_non_existent():
    filters = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION, evaluation_year=2099
    )
    cached_data = ReportCache.get("supplier", filters)
    assert cached_data is None


def test_cache_expiration():
    filters = SupplierEvaluationFilters(
        report_type=ReportType.SUPPLIER_EVALUATION, evaluation_year=2024
    )
    data = [{"id": 1, "name": "Supplier A"}]

    ReportCache.set("supplier", filters, data)

    # Modificar o expires_at manualmente para simular expiração
    cache_key = ReportCache.generate_key("supplier", filters)
    entry = ReportCache._cache_store[cache_key]
    entry.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    cached_data = ReportCache.get("supplier", filters)
    assert cached_data is None
    assert cache_key not in ReportCache._cache_store
