import { Button, Layout, Popconfirm, Table, Tag, Upload } from 'antd';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { Site } from './types';
import {
  useDeleteSiteMutation,
  useGetChangeLogQuery,
  useGetSitesQuery,
} from './sitesApi';
import { SiteBreadcrumbs } from './SiteBreadcrumbs';
import { LoadingOutlined, UploadOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import { ButtonLink } from '../../components/ButtonLink';
import { format, parseISO } from 'date-fns';

export function SitesHomePage() {
  const { data: sites, refetch } = useGetSitesQuery(undefined, {
    pollingInterval: 5000,
  });
  const [deleteSite] = useDeleteSiteMutation();
  const [uploading, setUploading] = useState(false);
  const formattedSites =
    sites?.filter((u) => !u.disabled).map((u) => ({ ...u, key: u._id })) || [];
  const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];
  const columns = [
    {
      title: 'Name',
      key: 'name',
      render: (site: Site) => {
        return <ButtonLink to={`${site._id}/scrapes`}>{site.name}</ButtonLink>;
      },
    },
    {
      title: 'Last Run Time',
      key: 'last_run_time',
      render: (site: Site) => {
        if (!site.last_run_time) return null;
        return <>{format(parseISO(site.last_run_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Last Status',
      key: 'last_status',
      render: (site: Site) => {
        const status = site.last_status;
        if (status === 'FINISHED') {
          return <span className="text-green-500">Success</span>;
        } else if (status === 'CANCELED') {
          return <span className="text-orange-500">Forced End</span>;
        } else if (status === 'QUEUED') {
          return <span className="text-yellow-500">Queued</span>;
        } else if (status === 'FAILED') {
          return <span className="text-red-500">Failed</span>;
        } else if (status === 'IN_PROGRESS') {
          return <span className="text-blue-500">In Progress</span>;
        }
        return <></>;
      },
    },
    {
      title: 'Tags',
      key: 'tags',
      render: (site: Site) => {
        return site.tags
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
      title: 'Actions',
      key: 'action',
      render: (site: Site) => {
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
              onConfirm={() => deleteSite(site)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];
  const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
    if (info.file.status === 'uploading') {
      setUploading(true);
    }
    if (info.file.status === 'done') {
      setUploading(false);
      refetch();
    }
  };
  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <SiteBreadcrumbs />
        <div className="ml-auto space-x-2">
          <Link to="new">
            <Button>Create Site</Button>
          </Link>
          <Upload
            name="file"
            accept=".csv,.txt,.xlsx"
            action="/api/v1/sites/upload"
            showUploadList={false}
            onChange={onChange}
          >
            <Button
              icon={uploading ? <LoadingOutlined /> : <UploadOutlined />}
            />
          </Upload>
        </div>
      </div>
      <Table dataSource={formattedSites} columns={columns} />
    </Layout>
  );
}
