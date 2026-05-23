import streamlit as st
import pandas as pd
import numpy as np
import json
from config import *
from data_loader import *
from analytics_engine import AnalyticsEngine
from advanced_analytics_engine import AdvancedAnalyticsEngine
from narrative_engine import NarrativeEngine

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.title(APP_TITLE)
st.markdown(f"**{APP_SUBTITLE}** | 最終更新: {GENERATED_AT}")

# データロード
with st.spinner("📂 データをロード中..."):
    exec_report = load_executive_report()
    insight_specs = load_insight_specs()
    analytics = AnalyticsEngine()
    advanced_analytics = AdvancedAnalyticsEngine()
    try:
        narrative_engine = NarrativeEngine()
        analysis_available = True
    except Exception as e:
        st.warning(f"⚠️ 分析エンジン初期化エラー")
        analysis_available = False

if exec_report is None:
    st.error("❌ データが見つかりません")
    st.stop()

# ================================================================
# モード選択
analysis_mode = st.radio("**分析モード選択:**", 
    ["チャンネル全体分析", "個別動画分析"], 
    index=0, horizontal=True)

# ================================================================
# チャンネル全体分析
if analysis_mode == "チャンネル全体分析":
    st.header("📊 チャンネル全体分析")
    
    metrics = analytics.calculate_aggregate_metrics()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 品質診断", "🎨 コンテンツ分析", "💡 改善提案", "📄 レポート"])
    
    with tab1:
        st.subheader("KPI メトリクス")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均 Semantic Purity", f"{metrics.get('avg_semantic_purity', 0):.1f}")
        with col2:
            st.metric("平均 Quality Score", f"{metrics.get('avg_quality', 0):.1f}")
        with col3:
            st.metric("平均 Ranking Score", f"{metrics.get('avg_ranking', 0):.1f}")
        
        st.markdown("---")
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("総再生数", f"{metrics.get('total_views', 0):,}")
        with col5:
            st.metric("総いいね", f"{metrics.get('total_likes', 0):,}")
        with col6:
            st.metric("総コメント", f"{metrics.get('total_comments', 0):,}")
        
        st.markdown("---")
        
        if analysis_available:
            st.subheader("分析サマリー")
            with st.spinner("分析中..."):
                overview = narrative_engine.explain_channel_overview(metrics)
                st.markdown(overview)
    
    with tab2:
        st.subheader("コンテンツ分析")
        
        all_themes = {}
        for i in range(1, 6):
            themes = analytics.get_theme_distribution(i)
            if themes:
                for theme, count in themes.items():
                    all_themes[theme] = all_themes.get(theme, 0) + count
        
        if all_themes:
            theme_df = pd.Series(all_themes).sort_values(ascending=False)
            st.bar_chart(theme_df)
        
        st.markdown("---")
        
        st.subheader("講座ランキング（Quality Score）")
        lectures_dict = exec_report['lectures']
        ranking = []
        for lec_id, lec in sorted(lectures_dict.items(), 
                                  key=lambda x: x[1].get('quality_score', 0), 
                                  reverse=True):
            ranking.append({
                '順位': len(ranking) + 1,
                '講座': f"講座{lec_id}",
                'タイトル': lec.get('title', '')[:35],
                'Quality': lec.get('quality_score', 0),
                'Purity': lec.get('semantic_purity_score', 0)
            })
        
        st.dataframe(pd.DataFrame(ranking), use_container_width=True)
    
    with tab3:
        st.subheader("改善提案")
        if analysis_available:
            with st.spinner("分析中..."):
                proposal = narrative_engine.explain_channel_overview(metrics)
                st.info(proposal)
    
    with tab4:
        st.subheader("📊 チャンネル品質分析レポート")
        st.markdown(f"""
        **生成日時**: {GENERATED_AT}  
        **バージョン**: {VERSION}  
        **フェーズ**: {PHASE}
        
        ---
        
        ## エグゼクティブサマリー
        
        | メトリクス | 値 |
        |---|---|
        | 平均 Semantic Purity | {metrics.get('avg_semantic_purity', 0):.1f} |
        | 平均 Quality Score | {metrics.get('avg_quality', 0):.1f} |
        | 平均 Ranking Score | {metrics.get('avg_ranking', 0):.1f} |
        | 総再生数 | {metrics.get('total_views', 0):,} |
        | 総いいね | {metrics.get('total_likes', 0):,} |
        | 総コメント | {metrics.get('total_comments', 0):,} |
        """)
        
        st.markdown("---")
        st.subheader("講座別詳細スコア")
        
        detail_data = []
        for lec_id in sorted(lectures_dict.keys()):
            lec = lectures_dict[lec_id]
            metadata = lec.get('metadata', {})
            detail_data.append({
                '講座': f"講座{lec_id}",
                'タイトル': lec.get('title', '')[:40],
                'Semantic Purity': lec.get('semantic_purity_score', 0),
                'Quality Score': lec.get('quality_score', 0),
                'Ranking Score': lec.get('ranking_score', 0),
                '再生数': metadata.get('views', 0),
                'いいね': metadata.get('likes', 0),
                'コメント': metadata.get('comments', 0)
            })
        
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True)

        st.markdown("---")
        st.subheader("💾 レポートダウンロード")
        
        try:
            with open('data/analysis_result.json', 'r', encoding='utf-8') as f:
                analysis_result = json.load(f)
            
            from fpdf import FPDF
            from io import BytesIO
            import os
            
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            font_path = r'C:\Windows\Fonts\NotoSansJP-VF.ttf'
            if os.path.exists(font_path):
                pdf.add_font('NotoSansJP', '', font_path)
                pdf.set_font('NotoSansJP', '', 12)
            else:
                pdf.set_font('Helvetica', '', 12)
            
            pdf.set_font_size(18)
            pdf.cell(0, 15, 'YouTubeチャンネル品質分析レポート', new_x='LMARGIN', new_y='NEXT', align='C')
            pdf.set_font_size(10)
            pdf.cell(0, 8, f"生成日時: {analysis_result.get('generated_at', 'N/A')}", new_x='LMARGIN', new_y='NEXT')
            pdf.cell(0, 8, f"バージョン: {analysis_result.get('version', 'N/A')} | フェーズ: {analysis_result.get('phase', 'N/A')}", new_x='LMARGIN', new_y='NEXT')
            pdf.ln(5)
            
            pdf.set_font_size(12)
            pdf.cell(0, 8, '【チャンネル全体メトリクス】', new_x='LMARGIN', new_y='NEXT')
            pdf.set_font_size(10)
            pdf.ln(2)
            
            channel_metrics = analysis_result.get('channel_metrics', {})
            for k, v in channel_metrics.items():
                if isinstance(v, float):
                    pdf.cell(0, 6, f'{k}: {v:.2f}', new_x='LMARGIN', new_y='NEXT')
                else:
                    pdf.cell(0, 6, f'{k}: {v:,}', new_x='LMARGIN', new_y='NEXT')
            
            pdf.ln(5)
            pdf.set_font_size(12)
            pdf.cell(0, 8, '【分析対象講座一覧】', new_x='LMARGIN', new_y='NEXT')
            pdf.set_font_size(9)
            pdf.ln(2)
            
            lectures = analysis_result.get('lectures', {})
            for lid, ld in lectures.items():
                title = ld.get('title', 'N/A')[:30]
                pdf.cell(0, 6, f'講座{lid}: {title}', new_x='LMARGIN', new_y='NEXT')
            
            pdf_bytes = bytes(pdf.output())
            st.download_button('📄 PDF でダウンロード', pdf_bytes, 'report.pdf', 'application/pdf')
            
        except Exception as e:
            st.error(f'PDF生成エラー: {str(e)}')


