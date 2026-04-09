import os
import json
from pathlib import Path
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import logging
import re

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeChannelDownloader:
    """YouTube チャンネルから動画をダウンロード（個別動画のメタデータ記録）"""
    
    def __init__(self, base_output_dir: str = None):
        if base_output_dir is None:
            base_output_dir = r"D:\AI_Data\video-insight-spec\downloaded_videos"
        
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.current_channel_dir = None
        self.downloaded_metadata = []
    
    def _sanitize_channel_name(self, channel_name: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]', '', channel_name)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = sanitized.replace('@', '')
        return sanitized.strip()
    
    def _get_channel_name(self, channel_url: str) -> str:
        if channel_url.startswith('@'):
            return channel_url[1:]
        
        if '@' in channel_url:
            channel_name = channel_url.split('@')[-1].split('/')[0]
            return channel_name
        
        if '/c/' in channel_url:
            channel_name = channel_url.split('/c/')[-1].split('/')[0]
            return channel_name
        
        return "unknown_channel"
    
    def _setup_channel_directory(self, channel_name: str) -> Path:
        sanitized_name = self._sanitize_channel_name(channel_name)
        channel_dir = self.base_output_dir / sanitized_name
        channel_dir.mkdir(parents=True, exist_ok=True)
        self.current_channel_dir = channel_dir
        return channel_dir
    
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            speed = d['_speed_str']
            eta = d['_eta_str']
            print(f"  進度: {percent} | 速度: {speed} | 残り時間: {eta}", end='\r')
        elif d['status'] == 'finished':
            print()
    
    def _get_channel_video_urls(self, channel_url: str, max_videos: int = None) -> list:
        """
        チャンネルから個別動画の URL リストを取得
        
        Args:
            channel_url: チャンネル URL
            max_videos: 最大取得数
        
        Returns:
            動画 URL リスト
        """
        if not channel_url.startswith('http'):
            channel_url = f"https://www.youtube.com/{channel_url}"
        
        print(f"\n📋 動画 URL リストを取得中...\n")
        
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': 'in_playlist',
            'skip_download': True,
        }
        
        if max_videos:
            ydl_opts['playlistend'] = max_videos
        
        video_urls = []
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                
                if 'entries' in info:
                    for idx, entry in enumerate(info['entries'], 1):
                        if entry and isinstance(entry, dict):
                            # 正しい形式で URL を構築
                            video_id = entry.get('id')
                            title = entry.get('title', 'Unknown')
                            
                            if video_id and not video_id.startswith('UC'):  # チャンネル ID ではなく動画 ID
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                video_urls.append(video_url)
                                print(f"  [{idx}] {title}")
                                print(f"       URL: {video_url}\n")
        
        except Exception as e:
            logger.error(f"❌ URL 抽出エラー: {e}")
        
        print(f"\n✅ {len(video_urls)} 個の動画 URL を取得しました\n")
        return video_urls
    
    def download_channel(self, channel_url: str, max_videos: int = None) -> list:
        """
        チャンネルから動画をダウンロード（個別動画のメタデータ記録）
        """
        if not channel_url.startswith('http'):
            channel_url = f"https://www.youtube.com/{channel_url}"
        
        channel_name = self._get_channel_name(channel_url)
        channel_dir = self._setup_channel_directory(channel_name)
        
        print(f"📥 ダウンロード開始: {channel_url}")
        print(f"📁 チャンネル: {channel_name}")
        print(f"📂 保存先: {channel_dir}\n")
        
        # Step 1: 動画 URL リストを取得
        video_urls = self._get_channel_video_urls(channel_url, max_videos)
        
        if not video_urls:
            logger.error("❌ 動画が見つかりません")
            return []
        
        # Step 2: 各動画をダウンロード
        print(f"📥 動画をダウンロード中...\n")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(channel_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'progress_hooks': [self._progress_hook]
        }
        
        downloaded_files = []
        self.downloaded_metadata = []
        
        with YoutubeDL(ydl_opts) as ydl:
            for idx, video_url in enumerate(video_urls, 1):
                try:
                    print(f"  [{idx}/{len(video_urls)}] ダウンロード中...")
                    
                    info = ydl.extract_info(video_url, download=True)
                    
                    filename = ydl.prepare_filename(info)
                    downloaded_files.append(filename)
                    
                    # メタデータを記録
                    metadata = {
                        'video_id': info.get('id'),
                        'title': info.get('title'),
                        'filename': Path(filename).name,
                        'file_path': filename,
                        'duration': info.get('duration', 0),
                        'upload_date': info.get('upload_date'),
                        'channel': channel_name,
                        'uploader': info.get('uploader'),
                        'view_count': info.get('view_count', 0),
                        'like_count': info.get('like_count', 0)
                    }
                    self.downloaded_metadata.append(metadata)
                    
                    print(f"    ✅ ダウンロード完了: {info.get('title')}")
                    print(f"       動画 ID: {info.get('id')}")
                    print(f"       長さ: {info.get('duration', 0)}秒\n")
                
                except Exception as e:
                    logger.warning(f"    ⚠️  ダウンロード失敗: {e}\n")
                    continue
        
        print(f"\n✅ 合計 {len(downloaded_files)} 個のファイルをダウンロードしました")
        
        # メタデータを JSON に保存
        self._save_metadata(channel_name)
        
        return downloaded_files
    
    def _save_metadata(self, channel_name: str) -> None:
        """ダウンロード済みメタデータを JSON に保存"""
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        sanitized_name = self._sanitize_channel_name(channel_name)
        metadata_file = results_dir / f"{sanitized_name}_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.downloaded_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ メタデータを保存しました: {metadata_file}")
        print(f"   記録件数: {len(self.downloaded_metadata)} 個\n")
    
    def download_video(self, video_url: str, channel_name: str = "default") -> str:
        """単一動画 URL からダウンロード"""
        channel_dir = self._setup_channel_directory(channel_name)
        
        print(f"📥 ダウンロード開始: {video_url}")
        print(f"📂 保存先: {channel_dir}\n")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(channel_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'progress_hooks': [self._progress_hook]
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                print(f"✅ ダウンロード完了: {Path(filename).name}")
                print(f"   動画 ID: {info.get('id')}")
                return filename
        
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return None
    
    def download_playlist(self, playlist_url: str, max_videos: int = None) -> list:
        """プレイリスト URL からダウンロード"""
        playlist_name = self._get_channel_name(playlist_url)
        return self.download_channel(playlist_url, max_videos=max_videos)
    
    def list_downloaded_files(self, channel_name: str = None) -> dict:
        """ダウンロード済みファイルを列挙"""
        result = {}
        
        if channel_name:
            sanitized = self._sanitize_channel_name(channel_name)
            channel_dir = self.base_output_dir / sanitized
            if channel_dir.exists():
                files = list(channel_dir.glob('*.mp4'))
                result[channel_name] = sorted([str(f) for f in files])
        else:
            for channel_dir in self.base_output_dir.iterdir():
                if channel_dir.is_dir():
                    files = list(channel_dir.glob('*.mp4'))
                    result[channel_dir.name] = sorted([str(f) for f in files])
        
        return result
    
    def get_directory_structure(self) -> None:
        """ダウンロード済みディレクトリ構造を表示"""
        print(f"\n📂 ダウンロードディレクトリ構造:")
        print(f"   {self.base_output_dir}\n")
        
        if not list(self.base_output_dir.iterdir()):
            print("   （ファイルなし）\n")
            return
        
        for channel_dir in sorted(self.base_output_dir.iterdir()):
            if channel_dir.is_dir():
                files = list(channel_dir.glob('*.mp4'))
                print(f"   📁 {channel_dir.name}/ ({len(files)} 個)")
                for file in sorted(files)[:5]:  # 最初の5件だけ表示
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"      - {file.name} ({size_mb:.1f} MB)")
                if len(files) > 5:
                    print(f"      ... ほか {len(files) - 5} 個")
        
        print()


if __name__ == "__main__":
    downloader = YouTubeChannelDownloader()
    downloader.get_directory_structure()
    
    all_files = downloader.list_downloaded_files()
    if all_files:
        print("📋 全チャンネルのダウンロード済みファイル:\n")
        for channel, files in all_files.items():
            print(f"  【{channel}】 ({len(files)} 個)")
            for file in files[:3]:
                print(f"    - {Path(file).name}")
            if len(files) > 3:
                print(f"    ... ほか {len(files) - 3} 個")
