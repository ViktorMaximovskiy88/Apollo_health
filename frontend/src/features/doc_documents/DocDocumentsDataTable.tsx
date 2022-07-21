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
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
} from './docDocumentsSlice';
import {
  prettyDateTimeFromISO,
  scrapeTaskStatusDisplayName,
  scrapeTaskStatusStyledDisplay,
} from '../../common';
import { ButtonLink, GridPaginationToolbar } from '../../components';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { TaskStatus } from '../../common';
import { Site } from '../sites/types';
import { useGetChangeLogQuery, useLazyGetDocDocumentsQuery } from './docDocumentApi';
import { DocDocument } from './types';
import { useInterval } from '../../common/hooks';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

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

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(docDocumentTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocDocumentTableSkip(skip)),
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

export function DocDocumentsDataTable() {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn(tableInfo);
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    [getDocDocumentsFn, watermark]
  );

  const filterProps = useDataTableFilter(docDocumentTableState, setDocDocumentTableFilter);
  const sortProps = useDataTableSort(docDocumentTableState, setDocDocumentTableSort);
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
