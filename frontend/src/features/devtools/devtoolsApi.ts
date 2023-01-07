import type { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { DevToolsDoc } from './types';
import { Task } from '../tasks/types';
import { Site } from '../sites/types';

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
    getSiteLineage: builder.query<DevToolsDoc[], string | undefined>({
      query: (siteId) => `/devtools/lineage/${siteId}`,
      providesTags: (results) => {
        const tags = [{ type: 'DevToolsDoc' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'DevToolsDoc', id }));
        return tags;
      },
    }),
    searchSites: builder.query<Site[], string | undefined>({
      async queryFn(search_query, queryApi, extraOptions, fetchWithBQ) {
        console.log(search_query, queryApi, extraOptions, fetchWithBQ);
        const params = {
          search_query,
        };
        const result = await fetchWithBQ({ url: `/devtools/sites/search`, params });
        return result.data
          ? { data: result.data as Site[] }
          : { error: result.error as FetchBaseQueryError };
      },
    }),
  }),
});

export const { useProcessSiteLineageMutation, useGetSiteLineageQuery, useLazySearchSitesQuery } =
  devtoolsApi;
