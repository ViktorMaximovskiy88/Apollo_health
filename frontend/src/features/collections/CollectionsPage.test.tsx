import userEvent from '@testing-library/user-event';
import { render, screen, act, setMockLocation } from '../../test/test-utils';
import { setupServer } from 'msw/node';
import { CollectionsPage } from './CollectionsPage';
import { handlers } from './mocks/collectionsPageHandlers';
import { useParams, Params, useLocation, Location } from "react-router-dom"

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

describe(`CollectionsPage`, () => {
  it(`should open error log modal when button clicked`, async () => {
    const mockedUseParams = useParams as jest.Mock<Params>;
    mockedUseParams.mockImplementation(() => ({
      siteId: 'site-id1',
    }));

    const mockedUseLocation = useLocation as jest.Mock<Location>;
    mockedUseLocation.mockImplementation(() => ({
      pathname:"site-id1",
      key:"site-id1",
      state:"",
      search:"",
      hash:""
    }))   

   // fixes `act` warning
    // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
    const dataGridDoneRendering = Promise.resolve();
    render(
        <CollectionsPage />
    );
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

  // it(`should create scrape task and update status over time`, async () => {
  //   const mockedUseParams = useParams as jest.Mock<Params>;
  //   mockedUseParams.mockImplementation(() => ({
  //     siteId: 'site-id1',
  //   }));
  //   setMockLocation();

  //   // fixes `act` warning
  //   // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
  //   const dataGridDoneRendering = Promise.resolve();
  //   render(
  //       <CollectionsPage />
  //   );
  //   await act(async () => {
  //     await dataGridDoneRendering;
  //   });

  //   const runCollectionButton = await screen.findByRole('button', {
  //     name: /run collection/i,
  //   });
  //   expect(runCollectionButton).toBeInTheDocument();

  //   expect(screen.getByText(/Jun 20, 2022, 2:17 PM/i)).toBeInTheDocument();
  //   expect(screen.getByText(/3 seconds/i)).toBeInTheDocument();
  //   expect(screen.getByText(/failed/i)).toBeInTheDocument();

  //   userEvent.click(runCollectionButton);

  //   jest.advanceTimersByTime(2000);
  //   expect(await screen.findByText(/queued/i)).toBeInTheDocument();
  //   jest.advanceTimersByTime(3000);
  //   expect(await screen.findByText(/in progress/i)).toBeInTheDocument();
  //   jest.advanceTimersByTime(10000);
  //   expect(await screen.findByText(/finished/i)).toBeInTheDocument();
  // });

  // it(`should open create document modal for manual collections when create document button clicked`, async () => {
  //   const mockedUseParams = useParams as jest.Mock<Params>;
  //   mockedUseParams.mockImplementation(() => ({
  //     siteId: 'site-id1',
  //   }));
  //   setMockLocation()
  //   // fixes `act` warning
  //   // https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise
  //   const dataGridDoneRendering = Promise.resolve();
  //   render(
  //       <CollectionsPage />
  //   );
  //   await act(async () => {
  //     await dataGridDoneRendering;
  //   });

  //   expect(screen.getByText(/Manual/i)).toBeInTheDocument();

  //   const createDocumentButton = await screen.findByRole('button', {
  //     name: /Create Document/i,
  //   });
  //   expect(createDocumentButton).toBeInTheDocument();

  //   userEvent.click(createDocumentButton);
  //   expect(await screen.getByText(/Create Document/i)).toBeInTheDocument();
  // });
});




