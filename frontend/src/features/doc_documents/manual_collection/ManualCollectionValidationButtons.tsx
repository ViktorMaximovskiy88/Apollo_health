import { Button, Spin } from 'antd';
import {
  FileAddOutlined,
  FileDoneOutlined,
  FileExcelOutlined,
  FileExclamationOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import { SiteDocDocument } from '../types';
import { WorkItemOption as Option, WorkItemOption } from '../../collections/types';
import { useContext } from 'react';
import { ValidationButtonsContext, ValidationButtonsProvider } from './ManualCollectionContext';
import { useUpdateSelected } from './useUpdateSelected';

const Found = () => {
  const updateSelected = useUpdateSelected();

  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.Found:
      return (
        <Button type="primary" onClick={() => updateSelected(WorkItemOption.Unhandled)}>
          <FileDoneOutlined className="text-white" />
        </Button>
      );
    case Option.NewDocument:
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
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.NewDocument:
      return (
        <Button type="primary" disabled>
          <FileAddOutlined className="text-white" />
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
    case Option.NotFound:
      return (
        <Button type="primary" onClick={() => updateSelected(WorkItemOption.Unhandled)}>
          <FileExcelOutlined className="text-white" />
        </Button>
      );
    case Option.NewDocument:
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
  if (!workItem || !doc || !handleNewVersion) return null;

  switch (workItem.selected) {
    case Option.NewVersion:
      return (
        <Button type="primary">
          <FileExclamationOutlined onClick={() => handleNewVersion(doc)} />
        </Button>
      );
    default:
      return (
        <Button>
          <FileExclamationOutlined onClick={() => handleNewVersion(doc)} />
        </Button>
      );
  }
};

const Unhandled = () => {
  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.Unhandled:
      return (
        <Button type="primary" className="cursor-not-allowed">
          <FileUnknownOutlined className="text-white" />
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
