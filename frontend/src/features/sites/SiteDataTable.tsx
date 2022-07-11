import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import PaginationToolbar from '@inovua/reactdatagrid-community/packages/PaginationToolbar';
import { Popconfirm, Tag, notification, Switch } from 'antd';
import React, { ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSiteTableFilter, setSiteTableSort, siteTableState } from '../../app/uiSlice';
import {
  prettyDateTimeFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
} from '../../common';
import { isErrorWithData } from '../../common/helpers';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useDeleteSiteMutation, useGetChangeLogQuery, useLazyGetSitesQuery } from './sitesApi';
import { Site } from './types';
import { SiteStatus, siteStatusDisplayName, siteStatusStyledDisplay } from './siteStatus';
import useInterval from '../../app/use-interval';

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

const createColumns = (deleteSite: any) => {
  async function handleDeleteSite(site: Site) {
    try {
      await deleteSite(site).unwrap();
      notification.success({
        message: 'Site Deleted',
        description: `Successfully deleted ${site.name}`,
      });
    } catch (err) {
      if (isErrorWithData(err)) {
        notification.error({
          message: `Can't Delete ${site.name}`,
          description: `${err.data.detail}`,
        });
      } else {
        notification.error({
          message: "Can't Delete Site",
          description: JSON.stringify(err),
        });
      }
    }
  }

  return [
    {
      header: 'Name',
      name: 'name',
      render: ({ data: site }: { data: Site }) => {
        return <ButtonLink to={`${site._id}/scrapes`}>{site.name}</ButtonLink>;
      },
      defaultFlex: 1,
    },
    {
      header: 'Site Status',
      name: 'status',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: [
          {
            id: SiteStatus.New,
            label: siteStatusDisplayName(SiteStatus.New),
          },
          {
            id: SiteStatus.QualityHold,
            label: siteStatusDisplayName(SiteStatus.QualityHold),
          },
          {
            id: SiteStatus.Online,
            label: siteStatusDisplayName(SiteStatus.Online),
          },
          {
            id: SiteStatus.Inactive,
            label: siteStatusDisplayName(SiteStatus.Inactive),
          },
        ],
      },
      render: ({ value: status }: { value: SiteStatus }) => {
        return siteStatusStyledDisplay(status);
      },
    },
    {
      header: 'Last Run Time',
      name: 'last_run_time',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ value: last_run_time }: { value: string | undefined }) => {
        if (!last_run_time) return null;
        return prettyDateTimeFromISO(last_run_time);
      },
    },
    {
      header: 'Last Run Status',
      name: 'last_run_status',
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
      render: ({ value: status }: { value: TaskStatus }) => {
        return styledDisplay(status);
      },
    },
    {
      header: 'Tags',
      name: 'tags',
      render: ({ value }: { value: string[] }) => {
        return value
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
            <ButtonLink to={`${site._id}/edit`}>Edit</ButtonLink>
            <ChangeLogModal target={site} useChangeLogQuery={useGetChangeLogQuery} />
            <Popconfirm
              title={`Are you sure you want to delete '${site.name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => handleDeleteSite(site)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];
};

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

export function SiteDataTable() {
  const tableState = useSelector(siteTableState);
  const [getSitesFn] = useLazyGetSitesQuery();
  const [deleteSite] = useDeleteSiteMutation();
  const columns = useMemo(() => createColumns(deleteSite), [deleteSite]);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: any) => dispatch(setSiteTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback((sort: any) => dispatch(setSiteTableSort(sort)), [dispatch]);

  // Trigger update every 10 seconds by invalidating memoized callback
  const { setActive, isActive, watermark } = useInterval(10000);
  const [userInteraction, setUserInteraction] = useState<boolean>(false);

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getSitesFn(tableInfo);
      const sites = data?.data || [];
      const count = data?.total || 0;
      return { data: sites, count };
    },
    [getSitesFn, watermark]
  );

  const renderPaginationToolbar = useCallback(
    (paginationProps: any) => {
      return (
        <div className="flex flex-col">
          <PaginationToolbar
            {...paginationProps}
            bordered={false}
            style={{ width: 'fit-content' }}
            onClick={(e: React.SyntheticEvent) => {
              // we dont get individual click handlers
              // so if _anything_ in the pager is clicked except refresh; cancel
              if (e.target instanceof Element) {
                const isRefresh = e.target.classList.contains(
                  'inovua-react-pagination-toolbar__icon--named--REFRESH'
                );
                if (!isRefresh) setActive(false);
              }
            }}
          />
          <div
            className="flex justify-end items-end box-border leading-[2.5rem] h-[42px]"
            style={{
              borderTop: '2px solid #e4e3e2',
            }}
          >
            <div className="mx-4">
              <label className="cursor-pointer select-none">
                <Switch defaultChecked={isActive} checked={isActive} onChange={setActive} />
                &nbsp;&nbsp;Auto-refresh
              </label>
            </div>
          </div>
        </div>
      );
    },
    [isActive]
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
      renderLoadMask={disableLoadingMask}
      renderPaginationToolbar={renderPaginationToolbar}
      activateRowOnFocus={false}
    />
  );
}
