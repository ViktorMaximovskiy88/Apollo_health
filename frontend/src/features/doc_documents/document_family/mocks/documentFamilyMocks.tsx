import { rest } from 'msw';
import { faker } from '@faker-js/faker';
import { factory, primaryKey } from '@mswjs/data';
import documentFamilyFixture from '../mocks/documentFamily.fixture.json';

export const db = factory({
  documentFamily: {
    _id: primaryKey(String),
    name: String,
    document_type: String,
    description: String,
    site_id: String,
    relevance: Array,
    payer: {
      payer_type: String,
      payer_ids: Array,
      channels: Array,
      benefits: Array,
      plan_types: Array,
      regions: Array,
    },
  },
});

db.documentFamily.create({
  _id: faker.database.mongodbObjectId(),
  site_id: faker.database.mongodbObjectId(),
  name: 'Test Family 1',
  document_type: 'Treatment Request Form',
  relevance: [],
  description: 'Sample Description about the Test Family 1',
  payer: {
    payer_type: 'formulary',
    payer_ids: ['61344', '61452', '60482'],
    channels: ['HEALTH EXCHANGE'],
    benefits: ['MEDICAL'],
    plan_types: ['ADAP', 'GOVERNMENT'],
    regions: ['AR', 'FL', 'ID'],
  },
});

export const handlers = [
  rest.get('http://localhost/api/v1/document-family/', async (req, res, ctx) => {
    return res(ctx.json(db.documentFamily.getAll()));
  }),
  rest.get('http://localhost/api/v1/document-family/documeny-family-id1', async (req, res, ctx) => {
    return res(ctx.json(documentFamilyFixture));
  }),

  rest.put('http://localhost/api/v1/document-family/', async (req, res, ctx) => {
    const newDocumentFamily = db.documentFamily.create({
      _id: faker.database.mongodbObjectId(),
      site_id: faker.database.mongodbObjectId(),
      name: 'Test Family 2',
      document_type: 'Treatment Request Form',
      relevance: [],
      description: 'Sample Description about the Test Family 2',
      payer: {
        payer_type: 'formulary',
        payer_ids: ['61344', '61452', '60482'],
        channels: ['HEALTH EXCHANGE'],
        benefits: ['MEDICAL'],
        plan_types: ['ADAP', 'GOVERNMENT'],
        regions: ['MD', 'NY', 'NE'],
      },
    });
    return res(ctx.json(newDocumentFamily));
  }),
];
