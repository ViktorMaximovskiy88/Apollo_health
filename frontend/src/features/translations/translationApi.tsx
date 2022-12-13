import { createApi, fetchBaseQuery } from '../../app/base-api';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { ChangeLog } from '../change-log/types';
import { TranslationConfig } from './types';
import { makeTableQueryParams } from '../../common/helpers';

export const translationsApi = createApi({
  reducerPath: 'translationsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Translation', 'ChangeLog'],
  endpoints: (builder) => ({
    getTranslationConfig: builder.query<TranslationConfig, string | undefined>({
      query: (id) => `/translations/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'Translation', id }],
    }),
    getTranslationConfigs: builder.query<
      { data: TranslationConfig[]; total: number },
      {
        limit: number;
        skip: number;
        sortInfo: TypeSortInfo;
        filterValue: TypeFilterValue;
      }
    >({
      query: (queryArgs) => {
        return `/translations/?${makeTableQueryParams(queryArgs).join('&')}`;
      },
      providesTags: [{ type: 'Translation', id: 'LIST' }],
    }),
    getTranslationConfigByName: builder.query<TranslationConfig, string>({
      query: (name) => `/translations/search?name=${name}`,
      providesTags: (_r, _e, name) => [{ type: 'Translation' as const, name }],
    }),
    addTranslationConfig: builder.mutation<TranslationConfig, Partial<TranslationConfig>>({
      query: (body) => ({ url: '/translations/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'Translation', id: 'LIST' }],
    }),
    updateTranslationConfig: builder.mutation<TranslationConfig, Partial<TranslationConfig>>({
      query: (body) => ({ url: `/translations/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'Translation', id },
        { type: 'Translation', id: 'LIST' },
        { type: 'ChangeLog', id },
      ],
    }),
    extractSampleDocumentTables: builder.query<any[][][], TranslationConfig>({
      query: (config) => {
        const configStr = encodeURIComponent(JSON.stringify(config));
        return `/translations/sample-doc/${config.sample.doc_id}/extract?config=${configStr}`;
      },
    }),
    translateSampleDocumentTables: builder.query<any[], TranslationConfig>({
      query: (config) => {
        const configStr = encodeURIComponent(JSON.stringify(config));
        return `/translations/sample-doc/${config.sample.doc_id}/translate?config=${configStr}`;
      },
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useLazyGetTranslationConfigsQuery,
  useTranslateSampleDocumentTablesQuery,
  useGetTranslationConfigByNameQuery,
  useLazyGetTranslationConfigByNameQuery,
  useExtractSampleDocumentTablesQuery,
  useAddTranslationConfigMutation,
  useUpdateTranslationConfigMutation,
  useGetTranslationConfigsQuery,
  useGetTranslationConfigQuery,
  useGetChangeLogQuery,
} = translationsApi;
