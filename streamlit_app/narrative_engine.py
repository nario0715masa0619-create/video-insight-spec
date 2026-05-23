import os
import json
from openai import OpenAI
from pathlib import Path

class NarrativeEngine:
    """GPT-4o を活用した言語化エンジン"""
    
    def __init__(self):
        # .env ファイルから直接読み込む
        env_file = Path(__file__).parent.parent / ".env"
        api_key = ""
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        
        if not api_key:
            raise ValueError("❌ .env に OPENAI_API_KEY が見つかりません")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        self.temperature = 0.7
        self.max_tokens = 4000
    
    def _call_gpt(self, user_prompt, system_prompt="あなたはYouTubeチャンネル分析の専門家です。日本語で、分かりやすく、ビジネス的観点から解説してください。"):
        """GPT API呼び出し"""
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
    
    def explain_channel_overview(self, metrics):
        """チャンネル全体の解説"""
        prompt = f"""このYouTubeチャンネルの分析結果:
- 平均Quality Score: {metrics.get('avg_quality', 0):.1f}
- 平均Semantic Purity: {metrics.get('avg_semantic_purity', 0):.1f}
- 総再生数: {metrics.get('total_views', 0):,}
- 総いいね: {metrics.get('total_likes', 0):,}
- 総コメント: {metrics.get('total_comments', 0):,}

【解説】このチャンネルの総合的な評価と今後の方向性を説明してください。
【推奨アクション】3つの具体的な改善提案を提示してください。"""
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

