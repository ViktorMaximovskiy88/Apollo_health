import { useState } from 'react';
import Title from 'antd/lib/typography/Title';
import { Layout } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';

export function SiteViewPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const [readOnly, setReadOnly] = useState(true);

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
        <Title level={4}>{readOnly ? 'View' : 'Edit'} Site</Title>
      </div>
      <SiteForm
        readOnly={readOnly}
        setReadOnly={setReadOnly}
        initialValues={site}
        onFinish={tryUpdateSite}
      />
    </Layout>
  );
}
