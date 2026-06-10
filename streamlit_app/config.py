# config.py - 設定・定数定義

from pathlib import Path
from datetime import datetime

import os
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = Path("D:/AI_Data/video-insight-spec/archive")

VIS_MODE = os.getenv("VIS_MODE", "normal")  # デフォルトは normal
if VIS_MODE == "free_trial":
    FREE_TRIAL_ROOT = PROJECT_ROOT / "free_trial_cases"
    FREE_TRIAL_INCOMING = FREE_TRIAL_ROOT / "incoming"
    FREE_TRIAL_DELIVERABLES = FREE_TRIAL_ROOT / "deliverables"
else:
    FREE_TRIAL_ROOT = None
    FREE_TRIAL_INCOMING = None
    FREE_TRIAL_DELIVERABLES = None
APP_TITLE = "📊 YouTubeチャンネル品質分析ダッシュボード"
APP_SUBTITLE = "Streamlit Dashboard v1.0"
VERSION = "v1.0"
PHASE = "Phase 7.2.1"

COLOR_PALETTE = {
    "primary": "#1f77b4",
    "success": "#2ca02c",
    "warning": "#ff7f0e",
    "danger": "#d62728",
    "neutral": "#7f7f7f"
}

SCORE_LEVELS = {
    "超優秀": {"range": (90, 100), "color": "#006400", "label": "【超優秀】"},
    "優秀": {"range": (80, 89), "color": "#2ca02c", "label": "【優秀】"},
    "良好": {"range": (70, 79), "color": "#FFD700", "label": "【良好】"},
    "注意": {"range": (60, 69), "color": "#FF8C00", "label": "【注意】"},
    "改善必須": {"range": (0, 59), "color": "#DC143C", "label": "【改善必須】"}
}

LECTURES = {
    "01": "【独学で習得】初心者でも分かるwebマーケティング講座",
    "02": "【実践】SEO 基礎講座",
    "03": "【戦略】Webマーケティング全体戦略",
    "04": "【案外簡単】広告運用の基本",
    "05": "【応用】高度なマーケティング分析"
}

BUSINESS_THEMES = [
    "SEO",
    "Webマーケティング",
    "広告",
    "コンバージョン最適化",
    "マーケティング",
    "市場分析",
    "コピーライティング",
    "ビジネスモデル",
    "デジタルマーケティング",
    "プロダクト開発",
    "SNSマーケティング",
    "ウェブデザイン",
    "セールス",
    "商品開発"
]

GENERATED_AT = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

