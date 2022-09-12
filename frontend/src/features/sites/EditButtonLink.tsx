import { Button, Popconfirm } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { Site } from './types';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUpdateSiteMutation } from './sitesApi';
import { SiteStatus } from './siteStatus';
import { useCurrentUser } from '../../common/hooks/use-current-user';

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
