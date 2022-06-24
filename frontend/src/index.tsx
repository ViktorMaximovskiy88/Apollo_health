import React from 'react';
import ReactDOM from 'react-dom';
// import { createRoot } from 'react-dom/client';
import './index.css';
import '@inovua/reactdatagrid-community/index.css'
import App from './App';
import { store, history } from './app/store';
import { Provider } from 'react-redux';
import { HistoryRouter as Router } from 'redux-first-history/rr6';
import moment from 'moment';

window.moment = moment;

const container = document.getElementById('root');
if (!container) throw Error('root element not found');

const app = (
    <Provider store={store}>
      <Router history={history}>
        <App />
      </Router>
    </Provider>
);

const useCreateRoot = false;
if (useCreateRoot) {
  // const root = createRoot(container);
  // root.render(app);
} else {
  ReactDOM.render(app, container);
}
