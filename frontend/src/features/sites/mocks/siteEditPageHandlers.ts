import { rest } from 'msw';
import siteFixture from './site.fixture.json';

export const handlers = [
  rest.get('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json(siteFixture));
  }),
  rest.get('http://localhost/api/v1/sites/active-url', async (req, res, ctx) => {
    return res(ctx.json({ in_use: false }));
  }),
  rest.get('http://localhost/api/v1/proxies', async (req, res, ctx) => {
    return res(ctx.json([]));
  }),
  rest.post('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json({}));
  }),
  // to silence error
  rest.get('http://localhost/api/v1/sites/62bc78771c5e93fce7d5c0cf', async (req, res, ctx) => {
    return res(ctx.json(null));
  }),
  // to silence error
  rest.post('http://localhost/api/v1/sites/62bc78771c5e93fce7d5c0cf', async (req, res, ctx) => {
    return res(ctx.json(null));
  }),
  // to silence error
  rest.get('http://localhost/api/v1/users/', async (req, res, ctx) => {
    return res(ctx.json([]));
  }),
];
