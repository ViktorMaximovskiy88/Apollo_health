import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useCallback, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setDocDocumentTableFilter,
  setDocDocumentTableSort,
  docDocumentTableState,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
  setDocDocumentTableSelect,
} from './docDocumentsSlice';
import { GridPaginationToolbar } from '../../components';
import { useLazyGetDocDocumentsQuery } from './docDocumentApi';
import { DocDocument } from './types';
import { useInterval } from '../../common/hooks';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { useGetSitesQuery } from '../sites/sitesApi';
import { useGetPayerFamiliesQuery } from '../payer-family/payerFamilyApi';
import { useGetDocumentFamiliesQuery } from './document_family/documentFamilyApi';
import { useColumns } from './useDocDocumentColumns';
import { useDataTableSelection } from '../../common/hooks/use-data-table-select';

export function useGetSiteNamesById() {
  const [siteIds, setSiteIds] = useState<string[]>([]);
  const { data: sites } = useGetSitesQuery(
    {
      filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: siteIds }],
    },
    { skip: siteIds.length === 0 }
  );
  const siteNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    sites?.data.forEach((site) => {
      map[site._id] = site.name;
    });
    return map;
  }, [sites]);
  return { setSiteIds, siteNamesById };
}

function useGetPayerFamilyNamesById() {
  const [payerFamilyIds, setPayerFamilyIds] = useState<string[]>([]);
  const { data: payerFamilies } = useGetPayerFamiliesQuery({
    limit: 1000,
    skip: 0,
    sortInfo: { name: 'name', dir: 1 },
    filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: payerFamilyIds }],
  });
  const payerFamilyNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    payerFamilies?.data.forEach((payerFamily) => {
      map[payerFamily._id] = payerFamily.name;
    });
    return map;
  }, [payerFamilies]);
  return { setPayerFamilyIds, payerFamilyNamesById };
}

function useGetDocumentFamilyNamesById() {
  const [documentFamilyIds, setDocumentFamilyIds] = useState<string[]>([]);
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    limit: 1000,
    skip: 0,
    sortInfo: { name: 'name', dir: 1 },
    filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: documentFamilyIds }],
  });
  const documentFamilyNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    documentFamilies?.data.forEach((documentFamily) => {
      map[documentFamily._id] = documentFamily.name;
    });
    return map;
  }, [documentFamilies]);
  return { setDocumentFamilyIds, documentFamilyNamesById };
}

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(docDocumentTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocDocumentTableSkip(skip)),
    [dispatch]
  );

  const renderPaginationToolbar = useCallback(
    (paginationProps: TypePaginationProps) => {
      return (
        <GridPaginationToolbar
          paginationProps={{ ...paginationProps }}
          autoRefreshValue={isActive}
          autoRefreshClick={setActive}
        />
      );
    },
    [isActive, setActive]
  );

  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
    renderPaginationToolbar,
  };
  return controlledPaginationProps;
};

function uniqueSiteIds(items: DocDocument[]) {
  const usedSiteIds: { [key: string]: boolean } = {};
  items.forEach((item) => item.locations.forEach((l) => (usedSiteIds[l.site_id] = true)));
  return Object.keys(usedSiteIds);
}
const uniquePayerFamilyIds = (items: DocDocument[]) => {
  const usedPayerFamilyIds: { [key: string]: boolean } = {};
  items.forEach((item) =>
    item.locations.forEach((l) => (usedPayerFamilyIds[l.payer_family_id] = true))
  );
  return Object.keys(usedPayerFamilyIds);
};

const uniqueDocumentFamilyIds = (docDocuments: DocDocument[]): string[] => {
  const documentFamilyIds = docDocuments
    .map(({ document_family_id }) => document_family_id ?? '')
    .filter(Boolean);
  const usedDocumentFamilyIds = new Set(documentFamilyIds);
  return Array.from(usedDocumentFamilyIds);
};

export function DocDocumentsDataTable() {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();
  const { setPayerFamilyIds, payerFamilyNamesById } = useGetPayerFamilyNamesById();
  const { setDocumentFamilyIds, documentFamilyNamesById } = useGetDocumentFamilyNamesById();

  const { forceUpdate } = useSelector(docDocumentTableState);
  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn(tableInfo);
      const docDocuments = data?.data ?? [];
      const count = data?.total ?? 0;
      if (docDocuments) {
        setSiteIds(uniqueSiteIds(docDocuments));
        setPayerFamilyIds(uniquePayerFamilyIds(docDocuments));
        setDocumentFamilyIds(uniqueDocumentFamilyIds(docDocuments));
      }
      return { data: docDocuments, count };
    },
    [getDocDocumentsFn, setSiteIds, watermark, forceUpdate] // eslint-disable-line react-hooks/exhaustive-deps
  );

  const filterProps = useDataTableFilter(docDocumentTableState, setDocDocumentTableFilter);
  const sortProps = useDataTableSort(docDocumentTableState, setDocDocumentTableSort);
  const selectionProps = useDataTableSelection(docDocumentTableState, setDocDocumentTableSelect);
  const controlledPagination = useControlledPagination({ isActive, setActive });
  const columns = useColumns({ siteNamesById, payerFamilyNamesById, documentFamilyNamesById });

  return (
    <>
      <ReactDataGrid
        idProperty="_id"
        dataSource={loadData}
        {...filterProps}
        {...sortProps}
        {...selectionProps}
        {...controlledPagination}
        columns={columns}
        rowHeight={50}
        renderLoadMask={() => <></>}
        activateRowOnFocus={false}
        columnUserSelect
        checkboxColumn
        checkboxOnlyRowSelect
      />
    </>
  );
}
