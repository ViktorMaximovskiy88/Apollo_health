import { Button, Spin, Tooltip } from 'antd';
import {
  FileAddOutlined,
  FileDoneOutlined,
  FileExcelOutlined,
  FileExclamationOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import { SiteDocDocument } from '../types';
import { SiteScrapeTask, WorkItemOption } from '../../collections/types';
import { useContext, useState } from 'react';
import { ValidationButtonsContext, ValidationButtonsProvider } from './ManualCollectionContext';
import { useUpdateSelected } from './useUpdateSelected';
import { useParams, useSearchParams } from 'react-router-dom';
import { useGetSiteQuery } from '../../sites/sitesApi';
import { TaskStatus } from '../../../common/scrapeTaskStatus';
import { useGetScrapeTasksForSiteQuery } from '../../collections/siteScrapeTasksApi';
import { initialState } from '../../collections/collectionsSlice';

const Found = () => {
  const updateSelected = useUpdateSelected();
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Tooltip placement="top" title="Found">
            <Button type="primary" onClick={() => updateSelected(WorkItemOption.Found)}>
              <FileDoneOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Found">
            <Button type="primary">
              <FileDoneOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Tooltip placement="top" title="Found">
          <Button disabled>
            <FileDoneOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Tooltip placement="top" title="Found">
            <Button onClick={() => updateSelected(WorkItemOption.Found)}>
              <FileDoneOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Found">
            <Button>
              <FileDoneOutlined />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Tooltip placement="top" title="Found">
          <Button disabled>
            <FileDoneOutlined />
          </Button>
        </Tooltip>
      );
    default:
      if (workItem.is_new) {
        return (
          <Tooltip placement="top" title="Found">
            <Button onClick={() => updateSelected(WorkItemOption.Found)}>
              <FileDoneOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Found">
            <Button>
              <FileDoneOutlined />
            </Button>
          </Tooltip>
        );
      }
  }
};

const NewDocument = () => {
  const { doc, handleNewVersion, workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return (
        <Tooltip placement="top" title="New Document">
          <Button disabled>
            <FileAddOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NewDocument:
      return (
        <Tooltip placement="top" title="New Document">
          <Button type="primary">
            <FileAddOutlined className="text-white" />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NotFound:
      return (
        <Tooltip placement="top" title="New Document">
          <Button disabled>
            <FileAddOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NewVersion:
      return (
        <Tooltip placement="top" title="New Document">
          <Button disabled>
            <FileAddOutlined />
          </Button>
        </Tooltip>
      );
    default:
      return (
        <Tooltip placement="top" title="New Document">
          <Button disabled>
            <FileAddOutlined />
          </Button>
        </Tooltip>
      );
  }
};

const NotFound = () => {
  const updateSelected = useUpdateSelected();
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
              <FileExcelOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button>
              <FileExcelOutlined />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Tooltip placement="top" title="Not Found">
          <Button disabled>
            <FileExcelOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button type="primary" onClick={() => updateSelected(WorkItemOption.NotFound)}>
              <FileExcelOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button type="primary">
              <FileExcelOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Tooltip placement="top" title="Not Found">
          <Button disabled>
            <FileExcelOutlined />
          </Button>
        </Tooltip>
      );
    default:
      if (workItem.is_new) {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
              <FileExcelOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="Not Found">
            <Button>
              <FileExcelOutlined />
            </Button>
          </Tooltip>
        );
      }
  }
};

const NewVersion = () => {
  const { doc, handleNewVersion, workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new && workItem.is_current_version) {
        return (
          <Tooltip placement="top" title="New Version">
            <Button
              onClick={() => {
                handleNewVersion(doc);
              }}
            >
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="New Version">
            <Button disabled>
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Tooltip placement="top" title="New Version">
          <Button disabled>
            <FileExclamationOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new && workItem.is_current_version) {
        return (
          <Tooltip placement="top" title="New Version">
            <Button
              onClick={() => {
                handleNewVersion(doc);
              }}
            >
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="New Version">
            <Button disabled>
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      }
    case WorkItemOption.NewVersion:
      if (workItem.is_new && workItem.is_current_version) {
        return (
          <Tooltip placement="top" title="New Version">
            <Button
              type="primary"
              onClick={() => {
                handleNewVersion(doc);
              }}
            >
              <FileExclamationOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="New Version">
            <Button type="primary">
              <FileExclamationOutlined className="text-white" />
            </Button>
          </Tooltip>
        );
      }
    default:
      if (workItem.is_new) {
        return (
          <Tooltip placement="top" title="New Version">
            <Button
              onClick={() => {
                handleNewVersion(doc);
              }}
            >
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      } else {
        return (
          <Tooltip placement="top" title="New Version">
            <Button>
              <FileExclamationOutlined />
            </Button>
          </Tooltip>
        );
      }
  }
};

const Unhandled = () => {
  const { doc, handleNewVersion, workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return (
        <Tooltip placement="top" title="Unhandled">
          <Button disabled>
            <FileUnknownOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NewDocument:
      return (
        <Tooltip placement="top" title="Unhandled">
          <Button disabled>
            <FileUnknownOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NotFound:
      return (
        <Tooltip placement="top" title="Unhandled">
          <Button disabled>
            <FileUnknownOutlined />
          </Button>
        </Tooltip>
      );
    case WorkItemOption.NewVersion:
      return (
        <Tooltip placement="top" title="Unhandled">
          <Button disabled>
            <FileUnknownOutlined />
          </Button>
        </Tooltip>
      );
    default:
      return (
        <Tooltip placement="top" title="Unhandled">
          <Button type="primary">
            <FileUnknownOutlined />
          </Button>
        </Tooltip>
      );
  }
};

function ValidationButtons() {
  const { isLoading, showValidationButtons } = useContext(ValidationButtonsContext) ?? {};

  if (showValidationButtons) {
    return (
      <div className="flex space-x-1">
        <Found />
        <NewDocument />
        <NotFound />
        <NewVersion />
        <Unhandled />
        <Spin spinning={isLoading} size="small" className="pl-3 pt-2" />
      </div>
    );
  } else {
    return null;
  }
}

export function ManualCollectionValidationButtons({
  doc,
  handleNewVersion,
  siteScrapeTask,
}: {
  doc: SiteDocDocument;
  handleNewVersion: (doc: SiteDocDocument) => void;
  siteScrapeTask: SiteScrapeTask | undefined;
}) {
  const [showValidationButtons, setShowValidationButtons] = useState(false);
  const params = useParams();
  const siteId = params.siteId;
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const { data: site } = useGetSiteQuery(siteId);
  if (!site) return null;
  if (
    siteScrapeTask?.collection_method === 'MANUAL' &&
    activeStatuses.includes(siteScrapeTask.status)
  ) {
    if (!showValidationButtons) {
      setShowValidationButtons(true);
    }
  } else {
    if (showValidationButtons === true) {
      setShowValidationButtons(false);
    }
  }

  return (
    <ValidationButtonsProvider
      doc={doc}
      handleNewVersion={handleNewVersion}
      showValidationButtons={showValidationButtons}
      siteScrapeTask={siteScrapeTask}
    >
      <ValidationButtons />
    </ValidationButtonsProvider>
  );
}
