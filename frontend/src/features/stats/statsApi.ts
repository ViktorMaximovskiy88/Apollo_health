import { createApi, fetchBaseQuery } from '../../app/base-api';
import { CollectionStats } from './types';

export const statsApi = createApi({
  reducerPath: 'statsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['CollectionStats'],
  endpoints: (builder) => ({
    getCollectionStats: builder.query<CollectionStats[], string | undefined>({
      query: (siteId) => `/stats/collection?${+new Date()}`,
      providesTags: (_r, _e, id) => [{ type: 'CollectionStats' as const, id }],
    }),
  }),
});

export const { useGetCollectionStatsQuery } = statsApi;
