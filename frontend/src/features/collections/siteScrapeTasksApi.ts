import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { BulkActionTypes, SiteScrapeTask, CollectionConfig } from './types';
import { TableInfoType } from '../../common/types';

interface BulkRunResponse {
  type: BulkActionTypes;
  scrapes: number;
  sites: number;
}

export const siteScrapeTasksApi = createApi({
  reducerPath: 'siteScrapeTasksApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['SiteScrapeTask', 'ChangeLog'],
  endpoints: (builder) => ({
    getCollectionConfig: builder.query<{ data: CollectionConfig }, {}>({
      query: (type) => `/site-scrape-tasks/config?key=${type}`,
    }),
    getScrapeTasksForSite: builder.query<
      { data: SiteScrapeTask[]; total: number },
      Partial<TableInfoType>
    >({
      query: ({ limit, siteId, skip, filterValue, sortInfo }) => {
        const args = [];
        if (siteId) {
          args.push(`site_id=${encodeURIComponent(siteId)}`);
        }
        if (skip != null) {
          args.push(`skip=${encodeURIComponent(skip)}`);
        }
        if (limit) {
          args.push(`limit=${encodeURIComponent(limit)}`);
        }
        if (sortInfo) {
          args.push(`sorts=${encodeURIComponent(JSON.stringify([sortInfo]))}`);
        }
        if (filterValue) {
          args.push(`filters=${encodeURIComponent(JSON.stringify(filterValue))}`);
        }
        return `/site-scrape-tasks/?${args.join('&')}`;
      },
      providesTags: (results) => {
        const tags = [{ type: 'SiteScrapeTask' as const, id: 'LIST' }];
        results?.data.forEach(({ _id: id }) => tags.push({ type: 'SiteScrapeTask', id }));
        return tags;
      },
    }),

    runSiteScrapeTask: builder.mutation<SiteScrapeTask, string>({
      query: (siteId) => ({
        url: `/site-scrape-tasks/?site_id=${siteId}`,
        method: 'PUT',
      }),
      invalidatesTags: (_r, _e, id) => [{ type: 'SiteScrapeTask', id }],
    }),
    updateSiteScrapeTask: builder.mutation<SiteScrapeTask, Partial<SiteScrapeTask>>({
      query: (body) => ({
        url: `/site-scrape-tasks/${body._id}`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'SiteScrapeTask', id },
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
        { type: 'SiteScrapeTask', id },
        { type: 'ChangeLog', id },
      ],
    }),
    cancelSiteScrapeTask: builder.mutation<SiteScrapeTask, string | undefined>({
      query: (siteTaskId) => ({
        url: `/site-scrape-tasks/${siteTaskId}/cancel`,
        method: 'POST',
      }),
      invalidatesTags: (_r, _e, id) => [
        { type: 'SiteScrapeTask', id },
        { type: 'ChangeLog', id },
      ],
    }),
    cancelAllSiteScrapeTasks: builder.mutation<SiteScrapeTask, string | undefined>({
      query: (siteId) => ({
        url: `/site-scrape-tasks/cancel-all?site_id=${siteId}`,
        method: 'POST',
      }),
      invalidatesTags: (_r, _e, id) => [{ type: 'SiteScrapeTask', id }],
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
  useGetChangeLogQuery,
  useRunBulkMutation,
  useGetCollectionConfigQuery,
  endpoints,
} = siteScrapeTasksApi;
