import os
import json
from pathlib import Path
from yt_dlp import YoutubeDL
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeMetadataExtractor:
    """ダウンロード済み MP4 ファイルのメタデータを抽出"""
    
    def __init__(self, download_dir: str = None):
        if download_dir is None:
            download_dir = r"D:\AI_Data\video-insight-spec\downloaded_videos"
        
        self.download_dir = Path(download_dir)
    
    def extract_all_metadata(self) -> dict:
        """
        全チャンネルのダウンロード済み MP4 ファイルからメタデータを抽出
        """
        result = {}
        
        print("\n" + "=" * 70)
        print("📊 ダウンロード済み MP4 ファイルのメタデータを抽出中...")
        print("=" * 70 + "\n")
        
        # チャンネルごとのフォルダを列挙
        for channel_dir in sorted(self.download_dir.iterdir()):
            if channel_dir.is_dir():
                mp4_files = list(channel_dir.glob('*.mp4'))
                
                if mp4_files:
                    print(f"📁 チャンネル: {channel_dir.name}")
                    print(f"📹 ファイル数: {len(mp4_files)}\n")
                    
                    metadata_list = []
                    
                    for idx, mp4_file in enumerate(sorted(mp4_files), 1):
                        try:
                            metadata = self._extract_file_metadata(mp4_file)
                            
                            if metadata:
                                metadata_list.append(metadata)
                                print(f"  [{idx}] {mp4_file.name}")
                                print(f"       タイトル: {metadata.get('title', 'Unknown')}")
                                if metadata.get('video_id'):
                                    print(f"       動画 ID: {metadata['video_id']}")
                                if metadata.get('duration'):
                                    print(f"       長さ: {metadata['duration']}秒")
                                print()
                        
                        except Exception as e:
                            logger.warning(f"    ⚠️  メタデータ抽出失敗: {e}")
                    
                    if metadata_list:
                        result[channel_dir.name] = metadata_list
        
        return result
    
    def _extract_file_metadata(self, mp4_file: Path) -> dict:
        """
        MP4 ファイルのメタデータを抽出
        """
        filename = mp4_file.name
        
        metadata = {
            'filename': filename,
            'file_path': str(mp4_file),
            'file_size_mb': round(mp4_file.stat().st_size / (1024 * 1024), 1),
            'title': mp4_file.stem,
            'video_id': None,
            'duration': None
        }
        
        # ファイル名から動画 ID を抽出（複数の方法を試行）
        # 方法 1: 括弧内の 11 文字コード
        match = re.search(r'#\d+\(全\d+本\)\】(.+?)\.mp4', filename)
        if match:
            # この場合は講座番号から推測
            pass
        
        # 方法 2: YouTube の標準動画 ID 形式（11 文字の英数字、- と _）
        # 例：qOE5Zd7O12Q
        match = re.search(r'([a-zA-Z0-9_-]{11})', filename)
        if match:
            potential_id = match.group(1)
            # 検証：YouTube 動画 ID は通常、特定のパターンに従う
            # チャンネル ID（UC で始まる）ではないか確認
            if not potential_id.startswith('UC'):
                metadata['video_id'] = potential_id
        
        # 方法 3: yt-dlp で抽出（ローカルファイルの場合）
        if not metadata['video_id']:
            video_id = self._get_video_id_from_file(mp4_file)
            if video_id:
                metadata['video_id'] = video_id
        
        return metadata
    
    def _get_video_id_from_file(self, mp4_file: Path) -> str:
        """
        yt-dlp を使用して MP4 ファイルから動画 ID を取得
        """
        try:
            # ffprobe で MP4 の metadata を確認
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True
            }
            
            # ローカルファイルから直接メタデータを取得は困難なため、スキップ
            pass
        
        except:
            pass
        
        return None
    
    def save_metadata_json(self, output_file: str = None) -> str:
        """抽出したメタデータを JSON に保存"""
        if output_file is None:
            output_dir = Path("results")
            output_dir.mkdir(exist_ok=True)
            output_file = str(output_dir / "all_channels_metadata.json")
        
        metadata = self.extract_all_metadata()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ メタデータを保存しました: {output_file}\n")
        return output_file
    
    def create_video_mapping(self) -> dict:
        """
        ダウンロード済みファイルから動画 ID マッピングを生成
        """
        metadata_all = self.extract_all_metadata()
        result = {}
        
        print("\n" + "=" * 70)
        print("📊 動画 ID マッピングを生成中...")
        print("=" * 70 + "\n")
        
        for channel_name, metadata_list in metadata_all.items():
            channel_videos = {}
            
            for metadata in metadata_list:
                video_id = metadata.get('video_id')
                
                if video_id:
                    channel_videos[video_id] = metadata
                    print(f"  {video_id}: {metadata['title']}")
            
            if channel_videos:
                result[channel_name] = channel_videos
        
        return result
    
    def save_video_mapping(self, output_file: str = None) -> str:
        """動画 ID マッピングを JSON に保存"""
        if output_file is None:
            output_dir = Path("results")
            output_dir.mkdir(exist_ok=True)
            output_file = str(output_dir / "video_id_mapping.json")
        
        mapping = self.create_video_mapping()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 動画 ID マッピングを保存しました: {output_file}\n")
        
        # サマリーを表示
        total_videos = sum(len(videos) for videos in mapping.values())
        print("=" * 70)
        print("📊 動画 ID 抽出サマリー")
        print("=" * 70 + "\n")
        
        for channel_name, videos in mapping.items():
            print(f"【{channel_name}】 {len(videos)} 個")
        
        print(f"\n合計: {total_videos} 個の動画 ID を抽出しました\n")
        
        return output_file


if __name__ == "__main__":
    extractor = YouTubeMetadataExtractor()
    
    # メタデータを抽出して保存
    extractor.save_metadata_json()
    
    # 動画 ID マッピングを生成して保存
    extractor.save_video_mapping()
