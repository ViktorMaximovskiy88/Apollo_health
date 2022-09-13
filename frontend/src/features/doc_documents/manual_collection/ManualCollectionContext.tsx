import { createContext, ReactNode, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useGetScrapeTasksForSiteQuery } from '../../collections/siteScrapeTasksApi';
import { SiteScrapeTask, WorkItem } from '../../collections/types';
import { SiteDocDocument } from '../types';
import { initialState } from '../../collections/collectionsSlice';

const mostRecentTask = {
  limit: 1,
  skip: 0,
  sortInfo: initialState.table.sort,
  filterValue: initialState.table.filter,
};

export const ValidationButtonsContext = createContext<{
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  doc: SiteDocDocument;
  docId: string;
  workList?: WorkItem[];
  workItem?: WorkItem;
  handleNewVersion: (doc: SiteDocDocument) => void;
} | null>(null);

const useWorkList = (): { workList?: WorkItem[] } => {
  const { siteId } = useParams();
  const { data }: { data?: { data?: SiteScrapeTask[] } } = useGetScrapeTasksForSiteQuery({
    ...mostRecentTask,
    siteId,
  });
  const siteScrapeTask = data?.data?.[0];
  if (!siteScrapeTask) return {};
  const { work_list: workList } = siteScrapeTask;
  return { workList };
};

const useWorkItem = (docId: string): WorkItem | undefined => {
  const { siteId } = useParams();
  const { data }: { data?: { data?: SiteScrapeTask[] } } = useGetScrapeTasksForSiteQuery({
    ...mostRecentTask,
    siteId,
  });
  const siteScrapeTasks = data?.data;
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  const { work_list: workList } = siteScrapeTask;
  const workItem = workList.find((item) => item.document_id === docId);
  return workItem;
};

export const ValidationButtonsProvider = ({
  doc,
  handleNewVersion,
  children,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
  children: ReactNode;
}) => {
  const docId = doc._id;
  const [isLoading, setIsLoading] = useState(false);
  const { workList } = useWorkList();
  const workItem = useWorkItem(docId);
  const value = {
    isLoading,
    setIsLoading,
    doc,
    docId,
    workList,
    workItem,
    handleNewVersion,
  };
  return (
    <ValidationButtonsContext.Provider value={value}>{children}</ValidationButtonsContext.Provider>
  );
};
