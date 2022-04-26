import { Button, Layout, Menu, Table } from 'antd';
import { Link, Outlet, useLocation, useParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetSiteQuery } from './sitesApi';
import { SiteScrapeTask } from '../site_scrape_tasks/types';
import {
  useGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from '../site_scrape_tasks/siteScrapeTasksApi';
import {
  format,
  formatDistance,
  formatDistanceToNow,
  parseISO,
} from 'date-fns';
import Title from 'antd/lib/typography/Title';

export function SitePage() {
  const subpages = [
    { key: 'scrapes', label: 'Scapes' },
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
