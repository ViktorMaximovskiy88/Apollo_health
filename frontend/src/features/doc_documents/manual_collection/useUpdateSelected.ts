import { DateTime } from 'luxon';
import { useContext } from 'react';
import { useParams } from 'react-router-dom';
import {
  useGetScrapeTasksForSiteQuery,
  useUpdateSiteScrapeTaskMutation,
} from '../../collections/siteScrapeTasksApi';
import { SiteScrapeTask, WorkItemOption } from '../../collections/types';
import { initialState } from '../../collections/collectionsSlice';
import { ValidationButtonsContext } from './ManualCollectionContext';

const mostRecentTask = {
  limit: 1,
  skip: 0,
  sortInfo: initialState.table.sort,
  filterValue: initialState.table.filter,
};

const useSiteScrapeTaskId = () => {
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
  const { workList, refetch, docId, setIsLoading } = useContext(ValidationButtonsContext) ?? {};
  const siteScrapeTaskId = useSiteScrapeTaskId();
  const [updateSiteScrapeTask] = useUpdateSiteScrapeTaskMutation();

  return async (selected: WorkItemOption) => {
    if (!siteScrapeTaskId || !workList || !setIsLoading || !refetch) return;

    const newWorkList = workList.map((item) => {
      if (item.document_id === docId) {
        return { ...item, selected, action_datetime: DateTime.now().toISO() };
      }
      return item;
    }); // O(n^2) time, max n of 1500

    setIsLoading(true);
    await updateSiteScrapeTask({ _id: siteScrapeTaskId, work_list: newWorkList });
    refetch();
    setIsLoading(false);
  };
};
