import { createContext, ReactNode, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useGetScrapeTasksForSiteQuery } from '../../collections/siteScrapeTasksApi';
import { WorkItem } from '../../collections/types';
import { SiteDocDocument } from '../types';

export const ValidationButtonsContext = createContext<{
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  doc: SiteDocDocument;
  docId: string;
  workList?: WorkItem[];
  refetch: () => void;
  workItem?: WorkItem;
  handleNewVersion: (doc: SiteDocDocument) => void;
} | null>(null);

const useWorkList = (): { workList?: WorkItem[]; refetch: () => void } => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks, refetch } = useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return { refetch };
  const [siteScrapeTask] = siteScrapeTasks;
  const { work_list: workList } = siteScrapeTask;
  return { workList, refetch };
};

const useWorkItem = (docId: string): WorkItem | undefined => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks } = useGetScrapeTasksForSiteQuery(siteId);
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
  const { workList, refetch } = useWorkList();
  const workItem = useWorkItem(docId);
  const value = {
    isLoading,
    setIsLoading,
    doc,
    docId,
    workList,
    refetch,
    workItem,
    handleNewVersion,
  };
  return (
    <ValidationButtonsContext.Provider value={value}>{children}</ValidationButtonsContext.Provider>
  );
};
