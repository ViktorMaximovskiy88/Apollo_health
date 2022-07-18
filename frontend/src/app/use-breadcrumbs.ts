import { useEffect } from 'react';
import { sitesApi } from '../features/sites/sitesApi';
import { documentsApi } from '../features/retrieved_documents/documentsApi';
import { useLocation } from 'react-router-dom';
import { setBreadcrumbs, breadcrumbState } from './appSlice';
import { useDispatch, useSelector } from 'react-redux';

const routes = [
  '/sites',
  '/sites/:siteId/edit',
  '/sites/:siteId/scrapes',
  '/sites/:siteId/documents',
  '/sites/:siteId/documents/:docId/edit',
  '/sites/:siteId/extraction',
  '/documents',
];

export const useBreadcrumbs = async () => {
  const dispatch = useDispatch();
  const location = useLocation();

  // async resolvers that get cached and more or less act like prefetch
  const shared = {
    ':siteId': async (siteId: string) => {
      const result: any = await dispatch(sitesApi.endpoints.getSite.initiate(siteId));
      return { url: siteId, label: result.data.name };
    },
    ':docId': async (docId: string) => {
      const result: any = await dispatch(documentsApi.endpoints.getDocument.initiate(docId));
      return { url: docId, label: result.data.name } as any;
    },
  };

  // Mapping paths to display labels based on the root menu item; many are shared...
  // will move as needed
  const matched: any = {
    '/sites': {
      sites: 'Sites',
      edit: 'Edit',
      scrapes: 'Collections',
      documents: 'Documents',
      extraction: 'Extracted Content',
      ...shared,
    },
    '/documents': {
      documents: 'All Documents',
      ...shared,
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
