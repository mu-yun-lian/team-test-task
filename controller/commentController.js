const comment = require('../model/comment');
const notification = require('../model/notification');

// POST /api/comment
// Creates a comment and enqueues a notification for the recipient.
// Required body: { author_id, recipient_id, resource_type, body }
// Optional:       { resource_id }
exports.create = async function(req, res) {
  const { author_id, recipient_id, resource_type, resource_id, body } = req.body || {};
  if (!author_id || !recipient_id || !resource_type || !body) {
    return res.status(400).send({
      message: 'author_id, recipient_id, resource_type, body are required',
    });
  }

  const created = await comment.create({
    author_id, recipient_id, resource_type, resource_id, body,
  });

  await notification.create({
    recipient_id,
    source: 'in_app',
    event: 'comment.created',
    comment_id: created.id,
    summary: `New comment on ${resource_type}${resource_id ? ` ${resource_id}` : ''}`.trim(),
  });

  return res.status(201).send({ id: created.id });
};

// GET /api/comment?recipient_id=...
exports.list = async function(req, res) {
  const recipient_id = req.query.recipient_id;
  if (!recipient_id) {
    return res.status(400).send({ message: 'recipient_id query param required' });
  }
  const items = await comment.listForUser(recipient_id);
  return res.status(200).send({ items });
};
