"""Depends module for report endpoints"""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from application.report_service import ReportService
from core.database import get_session
from infrastructure.excel.supplier_evaluation import SupplierEvaluationExcelGenerator
from infrastructure.repositories.supplier_evaluation import SupplierEvaluationRepository


def get_report_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReportService:
    """
    Get report service.

    Args:
        session: Database session.

    Returns:
        ReportService: Report service.
    """
    repository = SupplierEvaluationRepository(session)
    excel_generator = SupplierEvaluationExcelGenerator()
    return ReportService(repository, excel_generator)
