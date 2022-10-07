import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './form/SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { ButtonLink, MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { useForm } from 'antd/lib/form/Form';

export function SiteViewPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const navigate = useNavigate();
  const [form] = useForm();

  if (!site) return null;

  async function tryUpdateSite(update: Partial<Site>) {
    update._id = params.siteId;
    await updateSite(update);
    navigate(-1);
  }

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <ButtonLink type="primary" to={`/sites/${site._id}/edit`}>
          Edit Site
        </ButtonLink>
      }
    >
      <SiteForm initialValues={site} onFinish={tryUpdateSite} form={form} />
    </MainLayout>
  );
}
