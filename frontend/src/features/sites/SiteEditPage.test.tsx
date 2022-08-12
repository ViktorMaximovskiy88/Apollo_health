import userEvent from '@testing-library/user-event';
import { render, screen } from '../../test/test-utils';
import { setupServer } from 'msw/node';
import { SiteEditPage } from './SiteEditPage';
import { handlers } from './mocks/siteEditPageHandlers';
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

  server.listen();
});
afterAll(() => {
  server.close();
});
afterEach(() => server.resetHandlers());

describe(`SiteEditPage`, () => {
  it(`displays initial data`, async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      siteId: 'site-id1',
    }));

    render(<SiteEditPage />);

    const elements = [];
    elements.push(await screen.findByDisplayValue('Test Site'));
    elements.push(await screen.findByText('https://www.test.com'));
    elements.push(await screen.findByText('Simple Document Scrape'));

    for (const element of elements) {
      expect(element).toBeInTheDocument();
    }
  });

  it(`hides, displays, and requires follow keywords`, async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      siteId: 'site-id1',
    }));

    const user = userEvent.setup();

    render(<SiteEditPage />);

    const followLinksCheck = screen.getByRole('checkbox', {
      name: /follow links/i,
    });
    let followLinkKeywords = screen.queryByText(/follow link keywords/i);
    expect(followLinkKeywords).not.toBeInTheDocument();

    await user.click(followLinksCheck);
    followLinkKeywords = screen.queryByText(/follow link keywords/i);
    expect(followLinkKeywords).toBeInTheDocument();

    const submit = await screen.findByRole('button', { name: /Submit/i });
    await user.click(submit);
    const validationWarning = await screen.findAllByText(
      'You must provide a Link or URL Keyword with Follow Links enabled'
    );
    expect(validationWarning.length === 2);
    for (const warning of validationWarning) {
      expect(warning).toBeInTheDocument();
    }
  });
});
