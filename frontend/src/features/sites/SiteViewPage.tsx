import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';

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
    <MainLayout pageTitle={`${readOnly ? 'View' : 'Edit'} Site`} sidebar={<SiteMenu />}>
      <SiteForm
        readOnly={readOnly}
        setReadOnly={setReadOnly}
        initialValues={site}
        onFinish={tryUpdateSite}
      />
    </MainLayout>
  );
}
