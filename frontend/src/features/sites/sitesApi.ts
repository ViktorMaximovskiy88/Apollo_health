import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { ChangeLog } from '../change_log/types';
import { Site } from './types';

export const sitesApi = createApi({
  reducerPath: 'sitesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1/' }),
  tagTypes: ['Site', 'ChangeLog'],
  endpoints: (builder) => ({
    getSites: builder.query<Site[], void>({
      query: () => '/sites/',
      providesTags: (results) => {
        const tags = [{ type: 'Site' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'Site', id }));
        return tags;
      },
    }),
    getSite: builder.query<Site, string | undefined>({
      query: (id) => `/sites/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'Site' as const, id }],
    }),
    addSite: builder.mutation<Site, Partial<Site>>({
      query: (body) => ({ url: '/sites/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'Site', id: 'LIST' }],
    }),
    updateSite: builder.mutation<Site, Partial<Site>>({
      query: (body) => ({ url: `/sites/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'Site', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteSite: builder.mutation<void, Pick<Site, '_id'> & Partial<Site>>({
      query: ({ _id: id }) => ({ url: `/sites/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'Site', id },
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
  useGetSitesQuery,
  useAddSiteMutation,
  useUpdateSiteMutation,
  useDeleteSiteMutation,
  useGetChangeLogQuery,
} = sitesApi;
