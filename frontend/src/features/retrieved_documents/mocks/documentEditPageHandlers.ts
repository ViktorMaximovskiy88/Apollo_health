import { resolve } from 'path';
import { readFileSync } from 'fs';
import { rest } from 'msw';
import docFixture from './docs.fixture.json';

export const handlers = [
  rest.get('http://localhost/api/v1/documents/doc-id1', async (req, res, ctx) => {
    return res(ctx.json(docFixture));
  }),
  rest.get('http://localhost:3000/api/v1/documents/test.pdf', async (req, res, ctx) => {
    const pdfBuffer = readFileSync(resolve(__dirname, './pdf_fixture.pdf'));
    return res(
      ctx.set('Content-Length', pdfBuffer.byteLength.toString()),
      ctx.set('Content-Type', 'application/pdf'),
      ctx.body(pdfBuffer)
    );
  }),
];
