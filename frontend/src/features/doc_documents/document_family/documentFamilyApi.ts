import { createApi, fetchBaseQuery } from '../../../app/base-api';
import { TableInfoType } from '../../../common/types';
import { ChangeLog } from '../../change-log/types';
import { DocumentFamily } from './types';
import { makeTableQueryParams } from '../../../common/helpers';

export const documentFamilyApi = createApi({
  reducerPath: 'documentFamilyApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DocumentFamily', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocumentFamilies: builder.query<
      { data: DocumentFamily[]; total: number },
      Partial<TableInfoType> & { documentType?: string }
    >({
      query: ({ documentType, ...queryArgs }) => {
        const args = makeTableQueryParams(queryArgs, { document_type: documentType });
        return `/document-family/?${args.join('&')}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'DocumentFamily' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'DocumentFamily', id }));
        return tags;
      },
    }),
    getDocumentFamily: builder.query<DocumentFamily, string | undefined>({
      query: (id) => `/document-family/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'DocumentFamily' as const, id }],
    }),
    getDocumentFamilyByName: builder.query<DocumentFamily, { name: string }>({
      query: ({ name }) => `/document-family/search?name=${name}`,
      providesTags: (_r, _e, name) => [{ type: 'DocumentFamily' as const, name }],
    }),
    addDocumentFamily: builder.mutation<DocumentFamily, Partial<DocumentFamily>>({
      query: (body) => ({ url: '/document-family/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'DocumentFamily', id: 'LIST' }],
    }),
    updateDocumentFamily: builder.mutation<
      DocumentFamily,
      { body: Partial<DocumentFamily>; _id?: string }
    >({
      query: ({ body, _id }) => ({
        url: `/document-family/${_id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'DocumentFamily', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteDocumentFamily: builder.mutation<
      void,
      Pick<DocumentFamily, '_id'> & Partial<DocumentFamily>
    >({
      query: ({ _id: id }) => ({ url: `/document-family/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'DocumentFamily', id },
        { type: 'DocumentFamily', id: 'LIST' },
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
  useGetDocumentFamiliesQuery,
  useLazyGetDocumentFamiliesQuery,
  useLazyGetDocumentFamilyByNameQuery,
  useGetDocumentFamilyQuery,
  useAddDocumentFamilyMutation,
  useUpdateDocumentFamilyMutation,
  useDeleteDocumentFamilyMutation,
  useGetChangeLogQuery,
} = documentFamilyApi;
