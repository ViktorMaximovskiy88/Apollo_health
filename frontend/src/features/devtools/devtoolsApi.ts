import type { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { Task } from '../tasks/types';

interface DocumentSearch {
  site_id: string | undefined;
  search_query: string | undefined;
  page: number;
  limit: number;
  sort: string;
}

interface PagedResuts {
  items: any[];
  total_count: number;
}

export const devtoolsApi = createApi({
  reducerPath: 'devtoolsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DevToolsDoc'],
  endpoints: (builder) => ({
    processSiteLineage: builder.mutation<Task, string | undefined>({
      query: (siteId) => ({
        url: `/devtools/lineage/reprocess/${siteId}`,
        method: 'POST',
      }),
    }),
    getDocuments: builder.query<PagedResuts, DocumentSearch>({
      query: (params: DocumentSearch) => ({ url: `/devtools/documents`, params }),
      providesTags: (results) => {
        const tags = [{ type: 'DevToolsDoc' as const, id: 'LIST' }];
        results?.items.forEach(({ _id: id }) => tags.push({ type: 'DevToolsDoc', id }));
        return tags;
      },
    }),
    searchSites: builder.query<PagedResuts, string | undefined>({
      async queryFn(search_query, queryApi, extraOptions, fetchWithBQ) {
        const params = { search_query };
        const result = await fetchWithBQ({ url: `/devtools/sites/search`, params });
        return result.data
          ? { data: result.data as PagedResuts }
          : { error: result.error as FetchBaseQueryError };
      },
    }),
  }),
});

export const {
  useProcessSiteLineageMutation,
  useGetDocumentsQuery,
  useLazyGetDocumentsQuery,
  useLazySearchSitesQuery,
} = devtoolsApi;
