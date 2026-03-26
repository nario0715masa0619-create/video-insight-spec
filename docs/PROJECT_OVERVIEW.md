# Project Overview: video-insight-spec

## Phase Progress

| Phase | Status | Date |
|-------|--------|------|
| Phase 1-3 | ✅ Complete | - |
| Phase 4 | ✅ Complete | 2026-03-26 |
| Phase 4.1 | ✅ Complete | 2026-03-26 |
| Phase 4.2 | ✅ Complete | 2026-03-26 |
| Phase 4.3 | 🔄 In Progress | - |

## Phase 4.2: Competitor Analytics

### 1. Portfolio View

**Purpose:** All courses with metadata and engagement metrics.

**Data:** 5 lectures

| Lecture | Views | Engagement | Dominant Stage |
|---------|-------|------------|-----------------|
| 01 | 118,000 | 1.61% | 認知 |
| 02 | 47,739 | 1.68% | 比較検討 |
| 03 | 33,800 | 1.89% | クロージング |
| 04 | 26,026 | 1.75% | 興味・関心 |
| 05 | 21,064 | 1.60% | 教育 |

### 2. Growth View

**Purpose:** Courses with recent growth (snapshot_history ≥ 2 only).

**Period:** 2026-03-26 to 2026-04-02

**Data:** 1 lecture

| Lecture | View Delta | Growth Rate |
|---------|-----------|-------------|
| 01 | +2,166 | +1.87% |

**Note:** Lectures 02-05 excluded (single snapshot).

### 3. Theme View

**Purpose:** Top course per business theme.

**Data:** 8 themes, 14 lectures

| Theme | Top Lecture | Views | Engagement |
|-------|------------|-------|------------|
| マーケティング | 01 | 118,000 | 1.61% |
| Webマーケティング | 01 | 118,000 | 1.61% |
| 自社分析 | 02 | 47,739 | 1.68% |
| コピーライティング | 03 | 33,800 | 1.89% |
| Webデザイン | 03 | 33,800 | 1.89% |
| Web制作 | 03 | 33,800 | 1.89% |
| Webサイト制作 | 03 | 33,800 | 1.89% |
| データ分析 | 05 | 21,064 | 1.60% |

## Technical Details

### Engagement Score Formula

engagement_score = 0.6 × purity_norm + 0.2 × type_weight + 0.2 × stage_weight

**type_weight:**
- framework: 1.0
- strategy: 0.8
- tactic: 0.6
- concept: 0.4

**stage_weight:**
- クロージング: 1.0
- 継続・LTV: 0.9
- 比較検討: 0.8
- 教育: 0.7
- 興味・関心: 0.5
- 認知: 0.3

## Implementation Files

| File | Purpose |
|------|---------|
| `competitor_analytics_generator.py` | CLI entry point |
| `converter/portfolio_view_service.py` | Portfolio view generation |
| `converter/growth_view_service.py` | Growth view generation (≥2 snapshots) |
| `converter/theme_view_service.py` | Theme view generation |
| `converter/engagement_scorer.py` | Engagement score calculation |
| `converter/views_generator_service.py` | Views data handling |
| `converter/insight_spec_repository.py` | Spec loading |
| `docs/phases/PHASE4_2_DESIGN.md` | Design specifications |
| `reports/competitor_analytics/competitor_analytics_20260326.json` | Generated output |

## Command

python competitor_analytics_generator.py

## Validation Results

| Item | Result |
|------|--------|
| portfolio_view | ✅ 5 lectures |
| growth_view | ✅ 1 lecture |
| theme_view | ✅ 8 themes |
| JSON format | ✅ Valid |
| Timestamps | ✅ ISO8601 JST |

## Next: Phase 4.3

HTML/Text Formatter
- JSON → HTML report
- Theme ranking tables
- Growth highlights

**Status:** 🔄 In Progress

---

**Last Updated:** 2026-03-26
**Commit:** afa2bd2
