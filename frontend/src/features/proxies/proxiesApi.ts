import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Proxy } from './types';

export const proxiesApi = createApi({
  reducerPath: 'proxiesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1/' }),
  tagTypes: ['Proxy'],
  endpoints: (builder) => ({
    getProxies: builder.query<Proxy[], void>({
      query: () => '/proxies/',
      providesTags: () => [{ type: 'Proxy' as const, id: 'LIST' }],
    }),
  }),
});

export const {
  useGetProxiesQuery,
} = proxiesApi;
