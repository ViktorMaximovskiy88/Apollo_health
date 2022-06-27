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
import { prettyDateDistance, prettyDateFromISO } from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { Status } from '../../common/types';
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
        { id: Status.Finished, label: 'Success' },
        { id: Status.Canceled, label: 'Canceled' },
        { id: Status.Queued, label: 'Queued' },
        { id: Status.Failed, label: 'Failed' },
        { id: Status.InProgress, label: 'In Progress' },
      ],
    },
    render: ({ value: status }: { value: Status }) => {
      switch (status) {
        case Status.Finished:
          return <span className="text-green-500">Success</span>;
        case Status.Canceled:
          return <span className="text-orange-500">Canceled</span>;
        case Status.Queued:
          return <span className="text-yellow-500">Queued</span>;
        case Status.Failed:
          return <span className="text-red-500">Failed</span>;
        case Status.InProgress:
          return <span className="text-blue-500">In Progress</span>;
        default:
          return null;
      }
    },
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
