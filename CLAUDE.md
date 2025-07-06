# CLAUDE.md - One Big Beautiful Bill Research Project

## Project Overview
Systematic analysis of HR119 (One Big Beautiful Bill) to identify profit opportunities across economic roles, sectors, and regions.

## Commands
- `uv run parse-bill` - Parse bill sections into markdown
- `uv run analyze-opportunities` - Generate profit vector analysis
- `uv run build-index` - Create cross-referenced master index
- `uv sync` - Install dependencies
- `npm run lint` - Lint markdown files
- `npm run build` - Build static site from research

## Research Structure
- `research/` - Main research database
- `scripts/` - Analysis automation tools
- `data/` - Extracted bill data and metrics

## Analysis Methodology
1. Multi-agent bill parsing by section
2. Profit vector extraction and scoring
3. Cross-reference mapping across roles/sectors/regions
4. Publication-ready research compilation

## Important Notes
- **NO REWARD HACKING**: Don't claim success without real results. The initial parser was broken (extracting TOC repeatedly). The fixed parser found 379 real funding opportunities.
- **ULTRATHINK AND ULTRAWORK**: Deep analysis, not surface-level claims. Each profit vector must be actionable with specific dollar amounts and implementation paths.

## Current Status
- ✅ Extracted 379 defense funding opportunities from 5 sections
- ✅ Found specific dollar amounts ($1.4B drone expansion, $2B satellites, etc.)
- ❌ Need to analyze Finance sections for $250K-400K tax opportunities
- ❌ Need to build GraphRAG knowledge system
- ❌ Need interactive query interfaces

## Collaboration
Co-authored with Claude (Anthropic) for AI-assisted legal and economic analysis.