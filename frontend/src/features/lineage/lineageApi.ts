import { createApi, fetchBaseQuery } from '../../app/base-api';
import { LineageDoc } from './types';

export const lineageApi = createApi({
  reducerPath: 'lineageApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['LineageDoc'],
  endpoints: (builder) => ({
    processSiteLineage: builder.query<undefined, string | undefined>({
      query: (siteId) => `/lineage/reprocess/${siteId}?_=${+new Date()}`,
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

export const { useLazyProcessSiteLineageQuery, useGetSiteLineageQuery } = lineageApi;
