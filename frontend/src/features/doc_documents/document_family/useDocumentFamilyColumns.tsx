import { useMemo } from 'react';
import { DocumentFamily } from './types';
import { Link } from 'react-router-dom';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { DocumentTypes } from '../../retrieved_documents/types';
import { ChangeLogModal } from '../../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './documentFamilyApi';
interface CreateColumnsType {
  handleNewVersion?: (data: DocumentFamily) => void;
}

export const createColumns = ({ handleNewVersion }: CreateColumnsType) => {
  return [
    {
      header: 'Family Name',
      name: 'name',
      defaultFlex: 1,
      minWidth: 200,
      render: ({ data: docFamily }: { data: DocumentFamily }) => {
        return <>{docFamily.name}</>;
      },
    },
    {
      header: 'Document Type',
      name: 'document_type',
      filterEditor: SelectFilter,
      minWidth: 200,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: DocumentTypes,
      },
      render: ({ data: docFamily }: { data: DocumentFamily }) => <>{docFamily.document_type}</>,
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: docFamily }: { data: DocumentFamily }) => (
        <>
          <ChangeLogModal target={docFamily} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      ),
    },
  ];
};

export const useDocumentFamilyColumns = ({ handleNewVersion }: CreateColumnsType) =>
  useMemo(() => createColumns({ handleNewVersion }), [handleNewVersion]);
