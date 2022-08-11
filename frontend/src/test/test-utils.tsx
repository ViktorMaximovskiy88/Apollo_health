import * as React from 'react';
import { render as rtlRender } from '@testing-library/react';
import { Provider } from 'react-redux';
import { useLocation } from "react-router-dom";
import { store as defaultStore, history } from '../app/store';
import { HistoryRouter as Router } from "redux-first-history/rr6";

function render(ui: React.ReactElement, { store = defaultStore, ...renderOptions } = {}) {
  function Wrapper({ children }: { children: React.ReactElement }) {
    return (
      <Provider store={store}>
        <Router history={history}>
            {children}
        </Router>
      </Provider>
    );
  }
  return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
}


const mockedUseLocation = useLocation as jest.Mock<Location>;
mockedUseLocation.mockImplementation(() => ({
  pathname:"test",
  key:"asd",
  state:"",
  search:"",
  hash:""
}))

export * from '@testing-library/react';

// override React Testing Library's render with our own
export { render, mockedUseLocation };
