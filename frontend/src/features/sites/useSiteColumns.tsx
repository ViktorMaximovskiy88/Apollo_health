import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Popconfirm, Tag, notification } from 'antd';
import { EditOutlined, InfoCircleOutlined } from '@ant-design/icons';
import {
  prettyDateTimeFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
} from '../../common';
import { isErrorWithData } from '../../common/helpers';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './sitesApi';
import { Site } from './types';
import { SiteStatus, siteStatusDisplayName, siteStatusStyledDisplay } from './siteStatus';
import { ReactNode, useMemo } from 'react';
import { User } from '../users/types';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

interface CreateColumnsType {
  deleteSite: any;
  setDeletedSite: (site: string) => void;
  users?: User[];
}
const createColumns = ({ deleteSite, setDeletedSite, users }: CreateColumnsType) => {
  async function handleDeleteSite(site: Site) {
    try {
      await deleteSite(site).unwrap();
      notification.success({
        message: 'Site Deleted',
        description: `Successfully deleted ${site.name}`,
      });
      setDeletedSite(site._id);
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
      minWidth: 300,
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
      header: 'Last Run Document Count',
      name: 'last_run_documents',
      filterEditor: NumberFilter,
      minWidth: 200,
    },
    {
      header: 'Assignee',
      name: 'assignee',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: users ? users.map((user) => ({ id: user._id, label: user.full_name })) : [],
      },
      render: ({ value: id }: { value: string }): ReactNode => {
        const [assignee] = users?.filter((user) => user._id === id) ?? [];
        return <>{assignee?.full_name}</>;
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
            <ButtonLink to={`${site._id}/view`}>
              <InfoCircleOutlined />
            </ButtonLink>
            <ButtonLink to={`${site._id}/edit`}>
              <EditOutlined />
            </ButtonLink>
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

export const useColumns = ({
  deleteSite,
  setDeletedSite,
  users,
}: CreateColumnsType): TypeColumn[] =>
  useMemo(
    () => createColumns({ deleteSite, setDeletedSite, users }),
    [deleteSite, setDeletedSite, users]
  );
