import values from 'lodash/values';
import { Button, Upload, Dropdown, Space, Menu, notification } from 'antd';
import { LoadingOutlined, UploadOutlined, DownOutlined, DownloadOutlined } from '@ant-design/icons';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import { useRunBulkMutation } from '../collections/siteScrapeTasksApi';
import { SiteDataTable } from './SiteDataTable';
import { QuickFilter } from './QuickFilter';
import { baseApiUrl, client, fetchWithAuth } from '../../app/base-api';
import { MainLayout } from '../../components';
import { isErrorWithData } from '../../common/helpers';
import { BulkActionTypes } from '../collections/types';

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

  const assignSites = async () => {
    const sites = values(selected);
    const resp = await updateMultipleSites(sites);
  };
  return <Button onClick={assignSites}>Assign to me</Button>;
}

function BulkActions() {
  const [runBulk] = useRunBulkMutation();
  const onMenuSelect = async (key: string) => {
    try {
      const response = await runBulk(key).unwrap();
      if (response.type === BulkActionTypes.Hold) {
        notification.success({
          message: 'Sites Held From Collections',
          description: `${response.scrapes} in progress scrape${
            response.scrapes === 1 ? ' was' : 's were'
          } canceled. ${response.sites} site${
            response.sites > 1 ? 's were' : ' was'
          } held until tomorrow.`,
        });
      } else if (response.type === BulkActionTypes.Cancel) {
        notification.success({
          message: 'Collections Canceled',
          description: `Canceled ${response.scrapes} scrape${
            response.scrapes === 1 ? '' : 's'
          } with queued or in progress collections.`,
        });
      } else if (response.type === BulkActionTypes.CancelHold) {
        notification.success({
          message: 'Hold Removed From Sites',
          description: `Holds removed from ${response.sites} site${
            response.sites === 1 ? '' : 's'
          }.`,
        });
      } else {
        notification.success({
          message: 'Collections Queued',
          description: `${response.scrapes} scrape${
            response.scrapes === 1 ? ' has' : 's have'
          } been added to the collection queue.`,
        });
      }
    } catch (err) {
      if (isErrorWithData(err)) {
        notification.error({
          message: 'Error Running Bulk Action',
          description: `${err.data.detail}`,
        });
      } else {
        notification.error({
          message: 'Error Running Bulk Action',
          description: JSON.stringify(err),
        });
      }
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
          key: 'cancel-hold-all',
          label: 'Cancel Hold All',
        },
        {
          key: 'hold-all',
          label: 'Hold All',
          danger: true,
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
