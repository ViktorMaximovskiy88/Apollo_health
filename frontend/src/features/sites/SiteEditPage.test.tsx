import userEvent from '@testing-library/user-event';
import { mockUrl, render, screen } from '../../test/test-utils';
import { setupServer } from 'msw/node';
import { SiteEditPage } from './SiteEditPage';
import { handlers } from './mocks/siteEditPageHandlers';
import { useParams, Params, useLocation, Location, useSearchParams } from 'react-router-dom';

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
beforeEach(() => {
  mockUrl({ params: { siteId: 'site-id1' } });
});
afterAll(() => {
  server.close();
});
afterEach(() => server.resetHandlers());

describe(`SiteEditPage`, () => {
  it(`displays initial data`, async () => {
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

  it(`hides, displays HTML Config`, async () => {
    const user = userEvent.setup();

    render(<SiteEditPage />);

    const scrapeMethodSelect = screen.getByText('Simple Document Scrape');
    expect(scrapeMethodSelect).toBeInTheDocument();
    const targetSelectorHidden = screen.queryByRole('heading', { name: /html target selector/i });
    expect(targetSelectorHidden).not.toBeInTheDocument();
    const exclusionSelectorHidden = screen.queryByRole('heading', {
      name: /html exclusion selector/i,
    });
    expect(exclusionSelectorHidden).not.toBeInTheDocument();

    await user.click(scrapeMethodSelect);
    const htmlOption = screen.getByTitle(/html scrape/i);
    await user.click(htmlOption);

    const targetSelector = screen.queryByRole('heading', { name: /html target selector/i });
    expect(targetSelector).toBeInTheDocument();
    const exclusionSelector = screen.queryByRole('heading', { name: /html exclusion selector/i });
    expect(exclusionSelector).toBeInTheDocument();
  });

  it(`hides, displays, validates Searchable Config`, async () => {
    const user = userEvent.setup();

    render(<SiteEditPage />);

    const searchableTypeHidden = screen.queryByText(/searchable type/i);
    const inputSelectorHidden = screen.queryByText(/searchable input/i);
    const submitSelectorHidden = screen.queryByText(/searchable submit button/i);
    expect(inputSelectorHidden).not.toBeInTheDocument();
    expect(submitSelectorHidden).not.toBeInTheDocument();
    expect(searchableTypeHidden).not.toBeInTheDocument();

    const searchableSwitch = screen.getByLabelText('Searchable');
    await user.click(searchableSwitch);

    const inputSelector = screen.getByText(/searchable input/i);
    const submitSelector = screen.getByText(/searchable submit button/i);
    const searchableType = screen.getByText(/searchable type/i);
    expect(inputSelector).toBeInTheDocument();
    expect(submitSelector).toBeInTheDocument();
    expect(searchableType).toBeInTheDocument();

    const submit = await screen.findByRole('button', { name: /Submit/i });
    await user.click(submit);
    const validationWarning = await screen.findAllByText('Required');
    expect(validationWarning.length === 5); // Required searchable fields
    for (const warning of validationWarning) {
      expect(warning).toBeInTheDocument();
    }
  });
});
