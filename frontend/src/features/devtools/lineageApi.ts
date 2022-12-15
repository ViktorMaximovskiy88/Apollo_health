import { createApi, fetchBaseQuery } from '../../app/base-api';
import { LineageDoc } from './types';
import { Task } from '../tasks/taskApi';

export const lineageApi = createApi({
  reducerPath: 'lineageApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['LineageDoc'],
  endpoints: (builder) => ({
    processSiteLineage: builder.mutation<Task, string | undefined>({
      query: (siteId) => ({
        url: `/lineage/reprocess/${siteId}`,
        method: 'POST',
      }),
    }),
    getSiteLineage: builder.query<LineageDoc[], string | undefined>({
      query: (siteId) => `/lineage/${siteId}`,
      providesTags: (results) => {
        const tags = [{ type: 'LineageDoc' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'LineageDoc', id }));
        return tags;
      },
    }),
  }),
});

export const { useProcessSiteLineageMutation, useGetSiteLineageQuery } = lineageApi;
