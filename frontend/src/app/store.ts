import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import { createReduxHistoryContext } from 'redux-first-history';
import { createBrowserHistory } from 'history';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { usersApi } from '../features/users/usersApi';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { siteScrapeTasksApi } from '../features/collections/siteScrapeTasksApi';
import { extractionTasksApi } from '../features/extractions/extractionsApi';
import { proxiesApi } from '../features/proxies/proxiesApi';
import { docDocumentsApi } from '../features/doc_documents/docDocumentApi';
import { rtkAuth } from '../common/auth-middleware';

import navSlice from './navSlice';
import sitesReducer from '../features/sites/sitesSlice';
import collectionsReducer from '../features/collections/collectionsSlice';
import docDocumentsReducer from '../features/doc_documents/docDocumentsSlice';
import documentsReducer from '../features/sites/documentsSlice';
import extractionsReducer from '../features/extractions/extractionsSlice';

const { createReduxHistory, routerMiddleware, routerReducer } = createReduxHistoryContext({
  history: createBrowserHistory(),
});

export const store = configureStore({
  reducer: {
    [usersApi.reducerPath]: usersApi.reducer,
    [sitesApi.reducerPath]: sitesApi.reducer,
    [siteScrapeTasksApi.reducerPath]: siteScrapeTasksApi.reducer,
    [documentsApi.reducerPath]: documentsApi.reducer,
    [extractionTasksApi.reducerPath]: extractionTasksApi.reducer,
    [proxiesApi.reducerPath]: proxiesApi.reducer,
    [docDocumentsApi.reducerPath]: docDocumentsApi.reducer,
    nav: navSlice.reducer,
    sites: sitesReducer,
    collections: collectionsReducer,
    docDocuments: docDocumentsReducer,
    documents: documentsReducer,
    extractions: extractionsReducer,
    router: routerReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      usersApi.middleware,
      sitesApi.middleware,
      siteScrapeTasksApi.middleware,
      documentsApi.middleware,
      extractionTasksApi.middleware,
      proxiesApi.middleware,
      docDocumentsApi.middleware,
      routerMiddleware,
      rtkAuth
    ),
});

export const history = createReduxHistory(store);

export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export type RootState = ReturnType<typeof store.getState>;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
