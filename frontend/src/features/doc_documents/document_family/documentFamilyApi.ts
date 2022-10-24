import { createApi, fetchBaseQuery } from '../../../app/base-api';
import { TableInfoType } from '../../../common/types';
import { ChangeLog } from '../../change-log/types';
import { DocumentFamily } from './types';

export const documentFamilyApi = createApi({
  reducerPath: 'documentFamilyApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DocumentFamily', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocumentFamilies: builder.query<
      { data: DocumentFamily[]; total: number },
      Partial<TableInfoType> & { documentType?: string }
    >({
      query: ({ limit, skip, filterValue, sortInfo, documentType }) => {
        const args = [];
        if (limit && skip != null && filterValue && sortInfo) {
          args.push(
            `limit=${encodeURIComponent(limit)}`,
            `skip=${encodeURIComponent(skip)}`,
            `sorts=${encodeURIComponent(JSON.stringify([sortInfo]))}`,
            `filters=${encodeURIComponent(JSON.stringify(filterValue))}`
          );
        }
        if (documentType) {
          args.push(`document_type=${encodeURIComponent(documentType)}`);
        }
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
  useGetChangeLogQuery,
} = documentFamilyApi;
