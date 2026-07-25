const { expect } = require('chai');
const request = require('supertest');
const app = require('../server');

describe('auth api', () => {
  it('POST /api/auth -> 200 (signin stub from boilerplate)', async () => {
    const res = await request(app).post('/api/auth').send({});
    expect(res.status).to.equal(200);
  });
});
