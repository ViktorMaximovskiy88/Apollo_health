import { createApi, fetchBaseQuery } from '../../../app/base-api';
import { DocumentFamily } from './types';

export const documentFamilyApi = createApi({
  reducerPath: 'documentFamilyApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['DocumentFamily', 'ChangeLog'],
  endpoints: (builder) => ({
    getDocumentFamilies: builder.query<DocumentFamily[], { siteId: string; documentType: string }>({
      query: ({ siteId, documentType }) => {
        const args = [
          `site_id=${encodeURIComponent(siteId)}`,
          `document_type=${encodeURIComponent(documentType)}`,
        ].join('&');
        return `/document-family/?${args}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'DocumentFamily' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'DocumentFamily', id }));
        return tags;
      },
    }),
    getDocumentFamily: builder.query<DocumentFamily, string | undefined>({
      query: (id) => `/document-family/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'DocumentFamily' as const, id }],
    }),
    getDocumentFamilyByName: builder.query<DocumentFamily, { name: string; siteId: string }>({
      query: ({ name, siteId }) => `/document-family/search?name=${name}&site_id=${siteId}`,
      providesTags: (_r, _e, name) => [{ type: 'DocumentFamily' as const, name }],
    }),
    addDocumentFamily: builder.mutation<DocumentFamily, Partial<DocumentFamily>>({
      query: (body) => ({ url: '/document-family/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'DocumentFamily', id: 'LIST' }],
    }),
    updateDocumentFamily: builder.mutation<DocumentFamily, Partial<DocumentFamily>>({
      query: (body) => ({
        url: `/document-family/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'DocumentFamily', id },
        { type: 'ChangeLog', id },
      ],
    }),
  }),
});

export const {
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamilyByNameQuery,
  useGetDocumentFamiliesQuery,
  useLazyGetDocumentFamiliesQuery,
  useAddDocumentFamilyMutation,
  useUpdateDocumentFamilyMutation,
} = documentFamilyApi;
