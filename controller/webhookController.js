const verify = require('../helper/githubSignature');
const notification = require('../model/notification');

// GitHub PR / Issue comment notification receiver.
//
// Subscribe your repo to send webhooks at:
//   <PUBLIC_BASE_URL>/api/webhook/github
// with content-type application/json, secret = GITHUB_WEBHOOK_SECRET,
// and these events enabled:
//   - issue_comment
//   - pull_request_review_comment
//   - pull_request_review
// Each accepted event writes a row into the `notification` table; if
// NOTIFY_WEBHOOK_URL is set we additionally POST a slim payload there for
// fan-out (Slack / Discord / Feishu / your own gateway).
exports.github = async function(req, res) {
  const secret = process.env.GITHUB_WEBHOOK_SECRET;
  const sig = req.get('X-Hub-Signature-256');
  const event = req.get('X-GitHub-Event');
  const raw = req.rawBody || (req.body ? JSON.stringify(req.body) : '');

  if (!verify.verify({ secret, signatureHeader: sig, rawBody: raw })) {
    return res.status(401).send({ message: 'invalid signature' });
  }

  const payload = req.body || {};
  let summary;
  let recipientHint;

  switch (event) {
    case 'issue_comment':
      summary = `${payload.sender?.login || 'someone'} commented on ` +
        `#${payload.issue?.number || ''}: ${(payload.comment?.body || '').slice(0, 80)}`;
      recipientHint = payload.issue?.user?.login;
      break;
    case 'pull_request_review_comment':
      summary = `${payload.sender?.login || 'someone'} reviewed at ` +
        `#${payload.pull_request?.number || ''}: ${(payload.comment?.body || '').slice(0, 80)}`;
      recipientHint = payload.pull_request?.user?.login;
      break;
    case 'pull_request_review':
      summary = `${payload.sender?.login || 'someone'} ${payload.action || 'reviewed'} ` +
        `PR #${payload.pull_request?.number || ''}`;
      recipientHint = payload.pull_request?.user?.login;
      break;
    default:
      summary = `GitHub event ${event} (${payload.action || 'unknown'})`;
      recipientHint = (payload.repository && payload.repository.full_name) || 'github';
  }

  const created = await notification.create({
    recipient_id: `github:${recipientHint}`,
    source: 'github',
    event: event || 'unknown',
    summary,
  });

  // Optional outbound fan-out. Failure here MUST NOT fail the webhook.
  const target = process.env.NOTIFY_WEBHOOK_URL;
  if (target) {
    try {
      await fetch(target, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event, summary, notification_id: created.id }),
      });
    } catch (err) {
      console.warn('notify fan-out failed:', err && err.message);
    }
  }

  return res.status(202).send({ id: created.id });
};
