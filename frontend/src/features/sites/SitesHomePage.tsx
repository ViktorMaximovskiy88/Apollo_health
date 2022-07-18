import { Button, Layout, Upload, Dropdown, Space, Menu, notification } from 'antd';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useRunBulkMutation } from '../collections/siteScrapeTasksApi';
import { LoadingOutlined, UploadOutlined, DownOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import { SiteDataTable } from './SiteDataTable';
import { QuickFilter } from './QuickFilter';
import { PageLayout, PageHeader } from '../../components';
import { client, baseApiUrl } from '../../app/base-api';

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
    if (response.data.scrapes_launched === 0 || response.data.canceled_srapes === 0) {
      notification.error({
        message: 'Whoops!',
        description: 'No sites were found!',
      });
    } else if (response.data.canceled_srapes) {
      notification.success({
        message: 'Success!',
        description: `${response.data.canceled_srapes} site${
          response.data.canceled_srapes > 1 ? 's was' : ' were'
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

function BulkUpload() {
  const [uploading, setUploading] = useState(false);
  const [token, setToken] = useState('');
  useEffect(() => {
    client.getTokenSilently().then((t) => setToken(t));
  }, [setToken]);

  const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
    if (info.file.status === 'uploading') {
      setUploading(true);
    }
    if (info.file.status === 'done') {
      setUploading(false);
    }
  };
  return (
    <Button>
      <Upload
        name="file"
        accept=".csv,.txt,.xlsx"
        action={`${baseApiUrl}/sites/upload`}
        headers={{
          Authorization: `Bearer ${token}`,
        }}
        showUploadList={false}
        onChange={onChange}
      >
        {uploading ? <LoadingOutlined /> : <UploadOutlined />}
      </Upload>
    </Button>
  );
}

export function SitesHomePage() {
  const [isLoading, setLoading] = useState(false);
  return (
    <PageLayout>
      <PageHeader header={'Sites'}>
        <QuickFilter isLoading={isLoading} />
        <CreateSite />
        <BulkActions />
        <BulkUpload />
      </PageHeader>
      <SiteDataTable setLoading={setLoading} />
    </PageLayout>
  );
}
