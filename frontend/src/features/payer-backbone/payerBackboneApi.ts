import { createApi, fetchBaseQuery } from '../../app/base-api';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { ChangeLog } from '../change-log/types';
import { PayerBackbone } from './types';

export const payerBackboneApi = createApi({
  reducerPath: 'payerBackboneApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['PayerBackbone', 'ChangeLog'],
  endpoints: (builder) => ({
    getPayerBackbone: builder.query<PayerBackbone, string | undefined>({
      query: (id) => `/payer-backbone/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'PayerBackbone', id }],
    }),
    getPayerBackbones: builder.query<
      { data: PayerBackbone[]; total: number },
      {
        type: string;
        limit: number;
        skip: number;
        sortInfo: TypeSortInfo;
        filterValue: TypeFilterValue;
      }
    >({
      query: ({ type, limit, skip, sortInfo, filterValue }) => {
        const sorts = sortInfo ? [sortInfo] : [];
        const args = [
          `type=${type}`,
          `limit=${encodeURIComponent(limit)}`,
          `skip=${encodeURIComponent(skip)}`,
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ].join('&');
        return `/payer-backbone/?${args}`;
      },
    }),
    addPayerBackbone: builder.mutation<PayerBackbone, Partial<PayerBackbone>>({
      query: (body) => ({ url: '/payer-backbone/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'PayerBackbone', id: 'LIST' }],
    }),
    updatePayerBackbone: builder.mutation<PayerBackbone, Partial<PayerBackbone>>({
      query: (body) => ({ url: `/payer-backbone/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'PayerBackbone', id },
        { type: 'PayerBackbone', id: 'LIST' },
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
  useLazyGetPayerBackbonesQuery,
  useAddPayerBackboneMutation,
  useUpdatePayerBackboneMutation,
  useGetPayerBackbonesQuery,
  useGetPayerBackboneQuery,
  useGetChangeLogQuery,
} = payerBackboneApi;
