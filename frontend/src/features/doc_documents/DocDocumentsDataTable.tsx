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
import { prettyDateTimeFromISO } from '../../common';
import { ButtonLink, GridPaginationToolbar } from '../../components';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { Site } from '../sites/types';
import { useGetChangeLogQuery, useLazyGetDocDocumentsQuery } from './docDocumentApi';
import { DocDocument } from './types';
import { useInterval } from '../../common/hooks';
import {
  ApprovalStatus,
  approvalStatusDisplayName,
  approvalStatusStyledDisplay,
} from '../../common/approvalStatus';

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
      dataSource: Object.values(ApprovalStatus).map((status) => ({
        id: status,
        label: approvalStatusDisplayName(status),
      })),
    },
    render: ({ data: doc }: { data: DocDocument }) => {
      return approvalStatusStyledDisplay(doc.classification_status);
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

  // Trigger update every 10 seconds by invalidating memoized callback
  const { setActive, isActive, watermark } = useInterval(10000);

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn(tableInfo);
      const sites = data?.data || [];
      const count = data?.total || 0;
      return { data: sites, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getDocDocumentsFn, watermark]
  );

  const renderPaginationToolbar = useCallback(
    (paginationProps: any) => {
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
      renderLoadMask={() => <></>}
      renderPaginationToolbar={renderPaginationToolbar}
      activateRowOnFocus={false}
    />
  );
}
