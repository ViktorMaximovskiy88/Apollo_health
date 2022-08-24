import values from 'lodash/values';
import { Button, Upload, Dropdown, Space, Menu, notification } from 'antd';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useRunBulkMutation } from '../collections/siteScrapeTasksApi';
import { LoadingOutlined, UploadOutlined, DownOutlined, DownloadOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import { SiteDataTable } from './SiteDataTable';
import { QuickFilter } from './QuickFilter';
import { baseApiUrl, client, fetchWithAuth } from '../../app/base-api';
import { MainLayout } from '../../components';

import { useUpdateMultipleSitesMutation } from './sitesApi';
import { Site } from './types';

function CreateSite() {
  return (
    <Link to="new">
      <Button>Create Site</Button>
    </Link>
  );
}

interface AssignTypes {
  selected: Object;
  setSelected: any;
}

function Assign({ selected, setSelected }: AssignTypes) {
  const [updateMultipleSites] = useUpdateMultipleSitesMutation();

  const assign = async () => {
    let temp = values(selected);
    let g = await updateMultipleSites(temp);
    console.log(g);
  };
  return <Button onClick={assign}>Assign to me</Button>;
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
          key: 'new',
          label: 'Run New',
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
        accept=".csv,.txt,.xlsx,.json"
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

function BulkDownload() {
  const downloadJson = () => {
    fetchWithAuth(`${baseApiUrl}/sites/download`)
      .then((res) => {
        return res.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sites.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
  };

  return (
    <Button onClick={downloadJson}>
      <DownloadOutlined />
    </Button>
  );
}

export function SitesHomePage() {
  const [isLoading, setLoading] = useState(false);
  const [selected, setSelected] = useState<{ [id: string]: Site }>({});
  return (
    <MainLayout
      pageToolbar={
        <>
          <QuickFilter isLoading={isLoading} />
          <Assign selected={selected} setSelected={setSelected} />
          <CreateSite />
          <BulkActions />
          <BulkUpload />
          <BulkDownload />
        </>
      }
    >
      <SiteDataTable setLoading={setLoading} selected={selected} setSelected={setSelected} />
    </MainLayout>
  );
}
