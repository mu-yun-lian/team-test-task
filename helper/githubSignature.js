const crypto = require('crypto');

// Timing-safe verification of a GitHub webhook signature.
// Inputs:
//   secret          - shared secret (env: GITHUB_WEBHOOK_SECRET)
//   signatureHeader - value of `X-Hub-Signature-256` (must start with `sha256=`)
//   rawBody         - the exact bytes GitHub sent, as a utf8 string
// Returns true iff the header is well-formed and matches the HMAC.
exports.verify = function({ secret, signatureHeader, rawBody }) {
  if (!secret || !signatureHeader || rawBody == null) return false;
  if (!signatureHeader.startsWith('sha256=')) return false;

  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');

  const a = Buffer.from(signatureHeader, 'utf8');
  const b = Buffer.from(expected, 'utf8');
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
};
