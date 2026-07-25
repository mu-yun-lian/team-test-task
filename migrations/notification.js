// Notification inbox -- one row per "you should look at this" event.
// `recipient_id` is a user id for in_app source, or `github:<login>` for GH
// webhook source. `source` distinguishes in-app from GitHub; `event` carries
// the action name (e.g. comment.created, pull_request_review_comment).
exports.up = function(knex) {
  return knex.schema.createTable('notification', table => {
    table.specificType('id', 'char(36) primary key');
    table.specificType('recipient_id', 'char(36)').notNullable();
    table.string('source').notNullable();
    table.string('event').notNullable();
    table.specificType('comment_id', 'char(36)');
    table.text('summary').notNullable();
    table.boolean('read').notNullable().defaultTo(false);
    table.timestamp('date_created').notNullable().defaultTo(knex.fn.now());

    table.index(['recipient_id', 'read', 'date_created']);
    table.index(['source', 'event']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('notification');
};
