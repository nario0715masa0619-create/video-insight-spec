\# フェーズドキュメント



このディレクトリには、各フェーズの実装ドキュメント、ロードマップ、改善提案が含まれています。



\## ファイル一覧



| ファイル | フェーズ | 説明 |

|---------|---------|------|

| \*\*PHASE1\_5\_HOTFIXES.md\*\* | Phase 1.5 | ホットフィックス、バグ修正、改善案 |

| \*\*PHASE2\_2\_YOUTUBE\_API\_INTEGRATION.md\*\* | Phase 2.2 | YouTube API 統合の詳細 |

| \*\*PHASE2\_2\_1\_ENGAGEMENT\_METRICS.md\*\* | Phase 2.2.1 | エンゲージメントメトリクスの実装 |

| \*\*PHASE2\_2\_2\_OCR\_TEXT\_CLEANING.md\*\* | Phase 2.2.2 | OCR テキスト前処理 |

| \*\*PHASE2\_2\_3\_VIDEO\_ID\_ENRICHER.md\*\* | Phase 2.2.3 | video\_id エンリッチメント |

| \*\*PHASE3\_GEMINI\_KNOWLEDGE\_EXPANSION.md\*\* | Phase 3 | Gemini による知識体系拡張 |

| \*\*PHASE3\_IMPROVEMENT\_ROADMAP.md\*\* | Phase 3 | 改善ロードマップ |

| \*\*PHASE3\_PREPARATION\_OCCURRENCE\_IMPORTANCE.md\*\* | Phase 3 | 前準備と重要度分析 |

| \*\*PHASE3\_2\_3\_ROADMAP.md\*\* | Phase 3.2.3 | Phase 3.2.3 ロードマップ |

| \*\*PHASE4\_2\_DESIGN.md\*\* | Phase 4.2 | データ仕様設計（Portfolio/Growth/Theme View） |

| \*\*PHASE4\_3\_DESIGN.md\*\* | Phase 4.3 | HTML/Text フォーマッタ設計 |

| \*\*PHASE4\_3\_PLAN.md\*\* | Phase 4.3 | 実装計画・タスク分解 |

| \*\*PHASE5\_1\_DESIGN.md\*\* | Phase 5.1 | Executive Summary フォーマット仕様 |

| \*\*PHASE5\_2\_PLAN.md\*\* | Phase 5.2 | サブスクリプション仕様・料金体系 |

| \*\*PHASE5\_3\_LP\_OUTLINE.md\*\* | Phase 5.3 | LP 構成メモ・営業ポイント・CTA |

| \*\*PHASE5\_3\_NOTE\_DRAFT.md\*\* | Phase 5.3 | note 記事草案（ビジネスモデル解説） |

| \*\*PHASE5\_3\_FINANCE\_BRIEF.md\*\* | Phase 5.3 | 金融機関向け説明書（市場・予測・リスク） |

| \*\*PHASE6\_PLAN.md\*\* | Phase 6 | PoC・営業支援計画（予定） |



\## フェーズ進捗



Phase 1-3 → Phase 4 → Phase 5 → Phase 6 → Phase 7+

✅ 完了     ✅ 完了    ✅ 完了   🔄 進行中  📋 計画中

（基盤）     （データ）   （商品）   （PoC）    （拡張）



\## 各フェーズの詳細



\### フェーズ1～3：基盤構築（✅完了）



YouTube API統合、テキスト処理、知識体系拡張に関する実装ドキュメント。詳細は各ファイルを参照。



\### フェーズ4：データ生成・レポート自動化（✅完了）



目的：YouTube動画データを構造化し、自動レポート生成を実現。



成果物：

\- 3層JSON構造（video\_meta / knowledge\_core / views）

\- Portfolio View：全講座メタデータ + エンゲージメント指標

\- Growth View：成長中講座の直近変化

\- Theme View：ビジネステーマ別トップ講座

\- HTML/Text デュアル出力フォーマッタ



ドキュメント：PHASE4\_2\_DESIGN.md、PHASE4\_3\_DESIGN.md、PHASE4\_3\_PLAN.md



\### フェーズ5：商品化・営業資料（✅完了）



目的：サービス仕様を確定し、営業・資金調達資料を整備。



成果物：

\- Executive Summary（1ページ）フォーマット

\- サブスク仕様：月額10万円 + 初期30～50万円

\- ターゲット：EdTechスタートアップ（講座5～20本）

\- Year 3予測：ARR 4,500万円、30社顧客、42～53%利益率

\- LP構成メモ、note記事草案、金融機関向けピッチ資料



ドキュメント：PHASE5\_1\_DESIGN.md、PHASE5\_2\_PLAN.md、PHASE5\_3\_LP\_OUTLINE.md、PHASE5\_3\_NOTE\_DRAFT.md、PHASE5\_3\_FINANCE\_BRIEF.md



\### フェーズ6：PoC・営業支援（🔄進行中）



目的：市場検証と営業支援を加速。



成果物：

1\. PoC用ランディングページ：サンプルレポート、計算機、デモ予約

2\. サンプルレポート1セット：実例3件（HTML + テキスト）

3\. 営業テンプレ・自動化ツール：提案書、メール、見積自動化

4\. オンボーディング支援：ドキュメント、チェックリスト



ドキュメント：PHASE6\_PLAN.md（予定）



\### フェーズ7以降：プロダクト拡張（📋計画中）



フェーズ7目標：自動化・統合を通じたUX向上



計画機能：

\- Webダッシュボード：リアルタイム・日次更新

\- REST API：JSON公開 + 認証・レート制限

\- Slack統合：月次通知、成長テーマアラート



フェーズ8以降：AI推奨、PDF出力、国際展開、モバイルアプリ



\---



最終更新：2026-03-27

ブランチ：main（フェーズ5.3 マージ済み）

次のフェーズ：フェーズ6 - PoC・営業支援

