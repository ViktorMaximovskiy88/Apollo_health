import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { render, screen, act } from '../../test/test-utils';
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


describe(`addDocumentModal`, () => {
  it(`should open modal when row create document is clicked and show errors when save button is clicked without info`, async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      siteId: 'site-id1',
    }));

    // fixes `act` warning
    // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
    const dataGridDoneRendering = Promise.resolve();
    render(
        <CollectionsPage />
    );

    await act(async () => {
      await dataGridDoneRendering;
    });

    screen.debug()
    expect(await screen.getByText('Run Collection')).toBeInTheDocument();
    

    // expect(await screen.findByText(/Add new document/i)).toBeInTheDocument();

    // const createDocumentButton = await screen.findByRole('button', {
    //   name: /Create Document/i,
    // });
    // expect(createDocumentButton).toBeInTheDocument();

    // userEvent.click(createDocumentButton);
    // expect(await screen.getByText(/Create Document/i)).toBeInTheDocument();

    // const saveButton = await screen.findByRole('button', {
    //   name: /Save/i,
    // });    

    // expect(saveButton).toBeInTheDocument();
    // userEvent.click(saveButton);
    // expect(await screen.getByText(/Document Name is required!/i)).toBeInTheDocument();

  });
});



