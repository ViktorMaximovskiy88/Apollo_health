import { DateTime } from 'luxon';
import { useContext } from 'react';
import { useParams } from 'react-router-dom';
import {
  useLazyGetScrapeTaskQuery,
  useUpdateWorkItemMutation,
} from '../../collections/siteScrapeTasksApi';
import { WorkItemOption } from '../../collections/types';
import { ValidationButtonsContext } from './ManualCollectionContext';
import { useLazyGetSiteDocDocumentsQuery } from '../../sites/sitesApi';

export const useUpdateSelected = () => {
  const { siteId } = useParams();
  const { workItem, setIsLoading, siteScrapeTask, setSiteScrapeTask } =
    useContext(ValidationButtonsContext) ?? {};
  const scrapeTaskId = siteScrapeTask?._id;
  const [updateWorkItem] = useUpdateWorkItemMutation();
  const [getScrapeTaskQuery] = useLazyGetScrapeTaskQuery();
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();

  return async (selected: WorkItemOption) => {
    if (!scrapeTaskId || !workItem || !setIsLoading) return;
    const newWorkItem = { ...workItem, selected, action_datetime: DateTime.now().toISO() };
    setIsLoading(true);

    await updateWorkItem({ ...newWorkItem, scrapeTaskId });
    await getDocDocumentsQuery({ siteId, scrapeTaskId });

    // Since work_list stored in siteScrapeTask, need to refresh siteScrapeTask.
    // Otherwise, option will not change on frontend.
    const { data: refreshedSiteScrapeTask } = await getScrapeTaskQuery(scrapeTaskId);
    if (refreshedSiteScrapeTask && setSiteScrapeTask) {
      setSiteScrapeTask(refreshedSiteScrapeTask);
    }

    setIsLoading(false);
  };
};
