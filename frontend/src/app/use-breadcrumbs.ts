import { useEffect } from 'react';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { docDocumentsApi } from '../features/doc_documents/docDocumentApi';
import { useLocation } from 'react-router-dom';
import { setBreadcrumbs, breadcrumbState } from './appSlice';
import { useDispatch, useSelector } from 'react-redux';
import { usersApi } from '../features/users/usersApi';

const routes = [
  '/sites',
  '/sites/new',
  '/sites/:siteId/edit',
  '/sites/:siteId/scrapes',
  '/sites/:siteId/documents',
  '/sites/:siteId/documents/:docId/edit',
  '/sites/:siteId/extraction',
  '/documents',
  '/documents/:docDocId',
  '/users',
  '/users/new',
  '/users/:userId/edit',
];

export const useBreadcrumbs = async () => {
  const dispatch = useDispatch();
  const location = useLocation();

  // async resolvers that get cached and more or less act like prefetch
  const asyncResolvers = {
    ':siteId': async (siteId: string) => {
      const result: any = await dispatch(sitesApi.endpoints.getSite.initiate(siteId));
      return { url: siteId, label: result.data.name };
    },
    ':docId': async (docId: string) => {
      const result: any = await dispatch(documentsApi.endpoints.getDocument.initiate(docId));
      return { url: docId, label: result.data.name } as any;
    },
    ':docDocId': async (docDocId: string) => {
      const result: any = await dispatch(
        docDocumentsApi.endpoints.getDocDocument.initiate(docDocId)
      );
      return { url: docDocId, label: result.data.name } as any;
    },
    ':userId': async (userId: string) => {
      const result: any = await dispatch(usersApi.endpoints.getUser.initiate(userId));
      return { url: userId, label: result.data.full_name } as any;
    },
  };

  // Mapping paths to display labels based on the root menu item; many are shared...
  // will move as needed
  const matched: any = {
    '/sites': {
      new: 'Create',
      sites: 'Sites',
      edit: 'Edit',
      scrapes: 'Collections',
      documents: 'Documents',
      extraction: 'Extracted Content',
      ...asyncResolvers,
    },
    '/documents': {
      documents: 'All Documents',
      ...asyncResolvers,
    },
    '/users': {
      users: 'Users',
      new: 'Create',
      edit: 'Edit',
      ...asyncResolvers,
    },
  };

  useEffect(() => {
    const promises: any[] = [];
    for (let route of routes) {
      const matcher = new URLPattern({ pathname: route });
      const match = matcher.exec(location);

      if (!match) {
        continue;
      }

      const pathParts = route.split('/').slice(1);
      const crumbs = matched[`/${pathParts[0]}`];

      for (const part of pathParts) {
        const resolver = crumbs[part];
        if (typeof resolver === 'string') {
          promises.push(Promise.resolve({ url: part, label: resolver }));
        } else if (resolver != undefined) {
          const id = match.pathname.groups[part.slice(1)] as string;
          promises.push(Promise.resolve(resolver(id)));
        }
      }
    }

    Promise.all(promises).then((results) => dispatch(setBreadcrumbs(results)));
  }, [location]);
};
