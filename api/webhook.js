const express = require('express');
const api = express.Router();
const webhookController = require('../controller/webhookController');
const utility = require('../helper/utility');

// The global json middleware in server.js retains req.rawBody (utf8), which
// this controller needs to verify the GitHub HMAC over the exact bytes.
api.post('/api/webhook/github', utility.use(webhookController.github));

module.exports = api;
