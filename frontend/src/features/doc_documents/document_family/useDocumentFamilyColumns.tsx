import { DocumentFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import {
  DocumentTypes,
  FieldGroupsOptions,
  getFieldGroupLabel,
  getLegacyRelevanceLable,
  LegacyRelevanceOptions,
} from '../../retrieved_documents/types';
import { ChangeLogModal } from '../../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './documentFamilyApi';
import { TypeColumn, TypeFilterValue } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';
import { useAppDispatch } from '../../../app/store';
import { useSelector } from 'react-redux';
import { docDocumentTableState, setDocDocumentTableFilter } from '../docDocumentsSlice';
import { ButtonLink } from '../../../components';
import { Button, Popconfirm } from 'antd';
import { Dispatch, SetStateAction, useMemo } from 'react';
import { CopyDocumentFamily } from './CopyDocumentFamily';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';
import { useCurrentUser } from '../../../common/hooks/use-current-user';

export const createColumns = ({
  dispatch,
  docDocumentFilters,
  deleteDocumentFamily,
  setDocFamilyId,
  setOpenEditDrawer,
  isAdminUser,
}: {
  dispatch: any;
  setDocFamilyId: Dispatch<SetStateAction<string>>;
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>;
  docDocumentFilters: TypeFilterValue;
  deleteDocumentFamily: (
    documentFamily: Pick<DocumentFamily, '_id'> & Partial<DocumentFamily>
  ) => void;
  isAdminUser?: boolean;
}) => [
  {
    header: 'Family Name',
    name: 'name',
    defaultFlex: 1,
    minWidth: 200,
    render: ({ data: docFam }: { data: DocumentFamily }) => {
      return (
        <Button
          onClick={() => {
            setDocFamilyId(docFam._id);
            setOpenEditDrawer(true);
          }}
          type="link"
        >
          {docFam.name}
        </Button>
      );
    },
  },
  {
    header: 'Legacy Relevance',
    name: 'legacy_relevance',
    filterEditor: SelectFilter,
    minWidth: 200,
    filterEditorProps: {
      multiple: true,
      wrapMultiple: false,
      dataSource: LegacyRelevanceOptions,
    },
    render: ({ data: docFam }: { data: DocumentFamily }) => {
      return docFam.legacy_relevance.map(getLegacyRelevanceLable).join(', ');
    },
  },
  {
    header: 'Field Group',
    name: 'field_groups',
    filterEditor: SelectFilter,
    minWidth: 300,
    filterEditorProps: {
      multiple: true,
      wrapMultiple: false,
      dataSource: FieldGroupsOptions,
    },
    render: ({ data: docFam }: { data: DocumentFamily }) => {
      return docFam.field_groups.map(getFieldGroupLabel).join(', ');
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
    type: 'number',
    filterEditor: NumberFilter,
    render: ({
      value: documentCount,
      data: { _id: documentFamilyId },
    }: {
      value: number;
      data: DocumentFamily;
    }) => {
      const handleClick = () => {
        const newDocDocumentFilters = docDocumentFilters?.map((filter) => {
          if (filter.name !== 'document_family_id') return filter;
          return {
            name: 'document_family_id',
            operator: 'eq',
            type: 'select',
            value: documentFamilyId,
          };
        });
        dispatch(setDocDocumentTableFilter(newDocDocumentFilters));
      };
      return (
        <Link to={`../../documents`} onClick={handleClick}>
          {documentCount}
        </Link>
      );
    },
  },
  {
    header: 'Actions',
    name: 'action',
    render: ({ data: docFamily }: { data: DocumentFamily }) => (
      <>
        <ChangeLogModal target={docFamily} useChangeLogQuery={useGetChangeLogQuery} />
        <CopyDocumentFamily documentFamily={docFamily} />

        <Popconfirm
          title={`Are you sure you want to delete '${docFamily.name}'?`}
          okText="Yes"
          cancelText="No"
          onConfirm={async () => {
            deleteDocumentFamily(docFamily);
          }}
        >
          {isAdminUser && <ButtonLink danger>Delete</ButtonLink>}
        </Popconfirm>
      </>
    ),
  },
];

export const useDocumentFamilyColumns = (
  siteNamesById: {
    [key: string]: string;
  },
  deleteDocumentFamily: (
    documentFamily: Pick<DocumentFamily, '_id'> & Partial<DocumentFamily>
  ) => void,
  setDocFamilyId: Dispatch<SetStateAction<string>>,
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>
): TypeColumn[] => {
  const dispatch = useAppDispatch();
  const user = useCurrentUser();
  const { filter: docDocumentFilters } = useSelector(docDocumentTableState);
  return useMemo(() => {
    return createColumns({
      dispatch,
      docDocumentFilters,
      deleteDocumentFamily,
      isAdminUser: user?.is_admin,
      setDocFamilyId,
      setOpenEditDrawer,
    });
  }, [
    dispatch,
    docDocumentFilters,
    deleteDocumentFamily,
    setOpenEditDrawer,
    setDocFamilyId,
    user?.is_admin,
  ]);
};
