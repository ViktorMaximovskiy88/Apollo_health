import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Tag } from 'antd';
import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setDocDocumentTableFilter,
  setDocDocumentTableSort,
  docDocumentTableState,
} from '../../app/uiSlice';
import {
  prettyDateTimeFromISO,
  scrapeTaskStatusDisplayName,
  scrapeTaskStatusStyledDisplay,
} from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { TaskStatus } from '../../common';
import { Site } from '../sites/types';
import { useGetChangeLogQuery, useLazyGetDocDocumentsQuery } from './docDocumentApi';
import { DocDocument } from './types';

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

const columns = [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: doc }: { data: DocDocument }) => {
      return <ButtonLink to={`${doc._id}`}>{doc.name}</ButtonLink>;
    },
    defaultFlex: 1,
  },
  {
    header: 'First Collected Date',
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
    render: ({ data: doc }: { data: DocDocument }) => {
      if (!doc.first_collected_date) return null;
      return prettyDateTimeFromISO(doc.first_collected_date);
    },
  },
  {
    header: 'Last Collected Date',
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
    render: ({ data: doc }: { data: DocDocument }) => {
      if (!doc.last_collected_date) return null;
      return prettyDateTimeFromISO(doc.last_collected_date);
    },
  },
  {
    header: 'Classification Status',
    name: 'classification_status',
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: [
        { id: TaskStatus.Finished, label: scrapeTaskStatusDisplayName(TaskStatus.Finished) },
        { id: TaskStatus.Canceled, label: scrapeTaskStatusDisplayName(TaskStatus.Canceled) },
        { id: TaskStatus.Queued, label: scrapeTaskStatusDisplayName(TaskStatus.Queued) },
        { id: TaskStatus.Failed, label: scrapeTaskStatusDisplayName(TaskStatus.Failed) },
        {
          id: TaskStatus.InProgress,
          label: scrapeTaskStatusDisplayName(TaskStatus.InProgress),
        },
      ],
    },
    render: ({ data: doc }: { data: DocDocument }) => {
      return scrapeTaskStatusStyledDisplay(doc.classification_status);
    },
  },
  {
    header: 'Tags',
    name: 'tags',
    render: ({ data: doc }: { data: DocDocument }) => {
      return doc.tags
        .filter((tag) => tag)
        .map((tag) => {
          const simpleHash = tag
            .split('')
            .map((c) => c.charCodeAt(0))
            .reduce((a, b) => a + b);
          const color = colors[simpleHash % colors.length];
          return (
            <Tag color={color} key={tag}>
              {tag}
            </Tag>
          );
        });
    },
  },
  {
    header: 'Actions',
    name: 'action',
    minWidth: 180,
    render: ({ data: site }: { data: Site }) => {
      return (
        <>
          <ChangeLogModal target={site} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      );
    },
  },
];

export function DocDocumentsDataTable() {
  const tableState = useSelector(docDocumentTableState);
  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: any) => dispatch(setDocDocumentTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback(
    (sort: any) => dispatch(setDocDocumentTableSort(sort)),
    [dispatch]
  );

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn(tableInfo);
      const sites = data?.data || [];
      const count = data?.total || 0;
      return { data: sites, count };
    },
    [getDocDocumentsFn]
  );

  return (
    <ReactDataGrid
      dataSource={loadData}
      columns={columns}
      rowHeight={50}
      pagination
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  );
}
