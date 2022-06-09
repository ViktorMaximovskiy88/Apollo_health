import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { ChangeLog } from '../change_log/types';
import { WorkQueue, WorkQueueCount } from './types';

export const workQueuesApi = createApi({
  reducerPath: 'workQueuesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1/' }),
  tagTypes: ['WorkQueue', 'WorkQueueSize', 'DocumentAssessment', 'ChangeLog'],
  endpoints: (builder) => ({
    getWorkQueues: builder.query<WorkQueue[], void>({
      query: () => '/work-queues/',
      providesTags: (results) => {
        const tags = [{ type: 'WorkQueue' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'WorkQueue', id }));
        return tags;
      },
    }),
    getWorkQueue: builder.query<WorkQueue, string | undefined>({
      query: (id) => `/work-queues/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'WorkQueue' as const, id }],
    }),
    getWorkQueueCounts: builder.query<WorkQueueCount[], void>({
      query: (id) => `/work-queues/counts`,
      providesTags: () => [{ type: 'WorkQueueSize' as const, id: 'LIST' }],
    }),
    addWorkQueue: builder.mutation<WorkQueue, Partial<WorkQueue>>({
      query: (body) => ({ url: '/work-queues/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'WorkQueue', id: 'LIST' }],
    }),
    updateWorkQueue: builder.mutation<WorkQueue, Partial<WorkQueue>>({
      query: (body) => ({ url: `/work-queue/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'WorkQueue', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteWorkQueue: builder.mutation<void, Pick<WorkQueue, '_id'> & Partial<WorkQueue>>({
      query: ({ _id: id }) => ({ url: `/work-queue/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'WorkQueue', id },
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
  useGetWorkQueueQuery,
  useGetWorkQueueCountsQuery,
  useGetWorkQueuesQuery,
  useAddWorkQueueMutation,
  useUpdateWorkQueueMutation,
  useDeleteWorkQueueMutation,
  useGetChangeLogQuery,
} = workQueuesApi;
