#!/usr/bin/env python3
"""
無料1本解析実行スクリプト
使い方: python run_free_trial_one_video.py --case-id trial_companyx_20260609
"""

import os
import sys
import json
import yaml
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# VIS 既存モジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app.narrative_engine import NarrativeEngine


class FreeTrialOneVideoProcessor:
    def __init__(self, case_id, free_trial_root="free_trial_cases"):
        self.case_id = case_id
        self.free_trial_root = Path(free_trial_root)
        self.log_file = self.free_trial_root / "logs" / f"{case_id}.log"
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger
        
    def load_case_metadata(self):
        """cases.yaml から案件情報を読み込み"""
        cases_file = self.free_trial_root / "cases.yaml"
        with open(cases_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for case in data.get("cases", []):
            if case["case_id"] == self.case_id:
                return case
        raise ValueError(f"Case not found: {self.case_id}")
        
    def validate_input(self, case):
        """入力値チェック"""
        required_fields = ["case_id", "client_name", "video_file"]
        for field in required_fields:
            if not case.get(field):
                raise ValueError(f"必須項目がありません: {field}")
        
        video_path = self.free_trial_root / "incoming" / case["video_file"]
        if not video_path.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
            
        self.logger.info(f"✅ 入力チェック成功: {self.case_id}")
        
    def process_video(self, case):
        """既存VIS分析フローで1本解析"""
        self.logger.info(f"📊 解析開始: {case['client_name']}")
        
        video_file = case["video_file"]
        video_path = self.free_trial_root / "incoming" / video_file
        
        # TODO: 将来的にはGemini API等を利用して動画ファイル(video_path)から直接抽出するパイプラインを実装する
        # 現在はダッシュボードの実装パターンを参考に、ダミーデータとして既存のJSONをロードして代用する
        self.logger.info("🤖 ビデオファイルからメタデータを抽出中... (モック実行)")
        
        mock_json_path = Path("D:/AI_Data/video-insight-spec/archive/insight_spec_01.json")
        if mock_json_path.exists():
            with open(mock_json_path, 'r', encoding='utf-8') as f:
                insight_spec = json.load(f)
            # lecture_id をダミーで付与（diagnostic_evidenceで必要な場合があるため）
            insight_spec['lecture_id'] = "01"
            # タイトルを案件に合わせて上書き
            insight_spec['video_meta']['title'] = video_file.replace(".mp4", "")
        else:
            raise FileNotFoundError(f"モック用データが見つかりません: {mock_json_path}")
            
        return insight_spec
        
    def generate_report(self, case, insight_spec):
        """顧客返却用レポート生成"""
        report_dir = self.free_trial_root / "deliverables" / self.case_id
        report_dir.mkdir(exist_ok=True, parents=True)
        
        # AI解析を実行
        self.logger.info("🤖 AI診断出力を生成中...")
        engine = NarrativeEngine()
        try:
            diagnosis_text = engine.explain_channel_diagnosis([insight_spec])
            improvement_text = engine.explain_channel_improvements([insight_spec])
        except Exception as e:
            self.logger.error(f"AI解析中にエラーが発生しました: {e}")
            diagnosis_text = "AI診断の生成に失敗しました。"
            improvement_text = "改善提案の生成に失敗しました。"

        # マークダウンレポート作成
        report_md = f"""# VIS 無料1本解析レポート

⚠️ 本資料はダッシュボード実演の補助資料です。
正式な診断結果はダッシュボード画面の【品質診断】【改善提案】タブでご確認ください。

**対象動画**: {case["video_file"]}
**顧客**: {case["client_name"]}
**解析日**: {datetime.now().strftime("%Y-%m-%d")}

## 品質診断

{diagnosis_text}

## 改善提案

{improvement_text}

---
*VIS（Video Insight Spec）による自動解析*
"""
        
        # ファイル出力
        report_file = report_dir / "report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_md)
        
        # JSON メタデータ出力
        metadata = {
            "case_id": self.case_id,
            "client_name": case["client_name"],
            "video_file": case["video_file"],
            "insight_spec": insight_spec,
            "generated_at": datetime.now().isoformat()
        }
        metadata_file = report_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"✅ レポート生成完了: {report_file}")
        return report_file, report_dir
        
    def run(self):
        """メイン処理"""
        try:
            self.logger.info(f"🚀 無料1本解析開始: {self.case_id}")
            
            case = self.load_case_metadata()
            self.validate_input(case)
            insight_spec = self.process_video(case)
            report_file, report_dir = self.generate_report(case, insight_spec)
            
            print(f"\n✅ 解析完了!")
            print(f"📄 返却物: {report_file}")
            print(f"📁 成果物フォルダ: {report_dir}")
            print(f"📋 ログ: {self.log_file}")
            print(f"")
            print(f"📊 次のステップ: ダッシュボードで対象動画を確認してください")
            print(f"🖥️ コマンド: streamlit run streamlit_app/app.py")
            print(f"📋 対象動画: {case['video_file']}")
            
            self.logger.info(f"✅ 解析完了")
            
        except Exception as e:
            self.logger.error(f"❌ エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
            print(f"📋 詳細はログを確認してください: {self.log_file}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="VIS 無料1本解析実行スクリプト"
    )
    parser.add_argument(
        "--case-id",
        required=True,
        help="案件ID (例: trial_companyx_20260609)"
    )
    parser.add_argument(
        "--free-trial-root",
        default="free_trial_cases",
        help="無料解析用ルートディレクトリ（デフォルト: free_trial_cases）"
    )
    
    args = parser.parse_args()
    
    processor = FreeTrialOneVideoProcessor(args.case_id, args.free_trial_root)
    processor.run()

if __name__ == "__main__":
    main()
