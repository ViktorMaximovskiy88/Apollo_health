import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { Site } from './types';
import { RetrievedDocument } from '../retrieved_documents/types';
import { SiteDocDocument } from '../doc_documents/types';

export const sitesApi = createApi({
  reducerPath: 'sitesApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Site', 'ChangeLog', 'SiteDocDocument', 'RetrievedDocument'],
  endpoints: (builder) => ({
    getSites: builder.query<
      { data: Site[]; total: number },
      { limit: number; skip: number; sortInfo: TypeSortInfo; filterValue: TypeFilterValue }
    >({
      query: ({ limit, skip, sortInfo, filterValue }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ].join('&');
        return `/sites/?${args}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'Site' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'Site', id }));
        return tags;
      },
    }),
    getSite: builder.query<Site, string | undefined>({
      query: (id) => `/sites/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'Site' as const, id }],
    }),
    getSiteRetrievedDocuments: builder.query<
      RetrievedDocument[],
      {
        siteId: String | undefined;
        scrapeTaskId: String | null;
      }
    >({
      query: ({ siteId, scrapeTaskId }) => {
        let url = `/sites/${siteId}/documents`;
        if (scrapeTaskId) {
          url += `?scrape_task_id=${scrapeTaskId}`;
        }
        return url;
      },
      providesTags: (results) => {
        const tags = [{ type: 'RetrievedDocument' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'RetrievedDocument', id }));
        return tags;
      },
    }),
    getSiteDocDocument: builder.query<SiteDocDocument, any>({
      query: ({ siteId, docId }) => `/sites/${siteId}/doc-documents/${docId}`,
      providesTags: (_r, _e, id) => [{ type: 'Site' as const, id }],
    }),
    getSiteDocDocuments: builder.query<
      SiteDocDocument[],
      {
        siteId: String | undefined;
        scrapeTaskId: String | null;
      }
    >({
      query: ({ siteId, scrapeTaskId }) => {
        let url = `/sites/${siteId}/doc-documents`;
        if (scrapeTaskId) {
          url += `?scrape_task_id=${scrapeTaskId}`;
        }
        return url;
      },
      providesTags: (results) => {
        const tags = [{ type: 'SiteDocDocument' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'SiteDocDocument', id }));
        return tags;
      },
    }),
    addSite: builder.mutation<Site, Partial<Site>>({
      query: (body) => ({ url: '/sites/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'Site', id: 'LIST' }],
    }),
    updateSite: builder.mutation<Site, Partial<Site>>({
      query: (body) => ({ url: `/sites/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'Site', id },
        { type: 'Site', id: 'LIST' },
        { type: 'ChangeLog', id },
      ],
    }),
    updateMultipleSites: builder.mutation<Site[], any>({
      query: (body) => {
        return { url: `/sites/bulk-assign`, method: 'POST', body };
      },
    }),
    deleteSite: builder.mutation<void, Pick<Site, '_id'> & Partial<Site>>({
      query: ({ _id: id }) => ({ url: `/sites/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'Site', id },
        { type: 'Site', id: 'LIST' },
        { type: 'ChangeLog', id },
      ],
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useGetSiteQuery,
  useLazyGetSiteQuery,
  useGetSitesQuery,
  useLazyGetSitesQuery,
  useAddSiteMutation,
  useUpdateSiteMutation,
  useUpdateMultipleSitesMutation,
  useDeleteSiteMutation,
  useGetChangeLogQuery,
  useGetSiteRetrievedDocumentsQuery,
  useGetSiteDocDocumentsQuery,
  useLazyGetSiteDocDocumentsQuery,
} = sitesApi;
