import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useCallback } from 'react';
import { useGetDocDocumentQuery, useLazyGetDocDocumentsQuery } from '../docDocumentApi';
import { DocDocument } from '../types';
import { useDataTablePagination } from '../../../common/hooks';
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
import { useLineageDocDocumentColumns } from './useLineageDocDocumentColumns';

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
  const { docDocumentId: currentDocDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(currentDocDocumentId ?? '');

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
      return { data: docDocuments, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [currentDocDocument, getDocDocumentsFn]
  );
  const columns = useLineageDocDocumentColumns();
  const filterProps = useDataTableFilter(
    lineageDocDocumentTableState,
    setLineageDocDocumentTableFilter
  );
  const sortProps = useDataTableSort(lineageDocDocumentTableState, setLineageDocDocumentTableSort);
  const controlledPagination = useDataTablePagination(
    lineageDocDocumentTableState,
    setLineageDocDocumentTableLimit,
    setLineageDocDocumentTableSkip
  );

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
