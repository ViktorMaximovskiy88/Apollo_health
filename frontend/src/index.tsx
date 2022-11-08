import React from 'react';
import { Worker } from '@react-pdf-viewer/core';
import { createRoot } from 'react-dom/client';
import './index.css';
import '@inovua/reactdatagrid-community/index.css';
import App from './App';
import { store, history } from './app/store';
import { Provider } from 'react-redux';
import { HistoryRouter as Router } from 'redux-first-history/rr6';
import { Auth0Provider } from '@auth0/auth0-react';
import settings from './settings';
import moment from 'moment';
import { notification } from 'antd';

window.moment = moment;

function onRedirectCallback(appState: any) {
  const returnTo = appState?.returnTo || window.location.pathname;
  history.push(returnTo);
}

const app = (
  <Worker workerUrl="/pdf.worker.min.js">
    <Auth0Provider {...settings.auth0} onRedirectCallback={onRedirectCallback}>
      <Provider store={store}>
        <Router history={history}>
          <App />
        </Router>
      </Provider>
    </Auth0Provider>
  </Worker>
);

const container = document.getElementById('root');
const root = createRoot(container as Element);
root.render(app);

notification.config({ duration: 2 });
