import { Button, Spin } from 'antd';
import {
  FileAddOutlined,
  FileDoneOutlined,
  FileExcelOutlined,
  FileExclamationOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import { SiteDocDocument } from './types';
import {
  useGetScrapeTasksForSiteQuery,
  useUpdateSiteScrapeTaskMutation,
} from '../collections/siteScrapeTasksApi';
import { useParams } from 'react-router-dom';
import {
  SiteScrapeTask,
  WorkItem,
  WorkItemOption as Option,
  WorkItemOption,
} from '../collections/types';
import { createContext, useState, ReactNode, useContext } from 'react';

const ValidationButtonsContext = createContext<{
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  doc: SiteDocDocument;
  docId: string;
  workList?: WorkItem[];
  refetch: () => void;
  workItem?: WorkItem;
  handleNewVersion: (doc: SiteDocDocument) => void;
} | null>(null);

const useSiteScrapeTaskId = () => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks }: { data?: SiteScrapeTask[] } =
    useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  return siteScrapeTask._id;
};

const useUpdateSelected = (selected: WorkItemOption) => {
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

const FoundSelected = () => (
  <Button type="primary">
    <FileDoneOutlined className="text-white" />
  </Button>
);
const FoundUnselected = () => {
  const updateSelected = useUpdateSelected(WorkItemOption.Found);
  return (
    <Button onClick={updateSelected}>
      <FileDoneOutlined />
    </Button>
  );
};
const FoundDisabled = () => (
  <Button disabled>
    <FileDoneOutlined />
  </Button>
);
const Found = () => {
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.Found:
      return <FoundSelected />;
    case Option.NewDocument:
      return <FoundDisabled />;
    default:
      return <FoundUnselected />;
  }
};

const NewDocumentSelected = () => (
  <Button type="primary" disabled>
    <FileAddOutlined className="text-white" />
  </Button>
);
const NewDocumentDisabled = () => (
  <Button disabled>
    <FileAddOutlined />
  </Button>
);
const NewDocument = () => {
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.NewDocument:
      return <NewDocumentSelected />;
    default:
      return <NewDocumentDisabled />;
  }
};

const NotFoundSelected = () => (
  <Button type="primary">
    <FileExcelOutlined className="text-white" />
  </Button>
);
const NotFoundUnselected = () => {
  const updateSelected = useUpdateSelected(WorkItemOption.NotFound);
  return (
    <Button onClick={updateSelected}>
      <FileExcelOutlined />
    </Button>
  );
};
const NotFoundDisabled = () => (
  <Button disabled>
    <FileExcelOutlined />
  </Button>
);
const NotFound = () => {
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.NotFound:
      return <NotFoundSelected />;
    case Option.NewDocument:
      return <NotFoundDisabled />;
    default:
      return <NotFoundUnselected />;
  }
};

const NewVersion = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  if (!doc || !handleNewVersion) return null;
  return (
    <Button>
      <FileExclamationOutlined onClick={() => handleNewVersion(doc)} />
    </Button>
  );
};

const UnhandledSelected = () => (
  <Button type="primary">
    <FileUnknownOutlined className="text-white" />
  </Button>
);
const UnhandledUnselected = () => {
  const updateSelected = useUpdateSelected(WorkItemOption.Unhandled);
  return (
    <Button onClick={updateSelected}>
      <FileUnknownOutlined />
    </Button>
  );
};
const UnhandledDisabled = () => (
  <Button disabled>
    <FileUnknownOutlined />
  </Button>
);
const Unhandled = () => {
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.Unhandled:
      return <UnhandledSelected />;
    case Option.NewDocument:
      return <UnhandledDisabled />;
    default:
      return <UnhandledUnselected />;
  }
};

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

const ValidationButtonsProvider = ({
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

function ValidationButtons() {
  const { isLoading } = useContext(ValidationButtonsContext) ?? {};
  return (
    <div className="flex space-x-1">
      <Found />
      <NewDocument />
      <NotFound />
      <NewVersion />
      <Unhandled />
      <Spin spinning={isLoading ?? false} size="small" className="pl-3 pt-2" />
    </div>
  );
}

export function ManualCollectionValidationButtons({
  doc,
  handleNewVersion,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
}) {
  return (
    <ValidationButtonsProvider doc={doc} handleNewVersion={handleNewVersion}>
      <ValidationButtons />
    </ValidationButtonsProvider>
  );
}
