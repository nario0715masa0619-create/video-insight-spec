import os
import sys
import json
from openai import OpenAI
from pathlib import Path

# リポジトリルートを sys.path に追加して env_loader を読み込む
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
from env_loader import load_env
load_env()

class NarrativeEngine:
    """GPT-4o を活用した言語化エンジン"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.available = bool(api_key)
        
        if self.available:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            
        self.model = "gpt-4o"
        self.temperature = 0.7
        self.max_tokens = 4000
    
    def _call_gpt(self, user_prompt, system_prompt="あなたはYouTubeチャンネル分析の専門家です。日本語で、分かりやすく、ビジネス的観点から解説してください。"):
        """GPT API呼び出し"""
        if not self.available:
            return "⚠️ AI 分析エンジンは無効化されています。(OPENAI_API_KEY が未設定です)"
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ GPT エラー: {str(e)}"
    
    def explain_channel_overview(self, metrics, channel_diag=None):
        """チャンネル全体の解説"""
        if channel_diag is None:
            channel_diag = {}
            
        theme_str = ", ".join([f"{k} {v}%" for k, v in channel_diag.get("dominant_themes", {}).items()])
        diff_str = ", ".join([f"{k} {v}%" for k, v in channel_diag.get("difficulty_distribution", {}).items()])
        funnel_str = ", ".join([f"{k} {v}%" for k, v in channel_diag.get("funnel_coverage", {}).items()])
        
        prompt = f"""このチャンネルの全体構造:
- 主要テーマ: {theme_str}
- コンテンツレベル: {diff_str}
- ファネルカバレッジ: {funnel_str}
- 合計動画数: {channel_diag.get('total_lectures', 0)} 本
- チャンネルの強み: {channel_diag.get('channel_strength', '')}
- チャンネルの弱み: {channel_diag.get('strategic_weakness', '')}

参考指標（根拠としてのみ使用）:
- 平均Quality Score: {f"{metrics.get('avg_quality'):.1f}" if metrics.get('avg_quality') is not None else "データ準備中"}
- 平均Semantic Purity: {f"{metrics.get('avg_semantic_purity'):.1f}" if metrics.get('avg_semantic_purity') is not None else "データ準備中"}
- 総再生数: {metrics.get('total_views', 0):,}
- 総いいね: {metrics.get('total_likes', 0):,}
- 総コメント: {metrics.get('total_comments', 0):,}

このチャンネルから以下を診断してください:
1) このチャンネルの『顧客獲得における役割』は何か
2) 現在の構造が達成できていることと、できていないことは何か
3) このチャンネルの『戦略的な弱点』は何か
4) 次にどのレベル・どのテーマのコンテンツを優先すべきか
5) 長期的なコンテンツロードマップの提案

※回答は「状態診断」として、スコアの説明ではなく、チャンネルが果たしている役割、その限界、次に何をすべきかを述べてください。"""
        return self._call_gpt(prompt)
    
    def explain_funnel_stage_analysis(self, lecture_id, funnel_data):
        """ファネルステージ分析の解説"""
        prompt = f"""講座{lecture_id:02d}のファネルステージ別分析結果:
{json.dumps(funnel_data, ensure_ascii=False, indent=2)}

【解説】各ステージでの視聴者反応傾向を分析し、ビジネス的な意味を説明してください。
【推奨アクション】高反応ステージを活かした具体的な改善策を提示してください。"""
        return self._call_gpt(prompt)
    
    def explain_content_type_quality(self, lecture_id, content_data):
        """コンテンツタイプ別品質の解説"""
        prompt = f"""講座{lecture_id:02d}のコンテンツタイプ別品質分析:
{json.dumps(content_data, ensure_ascii=False, indent=2)}

【解説】各コンテンツタイプの強み・弱みを分析してください。
【推奨アクション】品質向上のための具体的な施策を提示してください。"""
        return self._call_gpt(prompt)
    
    def explain_theme_analysis(self, lecture_id, themes):
        """テーマ分析の解説"""
        prompt = f"""講座{lecture_id:02d}のビジネステーマ分布:
{json.dumps(themes, ensure_ascii=False, indent=2)}

【解説】このテーマ分布が示す講座の特性を説明してください。
【推奨アクション】視聴者ニーズに対応したテーマ追加の提案をしてください。"""
        return self._call_gpt(prompt)
    
    def explain_engagement_efficiency(self, lecture_id, efficiency_score, likes_per_1k, comments_per_1k):
        """エンゲージメント効率の解説"""
        prompt = f"""講座{lecture_id:02d}のエンゲージメント効率:
- 効率スコア: {efficiency_score:.1f}/100
- 1000再生あたりのいいね: {likes_per_1k:.2f}
- 1000再生あたりのコメント: {comments_per_1k:.2f}

【解説】この講座の視聴者エンゲージメント水準を評価してください。
【推奨アクション】エンゲージメント向上の具体的な方法を提示してください。"""
        return self._call_gpt(prompt)

