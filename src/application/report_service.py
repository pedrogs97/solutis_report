"""Report service module"""

from io import BytesIO
from typing import Dict, List, Tuple

from domain.cache import ReportCache
from domain.schemas.report import SupplierEvaluationFilters
from infrastructure.excel.supplier_evaluation import SupplierEvaluationExcelGenerator
from infrastructure.repositories.supplier_evaluation import SupplierEvaluationRepository


class ReportService:
    """Report service."""

    def __init__(
        self,
        repository: SupplierEvaluationRepository,
        excel_generator: SupplierEvaluationExcelGenerator,
    ):
        self.repository = repository
        self.excel_generator = excel_generator

    async def generate_report(
        self, report_type: str, filters: SupplierEvaluationFilters
    ) -> Tuple[str, int]:
        """Generate report and store it in cache."""
        data = await self.repository.fetch_report_data(filters)
        cache_key = ReportCache.set(
            report_type, filters, [d.model_dump() for d in data]
        )
        return cache_key, len(data)

    async def get_paginated_report(
        self,
        report_type: str,
        filters: SupplierEvaluationFilters,
        limit: int,
        offset: int,
    ) -> Tuple[str, int, List[Dict]]:
        """Get paginated report."""
        data = ReportCache.get(report_type, filters)
        cache_key = ReportCache.generate_key(report_type, filters)

        if data is None:
            cache_key, _ = await self.generate_report(report_type, filters)
            data = ReportCache.get(report_type, filters)

        total = len(data) if data else 0
        paginated_data = data[offset : offset + limit] if data else []

        return cache_key, total, paginated_data

    async def download_excel(
        self, report_type: str, filters: SupplierEvaluationFilters
    ) -> BytesIO:
        """Download excel report."""
        data = ReportCache.get(report_type, filters)

        if data is None:
            await self.generate_report(report_type, filters)
            data = ReportCache.get(report_type, filters)

        return self.excel_generator.generate(data or [])
