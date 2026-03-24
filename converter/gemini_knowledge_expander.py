# -*- coding: utf-8 -*-
"""
Phase 3: Gemini Knowledge Labeling for insight_spec_XX.json
各 center_pin にビジネステーマ・ファネルステージ・難易度のラベルを自動付与
"""

import os, sys, json, time, logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai がインストールされていません")
    print("pip install google-generativeai を実行してください")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

class GeminiKnowledgeLabeler:
    """insight_spec_XX.json の center_pins にラベルを付与するクラス"""
    
    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id or os.getenv("GEMINI_MODEL_ID", "gemini-3-pro-preview")
        
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY が設定されていません。.env を確認してください。")
        
        genai.configure(api_key=self.api_key)
        self.gen_model = genai.GenerativeModel(self.model_id)
        logger.info(f"✅ Gemini モデル {self.model_id} を初期化しました")
    
    def _build_labeling_prompt(self, center_pin: Dict[str, Any], visual_text_excerpt: Optional[str] = None) -> str:
        """center_pin 用のラベル付与プロンプトを構築"""
        element_id = center_pin.get("element_id", "UNKNOWN")
        pin_type = center_pin.get("type", "UNKNOWN")
        content = center_pin.get("content", "")
        
        visual_text_info = ""
        if visual_text_excerpt:
            visual_text_info = f"\n参考情報（OCR テキスト抜粋）:\n{visual_text_excerpt}\n"
        
        # JSON スキーマは f-string の外で定義
        json_schema = '''{
  "labels": {
    "business_theme": ["...", "..."],
    "funnel_stage": "...",
    "difficulty": "..."
  }
}'''
        
        prompt = f"""あなたは、日本語話者向けビジネス講座の内容を分類するアナリストです。
以下のセンターピンは、この講座で強調されている重要な概念です。

要素 ID: {element_id}
タイプ: {pin_type}
コンセプト名: {content}
{visual_text_info}

このコンセプトについて、次の3つの観点でラベル付けを行ってください。

1. business_theme: ビジネステーマ（マーケティング / セールス / プロダクト / 組織 / マインドセット / オペレーション など）を1～3個、日本語の短いフレーズで。

2. funnel_stage: 顧客の購買ファネル上の段階（認知 / 興味・関心 / 教育 / 比較検討 / クロージング / 継続・LTV）から最も近いものを1つ。

3. difficulty: 概念の難易度（beginner / intermediate / advanced）のいずれか。

出力は次の JSON フォーマットに **厳密に従い、JSON のみ** を返してください。余計な文章は書かないでください。

{json_schema}
"""
        return prompt
    
    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Gemini API を呼び出し（リトライ付き）"""
        for attempt in range(max_retries):
            try:
                response = self.gen_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                return response.text
            except Exception as e:
                wait_time = 2 ** attempt
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ API エラー（試行 {attempt + 1}/{max_retries}）: {e}。{wait_time}秒待機後に再試行...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ API 呼び出し失敗（最大リトライ回数超過）: {e}")
                    raise
    
    def _validate_labels(self, labels: Dict[str, Any]) -> bool:
        """ラベルの妥当性をチェック"""
        try:
            # business_theme: 配列、1～3 個、すべて文字列
            if not isinstance(labels.get("business_theme"), list):
                return False
            if not (1 <= len(labels["business_theme"]) <= 3):
                return False
            if not all(isinstance(x, str) for x in labels["business_theme"]):
                return False
            
            # funnel_stage: 文字列
            if not isinstance(labels.get("funnel_stage"), str):
                return False
            
            # difficulty: 文字列、有効値チェック
            difficulty = labels.get("difficulty", "")
            if difficulty not in ["beginner", "intermediate", "advanced"]:
                return False
            
            return True
        except Exception:
            return False
    
    def label_center_pin(self, center_pin: Dict[str, Any], visual_text_excerpt: Optional[str] = None) -> Dict[str, Any]:
        """単一の center_pin にラベルを付与"""
        element_id = center_pin.get("element_id", "UNKNOWN")
        try:
            prompt = self._build_labeling_prompt(center_pin, visual_text_excerpt)
            response_text = self._call_gemini_with_retry(prompt)
            response_json = json.loads(response_text)
            
            # labels フィールドの抽出とバリデーション
            if "labels" not in response_json:
                logger.warning(f"⚠️ {element_id}: レスポンスに 'labels' フィールドがありません")
                return center_pin
            
            labels = response_json["labels"]
            if not self._validate_labels(labels):
                logger.warning(f"⚠️ {element_id}: ラベルの検証に失敗しました")
                return center_pin
            
            center_pin["labels"] = labels
            logger.info(f"✅ {element_id} にラベルを付与しました: {labels}")
            return center_pin
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ {element_id}: JSON パース失敗 - {e}")
            return center_pin
        except Exception as e:
            logger.error(f"❌ {element_id}: ラベル付与失敗 - {e}")
            return center_pin
    
    def label_insight_spec(self, input_path: str, top_n: int = 5) -> Dict[str, Any]:
        """insight_spec_XX.json の center_pins にラベルを付与"""
        logger.info(f"\n📖 {input_path} を読み込み中...")
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                insight_spec = json.load(f)
        except Exception as e:
            logger.error(f"❌ ファイル読み込み失敗: {e}")
            raise
        
        # center_pins を取得
        if "knowledge_core" not in insight_spec or "center_pins" not in insight_spec["knowledge_core"]:
            logger.error("❌ JSON に knowledge_core.center_pins が見つかりません")
            raise ValueError("Invalid insight_spec structure")
        
        center_pins = insight_spec["knowledge_core"]["center_pins"]
        
        if not isinstance(center_pins, list):
            logger.error("❌ center_pins は配列である必要があります")
            raise ValueError("center_pins must be a list")
        
        # importance_score でソート（降順）
        sorted_pins = sorted(enumerate(center_pins), 
                            key=lambda x: x[1].get("importance_score", 0), 
                            reverse=True)
        
        # TOP N のインデックスを抽出
        top_n_indices = {idx for idx, _ in sorted_pins[:top_n]}
        
        logger.info(f"📊 総レコード数: {len(center_pins)}, TOP {top_n} を対象にラベル付けします")
        
        # ラベル付与処理
        for i, center_pin in enumerate(center_pins):
            element_id = center_pin.get("element_id", "UNKNOWN")
            
            if i in top_n_indices:
                logger.info(f"\n🔄 [{i+1}/{len(center_pins)}] {element_id} を Gemini でラベル付与中...")
                # 注: 簡易実装では visual_text_excerpt は None（拡張可能）
                insight_spec["knowledge_core"]["center_pins"][i] = self.label_center_pin(center_pin, visual_text_excerpt=None)
            else:
                logger.debug(f"⏭️ {element_id} はスキップされました（TOP {top_n} 外）")
        
        return insight_spec
    
    def save_insight_spec(self, insight_spec: Dict[str, Any], output_path: str) -> bool:
        """ラベル付与済み JSON を保存"""
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(insight_spec, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ ラベル付与済み JSON を保存しました: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ ファイル保存失敗: {e}")
            return False
