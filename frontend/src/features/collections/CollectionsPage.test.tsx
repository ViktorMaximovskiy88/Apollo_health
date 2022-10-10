import userEvent from '@testing-library/user-event';
import { render, screen, act, mockUrl } from '../../test/test-utils';
import { setupServer } from 'msw/node';
import { CollectionsPage } from './CollectionsPage';
import { db, handlers } from './mocks/collectionsPageHandlers';
import { DateTime } from 'luxon';

jest.mock('react-router-dom');

const server = setupServer(...handlers);

beforeAll(() => {
  // fixes `window.matchMedia` is not a function error
  // https://jestjs.io/docs/manual-mocks#mocking-methods-which-are-not-implemented-in-jsdom
  global.matchMedia =
    global.matchMedia ||
    function () {
      return {
        addListener: jest.fn(),
        removeListener: jest.fn(),
      };
    };

  jest.useFakeTimers();

  server.listen({ onUnhandledRequest: 'error' });
});
beforeEach(() => {
  mockUrl({ location: { pathname: '/sites/site-id1/scrapes' }, params: { siteId: 'site-id1' } });
});
afterAll(() => {
  jest.useRealTimers();
  server.close();
});
afterEach(() => server.resetHandlers());

describe(`CollectionsPage`, () => {
  it('should filter dates before current date by date offset', async () => {
    const dataGridDoneRendering = Promise.resolve();
    const dateOffset = db.appConfig.getAll()[0].data.defaultLastNDays;
    const scrapeTaskQueuedTime = db.scrapeTask.getAll()[0].queued_time;
    const filterByDate = DateTime.fromObject(
      { year: 2022, day: 30, month: 6, hour: 14, minute: 17, second: 19, millisecond: 185 },
      { zone: 'America/Los_Angeles' }
    ).minus({ days: dateOffset });

    const user = userEvent.setup();

    expect(filterByDate.toLocaleString()).toEqual('6/20/2022');
    render(<CollectionsPage />);
    await act(async () => {
      await dataGridDoneRendering;
    });

    const runCollectionButton = await screen.findByRole('button', {
      name: /run collection/i,
    });
    expect(runCollectionButton).toBeInTheDocument();

    await user.click(runCollectionButton);

    expect(screen.getByText(/Jun 20, 2022, 2:17 PM/i)).toBeInTheDocument();
    expect(screen.getByText(/3 seconds/i)).toBeInTheDocument();
    expect(screen.getByText(/failed/i)).toBeInTheDocument();

    jest.advanceTimersByTime(2000);
    expect(await screen.findByText(/queued/i)).toBeInTheDocument();
    jest.advanceTimersByTime(3000);
    expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
    jest.advanceTimersByTime(10000);
    expect(await screen.findByText(/finished/i)).toBeInTheDocument();
    expect(filterByDate.equals(DateTime.fromISO(scrapeTaskQueuedTime))).toBe(true);
  });
  it(`should open error log modal when button clicked`, async () => {
    // fixes `act` warning
    // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
    const dataGridDoneRendering = Promise.resolve();
    render(<CollectionsPage />);
    await act(async () => {
      await dataGridDoneRendering;
    });

    expect(await screen.findByText(/failed/i)).toBeInTheDocument();

    const errorLogButton = await screen.findByRole('button', {
      name: /error log/i,
    });
    userEvent.click(errorLogButton);

    expect(await screen.findByText(/error traceback/i)).toBeInTheDocument();

    expect(screen.getByRole('button', { name: /ok/i })).toBeInTheDocument();
  });

  it(`should create scrape task and update status over time`, async () => {
    // fixes `act` warning
    // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
    const dataGridDoneRendering = Promise.resolve();
    render(<CollectionsPage />);
    await act(async () => {
      await dataGridDoneRendering;
    });

    const runCollectionButton = await screen.findByRole('button', {
      name: /run collection/i,
    });
    expect(runCollectionButton).toBeInTheDocument();

    expect(screen.getByText(/Jun 20, 2022, 2:17 PM/i)).toBeInTheDocument();
    expect(screen.getByText(/3 seconds/i)).toBeInTheDocument();
    expect(screen.getByText(/failed/i)).toBeInTheDocument();

    userEvent.click(runCollectionButton);

    jest.advanceTimersByTime(2000);
    expect(await screen.findByText(/queued/i)).toBeInTheDocument();
    jest.advanceTimersByTime(3000);
    expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
    jest.advanceTimersByTime(10000);
    expect(await screen.findByText(/finished/i)).toBeInTheDocument();
  });
});
