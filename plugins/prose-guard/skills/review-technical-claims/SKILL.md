---
name: "review-technical-claims"
description: "Audit a document for unverified technical claims, verify attributions against real sources, fix errors, and provide honest critical review."
user-invocable: true
argument-hint: "[path to document]"
---

# Review Technical Claims

Audit a document for unverified technical claims, verify attributions against real sources, fix errors, and provide honest critical review.

## Context

Read the target document. Identify all sections that make claims about external systems, competitors, or industry patterns.

## Task Workflow

### Phase 1: Claim Inventory

1. Read the entire target document
2. Extract every factual claim about external systems into a checklist:
   - "Used by" attributions
   - Technical architecture claims
   - Cost/pricing claims
   - Performance characteristics
   - Customer quotes (verify attribution, not content)
3. For each claim, note whether a source is cited. Flag unsourced claims.

### Phase 2: Source Verification (SIFT Method)

Apply the SIFT method — Stop, Investigate the source, Find better coverage, Trace claims to the original context.

#### Source Credibility Hierarchy:
- Official documentation, vendor whitepapers, changelogs
- Peer-reviewed research, conference proceedings
- Established engineering blogs (company tech blogs, well-known authors)
- Community wikis, tutorials, Stack Overflow answers
- Unattributed blog posts, social media, marketing copy

#### Process:
4. For claims WITH a source URL: verify it resolves and contains supporting content
5. Trace to primary source if secondary
6. For claims WITHOUT a source: find authoritative sources
7. Verify in parallel where possible

### Phase 3: Correction

8. Fix incorrect attributions
9. Replace broken source URLs with working alternatives
10. Upgrade weak sources to higher-tier ones
11. Add Sources subsections where missing
12. Remove or caveat unverifiable claims
13. When sources contradict, note the conflict and cite all sides

### Phase 4: Critical Review

14. After corrections, evaluate:
    - Fairness (same standard of evidence for own system vs. competitors?)
    - Scope honesty (apples-to-apples comparisons?)
    - Source quality
    - Staleness (claims older than 18 months?)
    - Bias signals
    - Internal consistency
15. Present findings by severity: Must fix, Should fix, Broken links, Consider

## Expected Outcome

- Every attribution has a cited, verified source
- Broken URLs are replaced
- Weak sources upgraded where possible
- Unverifiable claims flagged or removed
- Structured critical review provided
