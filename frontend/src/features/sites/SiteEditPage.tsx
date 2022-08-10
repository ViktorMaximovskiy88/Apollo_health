import { Modal } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout } from '../../components';
import { SiteStatus } from './siteStatus';
import { useCurrentUser } from './useCurrentUser';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { SiteMenu } from '../sites/SiteMenu';

const { confirm } = Modal;

const useAlreadyAssignedModal = () => {
  const params = useParams();
  const [updateSite] = useUpdateSiteMutation();
  const { data: site } = useGetSiteQuery(params.siteId);
  const currentUser = useCurrentUser();
  const navigate = useNavigate();
  useEffect(() => {
    if (!site?._id) return;

    const assignCurrentUser = {
      _id: site._id,
      assignee: currentUser?._id,
      status: SiteStatus.QualityHold,
    };

    if (!site.assignee) {
      updateSite(assignCurrentUser);
      return;
    }

    if (site.assignee !== currentUser?._id) {
      confirm({
        title: 'Site Already Assigned',
        icon: <ExclamationCircleOutlined />,
        content: 'Site is already assigned. Would you like to take over assignment?',
        onOk: () => {
          updateSite(assignCurrentUser);
        },
        onCancel: () => {
          navigate(`/sites/${site._id}/view`);
        },
      });
    }
  }, [currentUser?._id, navigate, site?._id, site?.assignee, updateSite]);
};

export function SiteEditPage() {
  const params = useParams();
  const [updateSite] = useUpdateSiteMutation();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  useAlreadyAssignedModal();

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
    <MainLayout pageTitle={'Edit Site'} sidebar={<SiteMenu />}>
      <SiteForm onFinish={tryUpdateSite} initialValues={initialValues} />
    </MainLayout>
  );
}
