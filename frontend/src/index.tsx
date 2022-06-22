import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import '@inovua/reactdatagrid-community/index.css'
import App from './App';
import { store, history } from './app/store';
import { Provider } from 'react-redux';
import { HistoryRouter as Router } from 'redux-first-history/rr6';
import { Auth0Provider } from '@auth0/auth0-react';
import settings from './settings';
import moment from 'moment';

window.moment = moment;

function onRedirectCallback(appState: any) {
  const returnTo = appState?.returnTo || window.location.pathname;
  history.push(returnTo);  
}

const app = (
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
);


const container = document.getElementById('root');
const root = createRoot(container as Element);
root.render(app);
