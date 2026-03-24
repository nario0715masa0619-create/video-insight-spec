# test_gemini_knowledge_labeler.py 強化計画

**評価元**: Perplexity AI  
**評価日**: 2026-03-24  
**現状**: 15/15 PASS（カバレッジ良好）  
**課題**: 境界・異常系・エラー分類の詳細テストが不足

---

## 現状評価

### ✅ 既にカバーされている点
- **初期化**: API キー有無の分岐テスト
- **プロンプト生成**: visual_text_excerpt 有無の分岐
- **ラベル検証**: 正常系、business_theme 過多、difficulty 不正値
- **label_center_pin**: JSON エラー、バリデーションエラーの基本
- **リトライ**: 成功 / 全失敗パターン
- **ファイル I/O**: 保存成功、内容一致確認

### ❌ テスト未カバーの領域
- _validate_labels の詳細な境界テスト
- label_center_pin のエッジケース
- リトライの「途中失敗 → 成功」パターン
- insight_spec の異常構造テスト
- ファイル保存の権限エラーシミュレーション
- API 呼び出しの引数検証（generation_config）

---

## テスト強化計画（詳細）

### Phase A: _validate_labels の拡張テスト

#### A1. business_theme の境界テスト
```python
def test_validate_labels_business_theme_empty_list(mock_labeler):
    """business_theme が空配列の場合は無効"""
    labels = {
        "business_theme": [],
        "funnel_stage": "教育",
        "difficulty": "intermediate"
    }
    assert mock_labeler._validate_labels(labels) is False

def test_validate_labels_business_theme_not_list(mock_labeler):
    """business_theme がリストではない場合は無効"""
    invalid_cases = [
        "マーケティング",  # 文字列単体
        None,
        123,
        {"main": "マーケティング"}  # dict
    ]
    for invalid_value in invalid_cases:
        labels = {
            "business_theme": invalid_value,
            "funnel_stage": "教育",
            "difficulty": "intermediate"
        }
        assert mock_labeler._validate_labels(labels) is False

def test_validate_labels_business_theme_non_string_elements(mock_labeler):
    """business_theme に非文字列要素が混ざる場合は無効"""
    invalid_cases = [
        [123, "マーケティング"],  # 数値混在
        ["マーケティング", None],  # None 混在
        ["マーケティング", {"sub": "詳細"}]  # dict 混在
    ]
    for invalid_list in invalid_cases:
        labels = {
            "business_theme": invalid_list,
            "funnel_stage": "教育",
            "difficulty": "intermediate"
        }
        assert mock_labeler._validate_labels(labels) is False
Copy
見積もり: 1 時間
優先度: ⭐⭐⭐

A2. funnel_stage の境界テスト
Copydef test_validate_labels_funnel_stage_missing(mock_labeler):
    """funnel_stage が無い場合は無効"""
    labels = {
        "business_theme": ["マーケティング"],
        # "funnel_stage" 欠落
        "difficulty": "intermediate"
    }
    assert mock_labeler._validate_labels(labels) is False

def test_validate_labels_funnel_stage_invalid_type(mock_labeler):
    """funnel_stage が文字列以外は無効"""
    invalid_cases = [None, 123, ["教育"], {"stage": "教育"}]
    for invalid_value in invalid_cases:
        labels = {
            "business_theme": ["マーケティング"],
            "funnel_stage": invalid_value,
            "difficulty": "intermediate"
        }
        assert mock_labeler._validate_labels(labels) is False
見積もり: 30 分
優先度: ⭐⭐⭐

A3. labels 構造の不完全性テスト
Copydef test_validate_labels_missing_required_field(mock_labeler):
    """必須キーが欠落している場合は無効"""
    incomplete_cases = [
        {"business_theme": ["マーケティング"], "funnel_stage": "教育"},  # difficulty 欠落
        {"business_theme": ["マーケティング"], "difficulty": "beginner"},  # funnel_stage 欠落
        {"funnel_stage": "教育", "difficulty": "beginner"}  # business_theme 欠落
    ]
    for incomplete_labels in incomplete_cases:
        assert mock_labeler._validate_labels(incomplete_labels) is False

def test_validate_labels_empty_dict(mock_labeler):
    """空の dict は無効"""
    assert mock_labeler._validate_labels({}) is False
見積もり: 30 分
優先度: ⭐⭐⭐

Phase B: label_center_pin の拡張異常ケース
B1. labels フィールド欠落テスト
Copydef test_label_center_pin_missing_labels_field(mock_labeler, sample_center_pin):
    """レスポンスに labels フィールドがない場合"""
    response_without_labels = {"some_other_field": "value"}
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps(response_without_labels)
    )
    
    result = mock_labeler.label_center_pin(sample_center_pin)
    
    # 元の pin が変更されずに返される
    assert result == sample_center_pin
    assert "labels" not in result
見積もり: 30 分
優先度: ⭐⭐⭐

B2. labels が dict ではないケース
Copydef test_label_center_pin_labels_not_dict(mock_labeler, sample_center_pin):
    """labels が dict ではない場合（文字列など）"""
    invalid_responses = [
        {"labels": "invalid_string"},
        {"labels": ["invalid", "array"]},
        {"labels": 123}
    ]
    
    for invalid_response in invalid_responses:
        mock_labeler.gen_model.generate_content.return_value = Mock(
            text=json.dumps(invalid_response)
        )
        
        result = mock_labeler.label_center_pin(sample_center_pin)
        
        # バリデーション失敗 → 元の pin を返す
        assert result == sample_center_pin
        assert "labels" not in result
見積もり: 30 分
優先度: ⭐⭐⭐

B3. visual_text_excerpt パラメータの検証
Copydef test_label_center_pin_with_long_visual_text(mock_labeler, sample_center_pin):
    """長い visual_text が正しくプロンプトに含まれること"""
    long_text = "あ" * 1000  # 長いテキスト
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({
            "labels": {
                "business_theme": ["マーケティング"],
                "funnel_stage": "教育",
                "difficulty": "beginner"
            }
        })
    )
    
    result = mock_labeler.label_center_pin(sample_center_pin, visual_text_excerpt=long_text)
    
    # プロンプトに visual_text が含まれたことを確認
    call_args = mock_labeler.gen_model.generate_content.call_args
    prompt = call_args[0][0]
    assert long_text in prompt
見積もり: 30 分
優先度: ⭐⭐

Phase C: _call_gemini_with_retry の詳細テスト
C1. 途中失敗 → 成功パターン
Copydef test_call_gemini_with_retry_partial_failure(mock_labeler):
    """1 回目失敗、2 回目で成功するケース"""
    response_text = '{"labels": {"business_theme": ["A"], "funnel_stage": "認知", "difficulty": "beginner"}}'
    
    # side_effect で 1 回目は Exception、2 回目は成功レスポンス
    mock_labeler.gen_model.generate_content.side_effect = [
        Exception("API Timeout"),
        Mock(text=response_text)
    ]
    
    result = mock_labeler._call_gemini_with_retry("test prompt", max_retries=3)
    
    # 成功レスポンスが返される
    assert result == response_text
    # generate_content が 2 回呼ばれたことを確認
    assert mock_labeler.gen_model.generate_content.call_count == 2
見積もり: 30 分
優先度: ⭐⭐⭐

C2. 複数エラータイプの区別
Copydef test_call_gemini_with_retry_different_error_types(mock_labeler):
    """異なるエラータイプでのリトライ挙動"""
    error_types = [
        Exception("Network Error"),
        Exception("Rate Limit Exceeded"),
        Exception("Invalid Request")
    ]
    
    for error in error_types:
        mock_labeler.gen_model.generate_content.side_effect = [error] * 3
        
        with pytest.raises(Exception):
            mock_labeler._call_gemini_with_retry("test", max_retries=3)
        
        # 3 回すべて試行されたこと
        assert mock_labeler.gen_model.generate_content.call_count == 3
        mock_labeler.gen_model.generate_content.reset_mock()
見積もり: 30 分
優先度: ⭐⭐

Phase D: label_insight_spec の境界テスト
D1. center_pins が list でないケース
Copydef test_label_insight_spec_center_pins_not_list(mock_labeler, tmp_path):
    """center_pins が list ではない場合は ValueError"""
    invalid_spec = {
        "video_meta": {"video_id": "test"},
        "knowledge_core": {
            "center_pins": "invalid_string"  # list ではない
        }
    }
    
    input_file = tmp_path / "invalid.json"
    input_file.write_text(json.dumps(invalid_spec), encoding='utf-8')
    
    with pytest.raises(ValueError, match="center_pins must be a list"):
        mock_labeler.label_insight_spec(str(input_file))
見積もり: 30 分
優先度: ⭐⭐⭐

D2. importance_score 欠落時の挙動確認
Copydef test_label_insight_spec_missing_importance_score(mock_labeler, tmp_path):
    """importance_score が欠落している center_pin は 0 扱いになること"""
    spec = {
        "video_meta": {"video_id": "test"},
        "knowledge_core": {
            "center_pins": [
                {"element_id": "PIN_001", "type": "FACT", "content": "C1", "importance_score": 5.0},
                {"element_id": "PIN_002", "type": "FACT", "content": "C2"},  # importance_score 欠落
                {"element_id": "PIN_003", "type": "FACT", "content": "C3", "importance_score": 3.0},
            ]
        }
    }
    
    input_file = tmp_path / "test.json"
    input_file.write_text(json.dumps(spec), encoding='utf-8')
    
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({
            "labels": {
                "business_theme": ["A"],
                "funnel_stage": "教育",
                "difficulty": "beginner"
            }
        })
    )
    
    result = mock_labeler.label_insight_spec(str(input_file), top_n=2)
    
    # TOP 2 は PIN_001（5.0）と PIN_003（3.0）のはず
    # PIN_002 は TOP 2 外
    assert "labels" in result["knowledge_core"]["center_pins"][0]  # PIN_001
    assert "labels" not in result["knowledge_core"]["center_pins"][1]  # PIN_002
Copy
見積もり: 30 分
優先度: ⭐⭐

D3. top_n が center_pins 数以上のケース
Copydef test_label_insight_spec_top_n_exceeds_count(mock_labeler, tmp_path, sample_insight_spec):
    """top_n が全件数以上の場合、全件にラベルが付与される"""
    input_file = tmp_path / "test.json"
    input_file.write_text(json.dumps(sample_insight_spec), encoding='utf-8')
    
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({
            "labels": {
                "business_theme": ["A"],
                "funnel_stage": "教育",
                "difficulty": "beginner"
            }
        })
    )
    
    # top_n=100 で、center_pins は 5 件
    result = mock_labeler.label_insight_spec(str(input_file), top_n=100)
    
    # すべてにラベルが付与される
    for pin in result["knowledge_core"]["center_pins"]:
        assert "labels" in pin
見積もり: 30 分
優先度: ⭐⭐

Phase E: save_insight_spec の異常系テスト
E1. 書き込み権限エラーシミュレーション
Copydef test_save_insight_spec_write_permission_error(mock_labeler, sample_insight_spec, monkeypatch):
    """ファイル書き込み権限がない場合、False を返す"""
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    monkeypatch.setattr("builtins.open", mock_open)
    
    result = mock_labeler.save_insight_spec(sample_insight_spec, "/invalid/path/file.json")
    
    assert result is False
見積もり: 30 分
優先度: ⭐⭐

E2. ディレクトリ作成エラー
Copydef test_save_insight_spec_mkdir_error(mock_labeler, sample_insight_spec, monkeypatch):
    """output_dir の mkdir が失敗した場合、False を返す"""
    def mock_mkdir(*args, **kwargs):
        raise OSError("Cannot create directory")
    
    monkeypatch.setattr("pathlib.Path.mkdir", mock_mkdir)
    
    result = mock_labeler.save_insight_spec(sample_insight_spec, "/some/path/file.json")
    
    assert result is False
見積もり: 30 分
優先度: ⭐⭐

Phase F: API 呼び出し引数の検証
F1. generation_config の検証
Copydef test_label_center_pin_generation_config(mock_labeler, sample_center_pin):
    """generate_content に response_mime_type="application/json" が指定されること"""
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({
            "labels": {
                "business_theme": ["マーケティング"],
                "funnel_stage": "教育",
                "difficulty": "beginner"
            }
        })
    )
    
    mock_labeler.label_center_pin(sample_center_pin)
    
    # generate_content の呼び出しを確認
    call_args = mock_labeler.gen_model.generate_content.call_args
    generation_config = call_args.kwargs.get("generation_config")
    
    assert generation_config is not None
    assert generation_config.response_mime_type == "application/json"
見積もり: 30 分
優先度: ⭐⭐⭐

Phase G: エラーハンドリング体系化テスト
G1. エラー種別の分類
Copydef test_error_categorization(mock_labeler, sample_center_pin):
    """異なるエラー種別でのログと戻り値を確認"""
    
    # ケース 1: API エラー（JSONDecodeError）
    mock_labeler.gen_model.generate_content.return_value = Mock(text="invalid json")
    result1 = mock_labeler.label_center_pin(sample_center_pin)
    assert "labels" not in result1  # ラベル未付与
    
    # ケース 2: スキーマバリデーションエラー
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({"labels": {"business_theme": [], ...}})  # 空配列
    )
    result2 = mock_labeler.label_center_pin(sample_center_pin)
    assert "labels" not in result2
    
    # ケース 3: レスポンスに labels キー がない
    mock_labeler.gen_model.generate_content.return_value = Mock(
        text=json.dumps({"other_field": "value"})
    )
    result3 = mock_labeler.label_center_pin(sample_center_pin)
    assert "labels" not in result3
見積もり: 1 時間
優先度: ⭐⭐⭐

実装優先順序
Tier 1（必須・高優先度） - 2～3 時間
Phase A: _validate_labels 拡張（A1, A2, A3）
Phase B: label_center_pin 異常ケース（B1, B2）
Phase F: generation_config 検証（F1）
Tier 2（重要） - 2～3 時間
Phase C: リトライ詳細テスト（C1）
Phase D: insight_spec 境界テスト（D1, D3）
Phase G: エラーハンドリング体系化（G1）
Tier 3（推奨） - 2～3 時間
Phase B: visual_text パラメータ検証（B3）
Phase C: エラータイプ区別（C2）
Phase D: importance_score 欠落（D2）
Phase E: ファイルエラー処理（E1, E2）
現在のテストの継続性
既存の 15 テストはすべて保持し、上記を追加することで：

テスト数: 15 → 35 程度
カバレッジ: ↑ 大幅に向上
エラーハンドリング: 明示的かつ検証可能に
関連ドキュメント
tests/test_gemini_knowledge_labeler.py - 現テストコード
converter/gemini_knowledge_expander.py - 実装コード
PHASE3_IMPROVEMENT_ROADMAP.md - Phase 3 改善ロードマップ
メモ
Perplexity テストレビュー日: 2026-03-24
現状合格率: 15/15（100%）
推奨追加テスト: 20 個
推定実装時間: 6～9 時間（Tier 1+2 を優先）