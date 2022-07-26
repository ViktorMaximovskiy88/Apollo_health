import { useNavigate } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useAddSiteMutation } from './sitesApi';
import { MainLayout } from '../../components';

export function SiteCreatePage() {
  const [addSite] = useAddSiteMutation();
  const navigate = useNavigate();

  async function tryAddSite(site: Partial<Site>) {
    console.log(site)
    await addSite(site);
    // navigate('..');
  }

  return (
    <MainLayout pageTitle={'Create Site'}>
      <SiteForm onFinish={tryAddSite} />
    </MainLayout>
  );
}
