import { createApi, fetchBaseQuery } from '../../app/base-api';
import { makeTableQueryParams } from '../../common/helpers';
import { TableInfoType } from '../../common/types';
import { ChangeLog } from '../change-log/types';
import { PayerFamily } from './types';

export const payerFamilyApi = createApi({
  reducerPath: 'payerFamilyApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['PayerFamily', 'ChangeLog'],
  endpoints: (builder) => ({
    getPayerFamilies: builder.query<{ data: PayerFamily[]; total: number }, TableInfoType>({
      query: (queryArgs) => {
        const args = makeTableQueryParams(queryArgs);
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
    deletePayerFamily: builder.mutation<void, Pick<PayerFamily, '_id'> & Partial<PayerFamily>>({
      query: ({ _id: id }) => ({ url: `/payer-family/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'PayerFamily', id },
        { type: 'PayerFamily', id: 'LIST' },
        { type: 'ChangeLog', id },
      ],
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
    convertPayerFamilyData: builder.query<
      PayerFamily,
      { payerType?: string; body: Partial<PayerFamily> }
    >({
      query: ({ payerType, body }) => ({
        url: `/payer-family/convert/${payerType}`,
        method: 'POST',
        body,
      }),
    }),
  }),
});

export const {
  useGetPayerFamiliesQuery,
  useGetPayerFamilyQuery,
  useLazyGetPayerFamilyQuery,
  useLazyGetPayerFamiliesQuery,
  useLazyGetPayerFamilyByNameQuery,
  useAddPayerFamilyMutation,
  useUpdatePayerFamilyMutation,
  useDeletePayerFamilyMutation,
  useGetChangeLogQuery,
  useLazyConvertPayerFamilyDataQuery,
  useConvertPayerFamilyDataQuery,
} = payerFamilyApi;
