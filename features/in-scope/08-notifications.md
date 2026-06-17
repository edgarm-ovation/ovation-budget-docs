# 08 — Notifications

**Sprint:** Weeks 5–6 | **Status:** Planned

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

- [01 — Authentication](./01-authentication.md) — notifications are per-user, auth required
- [07 — Approval Workflow](./07-approval-workflow.md) — approval events are the primary notification triggers
- [04 — File Import](./04-file-import.md) — import completion/failure also triggers notifications

---

## Related Features

- [02 — Project & Budget Navigation](./02-project-navigation.md) — bell icon lives in the app shell nav

## Related Docs

- [ovation-platform-docs/docs/](../../ovation-platform-docs/docs/)
- [ovation-platform-docs/schemas/](../../ovation-platform-docs/schemas/)
