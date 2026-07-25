// Mocha runs this before any test file. We pin NODE_ENV=test and set sane
// defaults so tests don't accidentally call a live DB or service.
process.env.NODE_ENV = 'test';
process.env.GITHUB_WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET || 'test_secret_for_mocha';
process.env.NOTIFY_WEBHOOK_URL = process.env.NOTIFY_WEBHOOK_URL || '';
// Stub DB env so model/knex.js can be required without a real connection.
process.env.DB_CLIENT = process.env.DB_CLIENT || 'mysql2';
