import { useMemo } from 'react';
import { PayerFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { DocumentTypes } from '../retrieved_documents/types';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './payerFamilyApi';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';

export const createColumns = () => {
  return [
    {
      header: 'Family Name',
      name: 'name',
      defaultFlex: 1,
      minWidth: 200,
      render: ({ data: payerFamily }: { data: PayerFamily }) => {
        return <Link to={`${payerFamily._id}`}>{payerFamily.name}</Link>;
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
      header: 'Document Count',
      name: 'doc_doc_count',
      minWidth: 50,
      render: ({
        value: documentCount,
        data: { _id: payerFamilyId },
      }: {
        value: number;
        data: PayerFamily;
      }) => <Link to={`../documents?payer-family-id=${payerFamilyId}`}>{documentCount}</Link>,
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: PayerFamily }: { data: PayerFamily }) => (
        <>
          <ChangeLogModal target={PayerFamily} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      ),
    },
  ];
};

export const usePayerFamilyColumns = (): TypeColumn[] => useMemo(() => createColumns(), []);
