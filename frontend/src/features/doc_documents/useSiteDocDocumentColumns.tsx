import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import { LinkOutlined } from '@ant-design/icons';
import { prettyDateTimeFromISO } from '../../common';
import { SiteDocDocument } from './types';
import { Link } from 'react-router-dom';
import { DocumentTypes } from '../retrieved_documents/types';

interface CreateColumnsType {
  handleNewVersion?: (data: SiteDocDocument) => void;
}

export const createColumns = ({ handleNewVersion }: CreateColumnsType) => {
  return [
    {
      header: 'Last Collected Date',
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
      header: 'Document Name',
      key: 'name',
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
      header: 'Link Text',
      name: 'link_text',
      minWidth: 200,
      render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
    },
    {
      header: 'Effective Date',
      name: 'effective_date',
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
        if (!doc.effective_date) return null;
        return prettyDateTimeFromISO(doc.effective_date);
      },
    },
    {
      header: 'Url',
      key: 'url',
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