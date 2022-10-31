import { Button, Form, Modal, Space, Spin } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './form/SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout, Notification } from '../../components';
import { useCurrentUser } from '../../common/hooks/use-current-user';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { SiteMenu } from '../sites/SiteMenu';
import { useForm } from 'antd/lib/form/Form';
import { SiteSubmitButton } from './form/SiteSubmitButton';
import { Link } from 'react-router-dom';

const { confirm } = Modal;

const useAlreadyAssignedModal = () => {
  const { siteId } = useParams();
  const [updateSite] = useUpdateSiteMutation();
  const { data: site } = useGetSiteQuery(siteId);
  const currentUser = useCurrentUser();
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      if (!site?._id || !currentUser?._id) return;

      const assignCurrentUser = {
        _id: site._id,
        assignee: currentUser?._id,
      };

      if (!site.assignee) {
        await updateSite(assignCurrentUser);
        return;
      }

      if (site.assignee !== currentUser?._id) {
        confirm({
          title: 'Site Already Assigned',
          icon: <ExclamationCircleOutlined />,
          content: 'Site is already assigned. Would you like to take over assignment?',
          onOk: async () => {
            await updateSite(assignCurrentUser);
            navigate(`/sites/${site._id}/edit`);
          },
          onCancel: () => {
            navigate(`/sites/${site._id}/view`);
          },
        });
      }
    })();
  }, [currentUser, currentUser?._id, navigate, site?._id, site?.assignee, siteId, updateSite]);
};

export function SiteEditPage() {
  const [form] = useForm();
  const params = useParams();
  const [updateSite, { status, isSuccess, isError }] = useUpdateSiteMutation();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  useAlreadyAssignedModal();

  useEffect(() => {
    if (isSuccess && status === 'fulfilled') {
      Notification('success', 'Success', 'Site updated successfully');
      navigate('../scrapes');
    }
  }, [isSuccess, status]);
  useEffect(() => {
    if (isError && status === 'rejected') {
      Notification('error', 'Something went wrong!', 'An error occured while updating the site!');
      navigate('../scrapes');
    }
  }, [isError, status]);

  if (!site || !currentUser) return <Spin size="large" />;

  const initialValues = {
    ...site,
    assignee: currentUser._id,
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
  }
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <Form.Item className="m-1">
          <Space>
            <SiteSubmitButton form={form} />
            <Link to="/sites">
              <Button htmlType="submit">Cancel</Button>
            </Link>
          </Space>
        </Form.Item>
      }
    >
      <SiteForm onFinish={tryUpdateSite} initialValues={initialValues} form={form} />
    </MainLayout>
  );
}
