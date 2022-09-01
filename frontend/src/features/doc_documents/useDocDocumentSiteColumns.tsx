import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { prettyDateTimeFromISO, prettyDateFromISO } from '../../common';
import { DocDocument } from './types';
import { Link } from 'react-router-dom';
import { DocumentTypes } from '../retrieved_documents/types';
import { ValidationButtons } from './ManualCollectionValidationButtons';

interface CreateColumnsType {
  handleNewVersion?: (data: DocDocument) => void;
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
      render: ({ data: doc }: { data: DocDocument }) => {
        if (!doc.last_collected_date) return null;
        return prettyDateTimeFromISO(doc.last_collected_date);
      },
    },
    {
      header: 'Link Text',
      name: 'link_text',
      defaultFlex: 1,
      minWidth: 200,
      render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
    },
    {
      header: 'Document Name',
      name: 'name',
      minWidth: 200,
      filterSearch: true,
      render: ({ data: doc }: { data: DocDocument }) => {
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
      render: ({ value: effective_date }: { value: string }) => {
        return prettyDateFromISO(effective_date);
      },
    },
    {
      header: 'Validation',
      name: 'validation',
      minWidth: 300,
      render: ({ data: doc }: { data: DocDocument }) => (
        <ValidationButtons doc={doc} handleNewVersion={handleNewVersion} />
      ),
    },
  ];
};

export const useDocDocumentSiteColumns = ({ handleNewVersion }: CreateColumnsType) =>
  useMemo(() => createColumns({ handleNewVersion }), [handleNewVersion]);
