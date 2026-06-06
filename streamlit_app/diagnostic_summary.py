def extract_diagnostic_summary(insight_spec: dict) -> dict:
    """
    insight_spec から AI 用の診断サマリーを抽出する。
    """
    result = {
        "themes": {},
        "difficulty": {},
        "funnel_stages": {},
        "center_pins_count": 0,
        "strongest_theme": "",
        "content_structure": ""
    }
    
    if not insight_spec or not isinstance(insight_spec, dict):
        return result
        
    knowledge_core = insight_spec.get("knowledge_core", {})
    if not isinstance(knowledge_core, dict):
        knowledge_core = {}
        
    center_pins = knowledge_core.get("center_pins", [])
    result["center_pins_count"] = len(center_pins)
    
    for pin in center_pins:
        labels = pin.get("labels", {})
        
        # テーマ
        themes = labels.get("business_theme", [])
        if isinstance(themes, list):
            for t in themes:
                result["themes"][t] = result["themes"].get(t, 0) + 1
        elif isinstance(themes, str):
            result["themes"][themes] = result["themes"].get(themes, 0) + 1
            
        # 難易度
        diff = labels.get("difficulty")
        if diff:
            result["difficulty"][diff] = result["difficulty"].get(diff, 0) + 1
            
        # ファネル
        funnel = labels.get("funnel_stage")
        if funnel:
            result["funnel_stages"][funnel] = result["funnel_stages"].get(funnel, 0) + 1
            
    # パーセンテージ化
    total_themes = sum(result["themes"].values())
    if total_themes > 0:
        for t in result["themes"]:
            result["themes"][t] = round(result["themes"][t] / total_themes * 100)
        # ソートして一番強いテーマを取得
        sorted_themes = sorted(result["themes"].items(), key=lambda x: x[1], reverse=True)
        result["strongest_theme"] = sorted_themes[0][0]
        
    total_diff = sum(result["difficulty"].values())
    if total_diff > 0:
        for d in result["difficulty"]:
            result["difficulty"][d] = round(result["difficulty"][d] / total_diff * 100)
            
    total_funnel = sum(result["funnel_stages"].values())
    if total_funnel > 0:
        for f in result["funnel_stages"]:
            result["funnel_stages"][f] = round(result["funnel_stages"][f] / total_funnel * 100)
            
    # 構造の言語化
    diff_desc = max(result["difficulty"].items(), key=lambda x: x[1])[0] if result["difficulty"] else "不明"
    if diff_desc == "beginner": diff_desc = "初心者向け"
    elif diff_desc == "intermediate": diff_desc = "中級者向け"
    elif diff_desc == "advanced": diff_desc = "上級者向け"
    
    theme_desc = result["strongest_theme"] if result["strongest_theme"] else "テーマ不明"
    
    result["content_structure"] = f"{diff_desc}の基礎講座、{theme_desc}中心"
    
    return result

