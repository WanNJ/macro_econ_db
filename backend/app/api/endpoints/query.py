from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...db.database import get_db
from ...services.nlp.query_processor import QueryProcessor
from ...services.analytics.analyzer import DataAnalyzer
from ...services.analytics.report_generator import ReportGenerator

router = APIRouter()


@router.post("/natural_language")
def natural_language_query(
    query: str = Body(..., embed=True), db: Session = Depends(get_db)
):
    """处理自然语言查询"""
    processor = QueryProcessor(db)
    result = processor.process_natural_language_query(query)

    # 进行数据分析
    analyzer = DataAnalyzer()
    analysis_result = analyzer.analyze_data(
        result.get("data", []), result.get("query", {})
    )

    # 生成报告
    report_generator = ReportGenerator()
    report = report_generator.generate_report(analysis_result, result.get("query", {}))

    return {"query_result": result, "analysis": analysis_result, "report": report}
