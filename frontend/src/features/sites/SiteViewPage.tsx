import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery } from './sitesApi';
import { Layout } from 'antd';

export function SiteViewPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  if (!site) return null;

  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <Title level={4}>View Site</Title>
      </div>
      <SiteForm readOnly initialValues={site} onFinish={() => {}} />
    </Layout>
  );
}
