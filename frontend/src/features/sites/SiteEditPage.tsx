import Title from 'antd/lib/typography/Title';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { Layout } from 'antd';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';

export function SiteEditPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  if (!site) return null;

  async function tryUpdateSite(update: Partial<Site>) {
    update._id = params.siteId;
    await updateSite(update);
    if (
      site!.collection_method === CollectionMethod.Automated &&
      update.collection_method === CollectionMethod.Manual
    ) {
      await cancelAllScrapes(params.siteId);
    }
    navigate(-1);
  }
  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <Title level={4}>Edit Site</Title>
      </div>
      <SiteForm onFinish={tryUpdateSite} initialValues={site} />
    </Layout>
  );
}
