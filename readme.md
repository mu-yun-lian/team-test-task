# Free Full-Stack SaaS Boilerplate

This is a free boilerplate based on the [Gravity SaaS Boilerplate for Node.js & React](https://usegravity.app?utm_source=github&utm_campaign=free_boilerplate)

Use it to build a full-stack web application using React, Tailwind, 
Node.js and Express.

> Branch `collaboration-release` adds release-engineering concerns on top of
> the upstream boilerplate: **Dockerized deployment**, **Mocha + Chai tests**,
> **in-app comment + notification module** with **GitHub PR/Issue webhook
> notifications** (HMAC-verified), and a **docs/** directory for
> contributing / API / deployment guides.

## Table of Contents

- [Quick start](#quick-start)
- [Documentation](#documentation)
- [Folder structure](#folder-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Comment notifications](#comment-notifications)
- [What's included](#whats-included)
- [What's not included](#whats-not-included)

This readme will cover what's included; what's not included; 
and how to install and use the boilerplate.

## Introduction

This boilerplate uses the model-view-controller (MVC) pattern 
and is split into two separate applications:

1. Server (API)
2. Client

The client makes HTTP requests to an API endpoint on
the server to send or get data. Each endpoint is handled
by a controller method wrapped in a utility helper to
catch errors within a controller. 

## What's Included

This boilerplate contains only the configuration for a 
SaaS application, not the functionality.

### Server

- Express API
- Error handling
- Environment config
- Knex query builder
- Database migrations
- Concurrently

### Client

- React 
- React Router
- Global view component
- Environment config
- 404 route and view
- Button, card, link and logo components

### What's Not Included

The following items are *not* included but are available in the 
[premium version of this boilerplate](https://usegravity.app?utm_source=github&utm_campaign=free_boilerplate):

- Authentication
- Subscription payments
- Organisations
- User permissions
- User management
- Social logins
- Email notifications
- Integration tests
- Scaffolding tools
- User feedback
- User onboarding
- Error and event logging
- UI views and component library
- User impersonation
- Content Security Policy
- CORS configuration
- Support

## Quick Start

### 1. Installation

Open up a terminal window and navigate into your project
folder and run the following command:

```npm run setup```

This will install the client and server packages for you,
and start both. You can also start them any time by running:

```npm run dev```

### 2. Database Configuration

1. Add your database credentials to the ```.env``` file
2. Run the database migration with:

```npm run migrate```

This will create the `user`, `comment`, and `notification` tables in your
database.

## Documentation

| Doc | Covers |
| --- | ------ |
| [API](docs/API.md) | Every HTTP endpoint |
| [CONTRIBUTING](docs/CONTRIBUTING.md) | Branches, commits, tests |
| [DEPLOYMENT](docs/DEPLOYMENT.md) | Docker, env, CI, webhook |

## Testing

```bash
npm install
npm test
```

Tests live under `tests/` (mocha + chai + supertest + sinon). They run the
express app in-process without a real port and stub model calls so no live
database is required. See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md#testing)
for the testing rules.

## Deployment

The repo ships a multi-stage `Dockerfile` and `docker-compose.yml` that
bring up the app + MySQL with one command:

```bash
cp .env.example .env       # then fill DB_* + GITHUB_WEBHOOK_SECRET
docker compose up --build
# app: http://localhost:8080
# mysql: localhost:3306
```

Container healthcheck polls `GET /health`. CI runs on push via
`.github/workflows/ci.yml`. Full guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Comment notifications

The `collaboration-release` branch adds two complementary notification paths
that both write to a unified `notification` inbox table:

1. **In-app comments** &mdash; `POST /api/comment` records a comment and
   enqueues an in-app notification for the recipient. The recipient polls
   `GET /api/notification` to read their inbox and `POST /api/notification/:id/read`
   to mark entries as seen.
2. **GitHub PR / Issue comments** &mdash; `POST /api/webhook/github` accepts
   `issue_comment`, `pull_request_review_comment`, and `pull_request_review`
   events, verifies `X-Hub-Signature-256` against `GITHUB_WEBHOOK_SECRET`,
   and persists each event as a notification row. Optionally forwards
   payloads to `NOTIFY_WEBHOOK_URL` (Slack/Discord/Feishu/your gateway).

Setup steps and a replay-able curl example are in
[docs/DEPLOYMENT.md#github-webhook](docs/DEPLOYMENT.md#github-webhook).

## Reference

### Folder Structure

#### Server Folder

The server code is located inside the root folder.

Controller files are located in ```/controller``` and
corresponding model files are located in the ```/model``` 
directory.

Database migrations are in ```/migrations``` and ```knexfile.js```
contains the database config, including the credentials you
added to the ```.env``` file.

There's a utility helper inside ```/helper``` for catching
errors.

#### Client Folder

The client application is located inside ```/client``` with 
the code located inside the ```/src``` folder.

```/app``` contains the main application and router imports.\
```/components``` contains the components with a lib file for universal imports.\
```/css``` contains the Tailwind input and output CSS files.\
```/routes``` contains the configuration for routes.\
```/views``` contains the client views.

The API URLs for development and production modes are defined in
```/src/settings.json```

### Nodemon

[Nodemon](https://nodemon.io/) automatically restarts your server
when making a code change. You can modify which files and directories
are ignored in package.json:

```javascript
"nodemonConfig": {
  "ignore": [
    "client/",
    "config/",
    "server.js",
    "knexfile.js"
  ]
}
```

### Express

[Express](https://expressjs.com/) is a framework for Node.js 
and powers the API. The main configuration is located in the 
```server.js``` file. This is where the server starts and also 
contains a global error handler.

```javascript
// error handling
app.use(function(err, req, res, next){

  console.error(err);
  const message = err.raw?.message || err.message || err.sqlMessage;
  return res.status(500).send({ message: message });

});
```

### API

The API endpoints are divided into separate concerns inside 
the ```/api``` directory. Each file defines a set of endpoints
containing a method, URL and respective controller.

**utility.use** is a higher order function (HOF) for
catching errors.

```javascript
api.post('/api/user', utility.use(userController.create));
```

### Knex

[Knex](https://knexjs.org/) is used to build the SQL queries, 
removing the need to deal with complex string manipulation
when writing complex queries.

When deploying to production, you'll need to configure
the SSL certificates or set ```ssl: { rejectUnauthorized: true }```
to ```false``` in knexfile.js.

Knex supports MySQL, Postgres and more.

▶️ [Watch how to configure the SSL certificates](https://www.youtube.com/watch?v=TkVwVHbzukw)

### Concurrently

[Concurrently](https://github.com/open-cli-tools/concurrently) 
enables both the client and server to run simultaneously with one command: 

```npm run dev```

### React

[React](https://reactjs.org/) will be served 
in development mode on your local machine. If you wish to 
deploy it, you can use the following command inside 
your ```/client``` folder:

```npm run build```

The express server is already configured to serve
the static files when in production mode.

### Tailwind

[Tailwind](https://tailwindcss.com/) is installed 
and configured with some sample components included. 
There is a watch script included to automatically recompile
the CSS upon any change.

```javascript
"watch:css": "postcss -w src/css/input.css -o src/css/output.css"
```

The Tailwind styling is decoupled from each JSX components and
stored into a separate file.

```
/card
  card.js
  card.tailwind.js
```  

### Axios

[Axios](https://axios-http.com/docs/intro) links the client
and server by making the HTTP requests. The package is installled
and the base URL configured in ```app.js```

### Next Steps

I have a premium boilerplate for sale, which has all the functionality
need to launch a SaaS product. I also have a course on how to 
build a SaaS product from scratch using this boilerplate.

[Get The Full Boilerplate](https://usegravity.app?utm_source=github&utm_campaign=free_boilerplate)\
[Get How To Build a SaaS Product From Scratch Course](https://usegravity.app/course)\
[Watch: How To Build a To-Do List Application](https://www.youtube.com/watch?v=HuVcp7r8HpY)
