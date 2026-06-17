# 07 — Approval Workflow

**Sprint:** Weeks 5–6 | **Status:** Planned

---

## Summary

Formal sign-off process that moves a budget level from editable to locked. Estimators submit; Managers review and approve or reject. Approved budgets are cryptographically hashed and locked — no edits without a new submission cycle.

---

## What It Does

- State machine: `Draft → Submitted → Approved | Rejected → Locked`
- Estimator submits a budget level for manager review
- Manager receives notification and reviews the current state of the budget
- Manager approves (locks the budget) or rejects (returns to Draft with comments)
- Approved budget generates a SHA-256 hash of the snapshot stored in `BudgetApprovals`
- Locked budget is read-only — all edit controls disabled
- Rejection returns the budget to Draft with rejection notes visible to the Estimator

---

## State Machine

```
[Draft]
   │
   │  Estimator: Submit
   ▼
[Submitted]
   │               │
   │ Manager:      │ Manager:
   │ Approve       │ Reject
   ▼               ▼
[Approved]      [Draft]
   │            (with rejection notes)
   │
   ▼
[Locked]
(read-only, hashed snapshot)
```

---

## Key Workflows

1. Estimator finishes editing → clicks "Submit for Approval"
2. Budget status changes to `Submitted`; Manager receives in-app + email notification
3. Manager opens the budget, reviews line items and totals
4. **Approve:** status → `Approved` → `Locked`; SHA-256 hash written to `BudgetApprovals`
5. **Reject:** status → `Draft`; rejection comment stored; Estimator notified
6. Locked budget shows approval badge with approver name, date, and hash

---

## Technical Notes

- Tables involved: `BudgetApprovals`, `BudgetLevels` (`status` field), `AuditLog`
- Hash: SHA-256 of the serialized budget snapshot at approval time (tamper detection)
- API: `POST /api/budgetlevels/{id}/submit`, `POST /api/budgetlevels/{id}/approve`, `POST /api/budgetlevels/{id}/reject`
- Role gate: submit = Estimator, approve/reject = Manager or Admin

---

## Open Spec Gap

> The approval package spec (signature block, checklist, certificate layout, snapshot PDF download) is not fully defined. The demo only needs the state machine and hash — the PDF export can be deferred.

---

## Dependencies

- [01 — Authentication](./01-authentication.md) — role-based gate on submit vs. approve
- [06 — Markup Formula Engine](./06-markup-engine.md) — the markup-adjusted total is what gets approved
- [08 — Notifications](./08-notifications.md) — submit and approve events trigger notifications

---

## Related Features

- [09 — Excel Export](./09-excel-export.md) — locked budgets are commonly exported immediately after approval
- [03 — Budget Table Editing](./03-budget-editing.md) — editing is disabled once locked

## Related Docs

- [ovation-platform-docs/security/](../../ovation-platform-docs/security/)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
- [ovation-platform-mockup Open Ai/](../../ovation-platform-mockup%20Open%20Ai/)
