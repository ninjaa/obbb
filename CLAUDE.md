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
- **REFERENCES REQUIRED**: Every opportunity must cite specific bill sections, line numbers, and exact legislative text. No handwaving allowed.
- **ACTIONABLE DETAIL**: When we say "Workforce Pell Grants", explain what Section 83002 actually says about eligibility, amounts, and how to access.

## Current Status
- ✅ Extracted 379 defense funding opportunities from 5 sections
- ✅ Found specific dollar amounts ($1.4B drone expansion, $2B satellites, etc.)
- ✅ Analyzed Finance sections - found SALT deduction increase, QSBS expansion, OZ permanence
- ✅ Discovered $50B+ non-defense opportunities (agriculture, space, critical minerals)
- ⚠️  Need deeper analysis with specific bill references (line numbers, exact text)
- ❌ Need to build GraphRAG knowledge system for querying relationships
- ❌ Need interactive query interfaces

## Collaboration
Co-authored with Claude (Anthropic) for AI-assisted legal and economic analysis.