const { expect } = require('chai');
const request = require('supertest');
const sinon = require('sinon');
const app = require('../server');
const comment = require('../model/comment');
const notification = require('../model/notification');

describe('comment api', () => {
  afterEach(() => sinon.restore());

  describe('POST /api/comment', () => {
    it('rejects missing fields with 400', async () => {
      const res = await request(app).post('/api/comment').send({ author_id: 'a' });
      expect(res.status).to.equal(400);
    });

    it('creates a comment + notification and returns 201', async () => {
      sinon.stub(comment, 'create').resolves({ id: 'fake-comment-id' });
      sinon.stub(notification, 'create').resolves({ id: 'fake-notification-id' });

      const res = await request(app)
        .post('/api/comment')
        .send({
          author_id: 'a', recipient_id: 'b',
          resource_type: 'post', resource_id: 'r',
          body: 'hello',
        });

      expect(res.status).to.equal(201);
      expect(res.body).to.deep.equal({ id: 'fake-comment-id' });
      sinon.assert.calledOnce(comment.create);
      sinon.assert.calledOnce(notification.create);
      const [notificationArg] = notification.create.firstCall.args;
      expect(notificationArg.source).to.equal('in_app');
      expect(notificationArg.event).to.equal('comment.created');
    });
  });

  describe('GET /api/comment', () => {
    it('rejects missing recipient_id with 400', async () => {
      const res = await request(app).get('/api/comment');
      expect(res.status).to.equal(400);
    });

    it('returns comment list for recipient', async () => {
      sinon.stub(comment, 'listForUser').resolves([{ id: 'c1' }, { id: 'c2' }]);
      const res = await request(app).get('/api/comment').query({ recipient_id: 'b' });
      expect(res.status).to.equal(200);
      expect(res.body.items).to.deep.equal([{ id: 'c1' }, { id: 'c2' }]);
      sinon.assert.calledWith(comment.listForUser, 'b');
    });
  });
});
