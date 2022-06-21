import { rest } from 'msw';
import scrapesFixture from './scrapes.fixture.json';
import { SiteScrapeTask } from '../types';
import {Status} from "../../types"

interface BackendSiteScrapeTask
  extends Omit<SiteScrapeTask, 'start_time' | 'end_time' | "status"> {
  _id: string;
  worker_id: string | null;
  start_time: string | null;
  end_time: string | null;
  error_message: null;
  status: Status | string;
}

const scrapes: BackendSiteScrapeTask[] = scrapesFixture;

const createNewScrape = (
  oldScrape: BackendSiteScrapeTask
): BackendSiteScrapeTask => {
  const newScrape = { ...oldScrape };
  newScrape._id = 'unique-id';
  newScrape.status = Status.Queued;
  newScrape.documents_found = 0;
  newScrape.new_documents_found = 0;
  return newScrape;
};

const timeOut = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

const processScrape = async (scrape: BackendSiteScrapeTask): Promise<void> => {
  await timeOut(1000);
  scrape.status = Status.InProgress;
  await timeOut(1000);
  scrape.links_found = 284;
  await timeOut(1000);
  scrape.documents_found = 123;
  await timeOut(1000);
  scrape.documents_found = 284;
  scrape.status = Status.Finished;
};

export const handlers = [
  rest.get('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json({ data: 'test-data' }));
  }),
  rest.get(
    'http://localhost/api/v1/site-scrape-tasks/',
    async (req, res, ctx) => {
      return res(ctx.json(scrapes));
    }
  ),
  rest.put(
    'http://localhost/api/v1/site-scrape-tasks/',
    async (req, res, ctx) => {
      const newScrape = createNewScrape(scrapes[0]);
      processScrape(newScrape);
      scrapes.unshift(newScrape);
      return res(ctx.json(scrapes));
    }
  ),
];
