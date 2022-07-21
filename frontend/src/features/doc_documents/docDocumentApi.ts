import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { DocDocument } from './types';

export const docDocumentsApi = createApi({
  reducerPath: 'docDocumentsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DocDocument', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocDocuments: builder.query<
      { data: DocDocument[]; total: number },
      { limit: number; skip: number; sortInfo: TypeSortInfo; filterValue: TypeFilterValue }
    >({
      query: ({ limit, skip, sortInfo, filterValue }) => {
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify([sortInfo]))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ].join('&');
        return `/doc-documents/?${args}`;
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
  useGetChangeLogQuery,
} = docDocumentsApi;