def extract_channel_diagnostic_summary(lectures: list) -> dict:
    """
    複数の insight_spec から、チャンネル全体の「状態診断」を作成する。
    """
    result = {
        "dominant_themes": {},
        "difficulty_distribution": {},
        "funnel_coverage": {},
        "total_lectures": len(lectures),
        "content_gap": "",
        "channel_strength": "",
        "strategic_weakness": "",
        "next_action": ""
    }
    
    if not lectures:
        return result
        
    for insight_spec in lectures:
        diag = extract_diagnostic_summary(insight_spec)
        
        for t, pct in diag.get("themes", {}).items():
            result["dominant_themes"][t] = result["dominant_themes"].get(t, 0) + pct
            
        for d, pct in diag.get("difficulty", {}).items():
            result["difficulty_distribution"][d] = result["difficulty_distribution"].get(d, 0) + pct
            
        for f, pct in diag.get("funnel_stages", {}).items():
            result["funnel_coverage"][f] = result["funnel_coverage"].get(f, 0) + pct
            
    num = len(lectures)
    for t in result["dominant_themes"]:
        result["dominant_themes"][t] = round(result["dominant_themes"][t] / num)
    for d in result["difficulty_distribution"]:
        result["difficulty_distribution"][d] = round(result["difficulty_distribution"][d] / num)
    for f in result["funnel_coverage"]:
        result["funnel_coverage"][f] = round(result["funnel_coverage"][f] / num)
        
    diff_sorted = sorted(result["difficulty_distribution"].items(), key=lambda x: x[1], reverse=True)
    top_diff = diff_sorted[0][0] if diff_sorted else "不明"
    if top_diff == "beginner": diff_desc = "初心者向け"
    elif top_diff == "intermediate": diff_desc = "中級者向け"
    elif top_diff == "advanced": diff_desc = "上級者向け"
    else: diff_desc = "対象不明"
    
    funnel_sorted = sorted(result["funnel_coverage"].items(), key=lambda x: x[1], reverse=True)
    top_funnel = funnel_sorted[0][0] if funnel_sorted else "不明"
    
    result["channel_strength"] = f"{diff_desc}の『{top_funnel}』に特化"
    
    if len(funnel_sorted) > 1:
        weak_funnel = funnel_sorted[-1][0]
        result["strategic_weakness"] = f"『{weak_funnel}』層向けコンテンツが手薄"
        result["content_gap"] = f"『{weak_funnel}』レベルのコンテンツが不足"
        result["next_action"] = f"『{weak_funnel}』向けの補強コンテンツを制作"
    else:
        result["strategic_weakness"] = "顧客ジャーニーの多様な層へのアプローチが不足"
        result["content_gap"] = "応用・実践レベルのコンテンツが不足"
        result["next_action"] = "新たなファネル層向けのシリーズを展開"
        
    return result

def extract_competitive_advantage_summary(advantage: dict) -> dict:
    """
    競争優位性スコアを「状態診断」に翻訳する。
    """
    result = {
        "beginner_focus": "",
        "theme_diversity_desc": "",
        "content_richness": "",
        "overall_positioning": ""
    }
    if not advantage:
        return result
        
    bs = advantage.get("beginner_suitability", 0)
    if bs > 70:
        result["beginner_focus"] = "初心者向けに最適化された構成"
    elif bs > 30:
        result["beginner_focus"] = "幅広い層（初〜中級者）に対応する構成"
    else:
        result["beginner_focus"] = "上級者・専門家向けに特化した構成"
        
    td = advantage.get("theme_diversity", 0)
    if td > 70:
        result["theme_diversity_desc"] = "多角的なテーマを扱う網羅的コンテンツ"
    elif td > 40:
        result["theme_diversity_desc"] = "テーマの多様性は中程度"
    else:
        result["theme_diversity_desc"] = "単一テーマに特化した専門的コンテンツ"
        
    cd = advantage.get("content_diversity", 0)
    if cd > 70:
        result["content_richness"] = "コンテンツの豊かさは高い"
    elif cd > 40:
        result["content_richness"] = "コンテンツの豊かさは標準的"
    else:
        result["content_richness"] = "コンテンツの豊かさは限定的"
        
    result["overall_positioning"] = f"{result['beginner_focus']}であり、{result['theme_diversity_desc']}。{result['content_richness']}。"
    
    return result

def extract_golden_pattern_summary(patterns: list) -> list:
    """
    高反応パターンの数字を削除し、構造的な勝因のみ抽出。
    """
    results = []
    if not patterns:
        return results
        
    for idx, p in enumerate(patterns):
        funnel = p.get('funnel_stage', '不明')
        ctype = p.get('content_type', '不明')
        theme = p.get('theme', '不明')
        results.append(f"パターン{idx+1}: {funnel}層 × {ctype} × {theme}")
        
    return results

def extract_hidden_weakness_diagnosis(weakness_data: dict) -> dict:
    """
    品質とエンゲージメントのギャップを「なぜ起きているのか」の文脈に翻訳。
    """
    result = {
        "state": "内容は充実しているが視聴者反応が期待値より低い",
        "funnel": weakness_data.get("funnel_stage", "不明"),
        "theme": weakness_data.get("themes", "不明"),
        "content_preview": weakness_data.get("content", "")
    }
    return result
