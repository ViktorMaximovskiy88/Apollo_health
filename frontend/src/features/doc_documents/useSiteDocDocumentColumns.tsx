import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import BoolFilter from '@inovua/reactdatagrid-community/BoolFilter';
import { Button } from 'antd';
import { LinkOutlined, CheckCircleFilled } from '@ant-design/icons';
import { prettyDateFromISO, prettyDateTimeFromISO } from '../../common';
import { SiteDocDocument } from './types';
import { Link } from 'react-router-dom';
import { DocumentTypes } from '../retrieved_documents/types';

interface CreateColumnsType {
  handleNewVersion?: (data: SiteDocDocument) => void;
}

export enum TextAlignType {
  Start = 'start',
  End = 'end',
  Left = 'left',
  Right = 'right',
  Center = 'center',
}

const InternalDocs = [
  { id: true, value: true, label: 'true' },
  { id: false, value: false, label: 'false' },
];

export const createColumns = ({ handleNewVersion }: CreateColumnsType) => {
  return [
    {
      header: 'Last Collected',
      name: 'last_collected_date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        if (!doc.last_collected_date) return null;
        return prettyDateTimeFromISO(doc.last_collected_date);
      },
    },
    {
      header: 'Link Text',
      name: 'link_text',
      minWidth: 200,
      render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
    },
    {
      header: 'Document Name',
      name: 'name',
      defaultFlex: 1,
      filterSearch: true,
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        return <Link to={`/documents/${doc._id}`}>{doc.name}</Link>;
      },
    },
    {
      header: 'Document Type',
      name: 'document_type',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: DocumentTypes,
      },
      render: ({ value: document_type }: { value: string }) => {
        return <>{document_type}</>;
      },
    },
    {
      header: 'Internal Document',
      name: 'internal_document',
      minWidth: 200,
      filterEditor: BoolFilter,
      textAlign: TextAlignType.Center,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: InternalDocs,
      },
      render: ({ value: internal_document }: { value: boolean }) => {
        return internal_document ? <CheckCircleFilled /> : null;
      },
    },
    {
      header: 'Final Effective Date',
      name: 'final_effective_date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        if (!doc.final_effective_date) return null;
        return prettyDateFromISO(doc.final_effective_date);
      },
    },
    {
      header: 'URL',
      name: 'url',
      minWidth: 200,
      filterSearch: true,
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        return (
          <>
            <Link to={`/documents/${doc._id}`}>{doc.url}</Link>
            <a className="mx-2" href={doc.url} target="_blank" rel="noreferrer">
              <LinkOutlined />
            </a>
          </>
        );
      },
    },
    {
      header: 'Actions',
      name: 'action',
      minWidth: 200,
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        return (
          <>
            {handleNewVersion && (
              <Button size="small" onClick={() => handleNewVersion(doc)}>
                Upload new version
              </Button>
            )}
          </>
        );
      },
    },
  ];
};

export const useSiteDocDocumentColumns = ({ handleNewVersion }: CreateColumnsType) =>
  useMemo(() => createColumns({ handleNewVersion }), [handleNewVersion]);
