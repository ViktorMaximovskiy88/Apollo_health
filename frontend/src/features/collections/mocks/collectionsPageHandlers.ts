import { rest } from 'msw';
import { TaskStatus } from '../../../common';
import { faker } from '@faker-js/faker';
import site from '../../sites/mocks/site.fixture.json';

import { factory, primaryKey } from '@mswjs/data';

const db = factory({
  scrapeTask: {
    status: String,
    _id: primaryKey(String),
    site_id: String,
    queued_time: String,
    worker_id: String,
    start_time: String,
    end_time: String,
    last_active: String,
    documents_found: Number,
    new_documents_found: Number,
    error_message: String,
    links_found: Number,
  },
});

const errorMessage =
  'Traceback (most recent call last):\n  File "/Users/andrewhorn/workspace/Apollo/backend/scrapeworker/main.py", line 145, in worker_fn\n    raise Exception()\nException\n';

db.scrapeTask.create({
  _id: faker.database.mongodbObjectId(),
  site_id: faker.database.mongodbObjectId(),
  queued_time: '2022-06-20T14:17:19.185000',
  start_time: '2022-06-20T14:17:22.497000',
  end_time: '2022-06-20T14:17:22.594000',
  last_active: '2022-06-20T14:17:22.594000',
  status: TaskStatus.Failed,
  documents_found: 0,
  new_documents_found: 0,
  worker_id: faker.database.mongodbObjectId(),
  error_message: errorMessage,
  links_found: 0,
});

const timeOut = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

const processScrape = async (scrapeTaskId: string): Promise<void> => {
  await timeOut(1000);
  db.scrapeTask.update({
    where: {
      _id: { equals: scrapeTaskId },
      status: { equals: TaskStatus.Queued },
    },
    data: {
      status: TaskStatus.InProgress,
    },
  });
  await timeOut(5000);
  db.scrapeTask.update({
    where: {
      _id: { equals: scrapeTaskId },
      status: { equals: TaskStatus.InProgress },
    },
    data: {
      status: TaskStatus.Finished,
    },
  });
};

export const handlers = [
  rest.get('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json(site));
  }),
  rest.get('http://localhost/api/v1/site-scrape-tasks/', async (req, res, ctx) => {
    return res(ctx.json(db.scrapeTask.getAll().reverse()));
  }),
  rest.put('http://localhost/api/v1/site-scrape-tasks/', async (req, res, ctx) => {
    const newScrape = db.scrapeTask.create({
      _id: faker.database.mongodbObjectId(),
      site_id: faker.database.mongodbObjectId(),
      queued_time: '2022-06-20T14:17:19.185000',
      start_time: '2022-06-20T14:17:22.497000',
      end_time: '2022-06-20T14:17:22.594000',
      last_active: '2022-06-20T14:17:22.594000',
      status: TaskStatus.Queued,
      documents_found: 0,
      new_documents_found: 0,
      worker_id: faker.database.mongodbObjectId(),
      error_message: '',
      links_found: 0,
    });
    processScrape(newScrape._id);
    return res(ctx.json(newScrape));
  }),
];
