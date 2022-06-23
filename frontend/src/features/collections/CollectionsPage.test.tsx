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

  server.listen();
});
afterAll(() => {
  jest.useRealTimers();
  server.close();
});
afterEach(() => server.resetHandlers());

describe(`CollectionsPage`, () => {
  it(`should respond correctly to running a collection`, async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      siteId: 'site-id1',
    }));

    render(<CollectionsPage isVirtualized={false} />);
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    const runCollection = await screen.findByRole('button', {
      name: /run collection/i,
    });
    jest.advanceTimersByTime(1000);
    expect(runCollection).toBeInTheDocument();
    jest.advanceTimersByTime(1000);

    expect(await screen.findByText(/canceled/i)).toBeInTheDocument();
    expect(await screen.findByText(/failed/i)).toBeInTheDocument();

    userEvent.click(runCollection);

    expect(await screen.findByText(/queued/i)).toBeInTheDocument();
    jest.advanceTimersByTime(3000);
    expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
    jest.advanceTimersByTime(3000);
    expect(await screen.findByText(/finished/i)).toBeInTheDocument();
  });

  // TODO: add these tests when above test is fixed
  it.skip(`should cancel task when 'cancel' button clicked`, () => {});
  it.skip(`should open ErrorLogModal when 'log' button clicked`, () => {});
});
