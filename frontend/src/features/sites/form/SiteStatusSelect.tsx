import { Form, Popconfirm, Select } from 'antd';
import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { Site } from '../types';
import { SiteStatus } from '../siteStatus';
import { FormInstance } from 'antd/lib/form/Form';
import { useUpdateSiteMutation } from '../sitesApi';
import { useCurrentUser } from '../../../common/hooks/use-current-user';

const siteStatuses = [
  { value: SiteStatus.New, label: 'New' },
  { value: SiteStatus.QualityHold, label: 'Quality Hold' },
  { value: SiteStatus.Inactive, label: 'Inactive' },
  { value: SiteStatus.Online, label: 'Online' },
];

export function SiteStatusSelect({ form }: { form: FormInstance }) {
  const params = useParams();
  const [visible, setVisible] = useState(false);
  const currentUser = useCurrentUser();
  const [updateSite] = useUpdateSiteMutation();

  const onEditPage = (): boolean => !!params.siteId;
  const onSelect = (_: string, { value }: { value: string }) => {
    if (onEditPage() && value === SiteStatus.Online) {
      setVisible(true);
    }
  };
  const release = async () => {
    if (!currentUser?._id) {
      throw new Error(`Current user id not found. Found instead: ${currentUser?._id}`);
    }
    const update: Partial<Site> = {
      _id: params.siteId,
      assignee: undefined,
    };
    await updateSite(update);
    form.setFieldsValue({ assignee: null });
    setVisible(false);
  };
  const keep = () => {
    setVisible(false);
  };

  return (
    <Popconfirm
      title="Keep site assignment or release?"
      visible={visible}
      onConfirm={release}
      onCancel={keep}
      okText="Release"
      cancelText="Keep"
    >
      <Form.Item name="status" label="Site Status">
        <Select options={siteStatuses} onSelect={onSelect} />
      </Form.Item>
    </Popconfirm>
  );
}
