import pytest
import sys
import json
from pathlib import Path
import math

# streamlit_app をモジュールパスに追加
sys.path.append(str(Path(__file__).parent.parent / "streamlit_app"))

from streamlit_app import data_loader

# ==========================================
# 関数1: load_insight_specs() のテスト
# ==========================================

def test_load_insight_specs_normal(monkeypatch, sample_json_files_dir):
    """TC-1-1 & TC-1-4: 正常なファイルと不正なファイルが混在するディレクトリからロード"""
    # config の DATA_DIR をモックする
    monkeypatch.setattr(data_loader, "DATA_DIR", sample_json_files_dir)
    
    # 実行
    specs = data_loader.load_insight_specs()
    
    # 期待結果: 01と02がロードされ、invalid はスキップされること
    assert isinstance(specs, dict)
    assert "01" in specs
    assert "02" in specs
    assert specs["01"]["video_meta"]["title"] == "Sample Complete Lecture"
    assert len(specs) == 2

def test_load_insight_specs_empty_dir(monkeypatch, sample_empty_dir):
    """TC-1-2 & TC-1-3: ディレクトリが存在しない or 空の場合"""
    monkeypatch.setattr(data_loader, "DATA_DIR", sample_empty_dir)
    specs = data_loader.load_insight_specs()
    assert specs == {}

def test_load_insight_specs_japanese_filename(monkeypatch, tmp_path, sample_minimal_insight_spec):
    """TC-1-5: 日本語を含む（ファイルエンコーディング等）のテスト"""
    # data_loaderの実装は "insight_spec_{lecture_id:02d}.json" を直で探しに行くため、
    # そのファイル名でUTF-8文字を含む内容をテストする
    jp_file = tmp_path / "insight_spec_01.json"
    jp_spec = sample_minimal_insight_spec.copy()
    jp_spec["video_meta"]["title"] = "日本語のタイトルテスト"
    with open(jp_file, "w", encoding="utf-8") as f:
        json.dump(jp_spec, f, ensure_ascii=False)
        
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)
    specs = data_loader.load_insight_specs()
    assert specs["01"]["video_meta"]["title"] == "日本語のタイトルテスト"

# ==========================================
# 関数2: build_executive_report_from_specs() のテスト
# ==========================================

def test_build_executive_report_complete(sample_insight_specs_dict):
    """TC-2-1 & TC-2-2: 複数の insight_spec を処理"""
    report = data_loader.build_executive_report_from_specs(sample_insight_specs_dict)
    
    assert "lectures" in report
    lectures = report["lectures"]
    
    assert "01" in lectures
    assert "02" in lectures
    
    # "01" の検証
    lec1 = lectures["01"]
    assert lec1["title"] == "Sample Complete Lecture"
    assert lec1["semantic_purity_score"] == 0.85  # (0.9 + 0.8) / 2
    assert lec1["metadata"]["views"] == 1000
    assert "quality_score" in lec1
    
    # "02" の検証
    lec2 = lectures["02"]
    assert lec2["title"] == "Minimal Lecture"
    assert lec2["semantic_purity_score"] is None

def test_build_executive_report_empty():
    """TC-2-3: 空の insight_spec 辞書"""
    report = data_loader.build_executive_report_from_specs({})
    assert report == {"lectures": {}}

def test_build_executive_report_broken_spec(sample_broken_insight_spec):
    """TC-2-5 & TC-2-7: 一部が不正・空の場合でもクラッシュしない"""
    specs = {"01": sample_broken_insight_spec}
    # 例外が投げられずに辞書が返されることを確認
    report = data_loader.build_executive_report_from_specs(specs)
    assert "lectures" in report
    assert "01" in report["lectures"]
    assert report["lectures"]["01"]["title"] == ""  # title はフォールバックして "" になる

# ==========================================
# 関数3: Fallback 機構のテスト
# ==========================================
# 現在の data_loader.py は executive_report.json を読み込まず、
# 常に build_executive_report_from_specs(load_insight_specs()) を行っています。
# そのため、「fallback 機構」とは load_executive_report() が安全に
# 動的生成された結果を返すかどうかのテストになります。

def test_load_executive_report_fallback(monkeypatch, sample_json_files_dir):
    """TC-3-1 ~ TC-3-8: executive_reportロード時に insight_spec 群から安全に動的生成されること"""
    monkeypatch.setattr(data_loader, "DATA_DIR", sample_json_files_dir)
    
    # 実行
    report = data_loader.load_executive_report()
    
    assert "lectures" in report
    assert "01" in report["lectures"]
    assert report["lectures"]["01"]["title"] == "Sample Complete Lecture"

# ==========================================
# 関数4: aggregate_theme_distribution() のテスト
# ==========================================

def test_aggregate_theme_distribution_normal(sample_insight_specs_dict):
    """TC-4-1: テーマが複数含まれる場合の集約"""
    # 01 には Leadership:50, Management:50 がある
    # 02 にはテーマがない
    dist = data_loader.aggregate_theme_distribution(sample_insight_specs_dict)
    
    assert dist == {"Leadership": 50, "Management": 50}

def test_aggregate_theme_distribution_empty():
    """TC-4-3: テーマが空の場合"""
    dist = data_loader.aggregate_theme_distribution({})
    assert dist == {}

def test_aggregate_theme_distribution_merged():
    """複数の spec で同一テーマがある場合の合算"""
    specs = {
        "01": {
            "views": {
                "self_improvement": {
                    "business_theme_distribution": {"ThemeA": 10, "ThemeB": 5}
                }
            }
        },
        "02": {
            "views": {
                "self_improvement": {
                    "business_theme_distribution": {"ThemeA": 20, "ThemeC": 15}
                }
            }
        }
    }
    dist = data_loader.aggregate_theme_distribution(specs)
    # 値が大きい順にソートされる
    assert list(dist.keys()) == ["ThemeA", "ThemeC", "ThemeB"]
    assert dist["ThemeA"] == 30
    assert dist["ThemeC"] == 15
    assert dist["ThemeB"] == 5

