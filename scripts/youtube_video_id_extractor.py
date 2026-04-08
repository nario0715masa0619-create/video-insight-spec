import os
import json
from pathlib import Path
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeVideoIDExtractor:
    """メタデータ JSON から動画 ID を抽出"""
    
    def __init__(self, results_dir: str = None):
        """
        初期化
        
        Args:
            results_dir: メタデータ JSON の保存先（デフォルト: results/）
        """
        if results_dir is None:
            results_dir = "results"
        
        self.results_dir = Path(results_dir)
    
    def extract_video_ids_from_metadata(self) -> Dict[str, Dict]:
        """
        メタデータ JSON ファイルから動画 ID を抽出
        
        Returns:
            {チャンネル名: {動画ID: メタデータ}} の構造
        """
        result = {}
        
        # results/ ディレクトリ内のすべての *_metadata.json ファイルを処理
        metadata_files = list(self.results_dir.glob('*_metadata.json'))
        
        print("\n" + "=" * 70)
        print("📊 メタデータから動画 ID を抽出中...")
        print("=" * 70 + "\n")
        
        for metadata_file in sorted(metadata_files):
            channel_name = metadata_file.stem.replace('_metadata', '')
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_list = json.load(f)
                
                print(f"📁 チャンネル: {channel_name}")
                print(f"📹 ファイル: {metadata_file.name}\n")
                
                channel_videos = {}
                for idx, metadata in enumerate(metadata_list, 1):
                    video_id = metadata.get('video_id')
                    title = metadata.get('title')
                    duration = metadata.get('duration', 0)
                    
                    if video_id:
                        channel_videos[video_id] = {
                            'title': title,
                            'duration': duration,
                            'filename': metadata.get('filename'),
                            'upload_date': metadata.get('upload_date'),
                            'channel': channel_name
                        }
                        
                        print(f"  [{idx}] {title}")
                        print(f"       動画 ID: {video_id}")
                        print(f"       長さ: {duration}秒")
                        print()
                
                result[channel_name] = channel_videos
            
            except Exception as e:
                logger.error(f"❌ エラー ({metadata_file}): {e}")
        
        return result
    
    def save_video_mapping(self, output_file: str = None) -> str:
        """
        抽出した動画 ID マッピングを JSON に保存
        
        Args:
            output_file: 出力ファイルパス（デフォルト: results/video_id_mapping.json）
        
        Returns:
            保存したファイルパス
        """
        if output_file is None:
            output_file = str(self.results_dir / "video_id_mapping.json")
        
        result = self.extract_video_ids_from_metadata()
        
        self.results_dir.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 動画 ID マッピングを保存しました: {output_file}\n")
        return output_file
    
    def get_video_mapping_summary(self) -> None:
        """抽出結果のサマリーを表示"""
        result = self.extract_video_ids_from_metadata()
        
        print("=" * 70)
        print("📊 動画 ID 抽出サマリー")
        print("=" * 70 + "\n")
        
        total_videos = 0
        for channel, videos in result.items():
            print(f"【{channel}】 {len(videos)} 個")
            total_videos += len(videos)
        
        print(f"\n合計: {total_videos} 個の動画 ID を抽出しました\n")


if __name__ == "__main__":
    extractor = YouTubeVideoIDExtractor()
    
    # 動画 ID マッピングを抽出して保存
    extractor.save_video_mapping()
    
    # サマリーを表示
    extractor.get_video_mapping_summary()
