
## Phase 4.2: Competitor Analytics Views

Three views for competitive analysis.

### 1. Portfolio View Design

Purpose: Display all courses overview.

Data Source:
- lecture_id from spec
- title from video_meta
- dominant_funnel_stage from center_pins
- engagement_rate from snapshot_history
- view_count from latest snapshot

Aggregation: No aggregation, 1:1 mapping.

### 2. Growth View Design

Purpose: Identify growing courses.

Filter: snapshot_history.length >= 2

Calculation:
- view_count_delta = current - baseline
- growth_rate = delta / baseline
- engagement_delta = current - baseline

Sorting: By view_count_delta descending.

Period: From first to last snapshot.

### 3. Theme View Design

Purpose: Top course per business theme.

Grouping: business_theme from center_pins.

Selection: Highest view_count per theme.

Representative Pin:
- Highest engagement_score
- Formula: 0.6×purity + 0.2×type + 0.2×stage

Limit: Up to 3 per theme.

## Data Pipeline

1. Load specs via InsightSpecRepository
2. Extract metadata (title, funnel_stage, etc)
3. Calculate engagement metrics
4. Generate portfolio_view
5. Filter growth_view (≥2 snapshots)
6. Group and rank theme_view
7. Output JSON with ISO8601 timestamp
