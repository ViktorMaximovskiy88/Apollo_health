import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import { createReduxHistoryContext } from 'redux-first-history';
import { createBrowserHistory } from 'history';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { usersApi } from '../features/users/usersApi';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { siteScrapeTasksApi } from '../features/collections/siteScrapeTasksApi';
import { extractionTasksApi } from '../features/extractions/extractionsApi';
import { workQueuesApi } from '../features/work_queue/workQueuesApi';
import { proxiesApi } from '../features/proxies/proxiesApi';
import { docDocumentsApi } from '../features/doc_documents/docDocumentApi';
import { translationsApi } from '../features/translations/translationApi';
import { payerBackboneApi } from '../features/payer-backbone/payerBackboneApi';
import { documentFamilyApi } from '../features/doc_documents/document_family/documentFamilyApi';
import { payerFamilyApi } from '../features/payer-family/payerFamilyApi';
import { devtoolsApi } from '../features/devtools/devtoolsApi';
import { statsApi } from '../features/stats/statsApi';
import { taskApi } from '../features/tasks/taskApi';
import { commentsApi } from '../features/comments/commentsApi';
import { rtkAuth } from '../common/auth-middleware';

import navSlice from './navSlice';
import documentFamilyReducer from '../features/doc_documents/document_family/documentFamilySlice';
import payerFamilyReducer from '../features/payer-family/payerFamilySlice';
import sitesReducer from '../features/sites/sitesSlice';
import userReducer from '../features/users/userSlice';
import collectionsReducer from '../features/collections/collectionsSlice';
import docDocumentsReducer from '../features/doc_documents/docDocumentsSlice';
import siteDocDocumentsReducer from '../features/doc_documents/siteDocDocumentsSlice';
import lineageDocDocumentsReducer from '../features/doc_documents/lineage/lineageDocDocumentsSlice';
import documentsReducer from '../features/collections/documentsSlice';
import extractionsReducer from '../features/extractions/extractionsSlice';
import translationsReducer from '../features/translations/translationSlice';
import payerBackboneReducer from '../features/payer-backbone/payerBackboneSlice';
import workQueueReducer from '../features/work_queue/workQueueSlice';
import devtools from '../features/devtools/devtools-slice';
import statsReducer from '../features/stats/stats-slice';
import taskSlice from '../features/tasks/taskSlice';

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
    [workQueuesApi.reducerPath]: workQueuesApi.reducer,
    [proxiesApi.reducerPath]: proxiesApi.reducer,
    [docDocumentsApi.reducerPath]: docDocumentsApi.reducer,
    [translationsApi.reducerPath]: translationsApi.reducer,
    [documentFamilyApi.reducerPath]: documentFamilyApi.reducer,
    [payerBackboneApi.reducerPath]: payerBackboneApi.reducer,
    [devtoolsApi.reducerPath]: devtoolsApi.reducer,
    [statsApi.reducerPath]: statsApi.reducer,
    [taskApi.reducerPath]: taskApi.reducer,
    [payerFamilyApi.reducerPath]: payerFamilyApi.reducer,
    [commentsApi.reducerPath]: commentsApi.reducer,
    nav: navSlice.reducer,
    sites: sitesReducer,
    users: userReducer,
    collections: collectionsReducer,
    docDocuments: docDocumentsReducer,
    siteDocDocuments: siteDocDocumentsReducer,
    lineageDocDocuments: lineageDocDocumentsReducer,
    documentFamilies: documentFamilyReducer,
    payerFamilies: payerFamilyReducer,
    documents: documentsReducer,
    extractions: extractionsReducer,
    translations: translationsReducer,
    workQueues: workQueueReducer,
    payerBackbone: payerBackboneReducer,
    router: routerReducer,
    devtools: devtools,
    stats: statsReducer,
    task: taskSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      usersApi.middleware,
      sitesApi.middleware,
      siteScrapeTasksApi.middleware,
      documentsApi.middleware,
      payerFamilyApi.middleware,
      extractionTasksApi.middleware,
      workQueuesApi.middleware,
      proxiesApi.middleware,
      docDocumentsApi.middleware,
      translationsApi.middleware,
      documentFamilyApi.middleware,
      payerBackboneApi.middleware,
      commentsApi.middleware,
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
