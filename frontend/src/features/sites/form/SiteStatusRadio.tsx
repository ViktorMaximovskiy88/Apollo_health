import { Form, Popconfirm, Radio, RadioChangeEvent } from 'antd';
import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { Site } from '../types';
import { SiteStatus } from '../siteStatus';
import { useUpdateSiteMutation } from '../sitesApi';
import { useCurrentUser } from '../../../common/hooks/use-current-user';

const siteStatuses = [
  { value: SiteStatus.New, label: 'New' },
  { value: SiteStatus.QualityHold, label: 'Quality Hold' },
  { value: SiteStatus.Inactive, label: 'Inactive' },
  { value: SiteStatus.Online, label: 'Online' },
];

export function SiteStatusRadio() {
  const form = Form.useFormInstance();
  const params = useParams();
  const [visible, setVisible] = useState(false);
  const currentUser = useCurrentUser();
  const [updateSite] = useUpdateSiteMutation();

  const isEditPage = (): boolean => !!params.siteId;
  const isAssignedToSelf = (): boolean => !!(currentUser?._id === form.getFieldValue('assignee'));
  const onChange = ({ target: { value } }: RadioChangeEvent) => {
    if (isEditPage() && isAssignedToSelf() && value === SiteStatus.Online) {
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
    <>
      <Popconfirm
        title="Keep site assignment or release?"
        visible={visible}
        onConfirm={release}
        onCancel={keep}
        okText="Release"
        cancelText="Keep"
        placement="bottomLeft"
      />
      <Form.Item name="status" label="Site Status">
        <Radio.Group
          options={siteStatuses}
          optionType="button"
          buttonStyle="solid"
          onChange={onChange}
        />
      </Form.Item>
    </>
  );
}
