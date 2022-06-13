import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '../../test/test-utils';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { ScrapesPage } from './ScrapesPage';
import scrapesFixture from './scrapes.fixture.json';

let timer = 0;

const server = setupServer(
  rest.get('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json({ data: 'aslkjfd' }));
  }),
  rest.get(
    'http://localhost/api/v1/site-scrape-tasks/',
    async (req, res, ctx) => {
      const [latestScrape] = scrapesFixture;
      if (latestScrape.status === 'QUEUED' && timer === 1) {
        scrapesFixture[0].status = 'IN_PROGRESS';
      } else if (latestScrape.status === 'IN_PROGRESS') {
        scrapesFixture[0].documents_found = 284;
        scrapesFixture[0].new_documents_found = 284;
        scrapesFixture[0].status = 'FINISHED';
      } else {
        timer++;
      }
      return res(ctx.json(scrapesFixture));
    }
  ),
  rest.put(
    'http://localhost/api/v1/site-scrape-tasks/',
    async (req, res, ctx) => {
      scrapesFixture.unshift({
        _id: '62a3be35bbd0e0a8de45b854',
        site_id: '629133320c8101ebeae35ce0',
        queued_time: '2022-06-10T17:57:09.279000',
        start_time: '2022-06-10T17:57:09.366000',
        end_time: '2022-06-10T18:01:58.351000',
        status: 'QUEUED',
        documents_found: 0,
        new_documents_found: 0,
        worker_id: '80cafc50-8e8f-4412-85a5-8f2020fee860',
        error_message: null,
        links_found: 284,
      });
      timer = 0;
      return res(ctx.json(scrapesFixture));
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
  global.matchMedia =
    global.matchMedia ||
    function () {
      return {
        addListener: jest.fn(),
        removeListener: jest.fn(),
      };
    };
  return server.listen({
    onUnhandledRequest: 'error',
  });
});
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test(`logging in displays the user's username`, async () => {
  render(<ScrapesPage />);
  await waitFor(() =>
    expect(screen.getByText(/collections/i)).toBeInTheDocument()
  );
  userEvent.click(screen.getByText(/run collection/i));
  await waitFor(() => expect(screen.getByText(/queued/i)).toBeInTheDocument());
  await waitFor(() =>
    expect(screen.getByText(/in progress/i)).toBeInTheDocument()
  );
  await waitFor(() =>
    expect(screen.getByText(/finished/i)).toBeInTheDocument()
  );
});
