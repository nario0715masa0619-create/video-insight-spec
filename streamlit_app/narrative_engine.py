import os
import sys
import json
from openai import OpenAI
from pathlib import Path

# リポジトリルートを sys.path に追加して env_loader を読み込む
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
from streamlit_app.env_loader import ensure_env_loaded
ensure_env_loaded()

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
    
    def explain_channel_diagnosis(self, insights_data: list) -> str:
        """
        現在のチャンネル状態を診断する（改善案は出さない）
        """
        from streamlit_app.diagnostic_evidence import extract_diagnostic_evidence, format_evidence_for_prompt
        
        evidence = extract_diagnostic_evidence(insights_data)
        evidence_text = format_evidence_for_prompt(evidence)
        
        prompt = f"""
あなたはビジネスコンサルタントです。
以下の【診断用中間材料】を元に、現在のチャンネル構造から、以下だけを述べてください。

{evidence_text}

1. 現在の役割：このチャンネルは誰の、どのステップ向けに機能しているか
2. 構造上の強み：テーマ・難易度・検討段階の観点から、何が充実しているか
3. 構造上の弱み：テーマ・難易度・検討段階の観点から、何が不足しているか
4. 欠けている橋渡し：ステップ間のギャップはどこか

【禁止】以下は絶対に書かないこと：
- 「～すべき」「次は～」などのアクション指示
- 「〜を追加する」「〜を増やす」などの改善提案
- 今後やるべきことの説明

【形式】
- 段落形式、日本語自然文
- 数値は参考情報として末尾に補足
"""
        return self._call_gpt(prompt)

    def explain_channel_improvements(self, insights_data: list) -> str:
        """
        チャンネルの次のアクションを提案する（現状は説明しない）
        """
        from streamlit_app.diagnostic_evidence import extract_diagnostic_evidence, format_evidence_for_prompt
        
        evidence = extract_diagnostic_evidence(insights_data)
        evidence_text = format_evidence_for_prompt(evidence)
        
        prompt = f"""
あなたはビジネスコンサルタントです。
以下の【診断用中間材料】を踏まえて、以下だけを述べてください。

{evidence_text}

1. 最優先のアクション：最初に何を作るべきか、その理由
2. 次点のアクション：その次に何を作るべきか、その理由
3. 対応順：なぜその順番か
4. 期待される効果：その順で作ることで、チャンネルはどう変わるか

【禁止】以下は絶対に書かないこと：
- 現状の長い説明（「入門に強い」「比較検討が弱い」など）
- 診断文の焼き直しや繰り返し
- 「現在〜である」という状態説明
- 数値やスコアの再説明

【形式】
- 段落形式、日本語自然文
- 「短期（1～3ヶ月）」「中期（3～6ヶ月）」などの時間軸があれば示す
"""
        return self._call_gpt(prompt)

    def explain_channel_overview(self, insights_data: list) -> str:
        """非推奨: explain_channel_diagnosis + explain_channel_improvements を使用すること"""
        pass

    def explain_single_video(self, insights_data: list, lecture_id: str) -> str:
        """個別動画の基本分析"""
        from diagnostic_evidence import extract_diagnostic_evidence, format_evidence_for_prompt
        evidence = extract_diagnostic_evidence(insights_data, lecture_id=lecture_id)
        evidence_text = format_evidence_for_prompt(evidence)
        
        prompt = f"""
あなたはビジネスコンサルタントです。
以下は、特定の個別動画の構造分析の結果です。
数字や指標の説明ではなく、この動画の「役割」「強み」「弱点」「次にとるべき方向」を診断してください。

【診断証拠（中間材料）】
{evidence_text}

以下の形式で診断してください：
1. 役割と強み：この動画が果たしている学習上の役割と強みは何か
2. 課題と弱点：構造上の課題や、不足している橋渡しは何か
3. 次のアクション：視聴者を次のステップへ導くため、次に追加・案内すべき内容は何か
4. 根拠：必要に応じて、上記の分析の根拠となる具体的な構造要素を簡潔に示す
"""
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

