import { Button, Layout, Upload, Dropdown, Space, Menu, notification } from 'antd';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useRunBulkMutation } from '../collections/siteScrapeTasksApi';

import { SiteBreadcrumbs } from './SiteBreadcrumbs';
import { LoadingOutlined, UploadOutlined, DownOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';

import { SiteDataTable } from './SiteDataTable';
import { client } from '../../app/base-api';
import { QuickFilter } from './QuickFilter';

function BulkUpload() {
  const [uploading, setUploading] = useState(false);
  const [token, setToken] = useState('');
  useEffect(() => {
    client.getTokenSilently().then((t) => setToken(t));
  }, [setToken]);

  const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
    console.log(info);
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
      headers={{
        Authorization: `Bearer ${token}`,
      }}
      showUploadList={false}
      onChange={onChange}
    >
      <Button icon={uploading ? <LoadingOutlined /> : <UploadOutlined />} />
    </Upload>
  );
}

function CreateSite() {
  return (
    <Link to="new">
      <Button>Create Site</Button>
    </Link>
  );
}

function BulkActions() {
  const [runBulk] = useRunBulkMutation();
  const onMenuSelect = async (key: string) => {
    const response: any = await runBulk(key);
    if (response.data.scrapes_launched === 0 || response.data.canceled_scrapes === 0) {
      notification.error({
        message: 'Whoops!',
        description: 'No sites were found!',
      });
    } else if (response.data.canceled_scrapes) {
      notification.success({
        message: 'Success!',
        description: `${response.data.canceled_scrapes} site${
          response.data.canceled_scrapes > 1 ? 's were' : ' was'
        } canceled from the collection queue!`,
      });
    } else {
      notification.success({
        message: 'Success!',
        description: `${response.data.scrapes_launched} site${
          response.data.scrapes_launched > 1 ? 's have' : ' has'
        } been added to the collection queue!`,
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
          key: 'canceled',
          label: 'Run Canceled',
        },
        {
          key: 'cancel-active',
          label: 'Cancel Active',
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
          Collection <DownOutlined className="text-sm" />
        </Button>
      </Space>
    </Dropdown>
  );
}

export function SitesHomePage() {
  const [isLoading, setLoading] = useState(false);
  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <SiteBreadcrumbs />
        <div className="ml-auto space-x-2">
          <QuickFilter isLoading={isLoading} />
          <CreateSite />
          <BulkActions />
          <BulkUpload />
        </div>
      </div>
      <SiteDataTable setLoading={setLoading} />
    </Layout>
  );
}
