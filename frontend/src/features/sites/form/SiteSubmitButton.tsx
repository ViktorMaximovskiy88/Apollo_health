import { Button, Popconfirm } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { useNavigate, useParams } from 'react-router-dom';
import { useState } from 'react';
import { useLazyGetSiteQuery } from '../sitesApi';
import { useCurrentUser } from '../../../common/hooks/use-current-user';

export function SiteSubmitButton(props: { form: FormInstance }) {
  const params = useParams();
  const currentUser = useCurrentUser();
  const [visible, setVisible] = useState(false);
  const [getSite] = useLazyGetSiteQuery();
  const navigate = useNavigate();
  const confirm = () => {
    navigate('/');
  };
  const cancel = () => {
    navigate(`/sites/${params.siteId}/view`);
  };
  const letFormSubmit = () => props.form.submit();
  const isCreateSitePage = () => !params.siteId;
  const handleVisibleChange = async () => {
    if (isCreateSitePage()) {
      letFormSubmit();
      return;
    }
    const { data: site } = await getSite(params.siteId);
    if (site?.assignee !== currentUser?._id) {
      setVisible(true);
      return;
    }
    letFormSubmit();
  };
  return (
    <Popconfirm
      title="You are no longer the assignee for this site."
      okText="Navigate to sites page"
      cancelText="Navigate to view page"
      onConfirm={confirm}
      onCancel={cancel}
      visible={visible}
      onVisibleChange={handleVisibleChange}
    >
      <Button type="primary">Submit</Button>
    </Popconfirm>
  );
}
