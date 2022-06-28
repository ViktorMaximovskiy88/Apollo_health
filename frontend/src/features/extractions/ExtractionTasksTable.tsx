import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useParams } from 'react-router-dom';
import {
  extractionTaskTableState,
  setExtractionTaskTableFilter,
  setExtractionTaskTableSort,
} from '../../app/uiSlice';
import {
  prettyDateDistance,
  prettyDateFromISO,
  Status,
  statusDisplayName,
  statusStyledDisplay,
} from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetExtractionTasksForDocQuery } from './extractionsApi';
import { ExtractionTask } from './types';

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
    render: ({ value: queued_time }: { value: string }) =>
      prettyDateFromISO(queued_time),
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
        { id: Status.Finished, label: statusDisplayName(Status.Finished) },
        { id: Status.Canceled, label: statusDisplayName(Status.Canceled) },
        { id: Status.Queued, label: statusDisplayName(Status.Queued) },
        { id: Status.Failed, label: statusDisplayName(Status.Failed) },
        {
          id: Status.InProgress,
          label: statusDisplayName(Status.InProgress),
        },
      ],
    },
    render: ({ value: status }: { value: Status }) =>
      statusStyledDisplay(status),
  },
  {
    header: 'Extracted Count',
    name: 'extraction_count',
    defaultFlex: 1,
    render: ({ data: task }: { data: ExtractionTask }) => {
      return (
        <ButtonLink to={task._id}>
          {task.extraction_count} Extractions
        </ButtonLink>
      );
    },
  },
];

export function ExtractionTasksTable() {
  const params = useParams();
  const docId = params.docId;
  const { data: documents } = useGetExtractionTasksForDocQuery(docId, {
    skip: !docId,
    pollingInterval: 1000,
  });

  const tableState = useSelector(extractionTaskTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: any) => dispatch(setExtractionTaskTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback(
    (sort: any) => dispatch(setExtractionTaskTableSort(sort)),
    [dispatch]
  );

  return (
    <ReactDataGrid
      dataSource={documents || []}
      rowHeight={50}
      columns={columns}
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  );
}
