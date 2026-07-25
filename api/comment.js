const express = require('express');
const api = express.Router();
const commentController = require('../controller/commentController');
const utility = require('../helper/utility');

api.post('/api/comment', utility.use(commentController.create));
api.get('/api/comment', utility.use(commentController.list));

module.exports = api;
