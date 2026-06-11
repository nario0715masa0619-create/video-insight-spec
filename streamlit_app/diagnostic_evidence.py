def extract_diagnostic_evidence(insight_specs: list, lecture_id: str = None) -> dict:
    """
    insight_spec_{id}.json から、数値説明ではなく
    「言葉・キーワード・意味構造」中心の診断用中間材料を抽出する
    """
    if lecture_id:
        insight_specs = [s for s in insight_specs if s.get('lecture_id') == lecture_id]
        
    all_pins = []
    all_difficulties = []
    all_funnels = []
    
    for spec in insight_specs:
        kc = spec.get('knowledge_core', {})
        pins = kc.get('center_pins', [])
        all_pins.extend(pins)
        for pin in pins:
            labels = pin.get('labels', {})
            diff = labels.get('difficulty')
            if diff: all_difficulties.append(diff)
            funnel = labels.get('funnel_stage')
            if funnel: all_funnels.append(funnel)
            
    theme_core = extract_theme_core(all_pins)
    learning_roles = extract_learning_roles(all_pins)
    funnel_profile = extract_funnel_profile(all_funnels)
    difficulty_profile = extract_difficulty_profile(all_difficulties)
    audience_clarity = extract_audience_clarity(all_pins, theme_core)
    bridge_gaps = extract_bridge_gaps(funnel_profile, difficulty_profile)
    message_consistency = extract_message_consistency(theme_core, learning_roles)
    hidden_strengths = extract_hidden_strengths(all_pins, audience_clarity)
    hidden_gaps = extract_hidden_gaps(bridge_gaps, funnel_profile)
    
    return {
        "theme_core": theme_core,
        "learning_roles": learning_roles,
        "funnel_profile": funnel_profile,
        "difficulty_profile": difficulty_profile,
        "audience_clarity": audience_clarity,
        "bridge_gaps": bridge_gaps,
        "message_consistency": message_consistency,
        "hidden_strengths": hidden_strengths,
        "hidden_gaps": hidden_gaps,
        "evidence_metrics": { "total_pins": len(all_pins) }
    }

def extract_theme_core(center_pins: list) -> dict:
    themes = {}
    keywords = []
    for pin in center_pins:
        t = pin.get('labels', {}).get('business_theme', [])
        if isinstance(t, str): t = [t]
        for th in t:
            themes[th] = themes.get(th, 0) + 1
        content = pin.get('content', '')
        if len(content) > 5:
            keywords.append(content[:15] + "...")
            
    sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_themes[0][0] if sorted_themes else "不明"
    
    return {
        "primary_theme": primary,
        "sub_themes": [t[0] for t in sorted_themes[1:3]],
        "key_topics": list(set(keywords))[:5]
    }

def extract_learning_roles(center_pins: list) -> dict:
    roles = set()
    for pin in center_pins:
        t = pin.get('type', '')
        if t == 'concept':
            roles.add("基礎概念・理論の理解と整理")
        elif t == 'framework':
            roles.add("分析フレームワーク・判断基準の提供")
        elif t == 'strategy':
            roles.add("戦略・方針の示唆")
        elif t == 'tactic':
            roles.add("実行手法・タクティクスの提示")
        else:
            roles.add("知識の総合提供")
    
    return {
        "primary_role": list(roles)[0] if roles else "不明",
        "observed_roles": list(roles)
    }

def extract_funnel_profile(funnels: list) -> dict:
    counts = {}
    for f in funnels: counts[f] = counts.get(f, 0) + 1
    total = len(funnels)
    
    profile = {}
    if total == 0:
        profile['summary'] = "段階不明"
        return profile
        
    for f, c in counts.items():
        ratio = c / total
        if ratio > 0.6:
            profile[f] = "非常に厚い（主軸）"
        elif ratio > 0.3:
            profile[f] = "厚い（主要要素）"
        elif ratio > 0.1:
            profile[f] = "薄い（補助的）"
        else:
            profile[f] = "ほとんどない"
            
    sorted_f = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top = sorted_f[0][0] if sorted_f else ""
    profile['summary'] = f"『{top}』段階を中心とした構成"
    
    return profile

