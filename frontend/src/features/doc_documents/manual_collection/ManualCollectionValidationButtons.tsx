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
  const updateSelected = useUpdateSelected(WorkItemOption.Found);

  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.Found:
      return (
        <Button type="primary">
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
        <Button onClick={updateSelected}>
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
  const updateSelected = useUpdateSelected(WorkItemOption.NotFound);

  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.NotFound:
      return (
        <Button type="primary">
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
        <Button onClick={updateSelected}>
          <FileExcelOutlined />
        </Button>
      );
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

const Unhandled = () => {
  const updateSelected = useUpdateSelected(WorkItemOption.Unhandled);

  const { workItem } = useContext(ValidationButtonsContext) ?? {};
  if (!workItem) return null;

  switch (workItem.selected) {
    case Option.Unhandled:
      return (
        <Button type="primary">
          <FileUnknownOutlined className="text-white" />
        </Button>
      );
    case Option.NewDocument:
      return (
        <Button disabled>
          <FileUnknownOutlined />
        </Button>
      );
    default:
      return (
        <Button onClick={updateSelected}>
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
