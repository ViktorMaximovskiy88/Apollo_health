import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setBreadcrumbs } from './appSlice';

import { usersApi } from '../features/users/usersApi';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { docDocumentsApi } from '../features/doc_documents/docDocumentApi';

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
    ':userId': async (userId: string, url: string) => {
      const result: any = await dispatch(usersApi.endpoints.getUser.initiate(userId));
      return { url, label: result.data.full_name } as any;
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
        } else if (resolver != undefined) {
          const id = match.pathname.groups[part.slice(1)] as string;
          promises.push(Promise.resolve(resolver(id, url)));
        }
        i++;
      }
    }

    Promise.all(promises).then((results) => dispatch(setBreadcrumbs(results)));
  }, [location]);
};
