import React from 'react';
import ReactDOM from 'react-dom';
// import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import { store, history } from './app/store';
import { Provider } from 'react-redux';
import { HistoryRouter as Router } from 'redux-first-history/rr6';

const container = document.getElementById('root');
if (!container) throw Error('root element not found');

const app = (
  <React.StrictMode>
    <Provider store={store}>
      <Router history={history}>
        <App />
      </Router>
    </Provider>
  </React.StrictMode>
);

const useCreateRoot = false;
if (useCreateRoot) {
  const root = createRoot(container);
  root.render(app);
} else {
  ReactDOM.render(app, container);
}
