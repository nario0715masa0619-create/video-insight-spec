# data_loader.py - データロード・キャッシング

import json
import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st
from config import DATA_DIR, EXEC_REPORT_PATH, SCORE_LEVELS

@st.cache_resource
def load_executive_report():
    """Executive Report JSON をロード（無ければ insight_spec から生成）"""
    try:
        with open(EXEC_REPORT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        # フォールバック: insight_spec をロードして動的生成する
        insight_specs = load_insight_specs()
        return build_executive_report_from_specs(insight_specs)

def build_executive_report_from_specs(insight_specs):
    """insight_specs からダッシュボード表示用の View-Model を動的に生成する"""
    lectures = {}
    for lecture_id, spec in insight_specs.items():
        # video_meta
        video_meta = spec.get("video_meta", {})
        title = video_meta.get("title", "")
        
        # calculate semantic purity
        center_pins = spec.get("knowledge_core", {}).get("center_pins", [])
        purity_scores = [pin.get("base_purity_score", 0) for pin in center_pins if isinstance(pin.get("base_purity_score"), (int, float))]
        semantic_purity_score = round(sum(purity_scores) / len(purity_scores), 2) if purity_scores else None
        
        # quality & ranking are not in insight_spec
        quality_score = None
        ranking_score = None
        
        # views metrics
        metrics = spec.get("views", {}).get("competitive", {}).get("metrics", {})
        views = metrics.get("view_count", 0)
        likes = metrics.get("like_count", 0)
        comments = metrics.get("comment_count", 0)
        
        lectures[lecture_id] = {
            "title": title,
            "semantic_purity_score": semantic_purity_score,
            "quality_score": quality_score,
            "ranking_score": ranking_score,
            "metadata": {
                "views": views,
                "likes": likes,
                "comments": comments
            }
        }
    
    return {"lectures": lectures}

@st.cache_resource
def load_insight_specs():
    """Insight Spec JSON をロード（全5講座）"""
    insight_specs = {}
    for lecture_id in range(1, 6):
        spec_file = DATA_DIR / f"insight_spec_{lecture_id:02d}.json"
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                insight_specs[f"{lecture_id:02d}"] = data
        except FileNotFoundError:
            st.warning(f"⚠️ 不見つかり: {spec_file}")
        except json.JSONDecodeError as e:
            st.warning(f"⚠️ JSON エラー: {spec_file}")
    return insight_specs

@st.cache_resource
def load_sqlite_db(lecture_id):
    """SQLite データベースをロード"""
    db_file = DATA_DIR / f"Mk2_Sidecar_{lecture_id:02d}.db"
    try:
        conn = sqlite3.connect(str(db_file))
        query = "SELECT * FROM evidence_index"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.DatabaseError as e:
        st.error(f"❌ SQLite エラー: {e}")
        return None
    except FileNotFoundError:
        st.warning(f"⚠️ DB 不見つかり: {db_file}")
        return None

def transform_executive_report(exec_report):
    """Executive Report を DataFrame に変換"""
    records = []
    lectures_data = exec_report.get("lectures", {})
    
    for lecture_id, data in lectures_data.items():
        record = {
            "講座ID": f"講座{lecture_id}",
            "タイトル": data.get("title", ""),
            "セマンティック純度スコア": data.get("semantic_purity_score", None),
            "品質スコア": data.get("quality_score", None),
            "ランキングスコア": data.get("ranking_score", None),
            "ビュー数": data.get("metadata", {}).get("views", 0),
            "いいね数": data.get("metadata", {}).get("likes", 0),
            "コメント数": data.get("metadata", {}).get("comments", 0)
        }
        records.append(record)
    
    if not records:
        return pd.DataFrame(columns=["講座ID", "タイトル", "セマンティック純度スコア", "品質スコア", "ランキングスコア", "ビュー数", "いいね数", "コメント数"])
    
    df = pd.DataFrame(records)
    df["講座番号"] = df["講座ID"].str.extract(r'(\d+)').astype(int)
    df = df.sort_values("講座番号").drop("講座番号", axis=1)
    return df

def aggregate_theme_distribution(insight_specs):
    """全講座のテーマ分布を集計"""
    theme_counts = {}
    
    for lecture_id, spec in insight_specs.items():
        business_themes = spec.get("views", {}).get("self_improvement", {}).get("business_theme_distribution", {})
        for theme, count in business_themes.items():
            if theme not in theme_counts:
                theme_counts[theme] = 0
            theme_counts[theme] += count
    
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_themes)

def create_theme_dataframe(theme_counts):
    """テーマ分布を DataFrame に変換"""
    total = sum(theme_counts.values())
    records = []
    
    for rank, (theme, count) in enumerate(theme_counts.items(), 1):
        percentage = (count / total * 100) if total > 0 else 0
        stars = "★" * min(5, max(1, int(percentage / 10)))
        
        record = {
            "順位": rank,
            "テーマ名": theme,
            "出現件数": count,
            "割合（％）": f"{percentage:.1f}%",
            "重要度": stars
        }
        records.append(record)
    
    return pd.DataFrame(records)

def calculate_aggregate_metrics(df_exec):
    """集計メトリクスを計算"""
    purity_series = pd.to_numeric(df_exec["セマンティック純度スコア"], errors='coerce').dropna()
    quality_series = pd.to_numeric(df_exec["品質スコア"], errors='coerce').dropna()
    ranking_series = pd.to_numeric(df_exec["ランキングスコア"], errors='coerce').dropna()
    
    return {
        "講座数": len(df_exec),
        "総ビュー数": int(df_exec["ビュー数"].sum()),
        "総いいね数": int(df_exec["いいね数"].sum()),
        "総コメント数": int(df_exec["コメント数"].sum()),
        "平均セマンティック純度": round(purity_series.mean(), 2) if not purity_series.empty else None,
        "平均品質スコア": round(quality_series.mean(), 2) if not quality_series.empty else None,
        "平均ランキングスコア": round(ranking_series.mean(), 2) if not ranking_series.empty else None,
        "セマンティック純度_算出件数": len(purity_series),
        "品質スコア_算出件数": len(quality_series),
        "ランキングスコア_算出件数": len(ranking_series),
    }

def get_score_level(score):
    """スコアから評価レベルを取得"""
    for level_name, level_info in SCORE_LEVELS.items():
        min_score, max_score = level_info["range"]
        if min_score <= score <= max_score:
            return level_info
    return SCORE_LEVELS["改善必須"]


@st.cache_resource
def load_latest_competitor_analytics():
    """最新の競合分析 JSON データをロード"""
    # reports/competitor_analytics から探す
    target_dir = Path(__file__).resolve().parent.parent / "reports" / "competitor_analytics"
    if not target_dir.exists():
        target_dir = Path("reports/competitor_analytics")
        
    if not target_dir.exists():
        st.error("❌ 競合分析ディレクトリが見つかりません。")
        return None
        
    json_files = list(target_dir.glob("competitor_analytics_*.json"))
    if not json_files:
        st.warning("⚠️ 競合分析データ (competitor_analytics_*.json) が見つかりません。")
        return None
        
    # ファイル名でソートして最新のものを選択
    latest_file = max(json_files, key=lambda p: p.name)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"❌ 最新の競合分析データのロードに失敗しました: {e}")
        return None


