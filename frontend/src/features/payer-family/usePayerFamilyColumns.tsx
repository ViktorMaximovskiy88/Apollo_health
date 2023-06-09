import { Dispatch, SetStateAction, useMemo } from 'react';
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
import { Button, Popconfirm } from 'antd';
import { ButtonLink } from '../../components';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';
import { useCurrentUser } from '../../common/hooks/use-current-user';

export const createColumns = ({
  dispatch,
  docDocumentFilters,
  deletePayerFamily,
  isAdminUser,
  setPayerFamilyId,
  setOpenEditDrawer,
}: {
  dispatch: any;
  docDocumentFilters: TypeFilterValue;
  deletePayerFamily: (payerFamily: Pick<PayerFamily, '_id'> & Partial<PayerFamily>) => void;
  isAdminUser?: boolean;
  setPayerFamilyId: Dispatch<SetStateAction<string>>;
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>;
}) => [
  {
    header: 'Family Name',
    name: 'name',
    defaultFlex: 1,
    minWidth: 200,
    render: ({ data: payerFamily }: { data: PayerFamily }) => {
      return (
        <Button
          onClick={() => {
            setPayerFamilyId(payerFamily._id);
            setOpenEditDrawer(true);
          }}
          type="link"
        >
          {payerFamily.name}
        </Button>
      );
    },
  },
  {
    header: 'Document Count',
    name: 'doc_doc_count',
    minWidth: 50,
    type: 'number',
    filterEditor: NumberFilter,
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
          {isAdminUser && <ButtonLink danger>Delete</ButtonLink>}
        </Popconfirm>
      </>
    ),
  },
];

export const usePayerFamilyColumns = (
  setPayerFamilyId: Dispatch<SetStateAction<string>>,
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>,
  deletePayerFamily: (payerFamily: Pick<PayerFamily, '_id'> & Partial<PayerFamily>) => void
): TypeColumn[] => {
  const user = useCurrentUser();
  const dispatch = useAppDispatch();
  const { filter: docDocumentFilters } = useSelector(docDocumentTableState);
  return useMemo(
    () =>
      createColumns({
        dispatch,
        docDocumentFilters,
        deletePayerFamily,
        isAdminUser: user?.is_admin,
        setPayerFamilyId,
        setOpenEditDrawer,
      }),
    [
      dispatch,
      docDocumentFilters,
      deletePayerFamily,
      user?.is_admin,
      setOpenEditDrawer,
      setPayerFamilyId,
    ]
  );
};
