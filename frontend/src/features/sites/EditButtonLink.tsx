import { Button, Popconfirm } from 'antd';
import { EditOutlined } from '@ant-design/icons';

import { Site } from './types';
import { useGetUsersQuery } from '../users/usersApi';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from '../users/types';
import { useAuth0 } from '@auth0/auth0-react';
import { useUpdateSiteMutation } from './sitesApi';
import { SiteStatus } from './siteStatus';

const useCurrentUser = (): User | undefined => {
  const { user: auth0User } = useAuth0();
  const { data: users } = useGetUsersQuery();
  const currentUser: User | undefined = users?.find((user) => user.email === auth0User?.email);
  return currentUser;
};
export const EditButtonLink = ({ site }: { site: Site }): JSX.Element => {
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [visible, setVisible] = useState(false);
  const [updateSite] = useUpdateSiteMutation();

  const confirm = async () => {
    if (!currentUser?._id) {
      throw new Error(`Current user id not found. Found instead: ${currentUser?._id}`);
    }
    const update = { _id: site._id, assignee: currentUser?._id, status: SiteStatus.QualityHold };
    await updateSite(update);
    navigate(`${site._id}/edit`);
  };
  const cancel = () => {
    setVisible(false);
  };

  const handleVisibleChange = () => {
    const siteAssignee = site.assignee;
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
      <Button type="link" size="small">
        <EditOutlined />
      </Button>
    </Popconfirm>
  );
};
