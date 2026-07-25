const express = require('express');
const api = express.Router();
const notificationController = require('../controller/notificationController');
const utility = require('../helper/utility');

api.get('/api/notification', utility.use(notificationController.list));
api.post('/api/notification/:id/read', utility.use(notificationController.markRead));

module.exports = api;
