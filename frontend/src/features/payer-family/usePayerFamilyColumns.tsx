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
import { Popconfirm } from 'antd';
import { ButtonLink } from '../../components';

export const createColumns = ({
  dispatch,
  docDocumentFilters,
  deletePayerFamily,
}: {
  dispatch: any;
  docDocumentFilters: TypeFilterValue;
  deletePayerFamily: (payerFamily: Pick<PayerFamily, '_id'> & Partial<PayerFamily>) => void;
}) => [
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
    type: 'number',
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
    render: ({ data: payerFamily }: { data: PayerFamily }) => (
      <>
        <ChangeLogModal target={payerFamily} useChangeLogQuery={useGetChangeLogQuery} />
        <Popconfirm
          title={`Are you sure you want to delete '${payerFamily.name}'?`}
          okText="Yes"
          cancelText="No"
          onConfirm={async () => {
            deletePayerFamily(payerFamily);
          }}
        >
          <ButtonLink danger>Delete</ButtonLink>
        </Popconfirm>
      </>
    ),
  },
];

export const usePayerFamilyColumns = (
  deletePayerFamily: (payerFamily: Pick<PayerFamily, '_id'> & Partial<PayerFamily>) => void
): TypeColumn[] => {
  const dispatch = useAppDispatch();
  const { filter: docDocumentFilters } = useSelector(docDocumentTableState);
  return useMemo(
    () => createColumns({ dispatch, docDocumentFilters, deletePayerFamily }),
    [dispatch, docDocumentFilters, deletePayerFamily]
  );
};
