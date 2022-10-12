import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { CompareRequest, CompareResponse, DocDocument } from './types';

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
        site_ids?: string[];
        scrape_task_id?: string;
      }
    >({
      query: ({ limit, skip, sortInfo, filterValue, site_ids, scrape_task_id }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ];
        if (site_ids) {
          args.push(`site_id=${site_ids}`);
        }
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
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'DocDocument', id },
        { type: 'ChangeLog', id },
      ],
    }),
    createDiff: builder.mutation<CompareResponse, CompareRequest>({
      query: (req) => ({
        url: `/doc-documents/${req.currentDocDocId}/diff?previous_doc_doc_id=${req.previousDocDocId}`,
        method: 'POST',
      }),
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useGetDocDocumentQuery,
  useGetDocDocumentsQuery,
  useLazyGetDocDocumentsQuery,
  useUpdateDocDocumentMutation,
  useCreateDiffMutation,
  useGetChangeLogQuery,
} = docDocumentsApi;
