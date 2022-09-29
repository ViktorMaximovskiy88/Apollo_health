import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Site, CollectionMethod } from './types';
import { SiteForm } from './form/SiteForm';
import { useGetSiteQuery, useUpdateSiteMutation } from './sitesApi';
import { useCancelAllSiteScrapeTasksMutation } from '../collections/siteScrapeTasksApi';
import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ToggleReadOnly } from './form/ToggleReadOnly';
import { Button, Form, Space } from 'antd';
import { SiteSubmitButton } from './form/SiteSubmitButton';
import { Link } from 'react-router-dom';
import { useForm } from 'antd/lib/form/Form';

export function SiteViewPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);
  const [updateSite] = useUpdateSiteMutation();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const navigate = useNavigate();
  const [readOnly, setReadOnly] = useState(true);
  const [form] = useForm();

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
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {readOnly ? (
            <ToggleReadOnly setReadOnly={setReadOnly} form={form} />
          ) : (
            <Form.Item className="m-1">
              <Space>
                <SiteSubmitButton form={form} />
                <Link to="/sites">
                  <Button htmlType="submit">Cancel</Button>
                </Link>
              </Space>
            </Form.Item>
          )}
        </>
      }
    >
      <SiteForm initialValues={site} onFinish={tryUpdateSite} form={form} />
    </MainLayout>
  );
}
