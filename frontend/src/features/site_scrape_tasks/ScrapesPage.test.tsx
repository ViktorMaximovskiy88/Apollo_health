// import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '../../test/test-utils';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { ScrapesPage } from './ScrapesPage';
import json from './scrapes.fixture.json';

global.matchMedia =
  global.matchMedia ||
  function () {
    return {
      addListener: jest.fn(),
      removeListener: jest.fn(),
    };
  };

const server = setupServer(
  rest.get('http://localhost/api/v1/sites/site-id1', async (req, res, ctx) => {
    return res(ctx.json({ data: 'aslkjfd' }));
  }),
  rest.get(
    'http://localhost/api/v1/site-scrape-tasks/',
    async (req, res, ctx) => {
      return res(ctx.json(json));
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

beforeAll(() =>
  server.listen({
    onUnhandledRequest: 'error',
  })
);
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test(`logging in displays the user's username`, async () => {
  render(<ScrapesPage />);
  await waitFor(() =>
    expect(screen.getByText('Collections')).toBeInTheDocument()
  );
  expect(1).toBe(1);
});
