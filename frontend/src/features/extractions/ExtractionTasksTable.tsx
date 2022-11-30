import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useParams } from 'react-router-dom';
import {
  extractionTaskTableState,
  setExtractionTaskTableFilter,
  setExtractionTaskTableLimit,
  setExtractionTaskTableSkip,
  setExtractionTaskTableSort,
} from './extractionsSlice';
import {
  prettyDateFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
  prettyDateDistanceSingle,
} from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetExtractionTasksForDocQuery } from './extractionsApi';
import { ExtractionTask } from './types';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

const columns = [
  {
    header: 'Start Time',
    name: 'queued_time',
    minWidth: 200,
    defaultFlex: 1,
    filterEditor: DateFilter,
    filterEditorProps: () => {
      return {
        dateFormat: 'YYYY-MM-DD',
        highlightWeekends: false,
        placeholder: 'Select Date',
      };
    },
    render: ({ value: queued_time }: { value: string }) => prettyDateFromISO(queued_time),
  },
  {
    header: 'Elapsed',
    name: 'elapsed',
    defaultFlex: 1,
    minWidth: 200,
    render: ({ data: task }: { data: ExtractionTask }) =>
      prettyDateDistanceSingle(task.start_time || task.queued_time, task.end_time),
  },
  {
    header: 'Status',
    name: 'status',
    defaultFlex: 1,
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: [
        {
          id: TaskStatus.Finished,
          label: displayName(TaskStatus.Finished),
        },
        {
          id: TaskStatus.Canceled,
          label: displayName(TaskStatus.Canceled),
        },
        {
          id: TaskStatus.Queued,
          label: displayName(TaskStatus.Queued),
        },
        {
          id: TaskStatus.Failed,
          label: displayName(TaskStatus.Failed),
        },
        {
          id: TaskStatus.InProgress,
          label: displayName(TaskStatus.InProgress),
        },
      ],
    },
    render: ({ value: status }: { value: TaskStatus }) => styledDisplay(status),
  },
  {
    header: 'Extracted Count',
    name: 'extraction_count',
    defaultFlex: 1,
    minWidth: 200,
    render: ({ data: task }: { data: ExtractionTask }) => {
      return (
        <ButtonLink to={`${task._id}/results`}>{task.extraction_count} Extractions</ButtonLink>
      );
    },
  },
];

const useControlledPagination = () => {
  const tableState = useSelector(extractionTaskTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setExtractionTaskTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setExtractionTaskTableSkip(skip)),
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

export function ExtractionTasksTable() {
  const params = useParams();
  const docId = params.docId;
  const { data: documents } = useGetExtractionTasksForDocQuery(docId, {
    skip: !docId,
    pollingInterval: 5000,
  });

  const filterProps = useDataTableFilter(extractionTaskTableState, setExtractionTaskTableFilter);
  const sortProps = useDataTableSort(extractionTaskTableState, setExtractionTaskTableSort);
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
