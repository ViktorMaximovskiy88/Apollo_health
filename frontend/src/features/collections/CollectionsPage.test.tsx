import userEvent from '@testing-library/user-event';
import { render, screen, act } from '../../test/test-utils';
import { setupServer } from 'msw/node';
import { CollectionsPage } from './CollectionsPage';
import { handlers } from './mocks/collectionsPageHandlers';
import { useParams, Params } from 'react-router-dom';

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
afterAll(() => {
  jest.useRealTimers();
  server.close();
});
afterEach(() => server.resetHandlers());

test(`CollectionsPage should work correctly`, async () => {
  const mockedUseParams = useParams as jest.Mock<Params>;
  mockedUseParams.mockImplementation(() => ({
    siteId: 'site-id1',
  }));

  // fixes `act` warning
  // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
  const dataGridDoneRendering = Promise.resolve();
  render(<CollectionsPage />);
  await act(async () => {
    await dataGridDoneRendering;
  });

  const runCollection = await screen.findByRole('button', {
    name: /run collection/i,
  });
  expect(runCollection).toBeInTheDocument();

  expect(await screen.findByText(/failed/i)).toBeInTheDocument();

  userEvent.click(runCollection);

  jest.advanceTimersByTime(2000);
  expect(await screen.findByText(/queued/i)).toBeInTheDocument();
  jest.advanceTimersByTime(3000);
  expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
  jest.advanceTimersByTime(10000);
  expect(await screen.findByText(/finished/i)).toBeInTheDocument();

  // it.skip(`should open ErrorLogModal when 'log' button clicked`, () => {});
});
