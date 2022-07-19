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
  prettyDateDistance,
  prettyDateFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
} from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetExtractionTasksForDocQuery } from './extractionsApi';
import { ExtractionTask } from './types';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';

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
    render: ({ data: task }: { data: ExtractionTask }) =>
      prettyDateDistance(task.queued_time, task.end_time),
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
    render: ({ data: task }: { data: ExtractionTask }) => {
      return <ButtonLink to={task._id}>{task.extraction_count} Extractions</ButtonLink>;
    },
  },
];

const useFilter = () => {
  const tableState = useSelector(extractionTaskTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setExtractionTaskTableFilter(filter)),
    [dispatch]
  );
  const filterProps = {
    defaultFilterValue: tableState.filter,
    onFilterValueChange: onFilterChange,
  };
  return filterProps;
};

const useSort = () => {
  const tableState = useSelector(extractionTaskTableState);
  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sort: TypeSortInfo) => dispatch(setExtractionTaskTableSort(sort)),
    [dispatch]
  );
  const sortProps = {
    defaultSortInfo: tableState.sort,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};

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

  const filterProps = useFilter();
  const sortProps = useSort();
  const controlledPagination = useControlledPagination();

  return (
    <ReactDataGrid
      dataSource={documents ?? []}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
    />
  );
}
