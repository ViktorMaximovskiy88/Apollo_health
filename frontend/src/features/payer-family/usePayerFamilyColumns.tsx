import { useMemo } from 'react';
import { PayerFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { DocumentTypes } from '../retrieved_documents/types';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './payerFamilyApi';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';

export const createColumns = () => {
  return [
    {
      header: 'Family Name',
      name: 'name',
      defaultFlex: 1,
      minWidth: 200,
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
      render: ({ data: PayerFamily }: { data: PayerFamily }) => (
        <>
          <ChangeLogModal target={PayerFamily} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      ),
    },
  ];
};

export const usePayerFamilyColumns = (): TypeColumn[] => useMemo(() => createColumns(), []);
