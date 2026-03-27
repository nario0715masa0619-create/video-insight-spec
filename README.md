# video-insight-spec

YouTube 動画の洞察・競合分析システム。

## Quick Start

**Requirements:**
- Python 3.8+
- YouTube API Key

**Setup:**
1. Clone repository
2. Install dependencies
3. Set YOUTUBE_API_KEY in .env
4. Run competitor_analytics_generator.py

## Phase Progress

| Phase | Status | Date |
|-------|--------|------|
| Phase 1-3 | ✅ Complete | - |
| Phase 4 | ✅ Complete | 2026-03-26 |
| Phase 4.1 | ✅ Complete | 2026-03-26 |
| Phase 4.2 | ✅ Complete | 2026-03-26 |
| Phase 4.3 | 🔄 In Progress | - |

## Documentation

- [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)
- [PHASE4_2_DESIGN.md](docs/phases/PHASE4_2_DESIGN.md)
- [JSON_SPEC.md](docs/specs/JSON_SPEC.md)
- [VIEWS_DESIGN.md](docs/specs/VIEWS_DESIGN.md)

## Commands

python competitor_analytics_generator.py --lecture-ids "01,02,03,04,05"

## Directory Structure

video-insight-spec/
├── docs/
├── converter/
├── scripts/
├── reports/
└── competitor_analytics_generator.py

## Security

Keep YOUTUBE_API_KEY in .env
Do not commit to Git

---

**Last Updated:** 2026-03-26
