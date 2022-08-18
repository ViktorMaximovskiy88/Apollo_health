import { Layout, Menu } from 'antd';
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom';

export function SiteMenu() {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const current = location.pathname.split('/')[3];
  const scrapeTaskId = searchParams.get('scrape_task_id');

  const subpages = [
    { key: 'scrapes', label: <Link to={`/sites/${siteId}/scrapes`}>Collections</Link> },
    { key: 'documents', label: <Link to={`/sites/${siteId}/documents`}>Retrieved Documents</Link> },
    { key: 'doc-documents', label: <Link to={`/sites/${siteId}/doc-documents`}>Documents</Link> },
    {
      key: 'extraction',
      label: <Link to={`/sites/${siteId}/extraction`}>Content Extraction</Link>,
    },
    {
      key: 'edit',
      label: <Link to={`/sites/${siteId}/edit`}>Edit Site</Link>,
    },
  ];

  return (
    <Layout.Sider width={175}>
      <Menu mode="inline" className="h-full" selectedKeys={[current]} items={subpages} />
    </Layout.Sider>
  );
}
