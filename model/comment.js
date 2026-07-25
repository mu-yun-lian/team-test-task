const { v4: uuidv4 } = require('uuid');
const knexFn = require('./knex');

// All model helpers lazily acquire a knex instance so tests can stub at this
// boundary without ever opening a DB connection.

exports.create = async function({ author_id, recipient_id, resource_type, resource_id, body }) {
  const id = uuidv4();
  await knexFn()('comment').insert({ id, author_id, recipient_id, resource_type, resource_id, body });
  return { id };
};

exports.listForUser = async function(recipient_id, { limit = 50, offset = 0 } = {}) {
  return knexFn()('comment')
    .where({ recipient_id })
    .orderBy('date_created', 'desc')
    .limit(limit)
    .offset(offset);
};

exports.find = async function(id) {
  return knexFn()('comment').where({ id }).first();
};
