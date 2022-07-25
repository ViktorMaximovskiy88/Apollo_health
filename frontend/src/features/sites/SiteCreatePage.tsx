import { Layout } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useAddSiteMutation } from './sitesApi';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();

  async function tryAddSite(site: Partial<Site>) {
    console.log(site)
    await addSite(site);
    // navigate('..');
  }

  return (
    <Layout className="bg-transparent p-4">
      <div className="flex">
        <Title level={3}>Create Site</Title>
      </div>
      <SiteForm onFinish={tryAddSite} />
    </Layout>
  );
}
