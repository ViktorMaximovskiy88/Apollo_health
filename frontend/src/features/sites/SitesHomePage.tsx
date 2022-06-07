import { Button, Layout, Popconfirm, Table, Tag, Upload, Dropdown, Space, Menu } from 'antd';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { Site } from './types';
import {
  useDeleteSiteMutation,
  useGetChangeLogQuery,
  useGetSitesQuery,
} from './sitesApi';
import { useRunBulkMutation } from "../site_scrape_tasks/siteScrapeTasksApi";

import { SiteBreadcrumbs } from './SiteBreadcrumbs';
import { LoadingOutlined, UploadOutlined, DownOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import { ButtonLink } from '../../components/ButtonLink';

export function SitesHomePage() {
    const { data: sites, refetch } = useGetSitesQuery();
    const [deleteSite] = useDeleteSiteMutation();
    const [ runBulk ] = useRunBulkMutation();
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
          title: 'Tags',
          key: 'tags',
          render: (site: Site) => {
            return site.tags.filter((tag) => tag).map((tag) => {
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
          refetch()
        }
    }
    const onMenuSelect = (key: string) => {
        runBulk(key)
        refetch()
    }
    const menu = (
      <Menu
        onClick={({key}) => onMenuSelect(key)}
        items={[
          {
            key: 'unrun',
            label: "Run Unrun"
          },
          {
            key: 'failed',
            label: "Run Failed"
          },
          {
            key: 'all',
            label: "Run All",
            danger: true
          }
        ]}
      />
    );
    return (
        <Layout className="p-4 bg-transparent">
          <div className="flex">
            <SiteBreadcrumbs />
            <div className="ml-auto space-x-2">
              <Link to="new">
                <Button>Create Site</Button>
              </Link>
              <Dropdown overlay={menu}>
                <Space>
                    <Button>Run <DownOutlined style={{fontSize:"10px"}} /></Button>
                </Space>
              </Dropdown>
              <Upload name="file" accept=".csv,.txt,.xlsx" action="/api/v1/sites/upload" showUploadList={false} onChange={onChange}>
                <Button icon={uploading ? <LoadingOutlined/> : <UploadOutlined/>} />
              </Upload>
            </div>
          </div>
          <Table dataSource={formattedSites} columns={columns} />
        </Layout>
    );
}






