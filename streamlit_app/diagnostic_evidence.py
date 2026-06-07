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
        if t == 'concept': roles.add("基礎概念の理解と整理")
        elif t == 'framework': roles.add("判断基準・フレームワークの提供")
        elif t == 'case_study': roles.add("実務事例からの学び")
        else: roles.add("知識のインプット")
    
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
    "\""高反応パターンを「構造的勝因」として言語化"\""
    if not golden_patterns:
        return "特定の高反応パターンは検出されていません。"
        
    lines = ["【構造的勝因の抽出】"]
    for i, p in enumerate(golden_patterns[:3], 1):
        lines.append(f"- 勝因パターン{i}: 『{p.get('funnel_stage', '')}』段階の視聴者に対して、『{p.get('theme', '')}』を『{p.get('content_type', '')}』で提示する構造が強く支持されています。")
    
    return "\n".join(lines)

def extract_weakness_evidence(weaknesses: list) -> str:
    "\""品質と反応のギャップを「状態」として言語化"\""
    if not weaknesses:
        return "特筆すべき構造的弱点は検出されていません。"
        
    lines = ["【隠れた弱点の状態】"]
    for i, w in enumerate(weaknesses[:2], 1):
        lines.append(f"- 課題{i}: 『{w.get('funnel_stage', '')}』層に向けた『{w.get('themes', '')}』のコンテンツは、内容は充実しているものの視聴者の期待や理解度とミスマッチを起こしており、反応が鈍い状態です。")
        
    return "\n".join(lines)

def extract_competitive_evidence(competitive_data: dict) -> str:
    "\""競争優位性を「ポジショニング」として言語化"\""
    if not competitive_data:
        return "競争優位性データが不足しています。"
        
    td = competitive_data.get('theme_diversity', 0)
    cd = competitive_data.get('content_diversity', 0)
    bs = competitive_data.get('beginner_suitability', 0)
    ed = competitive_data.get('engagement_density', 0)
    
    lines = ["【市場でのポジショニングと競争優位性】"]
    lines.append(f"- ターゲット適合度: {'初心者から中級者まで広くカバーする構成' if bs > 50 else '専門家・上級者に絞り込んだ尖った構成'}")
    lines.append(f"- テーマの網羅性: {'複数のテーマを横断的に扱う総合型' if td > 50 else '特定テーマに特化した専門型'}")
    lines.append(f"- コンテンツの厚み: {'多様な形式（概念、事例、ワーク等）で深く学べる構成' if cd > 50 else 'シンプルな形式で要点を絞った構成'}")
    lines.append(f"- 視聴者の熱量: {'非常に高く、活発なコミュニティが形成されている' if ed > 50 else 'まだ発展途上であり、働きかけが必要'}")
    
    return "\n".join(lines)
