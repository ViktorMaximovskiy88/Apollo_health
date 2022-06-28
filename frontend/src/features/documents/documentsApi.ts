import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { RetrievedDocument, DocumentQuery } from './types';

function queryString(params: DocumentQuery) {
  return Object.entries(params)
    .filter(([_, v]) => v)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');
}

export const documentsApi = createApi({
  reducerPath: 'documentsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['RetrievedDocument', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocuments: builder.query<RetrievedDocument[], DocumentQuery>({
      query: (query) => `/documents/?${queryString(query)}`,
      providesTags: (results) => {
        const tags = [{ type: 'RetrievedDocument' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) =>
          tags.push({ type: 'RetrievedDocument', id })
        );
        return tags;
      },
    }),
    getDocument: builder.query<RetrievedDocument, string | undefined>({
      query: (id) => `/documents/${id}`,
      providesTags: (_r, _e, id) => [
        { type: 'RetrievedDocument' as const, id },
      ],
    }),
    addDocument: builder.mutation<
      RetrievedDocument,
      Partial<RetrievedDocument>
    >({
      query: (body) => ({ url: '/documents/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'RetrievedDocument', id: 'LIST' }],
    }),
    updateDocument: builder.mutation<
      RetrievedDocument,
      Partial<RetrievedDocument>
    >({
      query: (body) => ({
        url: `/documents/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'RetrievedDocument', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteDocument: builder.mutation<
      void,
      Pick<RetrievedDocument, '_id'> & Partial<RetrievedDocument>
    >({
      query: ({ _id: id }) => ({ url: `/documents/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'RetrievedDocument', id },
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
  useGetDocumentQuery,
  useGetDocumentsQuery,
  useAddDocumentMutation,
  useUpdateDocumentMutation,
  useDeleteDocumentMutation,
  useGetChangeLogQuery,
} = documentsApi;
