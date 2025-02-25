from typing import Dict, List, Any
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import json


class ReportGenerator:
    """生成数据分析报告"""

    def generate_report(
        self, analysis_result: Dict[str, Any], query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据分析结果生成报告"""
        report = {
            "title": self._generate_title(query),
            "summary": self._generate_summary(analysis_result, query),
            "key_findings": self._extract_key_findings(analysis_result),
            "data_tables": self._prepare_data_tables(analysis_result),
            "charts": analysis_result.get("visualization", {}),
            "timestamp": datetime.now().isoformat(),
            "query_details": query,
        }

        return report

    def _generate_title(self, query: Dict[str, Any]) -> str:
        """基于查询生成报告标题"""
        countries = query.get("countries", [])
        indicators = query.get("indicators", [])

        country_str = "全球" if not countries else "、".join(countries)
        indicator_str = "宏观经济指标" if not indicators else "、".join(indicators)

        # 确定时间范围
        start_date = query.get("start_date")
        end_date = query.get("end_date")

        if start_date and end_date:
            time_str = f"{start_date.year}-{end_date.year}年"
        elif start_date:
            time_str = f"{start_date.year}年至今"
        elif end_date:
            time_str = f"截至{end_date.year}年"
        else:
            time_str = ""

        return f"{country_str} {indicator_str} {time_str}分析报告"

    def _generate_summary(
        self, analysis_result: Dict[str, Any], query: Dict[str, Any]
    ) -> str:
        """生成报告摘要"""
        # 获取基本信息
        countries = query.get("countries", [])
        indicators = query.get("indicators", [])

        summary_parts = []

        # 基本介绍
        intro = f"本报告分析了"
        if countries:
            intro += f"{', '.join(countries)}的"
        if indicators:
            indicator_names = []
            stats = analysis_result.get("statistics", {})
            for key, value in stats.items():
                if "indicator" in value and value["indicator"] not in indicator_names:
                    indicator_names.append(value["indicator"])
            if indicator_names:
                intro += f"{', '.join(indicator_names)}"
            else:
                intro += f"经济指标数据"

        start_date = query.get("start_date")
        end_date = query.get("end_date")
        if start_date and end_date:
            intro += f"在{start_date.year}年至{end_date.year}年期间的表现。"
        elif start_date:
            intro += f"从{start_date.year}年至今的表现。"
        elif end_date:
            intro += f"截至{end_date.year}年的表现。"
        else:
            intro += "的历史表现。"

        summary_parts.append(intro)

        # 关键统计数据
        stats_summary = []
        stats = analysis_result.get("statistics", {})
        for key, value in stats.items():
            country = value.get("country", "")
            indicator = value.get("indicator", "")
            mean = value.get("mean")
            latest = None

            # 尝试从可视化数据中获取最新值
            if "data" in analysis_result and analysis_result["data"]:
                for series in analysis_result["data"]:
                    if (
                        series.get("country") == country
                        and series.get("indicator") == indicator
                    ):
                        data_points = series.get("data", [])
                        if data_points:
                            latest_point = sorted(
                                data_points, key=lambda x: x.get("date", "")
                            )[-1]
                            latest = latest_point.get("value")

            unit = value.get("unit", "")
            unit_str = f" {unit}" if unit else ""

            if mean is not None:
                stats_summary.append(
                    f"{country}的{indicator}平均值为{mean:.2f}{unit_str}"
                )

            if latest is not None:
                stats_summary.append(
                    f"{country}的最新{indicator}为{latest:.2f}{unit_str}"
                )

        if stats_summary:
            summary_parts.append("主要统计数据显示，" + "；".join(stats_summary) + "。")

        # 趋势信息
        trend_summary = []
        trends = analysis_result.get("trend_analysis", {})
        for key, value in trends.items():
            country = value.get("country", "")
            indicator = value.get("indicator", "")
            overall_trend = value.get("overall_trend", "")
            recent_trend = value.get("recent_trend", "")

            if overall_trend:
                trend_summary.append(f"{country}的{indicator}总体呈{overall_trend}趋势")

            if recent_trend and recent_trend != "数据不足":
                trend_summary.append(f"{country}的{indicator}近期呈{recent_trend}趋势")

        if trend_summary:
            summary_parts.append("趋势分析表明，" + "；".join(trend_summary) + "。")

        # 比较信息
        comparison = analysis_result.get("comparison", {})
        if comparison:
            comparison_type = comparison.get("type", "")

            if comparison_type == "cross_country":
                rankings = comparison.get("rankings", [])
                if rankings:
                    top_country = rankings[0].get("country", "")
                    indicator = comparison.get("indicator", "")
                    comparison_summary = f"在{indicator}方面，{top_country}表现最好"

                    if len(rankings) > 1:
                        bottom_country = rankings[-1].get("country", "")
                        comparison_summary += f"，而{bottom_country}表现相对较弱"

                    summary_parts.append(comparison_summary + "。")

            elif comparison_type == "cross_indicator":
                country = comparison.get("country", "")
                changes = comparison.get("indicator_changes", [])
                if changes:
                    fastest_growing = changes[0].get("indicator", "")
                    change_pct = changes[0].get("change_pct")

                    if change_pct is not None:
                        if change_pct > 0:
                            comparison_summary = f"对于{country}而言，{fastest_growing}增长最快，增幅达{change_pct:.2f}%"
                        else:
                            comparison_summary = f"对于{country}而言，{fastest_growing}下降最显著，降幅达{abs(change_pct):.2f}%"

                        summary_parts.append(comparison_summary + "。")

        # 将所有部分组合为完整摘要
        return " ".join(summary_parts)

    def _extract_key_findings(self, analysis_result: Dict[str, Any]) -> List[str]:
        """提取分析结果中的关键发现"""
        findings = []

        # 从统计数据中提取
        stats = analysis_result.get("statistics", {})
        for key, value in stats.items():
            country = value.get("country", "")
            indicator = value.get("indicator", "")

            # 查找极值
            max_val = value.get("max")
            min_val = value.get("min")
            recent_change_pct = value.get("recent_change_pct")

            unit = value.get("unit", "")
            unit_str = f" {unit}" if unit else ""

            if max_val is not None and min_val is not None:
                findings.append(
                    f"{country}的{indicator}在分析期间最高达到{max_val:.2f}{unit_str}，最低为{min_val:.2f}{unit_str}"
                )

            # 查找显著变化
            if recent_change_pct is not None:
                if abs(recent_change_pct) > 10:  # 显著变化阈值
                    change_direction = "增长" if recent_change_pct > 0 else "下降"
                    findings.append(
                        f"{country}的{indicator}最近{change_direction}了{abs(recent_change_pct):.2f}%"
                    )

        # 从趋势分析中提取
        trends = analysis_result.get("trend_analysis", {})
        for key, value in trends.items():
            country = value.get("country", "")
            indicator = value.get("indicator", "")

            # 拐点信息
            inflection_points = value.get("inflection_points", [])
            if inflection_points:
                findings.append(
                    f"{country}的{indicator}在{', '.join(inflection_points)}出现趋势拐点"
                )

            # 显著趋势
            trend_strength = value.get("trend_strength")
            overall_trend = value.get("overall_trend", "")

            if (
                trend_strength is not None and trend_strength > 0.7 and overall_trend
            ):  # 强趋势阈值
                findings.append(
                    f"{country}的{indicator}呈现强烈的{overall_trend}趋势，相关性达{trend_strength:.2f}"
                )

            # 最近趋势与总体趋势的差异
            recent_trend = value.get("recent_trend", "")
            if (
                recent_trend
                and recent_trend != "数据不足"
                and recent_trend != overall_trend
            ):
                findings.append(
                    f"{country}的{indicator}总体趋势为{overall_trend}，但近期趋势转为{recent_trend}"
                )

        # 从比较中提取
        comparison = analysis_result.get("comparison", {})
        if comparison:
            comparison_type = comparison.get("type", "")

            if comparison_type == "cross_country":
                rankings = comparison.get("rankings", [])
                indicator = comparison.get("indicator", "")

                if len(rankings) >= 2:
                    top_country = rankings[0].get("country", "")
                    top_value = rankings[0].get("value")
                    second_country = rankings[1].get("country", "")
                    second_value = rankings[1].get("value")

                    if top_value is not None and second_value is not None:
                        diff_pct = (
                            ((top_value - second_value) / second_value) * 100
                            if second_value != 0
                            else float("inf")
                        )
                        findings.append(
                            f"在{indicator}方面，{top_country}领先{second_country} {abs(diff_pct):.2f}%"
                        )

            elif comparison_type == "cross_indicator":
                country = comparison.get("country", "")
                changes = comparison.get("indicator_changes", [])

                if len(changes) >= 2:
                    best_indicator = changes[0].get("indicator", "")
                    worst_indicator = changes[-1].get("indicator", "")

                    findings.append(
                        f"对于{country}，{best_indicator}表现最佳，而{worst_indicator}表现相对较弱"
                    )

        return findings

    def _prepare_data_tables(
        self, analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """准备报告中的数据表格"""
        tables = []

        # 把原始数据转换为表格形式
        if "data" in analysis_result:
            data = analysis_result["data"]
            for series in data:
                country = series.get("country", "")
                indicator = series.get("indicator", "")

                # 数据点
                data_points = series.get("data", [])
                if data_points:
                    rows = []
                    for point in data_points:
                        rows.append(
                            {
                                "date": point.get("date", ""),
                                "value": point.get("value", "N/A"),
                            }
                        )

                    tables.append(
                        {
                            "title": f"{country} - {indicator}",
                            "headers": ["日期", f"{indicator}值"],
                            "rows": rows,
                        }
                    )

        # 统计数据表
        stats = analysis_result.get("statistics", {})
        if stats:
            stat_rows = []
            for key, value in stats.items():
                stat_rows.append(
                    {
                        "country": value.get("country", ""),
                        "indicator": value.get("indicator", ""),
                        "mean": value.get("mean", "N/A"),
                        "median": value.get("median", "N/A"),
                        "min": value.get("min", "N/A"),
                        "max": value.get("max", "N/A"),
                    }
                )

            tables.append(
                {
                    "title": "统计数据摘要",
                    "headers": ["国家", "指标", "平均值", "中位数", "最小值", "最大值"],
                    "rows": stat_rows,
                }
            )

        return tables
