import { createApi, fetchBaseQuery } from '../../app/base-api';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { ChangeLog } from '../change-log/types';
import { ContentExtractionResult, ExtractionTask } from './types';

export const extractionTasksApi = createApi({
  reducerPath: 'extractionTasksApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['ExtractionTask', 'ExtractionTaskResult', 'ChangeLog'],
  endpoints: (builder) => ({
    getExtractionTasksForDoc: builder.query<ExtractionTask[], string | undefined>({
      query: (docId) => `/extraction-tasks/?doc_document_id=${docId}`,
      providesTags: (_r, _e, id) => [{ type: 'ExtractionTask' as const, id }],
    }),
    getExtractionTaskResults: builder.query<
      { data: ContentExtractionResult[]; total: number },
      {
        id: string;
        limit: number;
        skip: number;
        sortInfo: TypeSortInfo;
        filterValue: TypeFilterValue;
        delta: boolean;
      }
    >({
      query: ({ limit, skip, sortInfo, filterValue, delta, id }) => {
        const args = [
          `extraction_id=${encodeURIComponent(id)}`,
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `delta=${encodeURIComponent(delta)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sortInfo))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ].join('&');
        return `/extraction-tasks/results/?${args}`;
      },
      providesTags: (_r, _e, { id }) => [{ type: 'ExtractionTaskResult' as const, id }],
    }),
    runExtractionTask: builder.mutation<ExtractionTask, string>({
      query: (docId) => ({
        url: `/extraction-tasks/?doc_document_id=${docId}`,
        method: 'PUT',
      }),
      invalidatesTags: (_r, _e, id) => [{ type: 'ExtractionTask', id }],
    }),
    getExtractionTask: builder.query<ExtractionTask, string | undefined>({
      query: (id) => `/extraction-tasks/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ExtractionTask' as const, id }],
    }),
    updateExtractionTask: builder.mutation<ExtractionTask, Partial<ExtractionTask>>({
      query: (body) => ({
        url: `/extraction-tasks/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'ExtractionTask', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteExtractionTask: builder.mutation<
      void,
      Pick<ExtractionTask, '_id'> & Partial<ExtractionTask>
    >({
      query: ({ _id: id }) => ({
        url: `/extraction-tasks/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'ExtractionTask', id },
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
  useGetExtractionTasksForDocQuery,
  useGetExtractionTaskResultsQuery,
  useLazyGetExtractionTaskResultsQuery,
  useGetExtractionTaskQuery,
  useRunExtractionTaskMutation,
  useUpdateExtractionTaskMutation,
  useDeleteExtractionTaskMutation,
  useGetChangeLogQuery,
} = extractionTasksApi;
