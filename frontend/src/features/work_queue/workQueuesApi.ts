import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { DocDocument } from '../doc_documents/types';
import {
  SubmitWorkItemRequest,
  SubmitWorkItemResponse,
  TakeNextWorkItemResponse,
  TakeWorkItemResponse,
  WorkQueue,
  WorkQueueCount,
} from './types';
import { TableState } from './workQueueSlice';

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
    getWorkQueueItems: builder.query<
      { data: DocDocument[]; total: number },
      {
        id: string | undefined;
        limit: number;
        skip: number;
        sortInfo: TypeSortInfo;
        filterValue: TypeFilterValue;
      }
    >({
      query: ({ id, limit, skip, sortInfo, filterValue }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const filters = filterValue ?? [];
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filters))}`,
        ].join('&');
        return `/work-queues/${id}/items?${args}`;
      },
      providesTags: (_r, _e, { id }) => [{ type: 'WorkQueue' as const, id }],
    }),
    getWorkQueueCounts: builder.query<WorkQueueCount[], void>({
      query: (id) => `/work-queues/counts`,
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
    takeNextWorkItem: builder.mutation<
      TakeNextWorkItemResponse,
      { queueId: string | undefined; tableState: TableState }
    >({
      query: ({ queueId, tableState: body }) => ({
        url: `/work-queues/${queueId}/items/take-next`,
        method: 'POST',
        body,
      }),
    }),
    takeWorkItem: builder.mutation<TakeWorkItemResponse, { itemId?: string; workQueueId?: string }>(
      {
        query: ({ itemId, workQueueId }) => ({
          url: `/work-queues/${workQueueId}/items/${itemId}/take`,
          method: 'POST',
        }),
      }
    ),
    submitWorkItem: builder.mutation<
      SubmitWorkItemResponse,
      { itemId?: string; workQueueId?: string; body: SubmitWorkItemRequest }
    >({
      query: ({ itemId, body, workQueueId }) => ({
        url: `/work-queues/${workQueueId}/items/${itemId}/submit`,
        method: 'POST',
        body,
      }),
    }),
  }),
});

export const {
  useGetWorkQueueQuery,
  useGetWorkQueueItemsQuery,
  useLazyGetWorkQueueItemsQuery,
  useGetWorkQueueCountsQuery,
  useGetWorkQueuesQuery,
  useAddWorkQueueMutation,
  useUpdateWorkQueueMutation,
  useDeleteWorkQueueMutation,
  useGetChangeLogQuery,
  useTakeWorkItemMutation,
  useTakeNextWorkItemMutation,
  useSubmitWorkItemMutation,
} = workQueuesApi;
