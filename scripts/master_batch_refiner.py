# -*- coding: utf-8 -*-
"""
Master Batch Refiner: MP4 → Mk2_Core_XX.json + Mk2_Sidecar_XX.db
All configuration via .env environment variables
"""

import json
import os
import subprocess
import sqlite3
import re
import logging
import sys
import io
import whisper
import easyocr
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import time
from tqdm import tqdm

# ========== UTF-8 設定 ==========
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ========== 環境変数読み込み ==========
load_dotenv()

# ========== ログ設定 ==========
LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
os.makedirs(LOGS_DIR, exist_ok=True)

log_file = os.path.join(LOGS_DIR, f"antigravity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

# ========== Gemini API 設定 ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-3-pro-preview")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY は .env ファイルで設定されている必要があります。")

genai.configure(api_key=GEMINI_API_KEY)
logger.info(f"✅ Gemini API 初期化完了: {GEMINI_MODEL_ID}")

# ========== パス設定 ==========
VIDEOS_INPUT_DIR = os.getenv("VIDEOS_INPUT_DIR", r"D:\AI_Data\video-insight-spec\downloaded_videos")
ARCHIVE_OUTPUT_DIR = os.getenv("ARCHIVE_OUTPUT_DIR", r"D:\AI_Data\video-insight-spec\archive")
TEMP_DIR = os.getenv("TEMP_DIR", "./batch_refine_work")

os.makedirs(VIDEOS_INPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

logger.info(f"入力ディレクトリ: {VIDEOS_INPUT_DIR}")
logger.info(f"出力ディレクトリ: {ARCHIVE_OUTPUT_DIR}")

# ========== Whisper 設定 ==========
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")

logger.info(f"Whisper モデル読み込み中... ({WHISPER_MODEL_SIZE}, device={WHISPER_DEVICE})")
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE, device=WHISPER_DEVICE)
logger.info("✅ Whisper モデル読み込み完了")

# ========== EasyOCR 設定 ==========
EASYOCR_GPU = os.getenv("EASYOCR_GPU", "false").lower() == "true"
EASYOCR_LANGUAGES = os.getenv("EASYOCR_LANGUAGES", "ja,en").split(",")

logger.info(f"EasyOCR 初期化中... (GPU={EASYOCR_GPU}, languages={EASYOCR_LANGUAGES})")
reader = easyocr.Reader(EASYOCR_LANGUAGES, gpu=EASYOCR_GPU)
logger.info("✅ EasyOCR 初期化完了")

# ========== FFmpeg 設定 ==========
FRAMES_PER_MINUTE = int(os.getenv("FRAMES_PER_MINUTE", "3"))
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

logger.info(f"Frame extraction rate: {FRAMES_PER_MINUTE} frames/minute")

# ========== MasterBatchRefiner クラス ==========

class MasterBatchRefiner:
    MUD_KEYWORDS = [
        'chrome', 'ファイル', '編集', '表示', '履歴', 'ブックマーク', 'タブ', 'ヘルプ', '設定', '共有',
        'http', 'https', 'www', 'index', 'html', 'php', 'users', 'nario', 'AppData',
        'クリック', 'ドラッグ', '選択', '閉じる', '最小化', '最大化', '元に戻す', 'プロファイル'
    ]

    def __init__(self):
        self.gen_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_ID,
            generation_config={"response_mime_type": "application/json"}
        )

    def filter_mud(self, text):
        """不要なキーワードを除外"""
        for keyword in self.MUD_KEYWORDS:
            text = re.sub(rf'\b{re.escape(keyword)}\b', '', text, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', text).strip()

    def _call_gemini_with_retry(self, prompt, max_retries=3, backoff_base=2):
        """指数バックオフ付きで Gemini を呼び出し"""
        for attempt in range(max_retries):
            try:
                response = self.gen_model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = backoff_base ** attempt
                    logger.warning(f"  ⚠️ Gemini 呼び出し失敗 (試行 {attempt+1}/{max_retries}): {e}. {wait_time}秒待機...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"  ❌ Gemini 呼び出し失敗 ({max_retries} 回失敗): {e}")
                    return None

    def process_video(self, video_path):
        """ビデオ処理メイン"""
        video_name = Path(video_path).stem
        lecture_id = video_name.split('_')[0]

        logger.info(f"【{lecture_id}】処理開始: {Path(video_path).name}")

        # ========== Step 1: Whisper で音声認識 ==========
        logger.info(f"  [1/5] Whisper で音声認識中...")
        try:
            result = whisper_model.transcribe(video_path, language="ja")
            transcript = result["text"]
            logger.info(f"    ✅ 音声認識完了 ({len(transcript)} 文字)")
        except Exception as e:
            logger.error(f"    ❌ 音声認識失敗: {e}")
            return False

        # ========== Step 2: FFmpeg でフレーム抽出 ==========
        logger.info(f"  [2/5] FFmpeg でフレーム抽出中...")
        try:
            frames_dir = os.path.join(TEMP_DIR, lecture_id)
            os.makedirs(frames_dir, exist_ok=True)

            # ビデオ長を取得（mediainfo を使用）
            try:
                # Method 1: ffprobe（優先）
                probe_result = subprocess.run(
                    [FFMPEG_PATH, "-v", "error", "-show_entries", "format=duration", 
                     "-of", "default=noprint_wrappers=1:nokey=1:0", video_path],
                    capture_output=True, text=True, timeout=10
                )
                
                duration_str = probe_result.stdout.strip()
                
                if duration_str and duration_str != "":
                    try:
                        duration = float(duration_str)
                        logger.info(f"    ℹ️ ビデオ長: {duration:.1f}秒")
                    except ValueError:
                        duration = None
                else:
                    duration = None
                    logger.warning(f"    ⚠️ ffprobe で長さ取得失敗")
            except Exception as e:
                duration = None
                logger.warning(f"    ⚠️ ffprobe エラー: {e}")

            # Method 2: ビデオをサンプル再生して長さを推定
            if duration is None:
                logger.info(f"    ℹ️ 代替方法: ビデオをスキャンして長さを推定中...")
                try:
                    # ffmpeg でビデオ情報を取得
                    info_result = subprocess.run(
                        [FFMPEG_PATH, "-i", video_path],
                        capture_output=True, text=True, timeout=30
                    )
                    
                    # stderr から Duration を抽出
                    import re as regex
                    match = regex.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', info_result.stderr)
                    if match:
                        hours, minutes, seconds = match.groups()
                        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        logger.info(f"    ℹ️ ビデオ長（推定）: {duration:.1f}秒")
                    else:
                        duration = None
                except Exception as e:
                    logger.warning(f"    ⚠️ 推定失敗: {e}")
                    duration = None

            # フレーム抽出レート決定
            if duration and duration > 0:
                fps = FRAMES_PER_MINUTE / 60.0
                num_frames = int(duration * fps)
                logger.info(f"    ℹ️ 抽出フレーム数: {num_frames} ({FRAMES_PER_MINUTE}frames/min × {duration:.1f}sec)")
            else:
                # フォールバック: 固定値
                fps = FRAMES_PER_MINUTE / 60.0
                num_frames = 30  # デフォルト 30 フレーム
                logger.warning(f"    ⚠️ ビデオ長取得失敗。デフォルト {num_frames} フレーム を使用")

            # フレーム抽出
            logger.info(f"    ℹ️ FFmpeg でフレーム抽出中 (fps={fps:.2f})...")
            extract_result = subprocess.run(
                [FFMPEG_PATH, "-i", video_path, "-vf", f"fps={fps}", 
                 os.path.join(frames_dir, "frame_%04d.jpg")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600
            )

            frames = sorted(Path(frames_dir).glob("frame_*.jpg"))
            logger.info(f"    ✅ フレーム抽出完了 ({len(frames)} フレーム)")
            
            if len(frames) == 0:
                logger.warning(f"    ⚠️ フレームが抽出されませんでした")

        except subprocess.TimeoutExpired:
            logger.error(f"    ❌ FFmpeg タイムアウト")
            return False
        except Exception as e:
            logger.error(f"    ❌ フレーム抽出失敗: {e}")
            return False

        # ========== Step 3: EasyOCR で画面テキスト抽出 ==========
        logger.info(f"  [3/5] EasyOCR でテキスト抽出中...")
        try:
            ocr_texts = []
            for frame in frames:
                results = reader.readtext(str(frame))
                for result in results:
                    text = result[1]
                    confidence = result[2]
                    if confidence > 0.5:
                        ocr_texts.append(text)
            
            visual_text = " ".join(ocr_texts)
            visual_text = self.filter_mud(visual_text)

            # OCR テキスト保存
            ocr_file = os.path.join(ARCHIVE_OUTPUT_DIR, f"Mk2_OCR_{lecture_id}.txt")
            with open(ocr_file, 'w', encoding='utf-8') as f:
                f.write(visual_text)

            logger.info(f"    ✅ テキスト抽出完了 ({len(ocr_texts)} テキスト)")
        except Exception as e:
            logger.error(f"    ❌ テキスト抽出失敗: {e}")
            return False


        # ========== Step 4: Gemini でセンターピン生成 ==========
        logger.info(f"  [4/5] Gemini でセンターピン生成中...")
        
        prompt = f"""あなたはマーケティング教育の専門家です。以下のコンテンツから、実行可能で価値あるセンターピンを抽出してください。

【動画タイトル】
{video_name}

【文字起こし全文】
{transcript}

【画面テキスト】
{visual_text}

【抽出要件】
- 最低 8～15 個のセンターピン
- 各ピンは独立した知識ユニット（再利用可能）
- 「～する」「～とは」などの具体的な説明を含む
- 短すぎない（最低 80 文字）、長すぎない（最大 300 文字）

【ピンのタイプ定義】
- concept: マーケティング理論・概念・原則
- strategy: 戦略・アプローチ・施策
- tactic: 具体的な実行手法・テクニック
- framework: フレームワーク・分析モデル
- case: 具体例・事例

【JSON フォーマット】
{{
    "center_pins": [
        {{
            "element_id": "cp_001",
            "type": "concept",
            "content": "動画で述べられた内容を、視聴者が実装可能な形に落とし込んだ説明。なぜそうするのか、どうするのかを含める。（80～300文字）",
            "base_purity_score": 85
        }},
        ...
    ]
}}

【品質チェック】
✓ content は100文字以上300文字以下
✓ 「～の法則」だけでなく「～の法則では◯◯という考え方で、具体的には△△する」という形
✓ 重複がない
✓ タイプは文脈に応じて適切に選択
✓ 各ピンは動画で実際に説明されている内容のみ
"""

        gemini_response = self._call_gemini_with_retry(prompt)
        if not gemini_response:
            logger.error(f"    ❌ Gemini 呼び出し失敗")
            return False

        try:
            pin_data = json.loads(gemini_response)
            generated_pins = pin_data.get('center_pins', [])
            
            # 品質フィルタリング
            valid_pins = []
            for pin in generated_pins:
                content = pin.get('content', '')
                if len(content) >= 80:  # 最小 80 文字
                    valid_pins.append(pin)
                else:
                    logger.warning(f"    ⚠️ フィルタ: {pin.get('element_id')} - content が短い ({len(content)} 文字)")
            
            logger.info(f"    ✅ セン ターピン生成完了 ({len(valid_pins)} ピン / {len(generated_pins)} 生成)")
            
            # valid_pins で上書き
            pin_data['center_pins'] = valid_pins
            
        except json.JSONDecodeError as e:
            logger.error(f"    ❌ JSON パース失敗: {e}")
            return False

        # ========== Step 5: Mk2_Core JSON と Mk2_Sidecar DB 保存 ==========
        logger.info(f"  [5/5] ファイル保存中...")
        try:
            # Mk2_Core JSON
            core_json = {
                "lecture_id": lecture_id,
                "video_path": str(video_path),
                "generated_at": datetime.now().isoformat(),
                "knowledge_core": {
                    "center_pins": pin_data.get("center_pins", [])
                }
            }

            core_file = os.path.join(ARCHIVE_OUTPUT_DIR, f"Mk2_Core_{lecture_id}.json")
            with open(core_file, 'w', encoding='utf-8') as f:
                json.dump(core_json, f, ensure_ascii=False, indent=2)

            # Mk2_Sidecar DB
            sidecar_file = os.path.join(ARCHIVE_OUTPUT_DIR, f"Mk2_Sidecar_{lecture_id}.db")
            conn = sqlite3.connect(sidecar_file)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_index (
                    element_id TEXT,
                    start_ms INTEGER,
                    end_ms INTEGER,
                    visual_text TEXT,
                    visual_score REAL,
                    source_video_path TEXT
                )
            """)

            for pin in pin_data.get("center_pins", []):
                cursor.execute(
                    "INSERT INTO evidence_index VALUES (?, ?, ?, ?, ?, ?)",
                    (pin.get("element_id"), 0, 0, visual_text[:500], pin.get("base_purity_score", 0), str(video_path))
                )

            conn.commit()
            conn.close()

            logger.info(f"    ✅ ファイル保存完了")
            logger.info(f"      • {core_file}")
            logger.info(f"      • {sidecar_file}")

            return True

        except Exception as e:
            logger.error(f"    ❌ ファイル保存失敗: {e}")
            return False


# ========== メイン処理 ==========

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Master Batch Refiner 開始")
    logger.info("="*60)

    refiner = MasterBatchRefiner()

    # ビデオファイル取得
    if len(sys.argv) > 1:
        # コマンドライン引数で指定されたファイル
        video_files = [sys.argv[1]]
    else:
        # VIDEOS_INPUT_DIR から全 MP4 を取得
        video_files = sorted(Path(VIDEOS_INPUT_DIR).glob("*.mp4"))

    if not video_files:
        logger.error("処理対象のビデオファイルが見つかりません。")
        sys.exit(1)

    logger.info(f"処理対象: {len(video_files)} ファイル")

    # 処理結果記録
    results = {
        "started_at": datetime.now().isoformat(),
        "total": len(video_files),
        "success": 0,
        "failed": 0,
        "details": []
    }

    # バッチ処理
    for video_file in tqdm(video_files, desc="Processing"):
        start_time = time.time()
        success = refiner.process_video(str(video_file))
        duration = time.time() - start_time

        if success:
            results["success"] += 1
            results["details"].append({
                "file": Path(video_file).name,
                "status": "success",
                "duration_s": round(duration, 2)
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "file": Path(video_file).name,
                "status": "failed"
            })

    # 結果保存
    results["completed_at"] = datetime.now().isoformat()

    result_file = os.path.join(LOGS_DIR, f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("="*60)
    logger.info(f"✅ 処理完了: {results['success']}/{results['total']} 成功")
    logger.info(f"📁 結果ファイル: {result_file}")
    logger.info("="*60)

    sys.exit(0 if results["failed"] == 0 else 1)
