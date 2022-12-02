import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import {
  TakeNextWorkItemResponse,
  TakeWorkItemResponse,
  SubmitWorkItemResponse,
  SubmitWorkItemRequest,
} from '../work_queue/types';
import { TableState } from '../work_queue/workQueueSlice';
import { DocBulkUpdateResponse, CompareRequest, CompareResponse, DocDocument } from './types';

export const docDocumentsApi = createApi({
  reducerPath: 'docDocumentsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DocDocument', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocDocuments: builder.query<
      { data: DocDocument[]; total: number },
      {
        limit: number;
        skip: number;
        sortInfo: TypeSortInfo;
        filterValue: TypeFilterValue;
        scrape_task_id?: string;
      }
    >({
      query: ({ limit, skip, sortInfo, filterValue, scrape_task_id }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const textFilterValue = filterValue?.map((f) => {
          if (f.name === 'name' || f.name === 'link_text') {
            return { ...f, operator: `text${f.operator}` };
          }
          return f;
        });
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(textFilterValue))}`,
        ];
        if (scrape_task_id) {
          args.push(`scrape_task_id=${scrape_task_id}`);
        }
        return `/doc-documents/?${args.join('&')}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'DocDocument' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'DocDocument', id }));
        return tags;
      },
    }),
    getDocDocument: builder.query<DocDocument, string | undefined>({
      query: (id) => `/doc-documents/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'DocDocument' as const, id }],
    }),
    updateDocDocument: builder.mutation<DocDocument, Partial<DocDocument>>({
      query: (body) => ({
        url: `/doc-documents/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => ['DocDocument', { type: 'ChangeLog', id }],
    }),
    createDiff: builder.mutation<CompareResponse, CompareRequest>({
      query: (req) => ({
        url: `/doc-documents/diff/${req.currentDocDocId}?previous_doc_doc_id=${req.previousDocDocId}`,
        method: 'POST',
      }),
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
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
        const filters =
          filterValue?.map((f) => {
            if (f.name === 'name' || f.name === 'link_text') {
              return { ...f, operator: `text${f.operator}` };
            }
            return f;
          }) || [];
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filters))}`,
        ].join('&');
        return `/work-queues/${id}/items?${args}`;
      },
      providesTags: (_r, _e, { id }) => [{ type: 'DocDocument' as const, id }],
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
    takeWorkItem: builder.mutation<
      TakeWorkItemResponse,
      { docDocumentId?: string; workQueueId?: string }
    >({
      query: ({ docDocumentId, workQueueId }) => ({
        url: `/work-queues/${workQueueId}/items/${docDocumentId}/take`,
        method: 'POST',
      }),
    }),
    submitWorkItem: builder.mutation<
      SubmitWorkItemResponse,
      { docDocumentId?: string; workQueueId?: string; body: SubmitWorkItemRequest }
    >({
      query: ({ docDocumentId, body, workQueueId }) => ({
        url: `/work-queues/${workQueueId}/items/${docDocumentId}/submit`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { docDocumentId: id }) => [{ type: 'DocDocument', id }],
    }),
    updateMultipleDocs: builder.mutation<
      DocBulkUpdateResponse,
      {
        ids: string[];
        update: Partial<DocDocument>;
        site_id?: string;
        payer_family_id?: string;
        all_sites?: boolean;
      }
    >({
      query: (body) => {
        return {
          url: '/doc-documents/bulk',
          method: 'POST',
          body,
        };
      },
    }),
  }),
});

export const {
  useGetDocDocumentQuery,
  useGetDocDocumentsQuery,
  useLazyGetDocDocumentsQuery,
  useUpdateDocDocumentMutation,
  useUpdateMultipleDocsMutation,
  useCreateDiffMutation,
  useGetChangeLogQuery,
  useGetWorkQueueItemsQuery,
  useLazyGetWorkQueueItemsQuery,
  useTakeWorkItemMutation,
  useTakeNextWorkItemMutation,
  useSubmitWorkItemMutation,
} = docDocumentsApi;
