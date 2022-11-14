import { createApi, fetchBaseQuery } from '../../app/base-api';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { ChangeLog } from '../change-log/types';
import { PayerBackbone } from './types';

export const payerBackboneApi = createApi({
  reducerPath: 'payerBackboneApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['PayerBackbone', 'ChangeLog'],
  endpoints: (builder) => ({
    getPayerBackboneByLId: builder.query<PayerBackbone, { id?: string; payerType: string }>({
      query: ({ id, payerType }) => `/payer-backbone/${payerType}/l/${id}`,
      providesTags: (_r, _e, { id, payerType }) => [
        { type: 'PayerBackbone', id: `${payerType}-${id}` },
      ],
    }),
    getPayerBackbone: builder.query<PayerBackbone, { payerType?: string; id: string | undefined }>({
      query: ({ payerType, id }) => `/payer-backbone/${payerType}/${id}`,
      providesTags: (_r, _e, { id }) => [{ type: 'PayerBackbone', id }],
    }),
    getPayerBackbones: builder.query<
      { data: PayerBackbone[]; total: number },
      {
        type: string;
        limit?: number;
        skip?: number;
        sortInfo?: TypeSortInfo;
        filterValue?: TypeFilterValue;
      }
    >({
      query: ({ type, limit, skip, sortInfo, filterValue }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const args = [];
        if (limit) {
          args.push(`limit=${encodeURIComponent(limit)}`);
        }
        if (skip) {
          args.push(`skip=${encodeURIComponent(skip)}`);
        }
        if (sorts) {
          args.push(`sorts=${encodeURIComponent(JSON.stringify(sorts))}`);
        }
        if (filterValue) {
          args.push(`filters=${encodeURIComponent(JSON.stringify(filterValue))}`);
        }
        return `/payer-backbone/${type}?${args.join('&')}`;
      },
    }),
    addPayerBackbone: builder.mutation<
      PayerBackbone,
      { payerType?: string; body: Partial<PayerBackbone> }
    >({
      query: ({ payerType, body }) => ({
        url: `/payer-backbone/${payerType}`,
        method: 'PUT',
        body,
      }),
      invalidatesTags: [{ type: 'PayerBackbone', id: 'LIST' }],
    }),
    updatePayerBackbone: builder.mutation<
      PayerBackbone,
      { payerType?: string; body: Partial<PayerBackbone> }
    >({
      query: ({ payerType, body }) => ({
        url: `/payer-backbone/${payerType}/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { body }) => [
        { type: 'PayerBackbone', id: body._id },
        { type: 'PayerBackbone', id: 'LIST' },
        { type: 'ChangeLog', id: body._id },
      ],
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useLazyGetPayerBackbonesQuery,
  useAddPayerBackboneMutation,
  useUpdatePayerBackboneMutation,
  useGetPayerBackbonesQuery,
  useGetPayerBackboneQuery,
  useLazyGetPayerBackboneQuery,
  useGetPayerBackboneByLIdQuery,
  useLazyGetPayerBackboneByLIdQuery,
  useGetChangeLogQuery,
} = payerBackboneApi;
