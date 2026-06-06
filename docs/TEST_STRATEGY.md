# テスト戦略（Phase 3.5 以降）

## ユニットテストの目的
「言語化ファースト」の後戻り防止。

## 重点テスト項目
1. **数字排除テスト**
   - すべての診断関数から「数値（90.0, 25 等）」が出力されていないことを強制

2. **翻訳テスト**
   - Config の theme_labels / funnel_labels が正しく機能

3. **エッジケーステスト**
   - 低スコア、欠損ラベル、空の patterns リスト等

## CI/CD への展開（Phase 4）
将来 GitHub Actions 導入時：
```yaml
- name: Run diagnostic tests
  run: pytest tests/test_diagnostic_summary.py -v
  # 失敗時は自動で PR をブロック
```
