import { Button, Spin, Tooltip } from 'antd';
import {
  FileAddOutlined,
  FileDoneOutlined,
  FileExcelOutlined,
  FileExclamationOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import { SiteDocDocument } from '../types';
import { WorkItemOption } from '../../collections/types';
import { useContext } from 'react';
import { ValidationButtonsContext, ValidationButtonsProvider } from './ManualCollectionContext';
import { useUpdateSelected } from './useUpdateSelected';
import { useParams } from 'react-router-dom';
import { useGetSiteQuery } from '../../sites/sitesApi';
import { TaskStatus } from '../../../common/scrapeTaskStatus';

const Found = () => {
  const updateSelected = useUpdateSelected();
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Button type="primary" onClick={() => updateSelected(WorkItemOption.Found)}>
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Found">
            <FileDoneOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.Found)}>
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button>
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Found">
            <FileDoneOutlined />
          </Tooltip>
        </Button>
      );
    default:
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.Found)}>
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button>
            <Tooltip placement="top" title="Found">
              <FileDoneOutlined />
            </Tooltip>
          </Button>
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
        <Button disabled>
          <Tooltip placement="top" title="New Document">
            <FileAddOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NewDocument:
      return (
        <Button type="primary">
          <Tooltip placement="top" title="New Document">
            <FileAddOutlined className="text-white" />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button disabled>
          <Tooltip placement="top" title="New Document">
            <FileAddOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <Tooltip placement="top" title="New Document">
            <FileAddOutlined />
          </Tooltip>
        </Button>
      );
    default:
      return (
        <Button disabled>
          <Tooltip placement="top" title="New Document">
            <FileAddOutlined />
          </Tooltip>
        </Button>
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
          <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button>
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Not Found">
            <FileExcelOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new || workItem.new_doc) {
        return (
          <Button type="primary" onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Not Found">
            <FileExcelOutlined />
          </Tooltip>
        </Button>
      );
    default:
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button>
            <Tooltip placement="top" title="Not Found">
              <FileExcelOutlined />
            </Tooltip>
          </Button>
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
          <Button
            onClick={() => {
              handleNewVersion(doc);
            }}
          >
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button disabled>
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <Tooltip placement="top" title="New Version">
            <FileExclamationOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new && workItem.is_current_version) {
        return (
          <Button
            onClick={() => {
              handleNewVersion(doc);
            }}
          >
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button disabled>
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
        );
      }
    case WorkItemOption.NewVersion:
      if (workItem.is_new && workItem.is_current_version) {
        return (
          <Button
            type="primary"
            onClick={() => {
              handleNewVersion(doc);
            }}
          >
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined className="text-white" />
            </Tooltip>
          </Button>
        );
      }
    default:
      if (workItem.is_new) {
        return (
          <Button
            onClick={() => {
              handleNewVersion(doc);
            }}
          >
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
        );
      } else {
        return (
          <Button>
            <Tooltip placement="top" title="New Version">
              <FileExclamationOutlined />
            </Tooltip>
          </Button>
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
        <Button disabled>
          <Tooltip placement="top" title="Unhandled">
            <FileUnknownOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Unhandled">
            <FileUnknownOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Unhandled">
            <FileUnknownOutlined />
          </Tooltip>
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <Tooltip placement="top" title="Unhandled">
            <FileUnknownOutlined />
          </Tooltip>
        </Button>
      );
    default:
      return (
        <Button type="primary">
          <Tooltip placement="top" title="Unhandled">
            <FileUnknownOutlined />
          </Tooltip>
        </Button>
      );
  }
};

function ValidationButtons() {
  const { isLoading } = useContext(ValidationButtonsContext) ?? {};
  const params = useParams();
  const siteId = params.siteId;
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const { data: site } = useGetSiteQuery(siteId);
  if (!site) return null;

  if (site.collection_method == 'MANUAL' && activeStatuses.includes(site.last_run_status)) {
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
