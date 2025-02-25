import re
from typing import Dict, List, Tuple, Optional, Any
import logging
import os
from datetime import datetime, timedelta

# 如果使用Hugging Face
from transformers import pipeline

# 如果使用OpenAI (取决于预算和性能需求)
# import openai
# openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)


class QueryParser:
    """
    将自然语言查询解析为结构化查询参数
    """

    def __init__(self):
        """初始化查询解析器"""
        # 使用Hugging Face的命名实体识别
        try:
            self.ner_pipeline = pipeline(
                "ner", model="dbmdz/bert-large-cased-finetuned-conll03-english"
            )
        except Exception as e:
            logger.error(f"无法加载NER模型: {e}")
            self.ner_pipeline = None

        # 国家名称映射 (部分示例)
        self.country_map = {
            "中国": "CHN",
            "china": "CHN",
            "中华人民共和国": "CHN",
            "美国": "USA",
            "united states": "USA",
            "america": "USA",
            "us": "USA",
            "印度": "IND",
            "india": "IND",
            "日本": "JPN",
            "japan": "JPN",
            "德国": "DEU",
            "germany": "DEU",
            "法国": "FRA",
            "france": "FRA",
            "英国": "GBR",
            "uk": "GBR",
            "united kingdom": "GBR",
            "加拿大": "CAN",
            "canada": "CAN",
            "澳大利亚": "AUS",
            "australia": "AUS",
            "新加坡": "SGP",
            "singapore": "SGP",
        }

        # 经济指标映射 (部分示例)
        self.indicator_map = {
            "gdp": "NY.GDP.MKTP.CD",
            "人均gdp": "NY.GDP.PCAP.CD",
            "人均国内生产总值": "NY.GDP.PCAP.CD",
            "人均国民生产总值": "NY.GDP.PCAP.CD",
            "通胀率": "FP.CPI.TOTL.ZG",
            "cpi": "FP.CPI.TOTL.ZG",
            "消费者物价指数": "FP.CPI.TOTL.ZG",
            "失业率": "SL.UEM.TOTL.ZS",
            "unemployment": "SL.UEM.TOTL.ZS",
            "出口": "NE.EXP.GNFS.ZS",
            "exports": "NE.EXP.GNFS.ZS",
            "基准利率": "FR.INR.RINR",
            "interest rate": "FR.INR.RINR",
            "人口": "SP.POP.TOTL",
            "population": "SP.POP.TOTL",
            "负债率": "GC.DOD.TOTL.GD.ZS",
            "debt to gdp": "GC.DOD.TOTL.GD.ZS",
        }

    def extract_countries(self, query: str) -> List[str]:
        """从查询中提取国家信息"""
        countries = []

        # 尝试直接匹配国家名称
        for country_name, code in self.country_map.items():
            if country_name.lower() in query.lower() and code not in countries:
                countries.append(code)

        # 使用NER进一步识别可能的国家名称
        if self.ner_pipeline and not countries:
            try:
                entities = self.ner_pipeline(query)
                for entity in entities:
                    if entity["entity"].startswith("B-LOC") or entity[
                        "entity"
                    ].startswith("I-LOC"):
                        entity_text = entity["word"].lower()
                        for country_name, code in self.country_map.items():
                            if (
                                entity_text in country_name.lower()
                                and code not in countries
                            ):
                                countries.append(code)
            except Exception as e:
                logger.error(f"NER处理错误: {e}")

        return countries

    def extract_indicators(self, query: str) -> List[str]:
        """从查询中提取经济指标"""
        indicators = []

        # 匹配指标名称
        for indicator_name, code in self.indicator_map.items():
            if indicator_name.lower() in query.lower() and code not in indicators:
                indicators.append(code)

        return indicators

    def extract_time_period(
        self, query: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """从查询中提取时间范围"""
        # 匹配年份
        year_pattern = r"\b(19|20)\d{2}\b"
        years = re.findall(year_pattern, query)
        years = [int(year) for year in years]

        # 匹配时间范围描述
        current_year = datetime.now().year

        start_date = None
        end_date = None

        # 如果找到具体年份
        if len(years) == 1:
            # 单个年份可能是起始年或特定年
            if "以来" in query or "since" in query.lower():
                start_date = datetime(years[0], 1, 1)
                end_date = datetime(current_year, 12, 31)
            else:
                # 假设是查询特定年份
                start_date = datetime(years[0], 1, 1)
                end_date = datetime(years[0], 12, 31)
        elif len(years) >= 2:
            # 多个年份，使用最小和最大值作为范围
            years.sort()
            start_date = datetime(years[0], 1, 1)
            end_date = datetime(years[-1], 12, 31)
        else:
            # 没有具体年份，查找常见的时间范围表达
            if "过去十年" in query or "last decade" in query.lower():
                start_date = datetime(current_year - 10, 1, 1)
                end_date = datetime(current_year, 12, 31)
            elif (
                "过去五年" in query
                or "last five years" in query.lower()
                or "past 5 years" in query.lower()
            ):
                start_date = datetime(current_year - 5, 1, 1)
                end_date = datetime(current_year, 12, 31)
            elif "去年" in query or "last year" in query.lower():
                start_date = datetime(current_year - 1, 1, 1)
                end_date = datetime(current_year - 1, 12, 31)

        # 默认返回过去10年的数据
        if not start_date and not end_date:
            start_date = datetime(current_year - 10, 1, 1)
            end_date = datetime(current_year, 12, 31)

        return start_date, end_date

    def detect_comparison(self, query: str) -> bool:
        """检测查询是否为国家间的比较"""
        comparison_terms = [
            "比较",
            "compare",
            "对比",
            "versus",
            "vs",
            "相比",
            "compared to",
            "comparison",
            "与",
            "和",
            "及",
            "比",
        ]

        # 如果有比较词汇，且有多个国家，则可能是进行比较
        for term in comparison_terms:
            if term in query.lower():
                return True

        return False

    def detect_trend_analysis(self, query: str) -> bool:
        """检测查询是否要求趋势分析"""
        trend_terms = [
            "趋势",
            "trend",
            "变化",
            "change",
            "增长",
            "growth",
            "演变",
            "evolution",
            "发展",
            "development",
            "历史",
            "history",
        ]

        for term in trend_terms:
            if term in query.lower():
                return True

        return False

    def detect_visualization_type(self, query: str) -> str:
        """检测用户可能想要的可视化类型"""
        if "柱状图" in query or "bar chart" in query.lower() or "柱图" in query:
            return "bar"
        elif "饼图" in query or "pie chart" in query.lower():
            return "pie"
        elif "散点图" in query or "scatter" in query.lower():
            return "scatter"
        elif "热力图" in query or "heat map" in query.lower():
            return "heatmap"
        else:
            # 默认使用折线图，适合时间序列数据
            return "line"

    def parse_query(self, query: str) -> Dict[str, Any]:
        """解析自然语言查询，返回结构化查询参数"""
        try:
            countries = self.extract_countries(query)
            indicators = self.extract_indicators(query)
            start_date, end_date = self.extract_time_period(query)
            is_comparison = self.detect_comparison(query)
            is_trend = self.detect_trend_analysis(query)
            visualization_type = self.detect_visualization_type(query)

            # 如果没有识别出国家，使用默认国家列表
            if not countries:
                countries = ["CHN", "USA"]  # 默认中国和美国

            # 如果没有识别出指标，使用默认指标
            if not indicators:
                indicators = ["NY.GDP.MKTP.CD"]  # 默认GDP

            result = {
                "countries": countries,
                "indicators": indicators,
                "start_date": start_date,
                "end_date": end_date,
                "is_comparison": is_comparison,
                "is_trend": is_trend,
                "visualization_type": visualization_type,
                "original_query": query,
            }

            return result
        except Exception as e:
            logger.error(f"查询解析错误: {e}")
            # 返回一个基本的默认查询
            return {
                "countries": ["CHN", "USA"],
                "indicators": ["NY.GDP.MKTP.CD"],
                "start_date": datetime.now() - timedelta(days=365 * 10),
                "end_date": datetime.now(),
                "is_comparison": False,
                "is_trend": True,
                "visualization_type": "line",
                "original_query": query,
                "error": str(e),
            }
