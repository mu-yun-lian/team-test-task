# Deployment

The app is a Node 18 / Express server that also serves the built React client
in production. Everything you need to run it locally or in CI is in this
folder: a multi-stage `Dockerfile`, a `docker-compose.yml` that adds MySQL,
and a `.env.example` template.

## Quick start (local)

```bash
cp .env.example .env       # then edit the DB_* + GITHUB_WEBHOOK_SECRET values
docker compose up --build  # builds image, starts app + MySQL
# app -> http://localhost:8080
# mysql -> localhost:3306 (user: $DB_USER, db: $DB_NAME)
```

Run migrations once the DB is healthy:
```bash
docker compose exec app npx knex migrate:latest
```

## CI / CD

`.github/workflows/ci.yml` runs on every push to `main` or
`collaboration-release`, and on every PR. It:
- installs server + client deps,
- builds the client (`npm run build` inside `client/`),
- runs the mocha suite under `npm test`.

To deploy from CI to a target platform (Render / Railway / Fly / your VM):
either extend `.github/workflows/ci.yml` with a `deploy` job that runs
*after* the `test` job, or run the same `docker compose up` steps from a
self-hosted runner. The image produced by the `Dockerfile` is a drop-in
deployment unit.

## Environment variables

| Variable                  | Purpose                                       | Required |
| ------------------------- | --------------------------------------------- | -------- |
| `NODE_ENV`                | `production` enables static client serving   | yes      |
| `PORT`                    | listen port (default 8080)                    | no       |
| `DB_CLIENT`               | `mysql2` (only one supported by boilerplate)  | yes      |
| `DB_HOST`                 | MySQL host                                    | yes      |
| `DB_PORT`                 | MySQL port                                    | yes      |
| `DB_USER`                 | MySQL user                                    | yes      |
| `DB_PASSWORD`             | MySQL password                                | yes      |
| `DB_NAME`                 | MySQL database                                | yes      |
| `GITHUB_WEBHOOK_SECRET`   | shared secret with GitHub                     | yes (for the webhook) |
| `NOTIFY_WEBHOOK_URL`      | outbound fan-out target (Slack/Discord/...)   | no       |

Any value you add to `.env.example` should also appear here.

## GitHub webhook

1. In your repo &rarr; **Settings &rarr; Webhooks &rarr; Add webhook**
2. **Payload URL**: `https://<your-public-host>/api/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: same as `GITHUB_WEBHOOK_SECRET` in your env.
5. **Events**: enable `Issue comments`, `Pull request review comments`, and
   `Pull request reviews`.
6. Deliver a test ping; in the **Recent deliveries** panel the response
   should be `202 Accepted`.

You can replay a delivery locally with curl:
```bash
SECRET=your_secret
RAW='{"action":"created","sender":{"login":"me"},"issue":{"number":1,"user":{"login":"owner"},"id":1},"comment":{"body":"hi"}}'
SIG=$(printf '%s' "$RAW" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print "sha256=" $2}')
curl -i -X POST http://localhost:8080/api/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issue_comment" \
  -H "X-Hub-Signature-256: $SIG" \
  --data "$RAW"
```

## Container healthcheck

The image exposes a lightweight `/health` endpoint and the container has a
Docker-level healthcheck that polls it every 30 s. CI pipelines should
`curl -fsS http://app:8080/health` after deploy.

## Rollback

```bash
docker compose pull        # if you mirror the image to a registry
docker compose up -d       # bring down old, bring up new
```
To roll back a migration:
```bash
npm run rollback
```
