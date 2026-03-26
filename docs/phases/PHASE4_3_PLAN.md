# Phase 4.3: HTML/Text Formatter

Convert JSON reports to HTML and text formats.

## Objectives

1. Convert JSON to HTML report
2. Generate theme ranking tables
3. Highlight growth courses
4. Create text summary
5. Archive with timestamps

## Output Formats

### HTML Report

- Portfolio table
- Growth highlights
- Theme rankings
- Engagement metrics

### Text Summary

- Course overview
- Top performers
- Growth trends
- Theme analysis

## Implementation Plan

### New Files

- html_formatter.py - JSON to HTML
- text_formatter.py - JSON to text
- report_generator.py - Main entry point

### Modified Files

- competitor_analytics_generator.py - Call formatters

### Output Directory

reports/html/
reports/text/

## HTML Structure

<!DOCTYPE html>
<html>
<head>
  <title>Competitor Analytics</title>
</head>
<body>
  <h1>Report</h1>
  <section>Portfolio</section>
  <section>Growth</section>
  <section>Themes</section>
</body>
</html>

## Text Summary Format

COMPETITOR ANALYTICS REPORT
Generated: 2026-03-26

PORTFOLIO
- Lecture 01: 118,000 views
- Lecture 02: 47,739 views
- ...

GROWTH
- Lecture 01: +2,166 views (+1.87%)

THEMES
- Marketing: Lecture 01
- ...

## Timeline

- html_formatter.py: 30 min
- text_formatter.py: 30 min
- report_generator.py: 30 min
- Testing: 30 min

**Total:** 2 hours

## Status

**Status:** 🔄 In Progress
**Date:** 2026-03-26

---

**Last Updated:** 2026-03-26
