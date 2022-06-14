import React from 'react';
import ReactDOM from 'react-dom';
// import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import { store, history } from './app/store';
import { Provider } from 'react-redux';
import { HistoryRouter as Router } from 'redux-first-history/rr6';
import { Auth0Provider } from '@auth0/auth0-react';
import settings from './settings';

function onRedirectCallback(appState: any) {
  const returnTo = appState?.returnTo || window.location.pathname;
  history.push(returnTo);  
}

const app = (
  <React.StrictMode>
    <Auth0Provider
      {...settings.auth0}
      onRedirectCallback={onRedirectCallback}
    >
      <Provider store={store}>
        <Router history={history}>
          <App />
        </Router>
      </Provider>
    </Auth0Provider>
  </React.StrictMode>
);

const useCreateRoot = false;
const container = document.getElementById('root');
if (useCreateRoot) {
  // const root = createRoot(container);
  // root.render(app);
} else {
  ReactDOM.render(app, container);
}
