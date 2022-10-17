import { Button, Spin } from 'antd';
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

const Found = () => {
  const updateSelected = useUpdateSelected();
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new) {
        return (
          <Button type="primary" onClick={() => updateSelected(WorkItemOption.Found)}>
            <FileDoneOutlined className="text-white" />
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <FileDoneOutlined className="text-white" />
          </Button>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileDoneOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.Found)}>
            <FileDoneOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileDoneOutlined />
          </Button>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileDoneOutlined />
        </Button>
      );
    default:
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.Found)}>
            <FileDoneOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileDoneOutlined />
          </Button>
        );
      }
  }
};

const NewDocument = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return (
        <Button disabled>
          <FileAddOutlined />
        </Button>
      );
    case WorkItemOption.NewDocument:
      return (
        <Button type="primary">
          <FileAddOutlined className="text-white" />
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button disabled>
          <FileAddOutlined />
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileAddOutlined />
        </Button>
      );
    default:
      return (
        <Button disabled>
          <FileAddOutlined />
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
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <FileExcelOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileExcelOutlined />
          </Button>
        );
      }
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileExcelOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      if (workItem.is_new) {
        return (
          <Button type="primary" onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <FileExcelOutlined className="text-white" />
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <FileExcelOutlined className="text-white" />
          </Button>
        );
      }
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileExcelOutlined />
        </Button>
      );
    default:
      if (workItem.is_new) {
        return (
          <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
            <FileExcelOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileExcelOutlined />
          </Button>
        );
      }
  }
};

const NewVersion = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  const updateSelected = useUpdateSelected();
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      if (workItem.is_new) {
        return (
          <Button
            onClick={() => {
              handleNewVersion(doc);
              updateSelected(WorkItemOption.NewVersion);
            }}
          >
            <FileExclamationOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileExclamationOutlined />
          </Button>
        );
      }
    case WorkItemOption.Found:
      return (
        <Button disabled>
          <FileExclamationOutlined />
        </Button>
      );
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileExclamationOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button disabled>
          <FileExclamationOutlined />
        </Button>
      );
    case WorkItemOption.NewVersion:
      if (workItem.is_new) {
        return (
          <Button
            type="primary"
            onClick={() => {
              handleNewVersion(doc);
              updateSelected(WorkItemOption.NewVersion);
            }}
          >
            <FileExclamationOutlined className="text-white" />
          </Button>
        );
      } else {
        return (
          <Button type="primary">
            <FileExclamationOutlined className="text-white" />
          </Button>
        );
      }
    default:
      if (workItem.is_new) {
        return (
          <Button
            onClick={() => {
              handleNewVersion(doc);
              updateSelected(WorkItemOption.NewVersion);
            }}
          >
            <FileExclamationOutlined />
          </Button>
        );
      } else {
        return (
          <Button>
            <FileExclamationOutlined />
          </Button>
        );
      }
  }
};

const Unhandled = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
    default:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
  }
};

function ValidationButtons() {
  const { isLoading } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;
  if (workItem.selected == WorkItemOption.Found && workItem.is_new === false) {
    return null;
  } else {
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
