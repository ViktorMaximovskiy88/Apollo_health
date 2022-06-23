import userEvent from '@testing-library/user-event';
import { render, screen } from '../../test/test-utils';
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
    const runCollection = await screen.findByRole('button', {
      name: /run collection/i,
    });
    expect(runCollection).toBeInTheDocument();

    expect(await screen.findByText(/finished/i)).toBeInTheDocument();

    // TODO: fix this test
    //
    // Explanation of problem:
    //   test fails from here. `screen.debug(undefined, 100000)` shows that only the first task loads
    //     and, bafflingly, the data table renders "Loading" instead of the following tasks
    //
    // Clues toward a solution:
    //  - this test passed correctly before this component switched over to using a new data table that
    //      is not native to antd
    //  - `console.log(`screen height: ${window.screen.height}, screen width: ${window.screen.width}`);`
    //      shows that the window is 0 height and 0 width, so the new datatable may be truncating the
    //      rows
    //

    expect(await screen.findByText(/canceled/i)).toBeInTheDocument();
    expect(await screen.findByText(/failed/i)).toBeInTheDocument();

    userEvent.click(runCollection);

    expect(await screen.findByText(/queued/i)).toBeInTheDocument();
    jest.advanceTimersByTime(1000);
    expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
    jest.advanceTimersByTime(3000);
    expect(await screen.findByText(/finished/i)).toBeInTheDocument();
  });

  // TODO: add these tests when above test is fixed
  it.skip(`should cancel task when 'cancel' button clicked`, () => {});
  it.skip(`should open ErrorLogModal when 'log' button clicked`, () => {});
});
