# Accuracy Guidelines - Preventing Overestimation

## The Problem
When I claimed "75,000 words," we actually had 25,802 words. This 3x overestimation is exactly the "reward hacking" we must avoid.

## Mitigation Strategies

### 1. Always Verify Before Claiming
- Run `wc -w` before stating word counts
- Run `grep` before claiming sections exist
- Calculate math before stating numbers

### 2. Use Precise Language
❌ "We have ~75K words" (when unchecked)
✅ "Let me check... we have exactly 25,802 words"

❌ "This creates a $100B opportunity" (speculation)
✅ "With $7.5B in funding and 10:1 leverage possible, this could unlock $75B"

### 3. Source Everything
Every significant claim must have:
- Section number from bill
- Line number reference
- Exact quote or calculation shown

### 4. Automated Verification
Before publishing any research:
```bash
# Verify all claims
uv run verify_claims

# Count actual words
find research/ -name "*.md" -exec wc -w {} \; | awk '{sum += $1} END {print sum}'

# Check section references
grep -h "Section [0-9]" research/**/*.md | sort | uniq -c
```

### 5. Conservative Estimation Rules
- Round DOWN not up
- Use ranges with clear assumptions
- Separate facts from projections

### 6. Regular Audits
- Weekly claim verification
- Cross-check dollar amounts
- Validate section references

## Examples of Better Practices

### Word Counts
```bash
# Before claiming
WORD_COUNT=$(find research/ -name "*.md" -exec wc -w {} \; | awk '{sum += $1} END {print sum}')
echo "We have exactly $WORD_COUNT words of research"
```

### Dollar Amounts
```markdown
❌ "This is a $100B opportunity"
✅ "The bill allocates $7.5B (Section 20004, lines 2171-2235), which could unlock up to $75B in private capital through 90% loan guarantees"
```

### Market Sizing
```markdown
❌ "Millions will benefit"
✅ "43.2 million Americans have some college but no degree (source: National Student Clearinghouse). If 10% participate, that's 4.3M potential students."
```

## Verification Checklist

Before making any claim:
- [ ] Can I show the exact source?
- [ ] Have I verified the number/fact?
- [ ] Is my language precise, not approximate?
- [ ] Am I separating facts from analysis?
- [ ] Would this pass peer review?

## Trust Building

Users trust us when we:
1. Admit uncertainty ("I need to verify this")
2. Show our work (calculations, sources)
3. Correct mistakes immediately
4. Under-promise and over-deliver

The goal: Every claim we make should be defensible in court.