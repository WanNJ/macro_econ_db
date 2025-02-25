import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from ...db import crud, models

logger = logging.getLogger(__name__)


class BaseDataCollector:
    """所有数据采集器的基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_data(
        self, endpoint: str, params: Dict[str, Any] = None
    ) -> Optional[Dict]:
        """从API获取数据"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API请求错误: {e}")
            return None

    def process_data(self, raw_data: Dict) -> List[Dict]:
        """将原始API响应转换为标准格式（需要在子类中实现）"""
        raise NotImplementedError

    def save_to_db(self, processed_data: List[Dict], db: Session):
        """将处理后的数据保存到数据库"""
        raise NotImplementedError

    def collect(self, db: Session) -> bool:
        """完整的数据采集流程（需要在子类中实现）"""
        raise NotImplementedError


class WorldBankCollector(BaseDataCollector):
    """世界银行数据API采集器"""

    def __init__(self):
        super().__init__("https://api.worldbank.org/v2/")

    def fetch_countries(self) -> List[Dict]:
        """获取所有国家信息"""
        result = self.fetch_data("country", {"format": "json", "per_page": 300})
        if result and len(result) > 1:
            return result[1]  # 世界银行API返回格式中，第二个元素包含实际数据
        return []

    def fetch_indicator(self, indicator_code: str, country_code: str) -> Optional[Dict]:
        """获取特定国家和指标的数据"""
        params = {
            "format": "json",
            "per_page": 100,
            "date": "2000:2023",  # 获取2000-2023年的数据
        }

        result = self.fetch_data(
            f"country/{country_code}/indicator/{indicator_code}", params
        )
        return result

    def process_data(self, raw_data: Dict) -> List[Dict]:
        """处理世界银行API返回的数据"""
        processed_data = []

        if not raw_data or len(raw_data) < 2:
            return processed_data

        data_items = raw_data[1]  # 实际数据在第二个元素

        for item in data_items:
            if item.get("value") is not None:
                processed_item = {
                    "country_code": item.get("countryiso3code"),
                    "indicator_code": item.get("indicator", {}).get("id"),
                    "year": int(item.get("date")),
                    "value": float(item.get("value")),
                    "source": "World Bank",
                }
                processed_data.append(processed_item)

        return processed_data

    def save_to_db(self, processed_data: List[Dict], db: Session):
        """将处理后的数据保存到数据库"""
        # 获取或创建数据源
        source = crud.get_data_source_by_name(db, "World Bank")
        if not source:
            source = crud.create_data_source(
                db,
                {
                    "name": "World Bank",
                    "url": "https://data.worldbank.org/",
                    "reliability_score": 0.9,
                    "last_updated": datetime.now().date(),
                },
            )

        for item in processed_data:
            try:
                # 获取国家
                country = crud.get_country_by_code(db, item["country_code"])
                if not country:
                    logger.warning(f"国家代码不存在: {item['country_code']}")
                    continue

                # 获取指标
                indicator = crud.get_indicator_by_code(db, item["indicator_code"])
                if not indicator:
                    logger.warning(f"指标代码不存在: {item['indicator_code']}")
                    continue

                # 检查是否已存在该数据点
                existing_points = crud.get_data_points(
                    db,
                    country_id=country.id,
                    indicator_id=indicator.id,
                    start_date=datetime(item["year"], 1, 1).date(),
                    end_date=datetime(item["year"], 12, 31).date(),
                )

                if not existing_points:
                    # 创建新数据点
                    data_point = {
                        "country_id": country.id,
                        "indicator_id": indicator.id,
                        "date": datetime(item["year"], 1, 1).date(),
                        "value": item["value"],
                        "source_id": source.id,
                    }
                    crud.create_data_point(db, data_point)
                    logger.info(
                        f"已添加数据点: {country.name} - {indicator.name} - {item['year']}"
                    )
            except Exception as e:
                logger.error(f"保存数据点错误: {e}")
                continue

    def collect(
        self,
        db: Session,
        indicator_codes: List[str] = None,
        country_codes: List[str] = None,
    ) -> bool:
        """采集数据的完整流程"""
        try:
            if not indicator_codes:
                indicator_codes = [
                    "NY.GDP.MKTP.CD",
                    "FP.CPI.TOTL.ZG",
                    "SL.UEM.TOTL.ZS",
                ]  # 默认指标: GDP, CPI, 失业率

            if not country_codes:
                # 获取所有国家
                countries_data = self.fetch_countries()
                country_codes = [c["id"] for c in countries_data if c.get("id")]
                # 限制为主要国家，避免请求过多
                main_countries = [
                    "CHN",
                    "USA",
                    "JPN",
                    "DEU",
                    "GBR",
                    "FRA",
                    "IND",
                    "CAN",
                    "AUS",
                    "SGP",
                ]
                country_codes = [c for c in country_codes if c in main_countries]

            for indicator_code in indicator_codes:
                for country_code in country_codes:
                    logger.info(f"正在获取 {country_code} 的 {indicator_code} 数据")

                    # 获取数据
                    raw_data = self.fetch_indicator(indicator_code, country_code)

                    # 处理数据
                    if raw_data:
                        processed_data = self.process_data(raw_data)

                        # 保存到数据库
                        if processed_data:
                            self.save_to_db(processed_data, db)
                            logger.info(
                                f"成功保存 {country_code} 的 {indicator_code} 数据"
                            )
                        else:
                            logger.warning(
                                f"没有可用的 {country_code} 的 {indicator_code} 数据"
                            )

            return True
        except Exception as e:
            logger.error(f"数据采集错误: {e}")
            return False


class IMFCollector(BaseDataCollector):
    """国际货币基金组织数据采集器（简化版）"""

    def __init__(self):
        super().__init__("https://www.imf.org/external/datamapper/api/v1/")

    def fetch_indicator_data(self, indicator_code: str) -> Optional[Dict]:
        """获取特定指标的数据"""
        result = self.fetch_data(f"datasets/{indicator_code}/latest")
        return result

    def process_data(self, raw_data: Dict, indicator_code: str) -> List[Dict]:
        """处理IMF API返回的数据"""
        processed_data = []

        if not raw_data or "values" not in raw_data:
            return processed_data

        values = raw_data.get("values", {}).get(indicator_code, {})

        for country_code, yearly_data in values.items():
            for year, value in yearly_data.items():
                if value is not None:
                    processed_item = {
                        "country_code": country_code,
                        "indicator_code": indicator_code,
                        "year": int(year),
                        "value": float(value),
                        "source": "IMF",
                    }
                    processed_data.append(processed_item)

        return processed_data

    # 其他方法可以类似WorldBankCollector实现
