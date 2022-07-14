import { createApi, fetchBaseQuery } from '../../app/base-api';
import { Proxy } from './types';

export const proxiesApi = createApi({
  reducerPath: 'proxiesApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Proxy'],
  endpoints: (builder) => ({
    getProxies: builder.query<Proxy[], void>({
      query: () => '/proxies/',
      providesTags: () => [{ type: 'Proxy' as const, id: 'LIST' }],
    }),
  }),
});

export const { useGetProxiesQuery } = proxiesApi;
