import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.env_loader import ensure_env_loaded, is_demo_mode
ensure_env_loaded()

import streamlit as st
import pandas as pd
import numpy as np
import json
from streamlit_app.config import *
from streamlit_app.data_loader import *
from streamlit_app.config import DATA_DIR, SCORE_LEVELS, VIS_MODE
from streamlit_app.analytics_engine import AnalyticsEngine
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from converter.executive_summary_formatter import ExecutiveSummaryFormatter
from streamlit_app.advanced_analytics_engine import AdvancedAnalyticsEngine
from streamlit_app.narrative_engine import NarrativeEngine

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.title(APP_TITLE)
if st.button("🔄 キャッシュクリア"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()
st.markdown(f"**{APP_SUBTITLE}** | 最終更新: {GENERATED_AT}")

# モード表示
import os
from streamlit_app.config import VIS_MODE

st.sidebar.info(f"""
🔍 **デバッグ情報**
- VIS_MODE: {VIS_MODE}
- os.getenv('VIS_MODE'): {os.getenv('VIS_MODE', 'not set')}
""")

if VIS_MODE == "free_trial":
    st.sidebar.info("📊 モード: 無料1本解析（Free Trial Demo）")
else:
    st.sidebar.info("📊 モード: 通常（Normal）")

def get_quality_label(score):
    if score is None: return "データ準備中"
    if score >= 80: return f"{score:.1f} (優秀)"
    if score >= 60: return f"{score:.1f} (良好)"
    if score >= 40: return f"{score:.1f} (標準)"
    return f"{score:.1f} (要改善)"

if is_demo_mode():
    st.info(
        "ℹ️ **デモ環境**: サンプルデータによる分析結果をご覧いただけます。"
        "（新規分析機能は制限されています）"
    )

# データロード
with st.spinner("🔄 データをロード中..."):
    from streamlit_app.config import VIS_MODE
    exec_report = load_executive_report()
    insight_specs = load_insight_specs()
    analytics = AnalyticsEngine()
    advanced_analytics = AdvancedAnalyticsEngine()
    try:
        narrative_engine = NarrativeEngine()
        analysis_available = getattr(narrative_engine, 'available', True)
        if not analysis_available and not is_demo_mode():
            st.warning("⚠️ OPENAI_API_KEY が未設定のため、AI分析機能は制限されています")
    except Exception as e:
        if not is_demo_mode():
            st.warning(f"⚠️ 分析エンジン初期化エラー: {e}")
        analysis_available = False

if not exec_report or 'lectures' not in exec_report:
    st.warning("⚠️ 講座データが見つかりません。")
    # フォールバック処理で必ず生成されるためここは通常通り通過します

lectures_dict = exec_report.get('lectures', {}) if exec_report else {}

# ================================================================
# モード選択
analysis_mode = st.radio("**分析モード選択:**", 
    ["チャンネル全体分析", "個別動画分析"], 
    index=0, horizontal=True)

# ================================================================
# チャンネル全体分析
if analysis_mode == "チャンネル全体分析":
    st.header("📊 チャンネル全体分析" if VIS_MODE != "free_trial" else "📊 チャンネル・動画総合分析")
    
    metrics = analytics.calculate_aggregate_metrics()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 品質診断", "🎨 コンテンツ分析", "💡 改善提案", "📄 レポート", "🎯 競合分析サマリー"])
    
    with tab1:
        st.subheader("📝 チャンネルの現状とサマリー")
        if analysis_available:
            # 既に生成済みのai_analysis.jsonを使用する
            diagnosis_text = None
            if VIS_MODE == "free_trial" and lectures_dict:
                from streamlit_app.config import FREE_TRIAL_DELIVERABLES
                first_key = list(lectures_dict.keys())[0]
                ai_analysis_file = FREE_TRIAL_DELIVERABLES / first_key / "ai_analysis.json"
                if ai_analysis_file.exists():
                    import json
                    with open(ai_analysis_file, "r", encoding="utf-8") as f:
                        ai_data = json.load(f)
                        diagnosis_text = ai_data.get('diagnosis')
            
            if diagnosis_text:
                st.info(diagnosis_text)
            else:
                with st.spinner("診断中..."):
                    diagnosis = narrative_engine.explain_channel_diagnosis(list(insight_specs.values()))
                    st.info(diagnosis)
        else:
            st.info("💡 **【総合評価】** 高い品質を維持していますが、まだ改善の余地があります。以下のKPIに基づき次のアクションを検討してください。")
            
        st.markdown("---")
        st.subheader("📊 根拠となる主要KPI")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            val = metrics.get('avg_semantic_purity')
            st.metric("平均 Semantic Purity", f"{val:.1f}" if val is not None else "データ準備中")
        with col2:
            val = metrics.get('avg_quality')
            st.metric("平均 Quality Score", get_quality_label(val))
        with col3:
            val = metrics.get('avg_ranking')
            st.metric("平均 Ranking Score", "データ準備中")
        
        st.markdown("---")
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("総再生数", f"{metrics.get('total_views', 0):,}")
        with col5:
            st.metric("総いいね", f"{metrics.get('total_likes', 0):,}")
        with col6:
            st.metric("総コメント", f"{metrics.get('total_comments', 0):,}")
    
    with tab2:
        if VIS_MODE != "free_trial":
            st.subheader("📈 AI チャンネル全体分析")
            
            selected_lecture = list(insight_specs.values())[0] if insight_specs else {}
            st.write("### デバッグ: 現在のデータ")
            st.json({
                "lecture_id": selected_lecture.get("video_meta", {}).get("video_id", "Unknown"),
                "title": selected_lecture.get("video_meta", {}).get("title", "Unknown"),
                "metadata": selected_lecture.get("views", {}).get("competitive", {}).get("metrics", {}),
                "quality_score": selected_lecture.get("quality_score")
            })

            if analysis_available:
                with st.spinner("分析中..."):
                    overview = narrative_engine.explain_channel_overview(list(insight_specs.values()), metrics=metrics)
                    st.info(overview)
            else:
                st.info("ℹ️ 分析データがありません。")
                
            st.markdown("---")
        
        st.subheader("コンテンツ分析（定量）")
        
        all_themes = {}
        for key in lectures_dict.keys():
            themes = analytics.get_theme_distribution(key)
            if themes:
                for theme, count in themes.items():
                    all_themes[theme] = all_themes.get(theme, 0) + count
        
        if all_themes:
            theme_df = pd.Series(all_themes).sort_values(ascending=False)
            st.bar_chart(theme_df)
        
        st.markdown("---")
        
        st.subheader("講座ランキング（Quality Score）")
        ranking = []
        for lec_id, lec in sorted(lectures_dict.items(), 
                                  key=lambda x: x[1].get('quality_score') or 0, 
                                  reverse=True):
            ranking.append({
                '順位': len(ranking) + 1,
                '講座': f"講座{lec_id}",
                'タイトル': lec.get('title', '')[:35],
                'Quality': get_quality_label(lec.get('quality_score')),
                'Purity': f"{lec.get('semantic_purity_score'):.1f}" if lec.get('semantic_purity_score') is not None else "データ準備中"
            })
        
        st.dataframe(pd.DataFrame(ranking), use_container_width=True)
    
    with tab3:
        st.subheader("改善提案")
        if analysis_available:
            improvements_text = None
            if VIS_MODE == "free_trial" and lectures_dict:
                from streamlit_app.config import FREE_TRIAL_DELIVERABLES
                first_key = list(lectures_dict.keys())[0]
                ai_analysis_file = FREE_TRIAL_DELIVERABLES / first_key / "ai_analysis.json"
                if ai_analysis_file.exists():
                    import json
                    with open(ai_analysis_file, "r", encoding="utf-8") as f:
                        ai_data = json.load(f)
                        improvements_text = ai_data.get('improvements')
                
            if improvements_text:
                st.info(improvements_text)
            else:
                with st.spinner("改善案を生成中..."):
                    improvements = narrative_engine.explain_channel_improvements(list(insight_specs.values()))
                    st.info(improvements)
    
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
        | 平均 Semantic Purity | {f"{metrics.get('avg_semantic_purity'):.1f}" if metrics.get('avg_semantic_purity') is not None else "未算出"} |
        | 平均 Quality Score | {f"{metrics.get('avg_quality'):.1f}" if metrics.get('avg_quality') is not None else "未算出"} |
        | 平均 Ranking Score | {f"{metrics.get('avg_ranking'):.1f}" if metrics.get('avg_ranking') is not None else "未算出"} |
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
                'Semantic Purity': f"{lec.get('semantic_purity_score'):.1f}" if lec.get('semantic_purity_score') is not None else "データ準備中",
                'Quality Score': get_quality_label(lec.get('quality_score')),
                'Ranking Score': "データ準備中",
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
            
    with tab5:
        st.subheader("🎯 競合分析エグゼクティブサマリー")
        
        if VIS_MODE == "free_trial":
            st.info("💡 無料1本解析では、対象動画の強み・弱みと改善提案を【品質診断】【改善提案】タブでご確認ください。")
        else:
            # 最新の競合分析データをロード
            competitor_data = load_latest_competitor_analytics()
            
            if competitor_data is not None:
                # 共通ロジックを使ってサマリーを生成
                summary = ExecutiveSummaryFormatter.generate_executive_summary(competitor_data)
                
                # 美しく HTML 表示 (CSSが効いた美しい1枚レポートを埋め込み)
                st.components.v1.html(summary["html"], height=700, scrolling=True)
                
                st.markdown("---")
                st.subheader("💾 サマリーレポートダウンロード")
                
                # PDF 出力 (共通ロジックのテキストをそのまま流し込む)
                try:
                    from fpdf import FPDF
                    import os
                    
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.add_page()
                    
                    font_path = r'C:\Windows\Fonts\NotoSansJP-VF.ttf'
                    if os.path.exists(font_path):
                        pdf.add_font('NotoSansJP', '', font_path)
                        pdf.set_font('NotoSansJP', '', 10)
                    else:
                        pdf.set_font('Helvetica', '', 10)
                    
                    # テキストデータをそのまま流し込む
                    pdf.multi_cell(0, 5, summary["text"])
                    
                    pdf_bytes = bytes(pdf.output())
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button('📄 PDF でサマリーをダウンロード', pdf_bytes, 'executive_summary.pdf', 'application/pdf')
                    with col2:
                        st.download_button('📝 Text でサマリーをダウンロード', summary["text"].encode('utf-8'), 'executive_summary.txt', 'text/plain')
                        
                except Exception as e:
                    st.error(f'サマリーPDF生成エラー: {str(e)}')
            else:
                st.info("💡 競合分析データが存在しません。バッチ処理を実行してデータを生成してください。")


# ================================================================
# 個別動画分析
else:
    st.header("🎥 個別動画分析")
    
    lecture_options = {}
    for key, data in lectures_dict.items():
        title = data.get("title", f"動画 {key}")
        lecture_options[title] = key

    if not lecture_options:
        st.warning("動画が見つかりません。")
        st.stop()

    if VIS_MODE == "free_trial":
        selected_label = list(lecture_options.keys())[0]
        st.sidebar.success(f"分析対象: {selected_label}")
        selected_title = st.selectbox("**対象動画**", list(lecture_options.keys()), index=0)
        lecture_num = lecture_options[selected_title]
    else:
        selected_label = st.selectbox("**講座を選択**", list(lecture_options.keys()))
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
        exec_data = lectures_dict.get(str(lecture_num))
        metadata = exec_data.get('metadata', {}) if exec_data else {}
        
        st.subheader("📝 総合評価・結論")
        
        if analysis_available and exec_data:
            with st.spinner("分析中..."):
                summary = narrative_engine.explain_single_video(list(insight_specs.values()), str(lecture_num))
                st.info(summary)
        else:
            st.info("💡 **【総合評価】** データを基にした分析結果がここに表示されます。（デモモード等ではテキストが制限されています）")
            
        st.markdown("---")
        st.subheader("📊 根拠となる品質メトリクス")
        
        if exec_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                val = exec_data.get('semantic_purity_score')
                st.metric("Semantic Purity", f"{val:.1f}" if val is not None else "データ準備中")
            with col2:
                val = exec_data.get('quality_score')
                st.metric("Quality Score", get_quality_label(val))
                if val is not None:
                    st.progress(min(max(val / 100.0, 0.0), 1.0))
            with col3:
                val = exec_data.get('ranking_score')
                st.metric("Ranking Score", "データ準備中")
            
            st.markdown("---")
            
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
                        st.metric("品質スコア", f"{combo['avg_engagement']:.2f}")
                    st.divider()
            
            if analysis_available:
                st.markdown("---")
                st.subheader("分析")
                from diagnostic_evidence import extract_pattern_evidence
                with st.spinner("分析中..."):
                    patterns_evidence = extract_pattern_evidence(golden[:3])
                    
                    prompt = f"""
あなたはビジネスコンサルタントです。
以下の「構造的勝因パターン」を分析し、2段階の診断レポートを作成してください。

{patterns_evidence}

【第1段階：Executive Summary（1分で読める結論）】
以下の形式で、簡潔に記述してください：
- なぜ伸びなかったのか：コンテンツ品質と実際のエンゲージメント率の乖離、および原因（ターゲット層への到達不足）
- 今後、何をすべきか：最優先アクション 1 つ（SEO・SNS・プレイリスト等から選択）と理由

【第2段階：詳細分析（背景と戦略）】
以下の構成で展開してください：

1. 視聴者層の学習ニーズ分析
   - どのような視聴者が、何のテーマを、どのような形式で学びたいのか

2. 品質と到達度のギャップ詳細
   - コンテンツ品質スコアが高い理由
   - なぜエンゲージメント率が低いのか（発見機会不足の仮説）

3. 施策オプションと優先順位
   以下から優先度順に提案してください（具体的アクション名）：
   - SEO対策（タイトル・説明欄のキーワード最適化）
   - SNS投稿（Twitter/LinkedIn での告知・フック）
   - プレイリスト化（3-5本単位での構成）
   - クロスプロモーション（関連チャンネルへのゲスト出演依頼）
   - YouTubeコミュニティ機能の活用
   - メールニュースレター配信

4. 数値根拠
   - 品質スコア、エンゲージメント率、パターン出現回数等を引用

【重要な制約】
- 「必ずヒットする」「確実に高い反応を得られる」などの断定表現は禁止
- スコア 0.89-0.90 はコンテンツ品質を示すもので、視聴者反応の強さではない
- 「発見機会不足」は仮説であり、実施後の測定が重要であることを明記
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
                from diagnostic_evidence import extract_weakness_evidence
                st.subheader("改善ポイント")
                with st.spinner("分析中..."):
                    weakness_evidence = extract_weakness_evidence(weaknesses[:2])
                    
                    prompt = f"""
あなたはビジネスコンサルタントです。
以下の「隠れた弱点」の診断材料を元に診断を行ってください。

{weakness_evidence}

この状態（品質は高いが反応が鈍い）がなぜ生じているのか、
視聴者の視点に立って原因を分析し、どのように構成を改善すべきか診断してください。
※結論・意味を先に述べ、数字は最後の根拠としてのみ使用してください。
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
                from diagnostic_evidence import extract_competitive_evidence
                with st.spinner("分析中..."):
                    competitive_evidence = extract_competitive_evidence(advantage)
                    prompt = f"""
あなたはビジネスコンサルタントです。
以下の「市場ポジショニングと競争優位性」の診断材料を元に診断を行ってください。

{competitive_evidence}

このような構造の動画が、市場でどのような位置づけにあるかを診断してください。
また、他と比べた際の強みと、今後補強すべき領域についても解説してください。

※結論・意味を先に述べ、数字は最後の根拠としてのみ使用してください。
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



