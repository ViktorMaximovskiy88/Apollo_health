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
import { WorkItem, WorkItemOption as Option } from '../collections/types';
import { useState } from 'react';

const useWorkItem = (docId: string): WorkItem | undefined => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks } = useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  const { work_list: workList } = siteScrapeTask;
  const workItem = workList.find((item) => item.document_id === docId);
  return workItem;
};

const useWorkList = () => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks } = useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  const { work_list: workList } = siteScrapeTask;
  return workList;
};

const useSiteScrapeTaskId = () => {
  const { siteId } = useParams();
  const { data: siteScrapeTasks } = useGetScrapeTasksForSiteQuery(siteId);
  if (!siteScrapeTasks) return;
  const [siteScrapeTask] = siteScrapeTasks;
  return siteScrapeTask._id;
};

const FoundSelected = () => (
  <Button type="primary">
    <FileDoneOutlined className="text-white" />
  </Button>
);
const FoundUnselected = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => {
  const workList = useWorkList();
  const siteScrapeTaskId = useSiteScrapeTaskId();
  const [updateSiteScrapeTask] = useUpdateSiteScrapeTaskMutation();
  if (!siteScrapeTaskId || !workList) return null;
  const handleClick = async () => {
    const newWorkList = workList.map((item) => {
      if (item.document_id === docId) {
        return { ...item, selected: Option.Found };
      }
      return item;
    });
    setIsLoading(true);
    await updateSiteScrapeTask({ _id: siteScrapeTaskId, work_list: newWorkList });
    setIsLoading(false);
  };
  return (
    <Button onClick={handleClick}>
      <FileDoneOutlined />
    </Button>
  );
};
const FoundDisabled = () => (
  <Button disabled>
    <FileDoneOutlined />
  </Button>
);
const Found = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => {
  const workItem = useWorkItem(docId);
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.Found:
      return <FoundSelected />;
    case Option.NewDocument:
      return <FoundDisabled />;
    default:
      return <FoundUnselected docId={docId} setIsLoading={setIsLoading} />;
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
const NewDocument = ({ docId }: { docId: string }) => {
  const workItem = useWorkItem(docId);
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
const NotFoundUnselected = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => (
  <Button onClick={() => {}}>
    <FileExcelOutlined />
  </Button>
);
const NotFoundDisabled = () => (
  <Button disabled>
    <FileExcelOutlined />
  </Button>
);
const NotFound = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => {
  const workItem = useWorkItem(docId);
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.NotFound:
      return <NotFoundSelected />;
    case Option.NewDocument:
      return <NotFoundDisabled />;
    default:
      return <NotFoundUnselected docId={docId} setIsLoading={setIsLoading} />;
  }
};

export const NewVersion = ({
  doc,
  handleNewVersion,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
}) => (
  <Button>
    <FileExclamationOutlined onClick={() => handleNewVersion(doc)} />
  </Button>
);

const UnhandledSelected = () => (
  <Button type="primary">
    <FileUnknownOutlined className="text-white" />
  </Button>
);
const UnhandledUnselected = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => (
  <Button onClick={() => {}}>
    <FileUnknownOutlined />
  </Button>
);
const UnhandledDisabled = () => (
  <Button disabled>
    <FileUnknownOutlined />
  </Button>
);
const Unhandled = ({
  docId,
  setIsLoading,
}: {
  docId: string;
  setIsLoading: (isLoading: boolean) => void;
}) => {
  const workItem = useWorkItem(docId);
  if (!workItem) return null;
  switch (workItem.selected) {
    case Option.Unhandled:
      return <UnhandledSelected />;
    case Option.NewDocument:
      return <UnhandledDisabled />;
    default:
      return <UnhandledUnselected docId={docId} setIsLoading={setIsLoading} />;
  }
};

export function ValidationButtons({
  doc,
  handleNewVersion,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
}) {
  const [isLoading, setIsLoading] = useState(false);
  return (
    <div className="flex space-x-1">
      <Found docId={doc._id} setIsLoading={setIsLoading} />
      <NewDocument docId={doc._id} />
      <NotFound docId={doc._id} setIsLoading={setIsLoading} />
      <NewVersion doc={doc} handleNewVersion={handleNewVersion} />
      <Unhandled docId={doc._id} setIsLoading={setIsLoading} />
      <Spin spinning={isLoading} size="small" />
    </div>
  );
}
