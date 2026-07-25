const { v4: uuidv4 } = require('uuid');
const knexFn = require('./knex');

exports.create = async function({ recipient_id, source, event, comment_id, summary }) {
  const id = uuidv4();
  await knexFn()('notification').insert({
    id, recipient_id, source, event, comment_id, summary,
  });
  return { id };
};

exports.listForUser = async function(
  recipient_id,
  { limit = 50, offset = 0, only_unread = false } = {},
) {
  const q = knexFn()('notification')
    .where({ recipient_id })
    .orderBy('date_created', 'desc');
  if (only_unread) q.andWhere({ read: false });
  return q.limit(limit).offset(offset);
};

exports.markRead = async function(id) {
  return knexFn()('notification').where({ id }).update({ read: true });
};
