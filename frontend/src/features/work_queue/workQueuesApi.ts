import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { WorkQueue, WorkQueueCount } from './types';

export const workQueuesApi = createApi({
  reducerPath: 'workQueuesApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['WorkQueue', 'WorkQueueSize', 'DocDocument', 'ChangeLog'],
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
    getWorkQueueByName: builder.query<WorkQueue, { name: string }>({
      query: ({ name }) => `/work-queues/search?name=${encodeURIComponent(name)}`,
      providesTags: (_r, _e, name) => [{ type: 'WorkQueue' as const, name }],
    }),
    getWorkQueueCounts: builder.query<WorkQueueCount[], void>({
      query: (id) => `/work-queues/counts`,
      providesTags: () => [{ type: 'WorkQueueSize', id: 'LIST' }],
    }),
    addWorkQueue: builder.mutation<WorkQueue, Partial<WorkQueue>>({
      query: (body) => ({ url: '/work-queues/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'WorkQueue', id: 'LIST' }],
    }),
    updateWorkQueue: builder.mutation<WorkQueue, Partial<WorkQueue>>({
      query: (body) => ({ url: `/work-queues/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'WorkQueue', id },
        { type: 'ChangeLog', id },
        { type: 'WorkQueue', id: 'LIST' },
      ],
    }),
    deleteWorkQueue: builder.mutation<void, Pick<WorkQueue, '_id'> & Partial<WorkQueue>>({
      query: ({ _id: id }) => ({ url: `/work-queues/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'WorkQueue', id },
        { type: 'ChangeLog', id },
        { type: 'WorkQueue', id: 'LIST' },
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
  useLazyGetWorkQueueCountsQuery,
  useGetWorkQueueByNameQuery,
  useGetWorkQueuesQuery,
  useAddWorkQueueMutation,
  useUpdateWorkQueueMutation,
  useDeleteWorkQueueMutation,
  useGetChangeLogQuery,
} = workQueuesApi;
