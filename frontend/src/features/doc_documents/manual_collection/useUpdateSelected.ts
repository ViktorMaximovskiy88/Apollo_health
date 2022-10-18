import { DateTime } from 'luxon';
import { useContext } from 'react';
import { useParams } from 'react-router-dom';
import {
  useGetScrapeTasksForSiteQuery,
  useLazyGetScrapeTasksForSiteQuery,
  useUpdateWorkItemMutation,
} from '../../collections/siteScrapeTasksApi';
import { SiteScrapeTask, WorkItemOption } from '../../collections/types';
import { initialState } from '../../collections/collectionsSlice';
import { ValidationButtonsContext } from './ManualCollectionContext';
import { useLazyGetSiteDocDocumentsQuery } from '../../sites/sitesApi';

const mostRecentTask = {
  limit: 1,
  skip: 0,
  sortInfo: initialState.table.sort,
  filterValue: initialState.table.filter,
};

export const useSiteScrapeTaskId = () => {
  const { siteId } = useParams();
  const { data }: { data?: { data?: SiteScrapeTask[] } } = useGetScrapeTasksForSiteQuery({
    ...mostRecentTask,
    siteId,
  });
  const siteScrapeTask = data?.data?.[0];
  if (!siteScrapeTask) return;
  return siteScrapeTask._id;
};

export const useUpdateSelected = () => {
  const { siteId } = useParams();
  const { workItem, setIsLoading } = useContext(ValidationButtonsContext) ?? {};
  const scrapeTaskId = useSiteScrapeTaskId();
  const [updateWorkItem] = useUpdateWorkItemMutation();
  const [getScrapeTasksForSiteQuery] = useLazyGetScrapeTasksForSiteQuery();
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();

  return async (selected: WorkItemOption) => {
    if (!scrapeTaskId || !workItem || !setIsLoading) return;
    const newWorkItem = { ...workItem, selected, action_datetime: DateTime.now().toISO() };

    setIsLoading(true);
    await updateWorkItem({ ...newWorkItem, scrapeTaskId });
    await getScrapeTasksForSiteQuery({ ...mostRecentTask, siteId });
    await getDocDocumentsQuery({ siteId, scrapeTaskId });
    setIsLoading(false);
  };
};
