---
title: "Claim Verification Report - Learning from 34.5% Accuracy"
opportunity_id: "RES-GEN-56"
sector: "General"
role: "General"
capital_level: "Variable"
region: "National"
summary: "The goal isn't 100% direct matches - it's 100% traceable, defensible claims...."
tags:
  - "Defense"
  - "Tax Benefits"
---
# Claim Verification Report - Learning from 34.5% Accuracy

## The Problem
Our verification script showed only 34.5% of dollar claims could be directly verified. This doesn't mean 65.5% are wrong - it reveals how we're aggregating and presenting information.

## Why Claims Don't Match

### 1. Aggregation Without Attribution
**We claimed**: "$7.5B for critical minerals"
**Reality**: This comes from THREE separate appropriations:
- $2,000,000,000 - National Defense Stockpile (Line 2171)
- $5,000,000,000 - Industrial Base Fund investments (Line 2232)  
- $500,000,000 - Loan guarantees (Line 2235)
**Total**: $7,500,000,000

**Lesson**: Always show the math and cite each component.

### 2. Shorthand vs Full Format
**We write**: "$7.5B", "$150M", "$250K"
**Bill writes**: "7,500,000,000", "150,000,000", "250,000"
**Solution**: Our verification tool now converts, but we should cite exact bill language.

### 3. Calculated Values
**We claimed**: "$11,100 tax savings"
**Reality**: This is calculated from SALT deduction increase × 37% tax rate
**Better approach**: "$30,000 additional SALT deduction (Section 70120) × 37% bracket = $11,100 savings"

### 4. Market Estimates vs Appropriations
**We claimed**: "$100B opportunity"
**Reality**: Projection based on leverage ratios, not in bill
**Better**: "$5B appropriation could unlock $100B with 20:1 leverage typical in loan guarantees"

## Updated Guidelines

### For Dollar Claims:
```markdown
❌ BAD: "This is a $7.5B opportunity"
✅ GOOD: "This program receives $7.5B through three appropriations:
- $2B for stockpile purchases (Section 20004, line 2171)
- $5B for investments (Section 20004, line 2232)
- $500M for guarantees (Section 20004, line 2235)"
```

### For Tax Calculations:
```markdown
❌ BAD: "$11,100 annual savings"
✅ GOOD: "SALT deduction increases by $30,000 (from $10,000 to $40,000, Section 70120).
For taxpayers in the 37% bracket, this saves $11,100 annually."
```

### For Market Projections:
```markdown
❌ BAD: "$100B market opportunity"
✅ GOOD: "With 43.2M Americans having some college but no degree (NCES data),
and average program cost of $5,000, the total addressable market is $216B.
Assuming 10% participation over 5 years yields $21.6B."
```

## Verification Results by Category

### ✅ Directly Verifiable (High Confidence)
- Defense appropriations with specific line items
- Tax provision changes with exact amounts
- Grant program funding levels

### ⚠️ Calculated/Aggregated (Medium Confidence)
- Total program funding from multiple sections
- Tax savings based on bracket calculations
- Market size estimates with stated assumptions

### ❌ Projections/Interpretations (Lower Confidence)
- ROI estimates
- Market opportunity sizing
- Competitive advantage claims

## Action Items

1. **Update all deep-dives** to show component math for aggregated claims
2. **Add citation format** showing exact bill text
3. **Separate facts from analysis** more clearly
4. **Create source mapping** for every major claim

## The Real Insight

Our 34.5% "accuracy" actually reveals we're doing complex analysis - aggregating multiple provisions, calculating impacts, and projecting opportunities. This is valuable BUT must be transparent about sources and calculations.

The goal isn't 100% direct matches - it's 100% traceable, defensible claims.