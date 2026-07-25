const { expect } = require('chai');
const request = require('supertest');
const app = require('../server');

describe('GET /health', () => {
  it('returns 200 with status=ok', async () => {
    const res = await request(app).get('/health');
    expect(res.status).to.equal(200);
    expect(res.body).to.deep.equal({ status: 'ok' });
  });
});
