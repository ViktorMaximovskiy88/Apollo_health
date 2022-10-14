import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Dispatch, SetStateAction, useCallback, useContext, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { prettyDateFromISO } from '../../../common';
import { ButtonLink, GridPaginationToolbar } from '../../../components';
import { useGetDocDocumentQuery, useLazyGetDocDocumentsQuery } from '../docDocumentApi';
import { DocDocument } from '../types';
import { useInterval } from '../../../common/hooks';
import { DocumentTypes } from '../../retrieved_documents/types';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDataTableSort } from '../../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../../common/hooks/use-data-table-filter';
import { useParams } from 'react-router-dom';
import {
  lineageDocDocumentTableState,
  setLineageDocDocumentTableFilter,
  setLineageDocDocumentTableLimit,
  setLineageDocDocumentTableSkip,
  setLineageDocDocumentTableSort,
} from './lineageDocDocumentsSlice';
import { PreviousDocDocContext } from './PreviousDocDocContext';
import { useLineageDocDocumentColumns } from './useLineageDocDocumentColumns';

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(lineageDocDocumentTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setLineageDocDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setLineageDocDocumentTableSkip(skip)),
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

const buildFilterValue = ({
  tableInfo,
  currentDocDocument,
}: {
  tableInfo: any;
  currentDocDocument?: DocDocument;
}) => {
  const filterBySites =
    currentDocDocument?.locations.map(({ site_id }: { site_id: string }) => ({
      name: 'locations.site_id',
      operator: 'eq',
      type: 'string',
      value: site_id,
    })) ?? [];

  const filterOutCurrentDocDocument = {
    name: '_id',
    operator: 'neq',
    type: 'string',
    value: currentDocDocument?._id,
  };

  return [...tableInfo.filterValue, ...filterBySites, filterOutCurrentDocDocument];
};

export function LineageDocDocumentsTable() {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);
  const { docDocumentId: currentDocDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(currentDocDocumentId ?? '');
  const [previousDocDocumentId, setPreviousDocDocumentId] = useContext(PreviousDocDocContext);

  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();

  const loadData = useCallback(
    async (tableInfo: any) => {
      const filterValue = buildFilterValue({ tableInfo, currentDocDocument });
      const { data } = await getDocDocumentsFn({
        ...tableInfo,
        filterValue,
      });
      const docDocuments = data?.data ?? [];
      const count = data?.total ?? 0;
      if (!previousDocDocumentId) {
        setPreviousDocDocumentId(docDocuments[0]._id);
      }
      return { data: docDocuments, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      currentDocDocument,
      getDocDocumentsFn,
      previousDocDocumentId,
      setPreviousDocDocumentId,
      watermark,
    ]
  );
  const columns = useLineageDocDocumentColumns();
  const filterProps = useDataTableFilter(
    lineageDocDocumentTableState,
    setLineageDocDocumentTableFilter
  );
  const sortProps = useDataTableSort(lineageDocDocumentTableState, setLineageDocDocumentTableSort);
  const controlledPagination = useControlledPagination({ isActive, setActive });

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
      renderLoadMask={() => <></>}
      activateRowOnFocus={false}
    />
  );
}
