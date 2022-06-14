import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '../../test/test-utils';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { ScrapesPage } from './ScrapesPage';
import { SiteScrapeTask } from './types';
import scrapesFixture from './scrapes.fixture.json';

interface BackendSiteScrapeTask
  extends Omit<SiteScrapeTask, 'start_time' | 'end_time'> {
  _id: string;
  worker_id: string | null;
  start_time: string | null;
  end_time: string | null;
  error_message: null;
}

const scrapes: BackendSiteScrapeTask[] = scrapesFixture;

const timeOut = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

const processScrape = async (scrape: BackendSiteScrapeTask): Promise<void> => {
  await timeOut(1000);
  scrape.status = 'IN_PROGRESS';
  await timeOut(1000);
  scrape.links_found = 284;
  await timeOut(1000);
  scrape.documents_found = 123;
  await timeOut(1000);
  scrape.documents_found = 284;
  scrape.status = 'FINISHED';
};

const createNewScrape = (
  oldScrape: BackendSiteScrapeTask
): BackendSiteScrapeTask => {
  const newScrape = { ...oldScrape };
  newScrape._id = 'unique-id';
  newScrape.status = 'QUEUED';
  newScrape.documents_found = 0;
  newScrape.new_documents_found = 0;
  return newScrape;
};

const server = setupServer(
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
  )
);

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), // use actual for all non-hook parts
  useParams: () => ({
    siteId: 'site-id1',
  }),
  useRouteMatch: () => ({ url: '/' }),
}));

beforeAll(() => {
  // fixes `window.matchMedia` is not a function error
  global.matchMedia =
    global.matchMedia ||
    function () {
      return {
        addListener: jest.fn(),
        removeListener: jest.fn(),
      };
    };

  jest.useFakeTimers();

  return server.listen({
    onUnhandledRequest: 'error',
  });
});
afterEach(() => server.resetHandlers());
afterAll(() => {
  jest.useRealTimers();

  return server.close();
});

describe(`ScrapesPage`, () => {
  it(`should respond correctly to running a collection`, async () => {
    render(<ScrapesPage />);
    await waitFor(() =>
      expect(screen.getByText(/collections/i)).toBeInTheDocument()
    );
    userEvent.click(screen.getByText(/run collection/i));
    await waitFor(() =>
      expect(screen.getByText(/queued/i)).toBeInTheDocument()
    );
    jest.advanceTimersByTime(1000);
    await waitFor(() =>
      expect(screen.getByText(/in progress/i)).toBeInTheDocument()
    );
    jest.advanceTimersByTime(3000);
    await waitFor(() =>
      expect(screen.getByText(/finished/i)).toBeInTheDocument()
    );
  });
});
