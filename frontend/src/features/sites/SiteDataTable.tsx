import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Popconfirm, Tag, notification } from 'antd';
import { useCallback, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setSiteTableFilter,
  setSiteTableSort,
  siteTableState,
} from '../../app/uiSlice';
import {
  prettyDateTimeFromISO,
  statusDisplayName,
  statusStyledDisplay,
} from '../../common';
import { isErrorWithData } from '../../common/helpers';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { Status } from '../../common';
import {
  useDeleteSiteMutation,
  useGetChangeLogQuery,
  useGetSitesQuery,
} from './sitesApi';
import { Site } from './types';

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
      render: ({ value: status }: { value: Status }) => {
        return statusStyledDisplay(status);
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
            <ChangeLogModal
              target={site}
              useChangeLogQuery={useGetChangeLogQuery}
            />
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

export function SiteDataTable() {
  const { data: sites } = useGetSitesQuery(undefined, {
    pollingInterval: 5000,
  });
  const [deleteSite] = useDeleteSiteMutation();
  const columns = useMemo(() => createColumns(deleteSite), [deleteSite]);
  const tableState = useSelector(siteTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: any) => dispatch(setSiteTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback(
    (sort: any) => dispatch(setSiteTableSort(sort)),
    [dispatch]
  );

  const formattedSites = sites?.filter((u) => !u.disabled) || [];
  return (
    <ReactDataGrid
      dataSource={formattedSites}
      columns={columns}
      rowHeight={50}
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  );
}
