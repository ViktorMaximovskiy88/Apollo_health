import { Button, Form, Modal, Space, Spin } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './form/SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout } from '../../components';
import { useCurrentUser } from '../../common/hooks/use-current-user';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { SiteMenu } from '../sites/SiteMenu';
import { useForm } from 'antd/lib/form/Form';
import { SiteSubmitButton } from './form/SiteSubmitButton';
import { Link } from 'react-router-dom';
import { useNotifyMutation } from '../../common/hooks/use-notify-mutation';

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
  const [updateSite, result] = useUpdateSiteMutation();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  useAlreadyAssignedModal();

  useNotifyMutation(
    result,
    { description: 'Site Updated Successfully.' },
    { description: 'An error occurred while updating the Site.' }
  );

  useEffect(() => {
    if (result.isSuccess || result.isError) navigate('../scrapes');
  }, [result.isSuccess, result.isError]);

  if (!site || !currentUser) return <Spin size="large" />;

  const initialValues = {
    ...site,
    assignee: currentUser._id,
  };

  console.log(site);

  async function tryUpdateSite(update: Partial<Site>) {
    update._id = params.siteId;
    // Check if previous values exist for site collection setttings
    if (update.collection_method === CollectionMethod.Manual && site) {
      if (update.scrape_method_configuration?.focus_section_configs) {
        update.scrape_method_configuration = {
          ...site.scrape_method_configuration,
          focus_section_configs: update.scrape_method_configuration.focus_section_configs,
        };
      } else {
        update.scrape_method_configuration = {
          ...site.scrape_method_configuration,
        };
      }
    }
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
