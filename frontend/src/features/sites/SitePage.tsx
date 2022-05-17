import { Layout, Menu } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';

export function SitePage() {
  const subpages = [
    { key: 'scrapes', label: 'Collections' },
    { key: 'documents', label: 'Documents' },
    { key: 'extraction', label: 'Content Extraction' },
  ];
  const location = useLocation();
  const current = location.pathname.split('/')[3];
  return (
    <Layout className="bg-transparent">
      <Layout.Sider width={175}>
        <Menu mode="inline" className="h-full" selectedKeys={[current]}>
          {subpages.map(({ key, label }) => (
            <Menu.Item key={key}>
              <Link to={key}>{label}</Link>
            </Menu.Item>
          ))}
        </Menu>
      </Layout.Sider>
      <Layout className="p-4 bg-transparent">
        <Outlet />
      </Layout>
    </Layout>
  );
}
