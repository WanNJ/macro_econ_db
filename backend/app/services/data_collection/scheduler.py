import time
import schedule
import threading
from datetime import datetime
import logging
from typing import List, Dict
import pandas as pd
from sqlalchemy.orm import Session

from .collectors import WorldBankCollector, IMFCollector
from ...db.database import SessionLocal
from ...db import models, crud

logger = logging.getLogger(__name__)


class DataCollectionScheduler:
    """管理数据采集任务的调度器"""

    def __init__(self):
        self.wb_collector = WorldBankCollector()
        self.imf_collector = IMFCollector()

    def update_world_bank_data(self):
        """更新来自世界银行的数据"""
        logger.info(f"开始世界银行数据更新: {datetime.now()}")

        # 示例国家和指标
        countries = [
            "USA",
            "CHN",
            "DEU",
            "JPN",
            "GBR",
            "IND",
            "CAN",
            "SGP",
            "AUS",
            "FRA",
        ]
        indicators = {
            "NY.GDP.MKTP.CD": "GDP (current US$)",
            "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
            "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
            "SL.UEM.TOTL.ZS": "Unemployment, total (% of total labor force)",
            "NE.EXP.GNFS.ZS": "Exports of goods and services (% of GDP)",
        }

        for indicator_code, indicator_name in indicators.items():
            try:
                df = self.wb_collector.collect(indicator_code, countries)
                if not df.empty:
                    self._save_to_database(df, "World Bank")
                    logger.info(f"成功更新世界银行指标: {indicator_name}")
                else:
                    logger.warning(f"未获取到世界银行指标数据: {indicator_name}")
            except Exception as e:
                logger.error(f"世界银行指标 {indicator_name} 更新失败: {e}")

    def update_imf_data(self):
        """更新来自IMF的数据"""
        logger.info(f"开始IMF数据更新: {datetime.now()}")

        # 示例指标
        indicators = ["NGDP_RPCH", "PCPIPCH", "LUR", "GGXWDG_GDP"]

        for indicator_code in indicators:
            try:
                df = self.imf_collector.fetch_indicator_data(indicator_code)
                if df is not None and not df.empty:
                    self._save_to_database(df, "IMF")
                    logger.info(f"成功更新IMF指标: {indicator_code}")
                else:
                    logger.warning(f"未获取到IMF指标数据: {indicator_code}")
            except Exception as e:
                logger.error(f"IMF指标 {indicator_code} 更新失败: {e}")

    def _save_to_database(self, df: pd.DataFrame, source: str):
        """将采集的数据保存到数据库"""
        with SessionLocal() as db:
            # 获取或创建数据源
            data_source = crud.get_data_source_by_name(db, source)
            if not data_source:
                data_source = crud.create_data_source(
                    db,
                    {
                        "name": source,
                        "url": "",
                        "reliability_score": 0.9,
                        "last_updated": datetime.now(),
                    },
                )

            for _, row in df.iterrows():
                # 获取或创建国家
                country = crud.get_country_by_code(db, row["country_code"])
                if not country:
                    country = crud.create_country(
                        db,
                        {
                            "name": row["country_code"],
                            "code": row["country_code"],
                            "region": "",
                        },
                    )

                # 获取或创建指标
                indicator = crud.get_indicator_by_code(db, row["indicator_code"])
                if not indicator:
                    indicator = crud.create_indicator(
                        db,
                        {
                            "name": row["indicator_code"],
                            "code": row["indicator_code"],
                            "category": "",
                            "unit": "",
                            "description": "",
                        },
                    )

                # 创建数据点
                data_point = {
                    "country_id": country.id,
                    "indicator_id": indicator.id,
                    "date": datetime.strptime(str(row["year"]), "%Y"),
                    "value": float(row["value"]),
                    "source_id": data_source.id,
                }
                crud.create_data_point(db, data_point)

    def schedule_daily_updates(self):
        """设置每日数据更新"""
        schedule.every().day.at("02:00").do(
            self.update_world_bank_data
        )  # 凌晨2点更新世界银行数据
        schedule.every().day.at("03:00").do(self.update_imf_data)  # 凌晨3点更新IMF数据

        thread = threading.Thread(target=self._run_scheduler)
        thread.daemon = True
        thread.start()

    def _run_scheduler(self):
        """在后台线程中运行调度器"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次计划任务

    def run_initial_collection(self):
        """首次运行时执行完整数据采集"""
        logger.info("执行初始数据采集...")
        self.update_world_bank_data()
        self.update_imf_data()
        logger.info("初始数据采集完成")
