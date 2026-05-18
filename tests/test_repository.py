from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.enums.report import ReportType
from domain.models.supplier import Supplier
from domain.models.supplier_evaluation import SupplierEvaluation
from domain.schemas.report import SupplierEvaluationFilters
from infrastructure.repositories.supplier_evaluation import SupplierEvaluationRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_fetch_report_data_quadrimester(mock_session):
    # Setup mocks
    mock_result = MagicMock()

    # Create fake models
    eval_obj = SupplierEvaluation(
        id=1,
        supplier_id=1,
        period_type="QUADRIMESTER",
        period_number=1,
        final_score=Decimal("95.5"),
        evaluation_year=2024,
        evaluator_name="João",
        evaluation_date=date(2024, 5, 16),
        score_quality=Decimal("100"),
        score_delivery=Decimal("90"),
        score_commercial=Decimal("95"),
    )
    supplier_obj = Supplier(
        id=1,
        trade_name="Test Supplier",
        tax_id="12345678901234",
        company_name="Test Supplier LTDA",
    )

    # Session returns a list of tuples (SupplierEvaluation, Supplier)
    mock_result.all.return_value = [(eval_obj, supplier_obj)]
    mock_session.exec.return_value = mock_result

    repo = SupplierEvaluationRepository(mock_session)
    filters = SupplierEvaluationFilters(report_type=ReportType.SUPPLIER_EVALUATION)

    data = await repo.fetch_report_data(filters)

    assert len(data) == 1
    response = data[0]
    assert response.trade_name == "Test Supplier"
    assert response.final_score == "95.5"
    assert response.period == "1º Quadrimestre"
    assert response.evaluation_date == "2024-05-16"


@pytest.mark.asyncio
async def test_fetch_report_data_semester(mock_session):
    # Setup mocks
    mock_result = MagicMock()

    eval_obj = SupplierEvaluation(
        id=2,
        supplier_id=2,
        period_type="SEMESTER",
        period_number=2,
        final_score=Decimal("80.0"),
        evaluation_year=2023,
        evaluator_name="Maria",
        evaluation_date=None,
        score_quality=Decimal("80"),
        score_delivery=Decimal("80"),
        score_commercial=Decimal("80"),
    )
    supplier_obj = Supplier(
        id=2,
        trade_name="Another Supplier",
        tax_id="09876543210987",
        company_name="Another Supplier SA",
    )

    mock_result.all.return_value = [(eval_obj, supplier_obj)]
    mock_session.exec.return_value = mock_result

    repo = SupplierEvaluationRepository(mock_session)
    filters = SupplierEvaluationFilters(report_type=ReportType.SUPPLIER_EVALUATION)

    data = await repo.fetch_report_data(filters)

    assert len(data) == 1
    response = data[0]
    assert response.period == "2º Semestre"
    assert response.evaluation_date is None
