import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { useParams, Params } from 'react-router-dom';

import { DocumentEditPage } from './DocumentEditPage';
import { handlers } from './mocks/documentEditPageHandlers';
import { render, screen, act } from '../../test/test-utils';
import { useAccessToken } from '../../common/hooks';

jest.mock('react-router-dom');
jest.mock('../../common/hooks');

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
beforeEach(() => {
  // Mocks intersection observer used by Viewer component
  const mockIntersectionObserver = jest.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.IntersectionObserver = mockIntersectionObserver;
});
afterAll(() => {
  jest.useRealTimers();
  server.close();
});
afterEach(() => server.resetHandlers());

describe('DocumentForm', () => {
  it('displays uneditable dates', async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      docId: 'doc-id1',
    }));
    const mockedUseAccessToken = useAccessToken as jest.Mock<string>;
    mockedUseAccessToken.mockReturnValue('123');

    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    render(
        <DocumentEditPage />
    );
    const effectiveDate = await screen.findByRole('textbox', {
      name: /Effective Date/i,
    });
    const lastUpdatedDate = screen.getByDisplayValue(/oct 2, 2000/i);
    const nextReviewDate = screen.getByDisplayValue(/nov 3, 2000/i);
    // check correct dates displayed
    expect(effectiveDate).toBeInTheDocument();
    expect(lastUpdatedDate).toBeInTheDocument();
    expect(nextReviewDate).toBeInTheDocument();

    // check that date picker doesn't open
    await user.click(effectiveDate);
    const datePicker = screen.queryByRole('cell', { name: /2000\-07\-31/i });
    expect(datePicker).not.toBeInTheDocument();
  });
});
