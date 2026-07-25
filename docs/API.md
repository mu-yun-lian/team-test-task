# API Reference

All endpoints are JSON over HTTP. The API surface added or hardened on the
`collaboration-release` branch is in **bold**.

| Method | Path                                  | Description                                    |
| ------ | ------------------------------------- | ---------------------------------------------- |
| GET    | `/health`                             | Liveness probe used by Docker / CI             |
| POST   | `/api/auth`                           | Sign-in (boilerplate stub)                     |
| POST   | `/api/user`                           | Create user (boilerplate stub)                 |
| **POST**   | **`/api/comment`**                    | **Create a comment + enqueue a notification**  |
| **GET**    | **`/api/comment?recipient_id=...`**   | **List comments received by a user**           |
| **GET**    | **`/api/notification?recipient_id=...&unread=true`** | **List a user's notification inbox** |
| **POST**   | **`/api/notification/:id/read`**      | **Mark a notification as read**                |
| **POST**   | **`/api/webhook/github`**             | **Receive GitHub PR/Issue comment webhooks**   |

---

## POST /api/comment

Create a comment and enqueue an in-app notification for the recipient.

**Request body**
```json
{
  "author_id":     "uuid",
  "recipient_id":  "uuid",
  "resource_type": "post",
  "resource_id":   "uuid (optional)",
  "body":          "string"
}
```

**Responses**
- `201 Created` &mdash; `{ "id": "uuid" }`
- `400 Bad Request` &mdash; `{ "message": "author_id, recipient_id, resource_type, body are required" }`

---

## GET /api/comment

List comments for a recipient, newest first.

**Query**
- `recipient_id` &mdash; required
- `limit`, `offset` &mdash; optional pagination

**Response**
```json
{ "items": [ { "id": "...", "author_id": "...", "body": "..." } ] }
```

---

## GET /api/notification

List a user's notification inbox.

**Query**
- `recipient_id` &mdash; required
- `unread=true` &mdash; only unread rows
- `limit`, `offset` &mdash; optional pagination

---

## POST /api/notification/:id/read

Mark one notification as read.

**Response** &mdash; `200 OK` `{ "ok": true }`

---

## POST /api/webhook/github

Receiver for GitHub `issue_comment`, `pull_request_review_comment`, and
`pull_request_review` webhooks. Verifies `X-Hub-Signature-256` against
`GITHUB_WEBHOOK_SECRET` and writes a row into the `notification` table.

**Response** &mdash; `202 Accepted` `{ "id": "uuid" }` on success,
`401 Unauthorized` for any signature failure.

Configuration: see [DEPLOYMENT.md](./DEPLOYMENT.md#github-webhook).

---

## Error format

The global error handler in `server.js` returns:
```json
{ "message": "<error message or sqlMessage>" }
```
with status `500` for unhandled errors thrown from any controller.
