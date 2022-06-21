import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '../../test/test-utils';
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

    render(<CollectionsPage />);
    await waitFor(() =>
      expect(screen.getByText(/collections/i)).toBeInTheDocument()
    );
    await waitFor(() => {
      expect(screen.getByText(/finished/i)).toBeInTheDocument();
    });

    // fails for some reason
    await waitFor(() => {
      expect(screen.getByText(/canceled/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/failed/i)).toBeInTheDocument();
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
