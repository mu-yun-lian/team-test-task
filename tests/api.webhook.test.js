const { expect } = require('chai');
const request = require('supertest');
const sinon = require('sinon');
const app = require('../server');
const notification = require('../model/notification');
const sign = require('./helpers/sign');

const SECRET = process.env.GITHUB_WEBHOOK_SECRET;

function postWebhook(event, payload, { badSignature = false } = {}) {
  const raw = JSON.stringify(payload);
  return request(app)
    .post('/api/webhook/github')
    .set('Content-Type', 'application/json')
    .set('X-GitHub-Event', event)
    .set(
      'X-Hub-Signature-256',
      badSignature ? 'sha256=deadbeefdeadbeefdeadbeefdeadbeef' : sign(SECRET, raw),
    )
    .send(raw);
}

describe('github webhook', () => {
  afterEach(() => sinon.restore());

  it('rejects requests with no signature', async () => {
    const res = await request(app)
      .post('/api/webhook/github')
      .set('Content-Type', 'application/json')
      .set('X-GitHub-Event', 'issue_comment')
      .send('{}');
    expect(res.status).to.equal(401);
  });

  it('rejects requests with a bad signature', async () => {
    const res = await postWebhook('issue_comment', {}, { badSignature: true });
    expect(res.status).to.equal(401);
  });

  it('persists notification for issue_comment and returns 202', async () => {
    sinon.stub(notification, 'create').resolves({ id: 'n-x' });
    const payload = {
      action: 'created',
      sender: { login: 'alice' },
      issue: { number: 7, user: { login: 'bob' } },
      comment: { body: 'looks good to me' },
    };
    const res = await postWebhook('issue_comment', payload);
    expect(res.status).to.equal(202);
    expect(res.body).to.deep.equal({ id: 'n-x' });
    sinon.assert.calledOnce(notification.create);
    const [arg] = notification.create.firstCall.args;
    expect(arg.source).to.equal('github');
    expect(arg.event).to.equal('issue_comment');
    expect(arg.recipient_id).to.equal('github:bob');
    expect(arg.summary).to.include('alice');
    expect(arg.summary).to.include('bob');
  });

  it('persists notification for pull_request_review_comment', async () => {
    sinon.stub(notification, 'create').resolves({ id: 'n-y' });
    const payload = {
      action: 'created',
      sender: { login: 'alice' },
      pull_request: { number: 11, user: { login: 'carol' } },
      comment: { body: 'fix this' },
    };
    const res = await postWebhook('pull_request_review_comment', payload);
    expect(res.status).to.equal(202);
    const [arg] = notification.create.firstCall.args;
    expect(arg.event).to.equal('pull_request_review_comment');
    expect(arg.recipient_id).to.equal('github:carol');
  });

  it('persists notification for pull_request_review', async () => {
    sinon.stub(notification, 'create').resolves({ id: 'n-z' });
    const payload = {
      action: 'submitted',
      sender: { login: 'alice' },
      pull_request: { number: 5, user: { login: 'dave' } },
    };
    const res = await postWebhook('pull_request_review', payload);
    expect(res.status).to.equal(202);
    const [arg] = notification.create.firstCall.args;
    expect(arg.event).to.equal('pull_request_review');
    expect(arg.recipient_id).to.equal('github:dave');
  });
});
