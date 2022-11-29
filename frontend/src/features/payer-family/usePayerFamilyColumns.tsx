import { useMemo } from 'react';
import { PayerFamily } from './types';

import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './payerFamilyApi';
import { TypeColumn, TypeFilterValue } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';
import { useAppDispatch } from '../../app/store';
import {
  docDocumentTableState,
  setDocDocumentTableFilter,
} from '../doc_documents/docDocumentsSlice';
import { useSelector } from 'react-redux';

export const createColumns = (dispatch: any, docDocumentFilters: TypeFilterValue) => {
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
      header: 'Document Count',
      name: 'doc_doc_count',
      minWidth: 50,
      render: ({
        value: documentCount,
        data: { _id: payerFamilyId },
      }: {
        value: number;
        data: PayerFamily;
      }) => {
        const handleClick = () => {
          const newDocDocumentFilters = docDocumentFilters?.map((filter) => {
            if (filter.name !== 'locations.payer_family_id') return filter;
            return {
              name: 'locations.payer_family_id',
              operator: 'eq',
              type: 'select',
              value: payerFamilyId,
            };
          });
          dispatch(setDocDocumentTableFilter(newDocDocumentFilters));
        };
        return (
          <Link to={`../documents`} onClick={handleClick}>
            {documentCount}
          </Link>
        );
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

export const usePayerFamilyColumns = (): TypeColumn[] => {
  const dispatch = useAppDispatch();
  const { filter: docDocumentFilters } = useSelector(docDocumentTableState);
  return useMemo(() => createColumns(dispatch, docDocumentFilters), [dispatch, docDocumentFilters]);
};
