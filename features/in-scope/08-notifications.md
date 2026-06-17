# 08 — Notifications

**Verdict:** 🟡 Add-on — **in-app bell only** | **Sprint:** Week 7 | **Status:** Scoped down 2026-06-17

---

> **H0 scope note:** Only the **in-app notification bell + feed** is in scope. **Email via Azure Communication Services is deferred** (Phase 2) — the email column in the table below does not apply to H0. SignalR real-time push is optional; a simple fetch-on-load feed is acceptable for the demo. Import-completion notifications (04) don't apply since import is deferred.

---

## Summary

Keeps all stakeholders in the loop without requiring them to constantly check the platform. In-app bell for real-time alerts; email via Azure Communication Services for events that require action when the user is offline.

---

## What It Does

- In-app notification bell in the top nav — unread count badge
- Notification feed (dropdown) with timestamp, type, and link to the relevant record
- Email notifications for high-priority events (submit, approve, reject)
- Notifications stored in the `Notifications` table per user
- Mark as read individually or all-at-once

---

## Notification Events

| Event | In-App | Email | Recipient |
|-------|--------|-------|-----------|
| Budget submitted for approval | Yes | Yes | Manager |
| Budget approved | Yes | Yes | Estimator |
| Budget rejected | Yes | Yes | Estimator |
| File import completed | Yes | No | Estimator who uploaded |
| File import failed | Yes | Yes | Estimator who uploaded |

---

## Key Workflows

1. Trigger event fires (e.g., budget submitted)
2. Backend writes a `Notification` record per affected user
3. In-app: SignalR pushes the notification to connected clients in real time
4. Email: Azure Communication Services sends formatted email to the user's Ovation address
5. User clicks notification → deep-linked to the specific budget level or upload

---

## Technical Notes

- Real-time push: SignalR hub on the .NET backend
- Email: Azure Communication Services (ACS) — uses Ovation M365 email domain
- Tables involved: `Notifications`, `Users`
- API: `GET /api/notifications`, `PATCH /api/notifications/{id}/read`, `PATCH /api/notifications/read-all`
- SignalR connection managed client-side by React (reconnects on drop)

---

## Dependencies

- [01 — Authentication](../later/01-authentication.md) — *deferred from H0; notifications keyed to the switcher user*
- [07 — Approval Workflow](./07-approval-workflow.md) — approval events are the primary notification triggers
- [04 — File Import](../later/04-file-import.md) — *deferred from H0; no import events in the demo*

---

## Related Features

- [02 — Project & Budget Navigation](./02-project-navigation.md) — bell icon lives in the app shell nav

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
