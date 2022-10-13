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

const createColumns = ({
  previousDocDocumentId,
  setPreviousDocDocumentId,
}: {
  previousDocDocumentId: string;
  setPreviousDocDocumentId: Dispatch<SetStateAction<string>>;
}) => [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: doc }: { data: DocDocument }) => {
      if (doc._id === previousDocDocumentId) {
        return <div className="ml-2">{doc.name}</div>;
      }
      return <ButtonLink onClick={() => setPreviousDocDocumentId(doc._id)}>{doc.name}</ButtonLink>;
    },
    defaultFlex: 1,
    minWidth: 300,
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
    header: 'Link Text',
    name: 'link_text',
    render: ({ data: { locations } }: { data: DocDocument }) => <>{locations[0].link_text}</>,
  },
  {
    header: 'Final Effective Date',
    name: 'final_effective_date',
    minWidth: 200,
    filterEditor: DateFilter,
    filterEditorProps: () => {
      return {
        dateFormat: 'YYYY-MM-DD',
        highlightWeekends: false,
        placeholder: 'Select Date',
      };
    },
    render: ({ value: final_effective_date }: { value: string }) => (
      <>{prettyDateFromISO(final_effective_date)}</>
    ),
  },
];

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

const useColumns = () => {
  const [previousDocDocumentId, setPreviousDocDocumentId] = useContext(PreviousDocDocContext);

  return useMemo(
    () => createColumns({ previousDocDocumentId, setPreviousDocDocumentId }),
    [previousDocDocumentId, setPreviousDocDocumentId]
  );
};

export function LineageDocDocumentsTable() {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);
  const { docDocumentId: currentDocDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(currentDocDocumentId ?? '');
  const [previousDocDocumentId, setPreviousDocDocumentId] = useContext(PreviousDocDocContext);

  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();

  const site_ids = useMemo(
    () => currentDocDocument?.locations.map((location) => location.site_id) ?? [],
    [currentDocDocument?.locations]
  );

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn({
        ...tableInfo,
        site_ids,
        exclude_doc_doc_id: currentDocDocumentId,
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
      getDocDocumentsFn,
      site_ids,
      currentDocDocumentId,
      previousDocDocumentId,
      setPreviousDocDocumentId,
      watermark,
    ]
  );
  const columns = useColumns();
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