# ================================================================
# 個別動画分析
else:
    st.header("🎥 個別動画分析")
    
    lecture_options = {f"講座{i:02d}": i for i in range(1, 6)}
    selected_label = st.selectbox("**講座を選択:**", list(lecture_options.keys()))
    lecture_num = lecture_options[selected_label]
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 基本分析", 
        "🏆 黄金の組み合わせ", 
        "⚠️ 隠れた弱点", 
        "🗺️ 心理ロードマップ",
        "🎯 競争優位性"
    ])
    
    # ========== Tab 1: 基本分析 ==========
    with tab1:
        st.subheader("動画品質メトリクス")
        
        exec_data = exec_report['lectures'].get(f"{lecture_num:02d}")
        if exec_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Semantic Purity", f"{exec_data.get('semantic_purity_score', 0):.1f}")
            with col2:
                st.metric("Quality Score", f"{exec_data.get('quality_score', 0):.1f}")
            with col3:
                st.metric("Ranking Score", f"{exec_data.get('ranking_score', 0):.1f}")
            
            st.markdown("---")
            
            metadata = exec_data.get('metadata', {})
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("再生数", f"{metadata.get('views', 0):,}")
            with col5:
                st.metric("いいね", f"{metadata.get('likes', 0):,}")
            with col6:
                st.metric("コメント", f"{metadata.get('comments', 0):,}")
        
        st.markdown("---")
        st.subheader("ビジネステーマ分布")
        themes = analytics.get_theme_distribution(lecture_num)
        if themes:
            st.bar_chart(pd.Series(themes).sort_values(ascending=False))
        
        st.markdown("---")
        st.subheader("総合評価")
        
        if analysis_available and exec_data:
            with st.spinner("分析中..."):
                engagement_metrics = analytics.get_engagement_metrics(lecture_num)
                efficiency = analytics.calculate_efficiency_score(lecture_num)
                
                prompt = f"""
                この講座の基本指標:
                - 講座ID: {lecture_num:02d}
                - タイトル: {exec_data.get('title', '')}
                - Semantic Purity: {exec_data.get('semantic_purity_score', 0):.1f}
                - Quality Score: {exec_data.get('quality_score', 0):.1f}
                - Ranking Score: {exec_data.get('ranking_score', 0):.1f}
                - 再生数: {metadata.get('views', 0):,}
                - いいね: {metadata.get('likes', 0):,} (1000再生あたり {engagement_metrics.get('likes_per_1000_views', 0):.2f})
                - コメント: {metadata.get('comments', 0):,} (1000再生あたり {engagement_metrics.get('comments_per_1000_views', 0):.2f})
                - エンゲージメント効率スコア: {efficiency:.1f}/100
                
                これらの指標から以下を分析してください:
                1) この講座の現在の位置付け（成功/課題）
                2) 視聴者層の特徴と反応傾向
                3) コンテンツとしての強み
                4) 短期的な改善ポイント
                """
                summary = narrative_engine._call_gpt(prompt)
                st.markdown(summary)
    
    # ========== Tab 2: 黄金の組み合わせ ==========
    with tab2:
        st.subheader("🏆 黄金の組み合わせ")
        st.markdown("""
        「どのファネルステージで、どのコンテンツタイプの、どのテーマが、最も視聴者反応を生むか」を特定した結果
        """)
        
        golden = advanced_analytics.detect_golden_combination(lecture_num)
        if golden:
            for i, combo in enumerate(golden[:5], 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        **#{i} パターン**
                        - **ファネルステージ**: {combo['funnel_stage']}
                        - **コンテンツタイプ**: {combo['content_type']}
                        - **テーマ**: {combo['theme']}
                        - **出現回数**: {combo['count']}回
                        """)
                    with col2:
                        st.metric("反応度", f"{combo['avg_engagement']:.2f}")
                    st.divider()
            
            if analysis_available:
                st.markdown("---")
                st.subheader("分析")
                with st.spinner("分析中..."):
                    prompt = f"""
                    この講座の高反応パターンデータ (上位3つ):
                    {json.dumps(golden[:3], ensure_ascii=False, indent=2)}
                    
                    これらのパターンについて:
                    1) なぜこれらが高反応なのか
                    2) 共通点は何か
                    3) 他のコンテンツに活かせる点は何か
                    """
                    explanation = narrative_engine._call_gpt(prompt)
                    st.markdown(explanation)
    
    # ========== Tab 3: 隠れた弱点 ==========
    with tab3:
        st.subheader("⚠️ 隠れた弱点")
        st.markdown("""
        品質は高いのにエンゲージメントが低い要素を検出
        → 改善すれば大きなリターンが期待できるポイント
        """)
        
        weaknesses = advanced_analytics.detect_hidden_weaknesses(lecture_num)
        if weaknesses:
            weakness_df = pd.DataFrame(weaknesses)
            st.dataframe(weakness_df, use_container_width=True)
            
            if analysis_available:
                st.markdown("---")
                st.subheader("改善ポイント")
                for idx, w in enumerate(weaknesses[:2], 1):
                    with st.spinner(f"分析中..."):
                        prompt = f"""
                        隠れた弱点 #{idx}:
                        - 要素ID: {w['element_id']}
                        - コンテンツ: {w['content']}
                        - 品質スコア: {w['base_purity_score']}
                        - 実際のエンゲージメント: {w['actual_engagement']}
                        - ギャップ: {w['gap']} (品質は高いが反応が低い)
                        - ファネルステージ: {w['funnel_stage']}
                        - テーマ: {w['themes']}
                        
                        なぜこのギャップが生じているのか、そして改善方法を具体的に提案してください。
                        """
                        explanation = narrative_engine._call_gpt(prompt)
                        st.markdown(explanation)
        else:
            st.info("✅ 隠れた弱点は検出されませんでした。品質とエンゲージメントのバランスが良好です。")
    
    # ========== Tab 4: 心理ロードマップ ==========
    with tab4:
        st.subheader("🗺️ 視聴者心理ロードマップ")
        st.markdown("""
        ファネルステージの推移に沿った視聴者の心理変化
        """)
        
        roadmap = advanced_analytics.generate_viewer_psychology_roadmap(lecture_num)
        if roadmap:
            for i, stage_info in enumerate(roadmap, 1):
                with st.container():
                    st.markdown(f"""
                    ### Stage {i}: **{stage_info['stage']}**
                    
                    **心理**: *"{stage_info['psychology_cue']}"*
                    
                    **段階説明**: {stage_info['description']}
                    
                    **最適コンテンツ**: {stage_info['best_content_type']}  
                    **エンゲージメント**: {stage_info['avg_engagement']:.2f}
                    
                    **推奨テーマ**: {', '.join(stage_info['recommended_themes'])}
                    """)
                    st.divider()
    
    # ========== Tab 5: 競争優位性 ==========
    with tab5:
        st.subheader("🎯 競争優位性分析")
        st.markdown("""
        この講座が他の講座と比べて何に強いか、多角的に分析
        """)
        
        advantage = advanced_analytics.calculate_competitive_advantage_score(lecture_num)
        if advantage:
            # 総合スコア
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("総合スコア", f"{advantage['total_score']:.1f}/100")
            with col2:
                st.metric("テーマ多様性", f"{advantage['theme_diversity']:.1f}%")
            with col3:
                st.metric("コンテンツ多様性", f"{advantage['content_diversity']:.1f}%")
            with col4:
                st.metric("エンゲージメント", f"{advantage['engagement_density']:.1f}%")
            
            st.markdown("---")
            
            st.markdown(f"### 📊 評価: **{advantage['interpretation']}**")
            
            # スコア表
            st.markdown(f"""
            | 指標 | スコア | 評価 |
            |---|---|---|
            | テーマ多様性 | {advantage['theme_diversity']:.1f}% | {'⭐⭐⭐' if advantage['theme_diversity'] > 70 else '⭐⭐' if advantage['theme_diversity'] > 40 else '⭐'} |
            | コンテンツ多様性 | {advantage['content_diversity']:.1f}% | {'⭐⭐⭐' if advantage['content_diversity'] > 70 else '⭐⭐' if advantage['content_diversity'] > 40 else '⭐'} |
            | エンゲージメント効率 | {advantage['engagement_density']:.1f}% | {'⭐⭐⭐' if advantage['engagement_density'] > 70 else '⭐⭐' if advantage['engagement_density'] > 40 else '⭐'} |
            | 初心者向け適性 | {advantage['beginner_suitability']:.1f}% | {'✅ 初心者向け' if advantage['beginner_suitability'] > 70 else '△ 混合' if advantage['beginner_suitability'] > 30 else '🔴 上級者向け'} |
            """)
            
            if analysis_available:
                st.markdown("---")
                st.subheader("詳細分析")
                with st.spinner("分析中..."):
                    prompt = f"""
                    この講座の競争優位性分析結果:
                    {json.dumps(advantage, ensure_ascii=False, indent=2)}
                    
                    このスコアが示す:
                    1) 強み領域は何か
                    2) 改善すべき領域は何か
                    3) 市場戦略上の位置付けは何か
                    """
                    explanation = narrative_engine._call_gpt(prompt)
                    st.markdown(explanation)
            
            # 次のステップ提案
            st.markdown("---")
            st.subheader("🎯 展開方向")
            next_steps = advanced_analytics.generate_next_step_recommendation(lecture_num)
            if next_steps:
                st.markdown(f"""
                **現在の段階**: {next_steps['current_stage']}  
                **次の段階**: {next_steps['next_stage']}
                
                **推奨テーマ**: {', '.join(next_steps['required_themes'])}
                
                **追加すべきコンテンツタイプ**: {', '.join(next_steps['missing_content_types']) if next_steps['missing_content_types'] else 'すべてのタイプが揀聘っています'}
                """)

st.markdown("---")
st.caption(f"**v{VERSION}** | {PHASE} | {GENERATED_AT}")

