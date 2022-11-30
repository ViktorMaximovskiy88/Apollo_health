import { useMemo } from 'react';
import { DocumentFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { DocumentTypes } from '../../retrieved_documents/types';
import { ChangeLogModal } from '../../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './documentFamilyApi';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';
import { CopyDocumentFamily } from './CopyDocumentFamily';

export const createColumns = () => {
  return [
    {
      header: 'Family Name',
      name: 'name',
      defaultFlex: 1,
      minWidth: 200,
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return <Link to={`/document-family/${docFam._id}`}>{docFam.name}</Link>;
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
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: docFamily }: { data: DocumentFamily }) => (
        <>
          <ChangeLogModal target={docFamily} useChangeLogQuery={useGetChangeLogQuery} />
          <CopyDocumentFamily documentFamily={docFamily} />
        </>
      ),
    },
  ];
};

export const useDocumentFamilyColumns = (): TypeColumn[] => useMemo(() => createColumns(), []);
