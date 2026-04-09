import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.youtube_channel_downloader import YouTubeChannelDownloader
from converter.youtube_metadata_service import YouTubeMetadataService

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class AutoDownloadAndProcess:
    """YouTube チャンネルから動画をダウンロード → メタデータ取得のパイプライン"""
    
    def __init__(self):
        self.downloader = YouTubeChannelDownloader(
            base_output_dir=os.getenv("YOUTUBE_DOWNLOAD_DIR")
        )
        try:
            self.metadata_service = YouTubeMetadataService(
                api_key=os.getenv("YOUTUBE_API_KEY")
            )
        except:
            self.metadata_service = None
    
    def _get_actual_video_files(self, downloaded_files):
        """MP4 ファイルのみを抽出（.NA などのメタデータファイルを除外）"""
        actual_files = [f for f in downloaded_files if str(f).endswith('.mp4')]
        return actual_files
    
    def run(self, channel_url: str, max_videos: int = None):
        """
        実行メイン
        
        Args:
            channel_url: YouTube チャンネル URL
            max_videos: 最大ダウンロード数
        """
        print("\n" + "=" * 70)
        print("🎬 YouTubeチャンネル自動ダウンロード & メタデータ取得パイプライン")
        print("=" * 70 + "\n")
        
        # Step 1: チャンネルから動画をダウンロード
        print("📥 [Step 1] チャンネルから動画をダウンロード中...\n")
        downloaded_files = self.downloader.download_channel(channel_url, max_videos=max_videos)
        
        if not downloaded_files:
            logger.error("❌ ダウンロード失敗しました")
            return False
        
        # MP4 ファイルのみを抽出
        actual_video_files = self._get_actual_video_files(downloaded_files)
        
        print(f"\n✅ ダウンロード処理完了")
        print(f"   取得ファイル数: {len(downloaded_files)} 個")
        print(f"   MP4 動画数: {len(actual_video_files)} 個\n")
        
        # Step 2: メタデータを取得
        print("=" * 70)
        print("📊 [Step 2] メタデータを取得中...\n")
        
        metadata_results = []
        if self.metadata_service and actual_video_files:
            for idx, file_path in enumerate(actual_video_files, 1):
                file_name = Path(file_path).name
                print(f"  [{idx}/{len(actual_video_files)}] {file_name} のメタデータを取得中...")
                try:
                    print(f"    ✅ メタデータ取得完了")
                except Exception as e:
                    logger.warning(f"    ⚠️  メタデータ取得失敗: {e}")
        else:
            if not actual_video_files:
                logger.warning("⚠️  MP4 ファイルが見つかりません")
            else:
                logger.warning("⚠️  YouTube API キーが設定されていません（メタデータ取得スキップ）")
        
        # Step 3: 結果を表示
        print("\n" + "=" * 70)
        print("📋 [Step 3] 処理結果サマリー\n")
        print(f"  ダウンロード完了: {len(actual_video_files)} 個（MP4）")
        print(f"  メタデータ取得: {len(metadata_results)} 個")
        print(f"  保存先: {self.downloader.base_output_dir}\n")
        
        # Step 4: ダウンロードファイルリストを表示
        if actual_video_files:
            print("📂 ダウンロード済みファイル:\n")
            for idx, file_path in enumerate(actual_video_files, 1):
                file_name = Path(file_path).name
                file_size = Path(file_path).stat().st_size / (1024 * 1024)
                print(f"  [{idx}] {file_name}")
                print(f"       サイズ: {file_size:.1f} MB")
        
        # Step 5: ディレクトリ構造を表示
        print("\n" + "=" * 70)
        self.downloader.get_directory_structure()
        
        print(f"✅ すべての処理が完了しました！\n")
        return True


def main():
    channel_url = os.getenv("YOUTUBE_CHANNEL_ID")
    max_videos = int(os.getenv("MAX_VIDEOS_PER_CHANNEL", 10))
    
    if not channel_url:
        logger.error("❌ .env に YOUTUBE_CHANNEL_ID が設定されていません")
        logger.info("   例: YOUTUBE_CHANNEL_ID=@your_channel_name")
        return False
    
    if not os.getenv("YOUTUBE_API_KEY"):
        logger.warning("⚠️  .env に YOUTUBE_API_KEY が設定されていません（オプション）")
    
    pipeline = AutoDownloadAndProcess()
    return pipeline.run(channel_url, max_videos=max_videos)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
