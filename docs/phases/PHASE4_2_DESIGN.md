# Phase 4.2: Competitor Analytics Design

Competitor analytics system for YouTube lectures.

## Overview

Three views for competitive analysis:
1. portfolio_view - All lectures
2. growth_view - Growth metrics
3. theme_view - Theme rankings

## 1. Portfolio View

Display all courses with metadata.

**Fields:**
- role
- lecture_id
- title
- dominant_funnel_stage
- dominant_difficulty
- total_center_pins
- view_count
- engagement_rate

## 2. Growth View

Courses with recent growth (snapshot_history ≥ 2).

**Fields:**
- role
- lecture_id
- title
- view_count_delta
- view_count_growth_rate
- engagement_rate_delta

**Note:** snapshot_history < 2 are excluded.

## 3. Theme View

Top course per business theme.

**Fields:**
- role
- theme
- top_lecture_id
- top_lecture_title
- view_count
- engagement_rate
- representative_pin

## Implementation

Files:
- competitor_analytics_generator.py
- converter/portfolio_view_service.py
- converter/growth_view_service.py
- converter/theme_view_service.py

Output:
- reports/competitor_analytics/competitor_analytics_YYYYMMDD.json

## Engagement Score

engagement_score = 0.6 × purity + 0.2 × type + 0.2 × stage

type_weight:
- framework: 1.0
- strategy: 0.8
- tactic: 0.6
- concept: 0.4

stage_weight:
- クロージング: 1.0
- 教育: 0.7
- 認知: 0.3

## Validation Results (2026-03-26)

portfolio_view: 5 lectures ✅
growth_view: 1 lecture ✅
theme_view: 8 themes ✅
JSON format: Valid ✅
Timestamps: ISO8601 JST ✅

## Status

**Status:** ✅ Complete
**Date:** 2026-03-26
**Commit:** afa2bd2

---

**Last Updated:** 2026-03-26
