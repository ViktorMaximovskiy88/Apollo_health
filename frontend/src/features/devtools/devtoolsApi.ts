import { createApi, fetchBaseQuery } from '../../app/base-api';
import { DevToolsDoc } from './types';
import { Task } from '../tasks/types';

export const devtoolsApi = createApi({
  reducerPath: 'devtoolsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DevToolsDoc'],
  endpoints: (builder) => ({
    processSiteLineage: builder.mutation<Task, string | undefined>({
      query: (siteId) => ({
        url: `/lineage/reprocess/${siteId}`,
        method: 'POST',
      }),
    }),
    getSiteLineage: builder.query<DevToolsDoc[], string | undefined>({
      query: (siteId) => `/lineage/${siteId}`,
      providesTags: (results) => {
        const tags = [{ type: 'DevToolsDoc' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'DevToolsDoc', id }));
        return tags;
      },
    }),
  }),
});

export const { useProcessSiteLineageMutation, useGetSiteLineageQuery } = devtoolsApi;
