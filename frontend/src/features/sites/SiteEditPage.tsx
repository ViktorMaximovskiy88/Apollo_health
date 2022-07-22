import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout } from '../../components';
import { SiteStatus } from './siteStatus';
import { useAuth0 } from '@auth0/auth0-react';
import { useGetUsersQuery } from '../users/usersApi';
import { User } from '../users/types';

const useCurrentUser = (): User | undefined => {
  const { user: auth0User } = useAuth0();
  const { data: users } = useGetUsersQuery();
  const currentUser: User | undefined = users?.find((user) => user.email === auth0User?.email);
  return currentUser;
};

export function SiteEditPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  if (!site) return null;

  const initialValues = {
    ...site,
    assignee: currentUser?._id,
    status: SiteStatus.QualityHold,
  };

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
    <MainLayout pageTitle={'Edit Site'}>
      <SiteForm onFinish={tryUpdateSite} initialValues={initialValues} />
    </MainLayout>
  );
}
