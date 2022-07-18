import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useAddSiteMutation } from './sitesApi';
import { PageLayout } from '../../components';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();

  async function tryAddSite(site: Partial<Site>) {
    await addSite(site);
    navigate('..');
  }

  return (
    <PageLayout title={'Create Site'}>
      <SiteForm onFinish={tryAddSite} />
    </PageLayout>
  );
}
