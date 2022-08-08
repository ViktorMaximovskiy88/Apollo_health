import { Layout, Menu } from 'antd';
import { Link, useLocation, useParams } from 'react-router-dom';

export function SiteMenu() {
  const { siteId } = useParams();
  const location = useLocation();
  const current = location.pathname.split('/')[3];

  const subpages = [
    { key: 'scrapes', label: <Link to={`/sites/${siteId}/scrapes`}>Collections</Link> },
    { key: 'documents', label: <Link to={`/sites/${siteId}/documents`}>Documents</Link> },
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
