const { expect } = require('chai');
const request = require('supertest');
const app = require('../server');

describe('user api', () => {
  it('POST /api/user -> 200 (signin stub from boilerplate)', async () => {
    const res = await request(app).post('/api/user').send({});
    expect(res.status).to.equal(200);
  });
});
