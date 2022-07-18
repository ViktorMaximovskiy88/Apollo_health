import { Layout } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useAddSiteMutation } from './sitesApi';
import { PageHeader, PageLayout } from '../../components';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();

  async function tryAddSite(site: Partial<Site>) {
    await addSite(site);
    navigate('..');
  }

  return (
    <PageLayout>
      <PageHeader header={'Create Site'} />
      <SiteForm onFinish={tryAddSite} />
    </PageLayout>
  );
}
