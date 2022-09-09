import { useContext } from 'react';
import { useParams } from 'react-router-dom';
import {
  useGetScrapeTasksForSiteQuery,
  useUpdateSiteScrapeTaskMutation,
} from '../../collections/siteScrapeTasksApi';
import { SiteScrapeTask, WorkItemOption } from '../../collections/types';
import { ValidationButtonsContext } from './ManualCollectionContext';

const useSiteScrapeTaskId = () => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks }: { data?: SiteScrapeTask[] } =
    useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  return siteScrapeTask._id;
};

export const useUpdateSelected = (selected: WorkItemOption) => {
  const { workList, refetch, docId, setIsLoading } = useContext(ValidationButtonsContext) ?? {};
  const siteScrapeTaskId = useSiteScrapeTaskId();
  const [updateSiteScrapeTask] = useUpdateSiteScrapeTaskMutation();

  return async () => {
    if (!siteScrapeTaskId || !workList || !setIsLoading || !refetch) return;

    const newWorkList = workList.map((item) => {
      if (item.document_id === docId) {
        return { ...item, selected };
      }
      return item;
    }); // O(n^2) time, max n of 1500

    setIsLoading(true);
    await updateSiteScrapeTask({ _id: siteScrapeTaskId, work_list: newWorkList });
    refetch();
    setIsLoading(false);
  };
};
