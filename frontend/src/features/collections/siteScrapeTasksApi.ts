import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { SiteScrapeTask } from './types';

export const siteScrapeTasksApi = createApi({
  reducerPath: 'siteScrapeTasksApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['SiteScrapeTask', 'ChangeLog'],
  endpoints: (builder) => ({
    getScrapeTasksForSite: builder.query<SiteScrapeTask[], string | undefined>({
      query: (siteId) => `/site-scrape-tasks/?site_id=${siteId}`,
      providesTags: (_r, _e, id) => [{ type: 'SiteScrapeTask' as const, id }],
    }),
    runSiteScrapeTask: builder.mutation<SiteScrapeTask, string>({
      query: (siteId) => ({
        url: `/site-scrape-tasks/?site_id=${siteId}`,
        method: 'PUT',
      }),
      invalidatesTags: (_r, _e, id) => [{ type: 'SiteScrapeTask', id }],
    }),
    updateSiteScrapeTask: builder.mutation<
      SiteScrapeTask,
      Partial<SiteScrapeTask>
    >({
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
      invalidatesTags: (_r, _e, id) => [
        { type: 'SiteScrapeTask', id }
      ],
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
    runBulk: builder.mutation<SiteScrapeTask, string>({
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
  useRunSiteScrapeTaskMutation,
  useUpdateSiteScrapeTaskMutation,
  useDeleteSiteScrapeTaskMutation,
  useCancelSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
  useGetChangeLogQuery,
  useRunBulkMutation,
} = siteScrapeTasksApi;
