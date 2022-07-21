import { useState } from 'react';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { SiteForm } from './SiteForm';
import { useGetSiteQuery } from './sitesApi';
import { Layout } from 'antd';

export function SiteViewPage() {
  const params = useParams();
  const { data: site } = useGetSiteQuery(params.siteId);

  const [readOnly, setReadOnly] = useState(true);

  if (!site) return null;

  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <Title level={4}>{readOnly ? 'View' : 'Edit'} Site</Title>
      </div>
      <SiteForm
        readOnly={readOnly}
        setReadOnly={setReadOnly}
        initialValues={site}
        onFinish={() => {}}
      />
    </Layout>
  );
}