def extract_difficulty_profile(difficulties: list) -> dict:
    counts = {}
    for d in difficulties: counts[d] = counts.get(d, 0) + 1
    total = len(difficulties)
    
    if total == 0:
        return {"summary": "難易度不明"}
        
    sorted_d = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top = sorted_d[0][0]
    
    desc = "初級" if top == "beginner" else "中級" if top == "intermediate" else "上級"
    
    return {
        "summary": f"{desc}向けが主体",
        "dominant_level": desc
    }

def extract_audience_clarity(center_pins: list, theme_core: dict) -> dict:
    is_clear = len(theme_core.get("sub_themes", [])) <= 1
    return {
        "is_clear": is_clear,
        "description": "想定視聴者が明確に絞り込まれている" if is_clear else "幅広い層に向けられており、対象がやや分散している"
    }

def extract_bridge_gaps(funnel_profile: dict, difficulty_profile: dict) -> dict:
    summary = funnel_profile.get("summary", "")
    diff = difficulty_profile.get("summary", "")
    
    gap = "特になし"
    if "認知" in summary and "初級" in diff:
        gap = "認知から次の『興味・検討』へ引き上げる中間ステップ（橋渡し）が不足しがち"
    elif "初級" in diff:
        gap = "基礎から実務応用への橋渡しが課題"
        
    return {
        "identified_gap": gap
    }

def extract_message_consistency(theme_core: dict, learning_roles: dict) -> dict:
    return {
        "consistency_level": "高い" if theme_core.get("primary_theme") != "不明" else "低い",
        "description": f"『{theme_core.get('primary_theme', '')}』を中心に、一貫したメッセージが展開されている"
    }

def extract_hidden_strengths(center_pins: list, audience_clarity: dict) -> dict:
    if audience_clarity.get("is_clear"):
        return {"strength": "ターゲットが明確で、メッセージのブレがない点"}
    return {"strength": "多様な視点から情報を網羅している点"}

def extract_hidden_gaps(bridge_gaps: dict, funnel_profile: dict) -> dict:
    return {
        "gap": bridge_gaps.get("identified_gap", "特になし")
    }

def format_evidence_for_prompt(evidence: dict) -> str:
    lines = [
        "【診断用中間材料】",
        f"- 中心となるテーマ: {evidence['theme_core'].get('primary_theme', '')}",
        f"- サブテーマ: {', '.join(evidence['theme_core'].get('sub_themes', []))}",
        f"- コンテンツが果たす学習役割: {', '.join(evidence['learning_roles'].get('observed_roles', []))}",
        f"- 視聴者の検討段階（ファネル）の厚み: {evidence['funnel_profile'].get('summary', '')}",
        f"- 難易度の設定: {evidence['difficulty_profile'].get('summary', '')}",
        f"- 想定視聴者の一貫性: {evidence['audience_clarity'].get('description', '')}",
        f"- 構造上の強み: {evidence['hidden_strengths'].get('strength', '')}",
        f"- 構造上の課題（不足・橋渡し）: {evidence['hidden_gaps'].get('gap', '')}"
    ]
    return "\n".join(lines)
def extract_pattern_evidence(golden_patterns: list) -> str:
    """高反応パターンを構造的勝因として言語化"""
    if not golden_patterns:
        return "特定の高反応パターンは検出されていません。"
        
    lines = ["【構造的勝因の抽出】"]
    for i, p in enumerate(golden_patterns[:3], 1):
        lines.append(f"- パターン{i}: 『{p.get('funnel_stage', '')}』ステージの視聴者が『{p.get('theme', '')}』テーマを『{p.get('content_type', '')}』形式で学習する構造が検出されました（出現回数: {p.get('count', 1)}回、スコア: {p.get('avg_engagement', 0):.2f}）。")
    
    return "\n".join(lines)

def extract_weakness_evidence(weaknesses: list) -> str:
    """品質と反応のギャップを状態として言語化"""
    if not weaknesses:
        return "特筆すべき構造的弱点は検出されていません。"
        
    lines = ["【隠れた弱点の状態】"]
    for i, w in enumerate(weaknesses[:2], 1):
        lines.append(f"- 課題{i}: 『{w.get('funnel_stage', '')}』層に向けた『{w.get('themes', '')}』のコンテンツは、内容は充実しているものの視聴者の期待や理解度とミスマッチを起こしており、反応が鈍い状態です。")
        
    return "\n".join(lines)

