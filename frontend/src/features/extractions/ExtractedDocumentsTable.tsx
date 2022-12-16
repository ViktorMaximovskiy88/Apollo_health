import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import {
  extractedDocumentTableState,
  setExtractedDocumentTableFilter,
  setExtractedDocumentTableLimit,
  setExtractedDocumentTableSkip,
  setExtractedDocumentTableSort,
} from './extractionsSlice';
import { prettyDateFromISO, prettyDateTimeFromISO } from '../../common';
import { RetrievedDocument, DocumentTypes } from '../retrieved_documents/types';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { useLazyGetDocDocumentsQuery } from '../doc_documents/docDocumentApi';
import { useInterval } from '../../common/hooks';

const columns = [
  {
    header: 'First Collected',
    name: 'first_collected_date',
    minWidth: 200,
    filterEditor: DateFilter,
    filterEditorProps: () => {
      return {
        dateFormat: 'YYYY-MM-DD',
        highlightWeekends: false,
        placeholder: 'Select Date',
      };
    },
    render: ({ value: first_collected_date }: { value: string }) => {
      return prettyDateTimeFromISO(first_collected_date);
    },
  },
  {
    header: 'Name',
    name: 'name',
    defaultFlex: 1,
    minWidth: 300,
    render: ({ data: doc }: { data: RetrievedDocument }) => {
      return <Link to={`document/${doc._id}`}>{doc.name}</Link>;
    },
  },
  {
    header: 'Document Type',
    name: 'document_type',
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: DocumentTypes,
    },
    render: ({ value: document_type }: { value: string }) => {
      return <>{document_type}</>;
    },
  },
  {
    header: 'Effective Date',
    name: 'effective_date',
    render: ({ value: effective_date }: { value: string }) => {
      if (!effective_date) return null;
      return prettyDateFromISO(effective_date);
    },
  },
];

const useControlledPagination = () => {
  const tableState = useSelector(extractedDocumentTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setExtractedDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setExtractedDocumentTableSkip(skip)),
    [dispatch]
  );
  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
  };
  return controlledPaginationProps;
};

export function ExtractedDocumentsTable() {
  const params = useParams();
  const siteId = params.siteId;
  const [getDocuments, { data }] = useLazyGetDocDocumentsQuery();
  const { watermark } = useInterval(5000);
  useEffect(() => {
    getDocuments({
      limit: 5000,
      skip: 0,
      sortInfo: { name: 'name', dir: 1 },
      filterValue: [
        { name: 'locations.site_id', operator: 'eq', type: 'string', value: siteId },
        { name: 'translation_id', operator: 'notEmpty', type: 'string', value: null },
      ],
    });
  }, [watermark, getDocuments, siteId]);
  const documents = data ? data.data : [];

  const filterProps = useDataTableFilter(
    extractedDocumentTableState,
    setExtractedDocumentTableFilter
  );
  const sortProps = useDataTableSort(extractedDocumentTableState, setExtractedDocumentTableSort);
  const controlledPagination = useControlledPagination();

  return (
    <ReactDataGrid
      dataSource={documents ?? []}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
      columnUserSelect
    />
  );
}
