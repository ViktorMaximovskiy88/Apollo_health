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
      return null;
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileDoneOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button onClick={() => updateSelected(WorkItemOption.Found)}>
          <FileDoneOutlined />
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileDoneOutlined />
        </Button>
      );
    default:
      return (
        <Button onClick={() => updateSelected(WorkItemOption.Found)}>
          <FileDoneOutlined />
        </Button>
      );
  }
};

const NewDocument = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return null;
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
      return null;
    case WorkItemOption.NewDocument:
      return (
        <Button disabled>
          <FileExcelOutlined />
        </Button>
      );
    case WorkItemOption.NotFound:
      return (
        <Button type="primary" onClick={() => updateSelected(WorkItemOption.NotFound)}>
          <FileExcelOutlined className="text-white" />
        </Button>
      );
    case WorkItemOption.NewVersion:
      return (
        <Button disabled>
          <FileExcelOutlined />
        </Button>
      );
    default:
      return (
        <Button onClick={() => updateSelected(WorkItemOption.NotFound)}>
          <FileExcelOutlined />
        </Button>
      );
  }
};

const NewVersion = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  const updateSelected = useUpdateSelected();
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return null;
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
    default:
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
  }
};

const Unhandled = () => {
  const { doc, handleNewVersion } = useContext(ValidationButtonsContext) ?? {};
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case WorkItemOption.Found:
      return null;
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
