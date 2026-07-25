const notification = require('../model/notification');

// GET /api/notification?recipient_id=...&unread=true
exports.list = async function(req, res) {
  const recipient_id = req.query.recipient_id;
  if (!recipient_id) {
    return res.status(400).send({ message: 'recipient_id query param required' });
  }
  const items = await notification.listForUser(recipient_id, {
    only_unread: req.query.unread === 'true',
  });
  return res.status(200).send({ items });
};

// POST /api/notification/:id/read  -- mark a single notification as read.
exports.markRead = async function(req, res) {
  await notification.markRead(req.params.id);
  return res.status(200).send({ ok: true });
};
