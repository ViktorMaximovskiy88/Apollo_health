import {
  Button,
  Layout,
  Upload,
  Dropdown,
  Space,
  Menu,
  notification,
} from 'antd';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useRunBulkMutation } from '../collections/siteScrapeTasksApi';

import { SiteBreadcrumbs } from './SiteBreadcrumbs';
import {
  LoadingOutlined,
  UploadOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';

import { SiteDataTable } from './SiteDataTable';

function BulkUpload() {
  const [uploading, setUploading] = useState(false);

  const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
    if (info.file.status === 'uploading') {
      setUploading(true);
    }
    if (info.file.status === 'done') {
      setUploading(false);
    }
  };
  return (
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
  )
}

function BulkActions() {
  const [runBulk] = useRunBulkMutation();
  const onMenuSelect = async (key: string) => {
    const response: any = await runBulk(key);
    if (response.data.scrapes_launched === 0) {
      notification.error({
        message: 'Whoops!',
        description: 'No sites were found!',
      });
    } else {
      notification.success({
        message: 'Success!',
        description:
          response.data.scrapes_launched +
          ' sites are added to the collection queue!',
      });
    }
  };
  const menu = (
    <Menu
      onClick={({ key }) => onMenuSelect(key)}
      items={[
        {
          key: 'unrun',
          label: 'Run Unrun',
        },
        {
          key: 'failed',
          label: 'Run Failed',
        },
        {
          key: 'all',
          label: 'Run All',
          danger: true,
        },
      ]}
    />
  );
  return (
    <Dropdown overlay={menu}>
      <Space>
        <Button>
          Run <DownOutlined className="text-sm" />
        </Button>
      </Space>
    </Dropdown>
  )
}

export function SitesHomePage() {
  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <SiteBreadcrumbs />
        <div className="ml-auto space-x-2">
          <Link to="new">
            <Button>Create Site</Button>
          </Link>
          <BulkActions />
          <BulkUpload />
        </div>
      </div>
      <SiteDataTable />
    </Layout>
  );
}
