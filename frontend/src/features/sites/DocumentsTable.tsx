import { prettyDateFromISO, prettyDateUTCFromISO } from '../../common';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useGetDocumentsQuery } from '../retrieved_documents/documentsApi';
import { RetrievedDocument } from '../retrieved_documents/types';
import { useGetChangeLogQuery } from './sitesApi';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  documentTableState,
  setDocumentTableFilter,
  setDocumentTableLimit,
  setDocumentTableSkip,
  setDocumentTableSort,
} from './documentsSlice';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

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
      return prettyDateFromISO(first_collected_date);
    },
  },
  {
    header: 'Last Collected',
    name: 'last_collected_date',
    minWidth: 200,
    filterEditor: DateFilter,
    filterEditorProps: () => {
      return {
        dateFormat: 'YYYY-MM-DD',
        highlightWeekends: false,
        placeholder: 'Select Date',
      };
    },
    render: ({ value: last_collected_date }: { value: string }) => {
      return prettyDateFromISO(last_collected_date);
    },
  },
  {
    header: 'Link Text',
    name: 'link_text',
    render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
  },
  {
    header: 'Name',
    name: 'name',
    defaultFlex: 1,
    render: ({ data: doc }: { data: RetrievedDocument }) => {
      return <Link to={`${doc._id}/edit`}>{doc.name}</Link>;
    },
  },
  {
    header: 'Document Type',
    name: 'document_type',
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: [
        { id: 'Authorization Policy', label: 'Authorization Policy' },
        { id: 'Provider Guide', label: 'Provider Guide' },
        { id: 'Treatment Request Form', label: 'Treatment Request Form' },
        { id: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
        { id: 'Covered Treatment List', label: 'Covered Treatment List' },
        { id: 'Regulatory Document', label: 'Regulatory Document' },
        { id: 'Formulary', label: 'Formulary' },
        { id: 'Internal Reference', label: 'Internal Reference' },
      ],
    },
    render: ({ value: document_type }: { value: string }) => {
      return <>{document_type}</>;
    },
  },
  {
    header: 'Doc Type Confidence',
    name: 'doc_type_confidence',
    minWidth: 200,
    render: ({ value: doc_type_confidence }: { value?: number }) => {
      return <>{doc_type_confidence && `${Math.round(100 * doc_type_confidence)}%`}</>;
    },
  },
  {
    header: 'Effective Date',
    name: 'effective_date',
    render: ({ value: effective_date }: { value: string }) => {
      if (!effective_date) return null;
      return prettyDateUTCFromISO(effective_date);
    },
  },
  {
    header: 'URL',
    name: 'url',
    render: ({ value: url }: { value: string }) => {
      return (
        <div className="w-48 whitespace-nowrap text-ellipsis overflow-hidden">
          <a target="_blank" rel="noreferrer" href={url}>
            {url}
          </a>
        </div>
      );
    },
  },
  {
    header: 'Actions',
    name: 'action',
    render: ({ data: doc }: { data: RetrievedDocument }) => {
      return (
        <>
          <ChangeLogModal target={doc} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      );
    },
  },
];

const useControlledPagination = () => {
  const tableState = useSelector(documentTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocumentTableSkip(skip)),
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

const useDocuments = (): RetrievedDocument[] => {
  const [searchParams] = useSearchParams();
  const params = useParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const siteId = params.siteId;
  const { data } = useGetDocumentsQuery(
    {
      scrape_task_id: scrapeTaskId,
      site_id: siteId,
    },
    { pollingInterval: 5000 }
  );
  const documents = data?.map((document) => ({
    ...document,
    link_text: document?.context_metadata?.link_text,
  }));
  return documents ?? [];
};

export function DocumentsTable() {
  const documents = useDocuments();

  const filterProps = useDataTableFilter(documentTableState, setDocumentTableFilter);
  const sortProps = useDataTableSort(documentTableState, setDocumentTableSort);
  const controlledPagination = useControlledPagination();

  return (
    <ReactDataGrid
      dataSource={documents}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
    />
  );
}
