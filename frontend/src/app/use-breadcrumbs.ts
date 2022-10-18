import { useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setBreadcrumbs } from './navSlice';

import { usersApi } from '../features/users/usersApi';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { docDocumentsApi } from '../features/doc_documents/docDocumentApi';
import { workQueuesApi } from '../features/work_queue/workQueuesApi';
import { translationsApi } from '../features/translations/translationApi';
import { payerBackboneApi } from '../features/payer-backbone/payerBackboneApi';
import { documentFamilyApi } from '../features/doc_documents/document_family/documentFamilyApi';

const routes = [
  '/documents',
  '/documents/:docDocId',
  '/document-family',
  '/document-family/:docFamilyId',
  '/sites',
  '/sites/:siteId',
  '/sites/:siteId/doc-documents',
  '/sites/:siteId/documents',
  '/sites/:siteId/documents/:docId',
  '/sites/:siteId/documents/:docId/edit',
  '/sites/:siteId/edit',
  '/sites/:siteId/extraction',
  '/sites/:siteId/extraction/document/:docDocId',
  '/sites/:siteId/extraction/document/:docDocId/:extractionId/results',
  '/sites/:siteId/extraction/document/:docDocId/edit',
  '/sites/:siteId/scrapes',
  '/sites/:siteId/view',
  '/sites/:siteId/lineage',
  '/sites/new',
  '/translations',
  '/translations/:translationId',
  '/translations/new',
  '/users',
  '/users/:userId/edit',
  '/users/new',
  '/work-queues',
  '/work-queues/:workQueueId',
  '/work-queues/:workQueueId/:docDocumentId/process',
  '/work-queues/:workQueueId/:docDocumentId/read-only',
  '/work-queues/new',
  '/payer-backbone',
  '/payer-backbone/:payerType',
  '/payer-backbone/:payerType/new',
  '/payer-backbone/:payerType/:payerId',
];

export const useBreadcrumbs = async () => {
  const dispatch = useDispatch();
  const location = useLocation();

  const matched: any = useMemo(() => {
    // async resolvers that get cached and more or less act like prefetch
    const asyncResolvers = {
      ':siteId': async (siteId: string, url: string) => {
        const result: any = await dispatch(sitesApi.endpoints.getSite.initiate(siteId));
        return { url, label: result.data.name };
      },
      ':docId': async (docId: string, url: string) => {
        const result: any = await dispatch(documentsApi.endpoints.getDocument.initiate(docId));
        return { url, label: result.data.name } as any;
      },
      ':docDocId': async (docDocId: string, url: string) => {
        const result: any = await dispatch(
          docDocumentsApi.endpoints.getDocDocument.initiate(docDocId)
        );
        return { url, label: result.data.name } as any;
      },
      ':docFamilyId': async (docFamilyId: string, url: string) => {
        const result: any = await dispatch(
          documentFamilyApi.endpoints.getDocumentFamily.initiate(docFamilyId)
        );
        return { url, label: result.data.name } as any;
      },
      ':userId': async (userId: string, url: string) => {
        const result: any = await dispatch(usersApi.endpoints.getUser.initiate(userId));
        return { url, label: result.data.full_name } as any;
      },
      ':workQueueId': async (userId: string, url: string) => {
        const result: any = await dispatch(workQueuesApi.endpoints.getWorkQueue.initiate(userId));
        return { url, label: result.data.name } as any;
      },
      ':translationId': async (userId: string, url: string) => {
        const result: any = await dispatch(
          translationsApi.endpoints.getTranslationConfig.initiate(userId)
        );
        return { url, label: result.data.name } as any;
      },
      ':payerId': async (payerId: string, url: string) => {
        const payerType = url.split('/')[2];
        const result: any = await dispatch(
          payerBackboneApi.endpoints.getPayerBackbone.initiate({ payerType, id: payerId })
        );
        return { url, label: result.data.name } as any;
      },
    };

    // Mapping paths to display labels based on the root menu item; many are shared...
    // will move as needed
    return {
      '/sites': {
        new: 'Create',
        sites: 'Sites',
        view: 'View',
        edit: 'Edit',
        scrapes: 'Collections',
        documents: 'Documents',
        'doc-documents': 'Documents',
        extraction: 'Extracted Content',
        results: 'Results',
        lineage: 'Lineage',
        ...asyncResolvers,
      },
      '/documents': {
        documents: 'All Documents',
        ...asyncResolvers,
      },
      '/document-family': {
        'document-family': 'Document Families',
        ...asyncResolvers,
      },
      '/users': {
        users: 'Users',
        new: 'Create',
        edit: 'Edit',
        ...asyncResolvers,
      },
      '/work-queues': {
        'work-queues': 'Work Queues',
        new: 'Create',
        process: 'Process',
        'read-only': 'View',
        ...asyncResolvers,
      },
      '/translations': {
        translations: 'Translations',
        new: 'New',
        ...asyncResolvers,
      },
      '/payer-backbone': {
        'payer-backbone': 'Payer Backbone',
        new: 'New',
        ':payerType': (part: string, url: string) => {
          const names: { [k: string]: string } = {
            mco: 'MCO',
            plan: 'Plan',
            parent: 'Parent',
            ump: 'UM Package',
            bm: 'Benefit Manager',
            formulary: 'Formulary',
          };
          const label = names[part];

          return Promise.resolve({ url, label } as any);
        },
        ...asyncResolvers,
      },
    };
  }, [dispatch]);

  useEffect(() => {
    const promises: any[] = [];
    const paths = location.pathname.split('/');
    for (let route of routes) {
      const matcher = new URLPattern({ pathname: route });
      const match = matcher.exec(location);

      if (!match) {
        continue;
      }

      const pathParts = route.split('/');
      const crumbs = matched[`/${pathParts[1]}`];

      let i = 0;
      for (const part of pathParts) {
        const url = paths.slice(0, i + 1).join('/');
        const resolver = crumbs[part];
        if (typeof resolver === 'string') {
          promises.push(Promise.resolve({ url, label: resolver }));
        } else if (resolver !== undefined) {
          const id = match.pathname.groups[part.slice(1)] as string;
          promises.push(Promise.resolve(resolver(id, url)));
        }
        i++;
      }
      break;
    }

    Promise.all(promises).then((results) => dispatch(setBreadcrumbs(results)));
  }, [location, dispatch, matched]);
};
