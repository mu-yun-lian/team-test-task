# Contributing

## Branch strategy

- `main` &mdash; stable. Every push to `main` triggers CI and a deploy.
- `feat/<name>` &mdash; a single feature branch. Open a PR into `main`.
- `fix/<name>` &mdash; single bug fix.
- `release/<version>` &mdash; release prep; cherry-picks / hotfixes go here.
- `collaboration-release` &mdash; release-engineering branch (CI, deploy,
  comment notifications, docs). All release-time changes land here first,
  get smoke-tested, then get merged into `main`.

## Workflow

1. Branch off `main`:
   ```bash
   git checkout main && git pull
   git checkout -b feat/your-feature
   ```
2. Commit in small, focused units. Conventional Commit style preferred:
   - `feat(scope): summary`
   - `fix(scope): summary`
   - `docs: summary`
   - `test: summary`
   - `chore(deps): summary`
3. Run the test suite before pushing:
   ```bash
   npm install
   npm test
   ```
4. Push and open a PR:
   ```bash
   git push -u origin feat/your-feature
   gh pr create --base main --fill
   ```
5. PR CI must be green. At least one review from a different person than
   the author. Squash-merge by default.

## Code conventions

- Node: CommonJS, 2-space indent, single quotes, trailing commas, semicolons.
- Filenames: `camelCase.js`. SQL migrations: `<table>.js`.
- Controllers must return `res.status(<code>).send({...})`; never `res.send(...)`
  with an object + status code on the same line.
- Every new model call must be stubbed in at least one test (use `sinon.stub`).
- Any new env var must be documented in `.env.example` and `docs/DEPLOYMENT.md`.

## Testing

`npm test` runs mocha against `tests/**/*.test.js`. The suite:

- does **not** require a database &mdash; model modules are stubbed via sinon;
- boots express in-process via supertest (no real port);
- covers `/health`, every controller route, and the GitHub webhook HMAC path.

Add a new test file under `tests/` whenever you add a controller or modify
a route signature. Keep one `*.test.js` per controller.

## Adding a comment-notification source

To add Slack (or any) inbound notifications from a third party:
1. Add a controller under `controller/`.
2. Add the route under `api/` and mount it in `api/index.js`.
3. Re-use `model/notification.create(...)` so the inbox stays unified.
4. Cover it with `tests/<feature>.test.js`.
