import Title from 'antd/lib/typography/Title';
import { useNavigate, useParams } from 'react-router-dom';
import { Site } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { Layout } from 'antd';

export function SiteEditPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const navigate = useNavigate();
  if (!site) return null;

  async function tryUpdateSite(site: Partial<Site>) {
    site._id = params.siteId;
    await updateSite(site);
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
