const { expect } = require('chai');
const request = require('supertest');
const sinon = require('sinon');
const app = require('../server');
const notification = require('../model/notification');

describe('notification api', () => {
  afterEach(() => sinon.restore());

  it('GET /api/notification rejects missing recipient_id with 400', async () => {
    const res = await request(app).get('/api/notification');
    expect(res.status).to.equal(400);
  });

  it('GET /api/notification returns list for recipient', async () => {
    sinon.stub(notification, 'listForUser').resolves([{ id: 'n1' }]);
    const res = await request(app)
      .get('/api/notification')
      .query({ recipient_id: 'u1', unread: 'true' });
    expect(res.status).to.equal(200);
    expect(res.body.items).to.deep.equal([{ id: 'n1' }]);
    sinon.assert.calledWith(
      notification.listForUser,
      'u1',
      sinon.match({ only_unread: true }),
    );
  });

  it('POST /api/notification/:id/read marks notification as read', async () => {
    sinon.stub(notification, 'markRead').resolves(1);
    const res = await request(app).post('/api/notification/n42/read').send();
    expect(res.status).to.equal(200);
    expect(res.body).to.deep.equal({ ok: true });
    sinon.assert.calledWith(notification.markRead, 'n42');
  });
});
