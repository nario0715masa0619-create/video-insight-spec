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
