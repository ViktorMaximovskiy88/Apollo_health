import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './form/SiteForm';
import { useAddSiteMutation } from './sitesApi';
import { MainLayout } from '../../components';
import { useForm } from 'antd/lib/form/Form';
import { Button, Form, Space } from 'antd';
import { SiteSubmitButton } from './form/SiteSubmitButton';
import { Link } from 'react-router-dom';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();
  const [form] = useForm();

  async function tryAddSite(site: Partial<Site>) {
    await addSite(site);
    navigate('..');
  }

  return (
    <MainLayout
      sectionToolbar={
        <Form.Item className="m-1">
          <Space>
            <SiteSubmitButton form={form} />
            <Link to="/sites">
              <Button htmlType="submit">Cancel</Button>
            </Link>
          </Space>
        </Form.Item>
      }
    >
      <SiteForm onFinish={tryAddSite} form={form} />
    </MainLayout>
  );
}
