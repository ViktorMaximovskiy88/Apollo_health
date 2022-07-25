import { Button, Popconfirm } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { Site } from './types';
import { SiteStatus } from './siteStatus';
import { useAuth0 } from '@auth0/auth0-react';
import { useGetUsersQuery } from '../users/usersApi';
import { User } from '../users/types';
import { useUpdateSiteMutation } from './sitesApi';

const useCurrentUser = (): User | undefined => {
  const { user: auth0User } = useAuth0();
  const { data: users } = useGetUsersQuery();
  const currentUser: User | undefined = users?.find((user) => user.email === auth0User?.email);
  return currentUser;
};

interface ToggleReadOnlyPropTypes {
  form: FormInstance;
  setReadOnly?: (readOnly: boolean) => void;
}
export function ToggleReadOnly({ setReadOnly, form }: ToggleReadOnlyPropTypes) {
  const currentUser = useCurrentUser();
  const [visible, setVisible] = useState(false);
  const [updateSite] = useUpdateSiteMutation();
  const params = useParams();

  const confirm = async () => {
    if (!currentUser?._id) {
      throw new Error(`Current user id not found. Found instead: ${currentUser?._id}`);
    }
    const update: Partial<Site> = {
      _id: params.siteId,
      assignee: currentUser._id,
      status: SiteStatus.QualityHold,
    };
    await updateSite(update);
    setReadOnly?.(false);
    form.setFieldsValue({
      assignee: currentUser?._id,
      status: SiteStatus.QualityHold,
    });
  };
  const cancel = () => {
    setVisible(false);
  };

  const handleVisibleChange = () => {
    const siteAssignee = form.getFieldValue('assignee');
    if (!siteAssignee || siteAssignee === currentUser?._id) {
      confirm();
    } else {
      setVisible(true);
    }
  };

  return (
    <Popconfirm
      title="Site is already assigned. Would you like to take over assignment?"
      okText="Yes"
      cancelText="No"
      onConfirm={confirm}
      onCancel={cancel}
      visible={visible}
      onVisibleChange={handleVisibleChange}
    >
      <Button type="primary">Edit Site</Button>
    </Popconfirm>
  );
}