def extract_competitive_evidence(competitive_data: dict) -> str:
    """競争優位性を数値根拠と計算方法を明記して言語化"""
    if not competitive_data:
        return "競争優位性データが不足しています。"

    td = competitive_data.get('theme_diversity', 0)
    cd = competitive_data.get('content_diversity', 0)
    bs = competitive_data.get('beginner_suitability', 0)
    ed = competitive_data.get('engagement_density', 0)
    total = competitive_data.get('total_score', 0)

    lines = ["【市場競争優位性の詳細分析】"]
    lines.append(f"総合スコア: {total:.1f}/100（テーマ 30% + コンテンツ形式 20% + エンゲージメント 30% + 初心者適性 20% で加重平均）")
    lines.append("")
    
    lines.append("【各指標の詳細解説】")
    lines.append("")
    
    # テーマ多様性
    lines.append(f"【1】テーマ多様性: {td:.1f}%")
    lines.append("  定義：このチャンネルが扱うビジネステーマの種類数を、標準的な 5 テーマを基準に指数化")
    lines.append("  分析:")
    if td >= 80:
        lines.append(f"    - {td:.1f}% は非常に高い多様性を示す。20+ のテーマをカバーしており、幅広い視聴者にリーチ可能")
        lines.append("    - 競合との差別化要因となり得る")
    elif td >= 50:
        lines.append(f"    - {td:.1f}% は中程度。複数テーマの均衡の取れた展開")
    else:
        lines.append(f"    - {td:.1f}% は低い。特定テーマへの深い専門性を示す")
    lines.append("")
    
    # コンテンツ多様性
    lines.append(f"【2】コンテンツ形式多様性: {cd:.1f}%")
    lines.append("  定義：使用しているコンテンツ形式の種類（最大 4 種：概念、戦略、フレームワーク、タクティクス）")
    lines.append("  分析:")
    if cd >= 75:
        lines.append(f"    - {cd:.1f}% は 4 形式すべてを活用。学習者のニーズに多角的に対応")
    elif cd >= 50:
        lines.append(f"    - {cd:.1f}% は 2 形式程度。現在は『{cd:.0f}%』の形式多様性。補強ポテンシャルあり")
    else:
        lines.append(f"    - {cd:.1f}% は 1 形式のみ。特定形式に一貫性を持たせた戦略")
    lines.append("")
    
    # エンゲージメント効率
    lines.append(f"【3】エンゲージメント効率: {ed:.1f}%")
    lines.append("  定義：（高評価 + コメント数）/ 再生数を、業界平均（8%）との相対値で指数化")
    lines.append("  分析:")
    if ed >= 75:
        lines.append(f"    - {ed:.1f}% は業界平均を大きく上回る高エンゲージメント")
    elif ed >= 50:
        lines.append(f"    - {ed:.1f}% は業界平均と同等程度。成長段階で改善の余地あり")
    else:
        lines.append(f"    - {ed:.1f}% は業界平均（8%）を下回る。プロモーション強化や発見機会拡大で改善可能")
    lines.append("")
    
    # 初心者適性
    lines.append(f"【4】初心者向け適性: {bs:.1f}%")
    lines.append("  定義：初級レベルコンテンツの比率（初心者向け / 全コンテンツ）")
    lines.append("  分析:")
    if bs >= 50:
        lines.append(f"    - {bs:.1f}% は初心者層向けが充実。新規視聴者獲得に有利")
    elif bs >= 30:
        lines.append(f"    - {bs:.1f}% は中級者メインで初心者層もカバー。バランス型")
    else:
        lines.append(f"    - {bs:.1f}% は上級者向け。ニッチ市場で専門性を活かした強いポジション")
    lines.append("")
    
    lines.append("【総合ポジショニング】")
    if total >= 75:
        lines.append("高い総合競争優位性を確保。多様性と専門性のバランスが優れている。")
    elif total >= 60:
        lines.append("中程度の優位性。強み領域を活かしながら、弱い指標を補強することで差別化を強化可能。")
    else:
        lines.append("成長段階。現在の強み（テーマ多様性など）を活かしつつ、エンゲージメント向上に注力する段階。")

    return "\n".join(lines)

