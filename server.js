require('dotenv').config();
const express = require('express');
const api = require('./api');
const path = require('path');
const port = process.env.PORT || 8080;
const app = express();

// config express. `verify` retains the raw body so the GitHub webhook controller
// can verify the X-Hub-Signature-256 HMAC over the exact bytes GitHub sent.
app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf.toString('utf8'); },
}));
app.use(express.urlencoded({ extended: true, verify: (req, res, buf) => { req.rawBody = buf.toString('utf8'); } }));

// health endpoint (consumed by Docker healthcheck + CI smoke tests)
app.get('/health', (req, res) => res.status(200).send({ status: 'ok' }));

// api
app.use(api);

// serve static react files in production
if (process.env.NODE_ENV === 'production'){

  app.use(express.static(path.join(__dirname, 'client/build')));

  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname + '/client/build/index.html'))
  });
}

// handle errors from controllers
app.use(function(err, req, res, next){

  console.error(err);
  const message = err.raw?.message || err.message || err.sqlMessage;
  return res.status(500).send({ message: message });

});

// Exporting `app` lets supertest wrap the express instance directly
// without binding a port when this module is required from tests.
module.exports = app;

// Only auto-listen when run directly (`node server.js`); tests use supertest.
if (require.main === module) {
  app.listen(port, () => {
    console.log('Welcome to Gravity 🚀');
  });
}