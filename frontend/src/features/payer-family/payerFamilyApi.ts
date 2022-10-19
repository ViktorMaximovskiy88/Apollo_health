import { createApi, fetchBaseQuery } from '../../app/base-api';
import { TableInfoType } from '../../common/types';
import { ChangeLog } from '../change-log/types';
import { PayerFamily } from './types';

export const payerFamilyApi = createApi({
  reducerPath: 'payerFamilyApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['PayerFamily', 'ChangeLog'],
  endpoints: (builder) => ({
    getPayerFamilies: builder.query<{ data: PayerFamily[]; total: number }, TableInfoType>({
      query: ({ limit, skip, filterValue, sortInfo }) => {
        const args = [
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify([sortInfo]))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ];

        return `/payer-family/?${args.join('&')}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'PayerFamily' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'PayerFamily', id }));
        return tags;
      },
    }),
    getPayerFamily: builder.query<PayerFamily, string | undefined>({
      query: (id) => `/payer-family/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'PayerFamily' as const, id }],
    }),
    getPayerFamilyByName: builder.query<PayerFamily, { name: string }>({
      query: ({ name }) => `/payer-family/search?name=${name}`,
      providesTags: (_r, _e, name) => [{ type: 'PayerFamily' as const, name }],
    }),
    addPayerFamily: builder.mutation<PayerFamily, Partial<PayerFamily>>({
      query: (body) => ({ url: '/payer-family/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'PayerFamily', id: 'LIST' }],
    }),
    updatePayerFamily: builder.mutation<PayerFamily, Partial<PayerFamily>>({
      query: (body) => ({
        url: `/payer-family/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'PayerFamily', id },
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
  useGetPayerFamiliesQuery,
  useLazyGetPayerFamiliesQuery,
  useLazyGetPayerFamilyByNameQuery,
  useAddPayerFamilyMutation,
  useUpdatePayerFamilyMutation,
  useGetChangeLogQuery,
} = payerFamilyApi;
