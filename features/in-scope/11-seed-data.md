# 11 — Seed Data

**Sprint:** Weeks 7–8 | **Status:** Planned

---

## Summary

Realistic demo-ready data for the two pilot projects — West Henderson Apartments (L3) and Robindale 215 (L2). Without good seed data, the demo is a blank screen. This is the final piece before the stakeholder dry run.

---

## What It Does

- Populates the database with two fully-fleshed projects for the demo
- Each project has realistic division structure, line items, quantities, and costs based on comparable Ovation projects
- West Henderson (L3): includes 2–3 bidder proposals per trade package with an awarded bid selected
- Robindale 215 (L2): includes line items with markups applied and an approval record
- Data is consistent — totals balance, markups calculate correctly, variance numbers are credible
- Loaded via seed scripts (run once against the Azure SQL demo database)

---

## Pilot Projects

| Project | Level | Key Data Points |
|---------|-------|-----------------|
| **West Henderson Apartments** | L3 | Full bid-based budget — multiple trade packages, 2–3 bidder proposals each, awarded bids selected, locked and approved |
| **Robindale 215** | L2 | Design development budget — full line items, escalation markup, submitted or approved state |

---

## Seed Data Scope

**West Henderson (L3):**
- 8–10 CSI divisions with line items
- 3 trade packages with 2–3 bidders each (Mechanical, Electrical, Concrete at minimum)
- 1 completed approval record with SHA-256 hash
- Realistic dollar amounts for a mid-density multifamily project in Las Vegas

**Robindale 215 (L2):**
- 6–8 CSI divisions
- Escalation markup set to 4%
- Budget in "Submitted" state (pending approval for demo flow)

---

## Key Workflows

1. Run seed migration script against Azure SQL
2. Verify project list shows both projects
3. Walk through each demo scenario: file import, bid selection, approval, export
4. Confirm all variance numbers make narrative sense for the demo story

---

## Technical Notes

- Seed format: EF Core data seeding (`modelBuilder.Entity<>().HasData()`) or a standalone SQL seed script
- Must run idempotently — re-running should not duplicate data
- Tables seeded: `Projects`, `BudgetLevels`, `Divisions`, `LineItems`, `TradePackages`, `Bidders`, `Proposals`, `ProposalLineItems`, `Markups`, `BudgetApprovals`, `Users`, `UserRoles`, `ProjectUsers`

---

## Open Spec Gap

> The West Henderson and Robindale datasets are noted as underdocumented in the current docs. Actual dollar amounts, trade package breakdowns, and bidder names need to be sourced from Ovation's existing project records or reasonable proxies before this seed can be built.

---

## Dependencies

All other in-scope features must be working before seed data can be validated end-to-end.

- [01–10](./01-authentication.md) — all features must function correctly against the seed data

## Related Docs

- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
- [ovation-platform-owner-demo-8-week claude/](../../ovation-platform-owner-demo-8-week%20claude/)
