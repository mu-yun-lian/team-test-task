const crypto = require('crypto');

// Returns the exact `X-Hub-Signature-256` header value GitHub would send
// for a given payload + secret. Use in webhook tests to forge valid requests.
module.exports.sign = function sign(secret, rawBody) {
  return 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');
};
