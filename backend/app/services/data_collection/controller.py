from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime

from .collectors import WorldBankCollector, IMFCollector

logger = logging.getLogger(__name__)


class DataCollectionController:
    """管理数据采集过程"""

    def __init__(self):
        self.wb_collector = WorldBankCollector()
        self.imf_collector = IMFCollector()

    def collect_world_bank_data(
        self, db: Session, indicators: List[str] = None, countries: List[str] = None
    ) -> bool:
        """从世界银行收集数据"""
        logger.info(f"开始收集世界银行数据: {datetime.now()}")

        if not indicators:
            indicators = [
                "NY.GDP.MKTP.CD",  # GDP (current US$)
                "NY.GDP.PCAP.CD",  # GDP per capita (current US$)
                "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
                "SL.UEM.TOTL.ZS",  # Unemployment, total (% of labor force)
                "SP.POP.TOTL",  # Population, total
            ]

        if not countries:
            countries = ["CHN", "USA", "JPN", "DEU", "GBR"]

        try:
            result = self.wb_collector.collect(db, indicators, countries)
            logger.info(
                f"世界银行数据采集完成: {datetime.now()}, 结果: {'成功' if result else '失败'}"
            )
            return result
        except Exception as e:
            logger.error(f"世界银行数据采集失败: {e}")
            return False

    def run_data_collection(self, db: Session) -> Dict[str, bool]:
        """运行所有数据采集器"""
        results = {}

        # 世界银行数据
        wb_result = self.collect_world_bank_data(db)
        results["world_bank"] = wb_result

        # IMF数据 (待实现)
        results["imf"] = False

        return results
