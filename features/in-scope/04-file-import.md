# 04 — File Import (Excel / CSV)

**Sprint:** Weeks 3–4 | **Status:** Planned

---

## Summary

Estimators upload a subcontractor's Excel or CSV file directly into the platform. The system attempts to auto-map columns (description, quantity, unit cost, total) and falls back to a manual mapping UI when it can't. Eliminates copy-paste between spreadsheets.

---

## What It Does

- Drag-and-drop or file-picker upload (.xlsx, .xls, .csv)
- File stored in Azure Blob Storage; metadata recorded in `UploadedFiles`
- Parser extracts rows and header columns
- Auto-mapping: heuristic column name matching (e.g. "Desc" → description, "Qty" → quantity)
- Manual mapping UI: when auto-map confidence is low, user sees a column-picker per field
- Preview table shows mapped data before committing
- On confirm, line items are written to the target budget level
- Upload history visible per budget level

---

## Key Workflows

1. Estimator clicks "Import File" on a budget level
2. Selects or drags a file → upload to Blob Storage
3. System parses the file and attempts auto-mapping
4. **Path A — Auto-map succeeds:** Preview shown, user confirms → data written
5. **Path B — Auto-map fails / low confidence:** Column-picker UI shown → user maps manually → preview → confirm
6. Duplicate detection warns if line items already exist for the trade

---

## Auto-Mapping Heuristics

| Field | Matched Column Names (examples) |
|-------|--------------------------------|
| Description | `desc`, `description`, `item`, `scope` |
| Quantity | `qty`, `quantity`, `count`, `units` |
| Unit | `unit`, `uom`, `measure` |
| Unit Cost | `unit cost`, `rate`, `$/unit`, `price` |
| Total | `total`, `amount`, `extended`, `subtotal` |

---

## Technical Notes

- File parsing: ClosedXML (.xlsx) + CsvHelper (.csv) on the .NET backend
- Storage: Azure Blob Storage (raw file retained for audit)
- Tables involved: `UploadedFiles`, `LineItems`, `Divisions`
- Endpoint: `POST /api/upload` → `POST /api/import/preview` → `POST /api/import/confirm`
- Max file size: TBD (recommend 10 MB for demo)

---

## Open Spec Gap

> Upload endpoint and auto-mapping rules are marked as stubs in the docs. These need to be fully specified before implementation begins. See manager alignment notes.

---

## Dependencies

- [02 — Project & Budget Navigation](./02-project-navigation.md) — import is scoped to a specific budget level
- [03 — Budget Table Editing](./03-budget-editing.md) — import writes into the same table
- [01 — Authentication](./01-authentication.md) — Estimator role required

---

## Related Features

- [05 — Bid Leveling](./05-bid-leveling.md) — uploaded proposals feed the bid leveling view

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
