import { createContext, ReactNode, useContext, useState } from 'react';
import { SiteScrapeTask, WorkItem } from '../../collections/types';
import { SiteDocDocument } from '../types';

export const ValidationButtonsContext = createContext<{
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  doc: SiteDocDocument;
  docId: string;
  workList?: WorkItem[];
  workItem?: WorkItem;
  handleNewVersion: (doc: SiteDocDocument) => void;
  showValidationButtons: boolean;
  siteScrapeTask: SiteScrapeTask | undefined;
} | null>(null);

const useWorkList = (siteScrapeTask: SiteScrapeTask | undefined): { workList?: WorkItem[] } => {
  if (!siteScrapeTask) return {};
  const { work_list: workList } = siteScrapeTask;

  return { workList };
};

const useWorkItem = (
  docId: string,
  siteScrapeTask: SiteScrapeTask | undefined
): WorkItem | undefined => {
  if (!siteScrapeTask || !('work_list' in siteScrapeTask)) return;
  const { work_list: workList } = siteScrapeTask;
  const workItem = workList.find((item) => item.document_id === docId);

  return workItem;
};

export const ValidationButtonsProvider = ({
  doc,
  handleNewVersion,
  showValidationButtons,
  children,
  siteScrapeTask,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
  showValidationButtons: boolean;
  children: ReactNode;
  siteScrapeTask: SiteScrapeTask | undefined;
}) => {
  const docId = doc._id;
  const [isLoading, setIsLoading] = useState(false);
  const { workList } = useWorkList(siteScrapeTask);
  const workItem = useWorkItem(docId, siteScrapeTask);
  const value = {
    isLoading,
    setIsLoading,
    doc,
    docId,
    workList,
    workItem,
    handleNewVersion,
    showValidationButtons,
    siteScrapeTask,
  };

  return (
    <ValidationButtonsContext.Provider value={value}>{children}</ValidationButtonsContext.Provider>
  );
};
