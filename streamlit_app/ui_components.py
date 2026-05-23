# ui_components.py - UI コンポーネント

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLOR_PALETTE, SCORE_LEVELS
from data_loader import get_score_level

def render_metric_card(label, value, color="primary"):
    """メトリクス カードを描画"""
    st.metric(label, value)

def render_kpi_section(metrics):
    """KPI セクションを描画"""
    st.subheader("📈 主要パフォーマンス指標（KPI）")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("🎬 講座数", metrics["講座数"])
    with col2:
        st.metric("👀 総ビュー数", f"{metrics['総ビュー数']:,}")
    with col3:
        st.metric("👍 総いいね数", f"{metrics['総いいね数']:,}")
    with col4:
        st.metric("💬 総コメント数", f"{metrics['総コメント数']:,}")
    with col5:
        st.metric("⭐ 平均品質", f"{metrics['平均品質スコア']:.2f}")
    with col6:
        st.metric("🔬 平均セマンティック", f"{metrics['平均セマンティック純度']:.2f}")

def render_score_metrics(sem_purity, quality, ranking):
    """3つのスコアメトリクスを表示"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        level = get_score_level(sem_purity)
        st.metric(
            "🎯 セマンティック純度スコア",
            f"{sem_purity:.1f}/100",
            delta=level["label"]
        )
    
    with col2:
        level = get_score_level(quality)
        st.metric(
            "📊 クオリティスコア",
            f"{quality:.1f}/100",
            delta=level["label"]
        )
    
    with col3:
        level = get_score_level(ranking)
        st.metric(
            "🏆 ランキングスコア",
            f"{ranking:.1f}/100",
            delta=level["label"]
        )

def render_lecture_comparison_chart(df_exec):
    """講座スコア比較チャートを描画"""
    st.subheader("📊 講座スコア比較")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_exec["講座ID"],
        y=df_exec["品質スコア"],
        name="品質スコア",
        marker_color=COLOR_PALETTE["primary"]
    ))
    
    fig.add_trace(go.Bar(
        x=df_exec["講座ID"],
        y=df_exec["セマンティック純度スコア"],
        name="セマンティック純度",
        marker_color=COLOR_PALETTE["success"]
    ))
    
    fig.add_trace(go.Bar(
        x=df_exec["講座ID"],
        y=df_exec["ランキングスコア"],
        name="ランキングスコア",
        marker_color=COLOR_PALETTE["warning"]
    ))
    
    fig.update_layout(
        title="講座別スコア比較",
        xaxis_title="講座",
        yaxis_title="スコア",
        barmode="group",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_engagement_chart(df_exec):
    """エンゲージメント分析チャートを描画"""
    st.subheader("💬 エンゲージメント分析")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_exec["講座ID"],
        y=df_exec["ビュー数"],
        mode="lines+markers",
        name="ビュー数",
        line=dict(color=COLOR_PALETTE["primary"], width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_exec["講座ID"],
        y=df_exec["いいね数"],
        mode="lines+markers",
        name="いいね数",
        line=dict(color=COLOR_PALETTE["success"], width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_exec["講座ID"],
        y=df_exec["コメント数"],
        mode="lines+markers",
        name="コメント数",
        line=dict(color=COLOR_PALETTE["warning"], width=2)
    ))
    
    fig.update_layout(
        title="講座別エンゲージメント推移",
        xaxis_title="講座",
        yaxis_title="エンゲージメント数",
        hovermode="x unified",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_theme_distribution_chart(theme_df):
    """テーマ分布チャートを描画"""
    st.subheader("🎯 テーマ分布")
    
    fig = px.bar(
        theme_df,
        x="テーマ名",
        y="出現件数",
        color="出現件数",
        color_continuous_scale="Blues",
        height=400
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def render_score_comparison_chart(scores_dict):
    """スコア比較チャート"""
    fig = go.Figure(data=[
        go.Bar(x=list(scores_dict.keys()), y=list(scores_dict.values()))
    ])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

