import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime


class DataAnalyzer:
    """执行数据分析并生成可视化"""

    def analyze_data(
        self, data: List[Dict[str, Any]], query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析数据并返回统计结果和可视化

        Args:
            data: 从数据库获取的数据点列表
            query_params: 包含分析参数的字典

        Returns:
            包含分析结果和可视化的字典
        """
        if not data:
            return {"error": "没有数据可供分析"}

        # 将数据转换为pandas DataFrame格式以便分析
        df = self._convert_to_dataframe(data)
        if df.empty:
            return {"error": "数据转换失败"}

        # 执行基础统计分析
        stats = self._calculate_statistics(df)

        # 生成可视化
        visualization = self._generate_visualization(df, query_params)

        # 如果请求了趋势分析，执行更深入的分析
        trend_analysis = {}
        if query_params.get("is_trend", False):
            trend_analysis = self._analyze_trends(df)

        # 如果是比较分析，添加比较信息
        comparison = {}
        if query_params.get("is_comparison", False) and len(set(df["country"])) > 1:
            comparison = self._compare_entities(df)

        return {
            "statistics": stats,
            "visualization": visualization,
            "trend_analysis": trend_analysis,
            "comparison": comparison,
        }

    def _convert_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """将API返回的数据转换为pandas DataFrame"""
        rows = []

        for series in data:
            country = series.get("country", "Unknown")
            country_code = series.get("country_code", "")
            indicator = series.get("indicator", "Unknown")
            indicator_code = series.get("indicator_code", "")
            unit = series.get("unit", "")

            for point in series.get("data", []):
                rows.append(
                    {
                        "country": country,
                        "country_code": country_code,
                        "indicator": indicator,
                        "indicator_code": indicator_code,
                        "unit": unit,
                        "date": pd.to_datetime(point.get("date")),
                        "value": point.get("value"),
                    }
                )

        return pd.DataFrame(rows)

    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算基础统计数据"""
        stats = {}

        # 按国家和指标分组计算统计数据
        grouped = df.groupby(["country", "indicator"])

        for (country, indicator), group in grouped:
            key = f"{country}_{indicator}"
            stats[key] = {
                "country": country,
                "indicator": indicator,
                "mean": group["value"].mean(),
                "median": group["value"].median(),
                "min": group["value"].min(),
                "max": group["value"].max(),
                "std": group["value"].std(),
                "count": len(group),
                "unit": group["unit"].iloc[0] if not group["unit"].empty else "",
            }

            # 计算年增长率
            if len(group) > 1:
                group_sorted = group.sort_values("date")
                if indicator.lower().find("gdp") >= 0:  # 如果是GDP类指标
                    first_value = group_sorted["value"].iloc[0]
                    last_value = group_sorted["value"].iloc[-1]
                    years = (
                        group_sorted["date"].iloc[-1] - group_sorted["date"].iloc[0]
                    ).days / 365.25
                    if years > 0 and first_value > 0:
                        cagr = (last_value / first_value) ** (1 / years) - 1
                        stats[key]["cagr"] = cagr * 100  # 转换为百分比

                # 计算近期变化率
                if len(group_sorted) >= 2:
                    latest = group_sorted["value"].iloc[-1]
                    previous = group_sorted["value"].iloc[-2]
                    if previous != 0:
                        recent_change = (latest - previous) / previous * 100
                        stats[key]["recent_change_pct"] = recent_change

        return stats

    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析数据趋势"""
        trends = {}

        # 按国家和指标分组分析趋势
        grouped = df.groupby(["country", "indicator"])

        for (country, indicator), group in grouped:
            key = f"{country}_{indicator}"
            group_sorted = group.sort_values("date")

            # 至少需要3个数据点来分析趋势
            if len(group_sorted) >= 3:
                # 简单线性回归分析趋势
                x = np.arange(len(group_sorted))
                y = group_sorted["value"].values

                if not np.isnan(y).any():  # 确保没有NaN值
                    slope, intercept = np.polyfit(x, y, 1)

                    # 判断趋势方向
                    if slope > 0:
                        trend_direction = "上升"
                    elif slope < 0:
                        trend_direction = "下降"
                    else:
                        trend_direction = "稳定"

                    # 计算趋势强度 (R方值)
                    y_pred = slope * x + intercept
                    ss_tot = np.sum((y - np.mean(y)) ** 2)
                    ss_res = np.sum((y - y_pred) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                    # 计算最近趋势 (最后3个点)
                    if len(group_sorted) >= 6:
                        recent_group = group_sorted.iloc[-6:]
                        recent_x = np.arange(len(recent_group))
                        recent_y = recent_group["value"].values
                        recent_slope, _ = np.polyfit(recent_x, recent_y, 1)

                        if recent_slope > 0:
                            recent_trend = "上升"
                        elif recent_slope < 0:
                            recent_trend = "下降"
                        else:
                            recent_trend = "稳定"
                    else:
                        recent_trend = "数据不足"

                    trends[key] = {
                        "country": country,
                        "indicator": indicator,
                        "overall_trend": trend_direction,
                        "trend_strength": r_squared,
                        "recent_trend": recent_trend,
                        "slope": slope,
                    }

                    # 检测拐点
                    # 使用简单方法：符号变化
                    diffs = np.diff(y)
                    sign_changes = np.where(np.diff(np.signbit(diffs)))[0]
                    if len(sign_changes) > 0:
                        # 转换为日期索引
                        inflection_dates = [
                            group_sorted["date"].iloc[idx + 1].strftime("%Y-%m-%d")
                            for idx in sign_changes
                        ]
                        trends[key]["inflection_points"] = inflection_dates

        return trends

    def _compare_entities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """比较不同实体（国家或指标）的数据"""
        comparison = {}

        # 确定是跨国家比较还是跨指标比较
        unique_countries = df["country"].unique()
        unique_indicators = df["indicator"].unique()

        if len(unique_countries) > 1 and len(unique_indicators) == 1:
            # 跨国家比较单一指标
            indicator = unique_indicators[0]

            # 获取最近值进行比较
            latest_values = []

            for country in unique_countries:
                country_data = df[
                    (df["country"] == country) & (df["indicator"] == indicator)
                ]
                if not country_data.empty:
                    country_data = country_data.sort_values("date")
                    latest_values.append(
                        {
                            "country": country,
                            "value": country_data["value"].iloc[-1],
                            "date": country_data["date"].iloc[-1],
                        }
                    )

            # 排序
            latest_values.sort(key=lambda x: x["value"], reverse=True)

            # 计算各国相对排名
            for i, item in enumerate(latest_values):
                item["rank"] = i + 1

            # 计算相对差异（与排名第一的国家比较）
            if latest_values:
                top_value = latest_values[0]["value"]
                for item in latest_values:
                    if top_value != 0:
                        item["difference_from_top"] = (
                            (item["value"] - top_value) / top_value * 100
                        )
                    else:
                        item["difference_from_top"] = 0

            comparison = {
                "type": "cross_country",
                "indicator": indicator,
                "rankings": latest_values,
            }

        elif len(unique_indicators) > 1 and len(unique_countries) == 1:
            # 单一国家跨指标比较
            country = unique_countries[0]

            # 这种比较可能不太有意义，因为不同指标单位不同
            # 但我们可以标准化数据进行比较
            indicator_trends = []

            for indicator in unique_indicators:
                indicator_data = df[
                    (df["country"] == country) & (df["indicator"] == indicator)
                ]
                if not indicator_data.empty:
                    indicator_data = indicator_data.sort_values("date")
                    if len(indicator_data) > 1:
                        first_value = indicator_data["value"].iloc[0]
                        last_value = indicator_data["value"].iloc[-1]
                        if first_value != 0:
                            change_pct = (last_value - first_value) / first_value * 100
                        else:
                            change_pct = (
                                float("inf") if last_value > 0 else float("-inf")
                            )

                        indicator_trends.append(
                            {
                                "indicator": indicator,
                                "first_value": first_value,
                                "last_value": last_value,
                                "change_pct": change_pct,
                            }
                        )

            # 按变化率排序
            indicator_trends.sort(key=lambda x: x["change_pct"], reverse=True)

            comparison = {
                "type": "cross_indicator",
                "country": country,
                "indicator_changes": indicator_trends,
            }

        return comparison

    def _generate_visualization(
        self, df: pd.DataFrame, query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据数据和查询参数生成可视化"""
        vis_type = query_params.get("visualization_type", "line")

        # 根据数据和查询生成适当的可视化类型
        unique_countries = df["country"].unique()
        unique_indicators = df["indicator"].unique()

        # 处理日期：确保是datetime类型并排序
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # 为每个国家和指标组合生成图表

        # 如果是单一指标多国家，生成比较图表
        if len(unique_indicators) == 1 and len(unique_countries) > 0:
            indicator = unique_indicators[0]

            if vis_type == "line":
                fig = go.Figure()

                for country in unique_countries:
                    country_data = df[
                        (df["country"] == country) & (df["indicator"] == indicator)
                    ]
                    if not country_data.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=country_data["date"],
                                y=country_data["value"],
                                mode="lines+markers",
                                name=country,
                            )
                        )

                # 更新布局
                fig.update_layout(
                    title=f"{indicator} 趋势比较",
                    xaxis_title="日期",
                    yaxis_title=(
                        df["unit"].iloc[0] if not df["unit"].empty else indicator
                    ),
                    legend_title="国家",
                    hovermode="x unified",
                )

            elif vis_type == "bar":
                # 对于柱状图，可以选择最新的数据点比较
                latest_data = []

                for country in unique_countries:
                    country_data = df[
                        (df["country"] == country) & (df["indicator"] == indicator)
                    ]
                    if not country_data.empty:
                        country_data = country_data.sort_values("date")
                        latest_data.append(
                            {
                                "country": country,
                                "value": country_data["value"].iloc[-1],
                                "date": country_data["date"].iloc[-1],
                            }
                        )

                latest_df = pd.DataFrame(latest_data)

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=latest_df["country"],
                            y=latest_df["value"],
                            text=latest_df["value"].round(2),
                            textposition="auto",
                        )
                    ]
                )

                # 更新布局
                fig.update_layout(
                    title=f"{indicator} 最新值比较",
                    xaxis_title="国家",
                    yaxis_title=(
                        df["unit"].iloc[0] if not df["unit"].empty else indicator
                    ),
                )

            elif vis_type == "scatter":
                # 对于散点图，我们可以使用年份作为大小
                fig = go.Figure()

                for country in unique_countries:
                    country_data = df[
                        (df["country"] == country) & (df["indicator"] == indicator)
                    ]
                    if not country_data.empty:
                        # 使用年份作为点的大小
                        years = [date.year for date in country_data["date"]]
                        sizes = [(year - min(years) + 5) * 2 for year in years]

                        fig.add_trace(
                            go.Scatter(
                                x=country_data["date"],
                                y=country_data["value"],
                                mode="markers",
                                name=country,
                                marker=dict(size=sizes),
                            )
                        )

                # 更新布局
                fig.update_layout(
                    title=f"{indicator} 散点图",
                    xaxis_title="日期",
                    yaxis_title=(
                        df["unit"].iloc[0] if not df["unit"].empty else indicator
                    ),
                    legend_title="国家",
                )

            else:  # 默认为线图
                fig = go.Figure()

                for country in unique_countries:
                    country_data = df[
                        (df["country"] == country) & (df["indicator"] == indicator)
                    ]
                    if not country_data.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=country_data["date"],
                                y=country_data["value"],
                                mode="lines+markers",
                                name=country,
                            )
                        )

                # 更新布局
                fig.update_layout(
                    title=f"{indicator} 趋势",
                    xaxis_title="日期",
                    yaxis_title=(
                        df["unit"].iloc[0] if not df["unit"].empty else indicator
                    ),
                    legend_title="国家",
                    hovermode="x unified",
                )

        # 如果是单一国家多指标，生成并排图表
        elif len(unique_countries) == 1 and len(unique_indicators) > 0:
            country = unique_countries[0]

            # 创建子图
            fig = make_subplots(
                rows=len(unique_indicators),
                cols=1,
                subplot_titles=[
                    f"{indicator} ({country})" for indicator in unique_indicators
                ],
                shared_xaxes=True,
                vertical_spacing=0.1,
            )

            for i, indicator in enumerate(unique_indicators):
                indicator_data = df[
                    (df["country"] == country) & (df["indicator"] == indicator)
                ]
                if not indicator_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=indicator_data["date"],
                            y=indicator_data["value"],
                            mode="lines+markers",
                            name=indicator,
                        ),
                        row=i + 1,
                        col=1,
                    )

                    # 添加y轴标题
                    fig.update_yaxes(
                        title_text=(
                            indicator_data["unit"].iloc[0]
                            if not indicator_data["unit"].empty
                            else indicator
                        ),
                        row=i + 1,
                        col=1,
                    )

            # 更新布局
            fig.update_layout(
                title_text=f"{country} 多指标分析",
                height=300 * len(unique_indicators),  # 动态调整高度
                showlegend=False,
                hovermode="x unified",
            )

            # 只为最底部的子图添加x轴标题
            fig.update_xaxes(title_text="日期", row=len(unique_indicators), col=1)

        else:
            # 默认图表
            fig = go.Figure()

            for country in unique_countries:
                for indicator in unique_indicators:
                    data_subset = df[
                        (df["country"] == country) & (df["indicator"] == indicator)
                    ]
                    if not data_subset.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=data_subset["date"],
                                y=data_subset["value"],
                                mode="lines+markers",
                                name=f"{country} - {indicator}",
                            )
                        )

            # 更新布局
            fig.update_layout(
                title="多指标多国家数据",
                xaxis_title="日期",
                yaxis_title="值",
                legend_title="指标和国家",
                hovermode="x unified",
            )

        # 保存为HTML或JSON格式
        plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        plot_json = json.loads(fig.to_json())

        return {"plot_html": plot_html, "plot_json": plot_json, "vis_type": vis_type}
