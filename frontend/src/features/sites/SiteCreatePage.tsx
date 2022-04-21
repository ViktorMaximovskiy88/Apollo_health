import Title from 'antd/lib/typography/Title';
import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useAddSiteMutation } from './sitesApi';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();

  async function tryAddSite(site: Partial<Site>) {
    await addSite(site);
    navigate('..');
  }

  return (
    <div>
      <div className="flex">
        <Title level={3}>Create Site</Title>
      </div>
      <SiteForm onFinish={tryAddSite} />
    </div>
  );
}
