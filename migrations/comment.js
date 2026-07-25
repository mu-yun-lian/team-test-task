// In-app comments table -- created for the "comment notification" feature.
// `author_id` and `recipient_id` reference user(id); comments can target any
// resource by (resource_type, resource_id) to avoid coupling the table to one
// domain object.
exports.up = function(knex) {
  return knex.schema.createTable('comment', table => {
    table.specificType('id', 'char(36) primary key');
    table.specificType('author_id', 'char(36)');
    table.specificType('recipient_id', 'char(36)');
    table.string('resource_type').notNullable();
    table.specificType('resource_id', 'char(36)');
    table.text('body').notNullable();
    table.timestamp('date_created').notNullable().defaultTo(knex.fn.now());

    table.index(['recipient_id', 'date_created']);
    table.index(['resource_type', 'resource_id']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('comment');
};
