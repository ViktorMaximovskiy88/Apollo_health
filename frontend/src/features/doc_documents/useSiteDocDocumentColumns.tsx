import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { LinkOutlined } from '@ant-design/icons';
import { prettyDateFromISO, prettyDateTimeFromISO } from '../../common';
import { SiteDocDocument } from './types';
import { Link } from 'react-router-dom';
import { DocumentTypes } from '../retrieved_documents/types';
import { ValidationButtons } from './ManualCollectionValidationButtons';

interface CreateColumnsType {
  handleNewVersion?: (data: SiteDocDocument) => void;
}

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
      header: 'Validation',
      name: 'validation',
      minWidth: 200,
      render: ({ data: doc }: { data: SiteDocDocument }) => {
        return (
          <>
            {handleNewVersion ? (
              <ValidationButtons doc={doc} handleNewVersion={handleNewVersion} />
            ) : null}
          </>
        );
      },
    },
  ];
};

export const useSiteDocDocumentColumns = ({ handleNewVersion }: CreateColumnsType) =>
  useMemo(() => createColumns({ handleNewVersion }), [handleNewVersion]);
