import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseDataCollector:
    """所有数据采集器的基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """从API获取数据"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API请求错误: {e}")
            return None

    def process_data(self, raw_data: Dict) -> pd.DataFrame:
        """将原始API响应转换为DataFrame（需要在子类中实现）"""
        raise NotImplementedError

    def collect(self) -> Optional[pd.DataFrame]:
        """完整的数据采集流程"""
        # 在子类中实现


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

    def fetch_indicator(
        self, indicator_code: str, country_code: str
    ) -> Optional[pd.DataFrame]:
        """获取特定国家和指标的数据"""
        params = {
            "format": "json",
            "per_page": 100,
            "date": "2000:2023",  # 获取2000-2023年的数据
        }

        result = self.fetch_data(
            f"country/{country_code}/indicator/{indicator_code}", params
        )
        if result and len(result) > 1:
            return self.process_data(result[1], indicator_code, country_code)
        return None

    def process_data(
        self, raw_data: List[Dict], indicator_code: str, country_code: str
    ) -> pd.DataFrame:
        """处理世界银行API返回的数据"""
        records = []

        for item in raw_data:
            if item.get("value") is not None:
                records.append(
                    {
                        "country_code": country_code,
                        "indicator_code": indicator_code,
                        "year": item.get("date"),
                        "value": item.get("value"),
                        "source": "World Bank",
                        "collected_at": datetime.now().isoformat(),
                    }
                )

        return pd.DataFrame(records)

    def collect(self, indicator_code: str, countries: List[str]) -> pd.DataFrame:
        """采集多个国家的特定指标数据"""
        all_data = []

        for country_code in countries:
            df = self.fetch_indicator(indicator_code, country_code)
            if df is not None and not df.empty:
                all_data.append(df)

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()


class IMFCollector(BaseDataCollector):
    """国际货币基金组织数据采集器"""

    def __init__(self):
        super().__init__("https://www.imf.org/external/datamapper/api/v1/")

    def fetch_indicators(self) -> List[str]:
        """获取可用指标列表"""
        result = self.fetch_data("indicators", {})
        if result and "indicators" in result:
            return list(result["indicators"].keys())
        return []

    def fetch_indicator_data(self, indicator_code: str) -> Optional[pd.DataFrame]:
        """获取特定指标的数据"""
        result = self.fetch_data(f"datasets/{indicator_code}/latest", {})
        if result and "values" in result:
            return self.process_data(result, indicator_code)
        return None

    def process_data(self, raw_data: Dict, indicator_code: str) -> pd.DataFrame:
        """处理IMF API返回的数据"""
        records = []

        values = raw_data.get("values", {})
        for country_code, yearly_data in values.items():
            for year, value in yearly_data.items():
                records.append(
                    {
                        "country_code": country_code,
                        "indicator_code": indicator_code,
                        "year": year,
                        "value": value,
                        "source": "IMF",
                        "collected_at": datetime.now().isoformat(),
                    }
                )

        return pd.DataFrame(records)
