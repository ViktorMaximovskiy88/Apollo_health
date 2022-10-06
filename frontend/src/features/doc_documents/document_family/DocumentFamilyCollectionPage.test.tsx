import { render, screen, act, mockUrl } from '../../../test/test-utils';
import { setupServer } from 'msw/node';
import { DocumentFamilyHomePage } from './DocumentFamilyHomePage';
import { db, handlers } from './mocks/documentFamilyMocks';

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
  mockUrl({
    location: { pathname: '/document-family/document-family-id1/scrapes' },
    params: { siteId: 'document-family-id1' },
  });
});
afterAll(() => {
  jest.useRealTimers();
  server.close();
});
afterEach(() => server.resetHandlers());

describe('DocumentFamily Page', () => {
  it('should render the table', async () => {
    const dataGridDoneRendering = Promise.resolve();

    render(<DocumentFamilyHomePage />);
    await act(async () => {
      await dataGridDoneRendering;
    });

    expect(screen.getByText(/Document Family/i)).toBeInTheDocument();
    expect(screen.getByText(/Family Name/i)).toBeInTheDocument();
  });

  it('should be able to populate the table with document families', async () => {
    const dataGridDoneRendering = Promise.resolve();
    db.documentFamily.getAll();

    render(<DocumentFamilyHomePage />);
    await act(async () => {
      await dataGridDoneRendering;
    });
    screen.debug();
  });
});
