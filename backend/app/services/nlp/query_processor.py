from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from ...db import crud, models
from .query_parser import QueryParser


class QueryProcessor:
    """处理解析后的查询并返回结果"""

    def __init__(self, db: Session):
        self.db = db
        self.parser = QueryParser()

    def process_natural_language_query(self, query_text: str) -> Dict[str, Any]:
        """处理自然语言查询并返回结果"""
        # 解析查询
        parsed_query = self.parser.parse_query(query_text)

        # 获取数据
        data = self._fetch_data(parsed_query)

        # 准备响应
        response = {
            "query": parsed_query,
            "data": data,
            "message": self._generate_response_message(parsed_query, data),
        }

        return response

    def _fetch_data(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据解析后的查询获取数据"""
        result_data = []

        for country_code in parsed_query["countries"]:
            # 获取国家ID
            country = crud.get_country_by_code(self.db, country_code)
            if not country:
                continue

            for indicator_code in parsed_query["indicators"]:
                # 获取指标ID
                indicator = crud.get_indicator_by_code(self.db, indicator_code)
                if not indicator:
                    continue

                # 获取数据点
                data_points = crud.get_data_points(
                    db=self.db,
                    country_id=country.id,
                    indicator_id=indicator.id,
                    start_date=parsed_query["start_date"],
                    end_date=parsed_query["end_date"],
                )

                # 构建数据系列
                if data_points:
                    series_data = []
                    for point in data_points:
                        series_data.append(
                            {"date": point.date.isoformat(), "value": point.value}
                        )

                    result_data.append(
                        {
                            "country": country.name,
                            "country_code": country.code,
                            "indicator": indicator.name,
                            "indicator_code": indicator_code,
                            "unit": indicator.unit,
                            "data": series_data,
                        }
                    )

        return result_data

    def _generate_response_message(
        self, parsed_query: Dict[str, Any], data: List[Dict[str, Any]]
    ) -> str:
        """生成用户友好的响应消息"""
        if not data:
            return (
                "抱歉，我没有找到符合您查询的数据。请尝试不同的国家、指标或时间范围。"
            )

        countries = [d["country"] for d in data]
        indicators = list(set([d["indicator"] for d in data]))

        start_year = (
            parsed_query["start_date"].year if parsed_query["start_date"] else "未知"
        )
        end_year = parsed_query["end_date"].year if parsed_query["end_date"] else "未知"

        time_range = (
            f"{start_year}年至{end_year}年"
            if start_year != end_year
            else f"{start_year}年"
        )

        if len(countries) > 1 and len(indicators) == 1:
            # 多国单指标比较
            return f"这是{', '.join(countries)}在{time_range}期间的{indicators[0]}数据比较。"
        elif len(countries) == 1 and len(indicators) > 1:
            # 单国多指标比较
            return (
                f"这是{countries[0]}在{time_range}期间的{', '.join(indicators)}数据。"
            )
        else:
            # 一般响应
            return f"这是您请求的{', '.join(countries)}在{time_range}期间的{', '.join(indicators)}数据。"
