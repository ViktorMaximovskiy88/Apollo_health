import { Layout, Menu } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';

export function SitePage() {
  const subpages = [
    { key: 'scrapes', label: <Link to="scrapes">Collections</Link> },
    { key: 'documents', label: <Link to="documents">Documents</Link> },
    { key: 'extraction', label: <Link to="extraction">Content Extraction</Link> },
  ];
  const location = useLocation();
  const current = location.pathname.split('/')[3];
  return (
    <Layout className="bg-transparent">
      <Layout.Sider width={175}>
        <Menu mode="inline" className="h-full" selectedKeys={[current]} items={subpages} />
      </Layout.Sider>
      <Layout className="p-4 bg-transparent">
        <Outlet />
      </Layout>
    </Layout>
  );
}
