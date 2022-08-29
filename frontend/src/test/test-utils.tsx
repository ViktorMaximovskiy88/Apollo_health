import * as React from 'react';
import { render as rtlRender } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store as defaultStore, history } from '../app/store';
import { HistoryRouter as Router } from 'redux-first-history/rr6';
import { useParams, Params, useSearchParams, Location, useLocation } from 'react-router-dom';

export function mockUrl({
  location,
  params,
  searchParams,
}: {
  location?: Partial<Location>;
  params?: { [k: string]: string };
  searchParams?: { [k: string]: string };
}) {
  const mockedUseParams = useParams as jest.Mock<Params>;
  const mockedParams = params ?? {};
  mockedUseParams.mockImplementation(() => mockedParams);

  const mockedUseSearchParams = useSearchParams as jest.Mock<[URLSearchParams, () => void]>;
  const mockedSearchParams: [URLSearchParams, () => void] = [
    new URLSearchParams(searchParams ?? {}),
    () => {},
  ];
  mockedUseSearchParams.mockImplementation(() => mockedSearchParams);

  const mockedUseLocation = useLocation as jest.Mock<Location>;
  const mockedLocation = {
    ...location,
    pathname: '',
    key: '',
    state: '',
    search: '',
    hash: '',
  };
  mockedUseLocation.mockImplementation(() => mockedLocation);
}

function render(ui: React.ReactElement, { store = defaultStore, ...renderOptions } = {}) {
  function Wrapper({ children }: { children: React.ReactElement }) {
    return (
      <Provider store={store}>
        <Router history={history}>{children}</Router>
      </Provider>
    );
  }
  return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
}

export * from '@testing-library/react';

// override React Testing Library's render with our own
export { render };
