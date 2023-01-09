import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { BulkActionTypes, SiteScrapeTask, CollectionConfig, WorkItem } from './types';
import { TableInfoType } from '../../common/types';
import { makeTableQueryParams } from '../../common/helpers';
import { FetchBaseQueryError } from '@reduxjs/toolkit/dist/query';

interface BulkRunResponse {
  type: BulkActionTypes;
  scrapes: number;
  sites: number;
}

export const siteScrapeTasksApi = createApi({
  reducerPath: 'siteScrapeTasksApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['SiteScrapeTask', 'ChangeLog', 'DocDocument', 'SiteDocDocument'],
  endpoints: (builder) => ({
    getCollectionConfig: builder.query<{ data: CollectionConfig }, void>({
      query: () => `/app-config/?key=collections`,
    }),
    getScrapeTasksForSite: builder.query<{ data: SiteScrapeTask[]; total: number }, TableInfoType>({
      query: ({ siteId, ...queryArgs }) => {
        const args = makeTableQueryParams(queryArgs, { site_id: siteId });
        return `/site-scrape-tasks/?${args.join('&')}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'SiteScrapeTask' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'SiteScrapeTask', id }));
        return tags;
      },
    }),
    getScrapeTask: builder.query<SiteScrapeTask, string | null | undefined>({
      async queryFn(search_query, queryApi, extraOptions, fetchWithBQ) {
        const params = { search_query };
        const result = await fetchWithBQ({ url: `/site-scrape-tasks/search`, params });
        return result.data
          ? { data: result.data as SiteScrapeTask }
          : { error: result.error as FetchBaseQueryError };
      },
    }),
    runSiteScrapeTask: builder.mutation<SiteScrapeTask, string>({
      query: (siteId) => ({
        url: `/site-scrape-tasks/?site_id=${siteId}`,
        method: 'PUT',
      }),
      invalidatesTags: (_r, _e, id) => ['SiteScrapeTask', 'DocDocument', 'SiteDocDocument'],
    }),
    updateSiteScrapeTask: builder.mutation<SiteScrapeTask, Partial<SiteScrapeTask>>({
      query: (body) => ({
        url: `/site-scrape-tasks/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        'SiteScrapeTask',
        'DocDocument',
        'SiteDocDocument',
        { type: 'ChangeLog', id },
      ],
    }),
    deleteSiteScrapeTask: builder.mutation<
      void,
      Pick<SiteScrapeTask, '_id'> & Partial<SiteScrapeTask>
    >({
      query: ({ _id: id }) => ({
        url: `/site-scrape-tasks/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        'SiteScrapeTask',
        'DocDocument',
        'SiteDocDocument',
        { type: 'ChangeLog', id },
      ],
    }),
    cancelSiteScrapeTask: builder.mutation<SiteScrapeTask, string | undefined>({
      query: (siteTaskId) => ({
        url: `/site-scrape-tasks/${siteTaskId}/cancel`,
        method: 'POST',
      }),
      invalidatesTags: (_r, _e, id) => [
        'SiteScrapeTask',
        'DocDocument',
        'SiteDocDocument',
        { type: 'ChangeLog', id },
      ],
    }),
    cancelAllSiteScrapeTasks: builder.mutation<SiteScrapeTask, string | undefined>({
      query: (siteId) => ({
        url: `/site-scrape-tasks/cancel-all?site_id=${siteId}`,
        method: 'POST',
      }),
      invalidatesTags: (_r, _e, id) => ['SiteScrapeTask', 'DocDocument', 'SiteDocDocument'],
    }),
    updateWorkItem: builder.mutation<SiteScrapeTask, WorkItem & { scrapeTaskId: string }>({
      query: (body) => ({
        url: `/site-scrape-tasks/${body.scrapeTaskId}/work-items/${body.document_id}`,
        method: 'POST',
        body,
      }),
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
    runBulk: builder.mutation<BulkRunResponse, string>({
      query: (type) => ({
        url: `/site-scrape-tasks/bulk-run?type=${type}`,
        method: 'POST',
      }),
      invalidatesTags: (_r, _e, id) => [{ type: 'SiteScrapeTask', id }],
    }),
  }),
});

export const {
  useGetScrapeTasksForSiteQuery,
  useLazyGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
  useUpdateSiteScrapeTaskMutation,
  useDeleteSiteScrapeTaskMutation,
  useCancelSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
  useUpdateWorkItemMutation,
  useGetChangeLogQuery,
  useRunBulkMutation,
  useGetCollectionConfigQuery,
  useGetScrapeTaskQuery,
  useLazyGetScrapeTaskQuery,
} = siteScrapeTasksApi;
