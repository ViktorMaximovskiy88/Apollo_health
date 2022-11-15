import { Layout, Menu } from 'antd';
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom';

export function SiteMenu() {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const parts = location.pathname.split('/');
  const current = parts.length > 4 ? `${parts.slice(3).join('-')}` : parts[3];
  const scrapeTaskId = searchParams.get('scrape_task_id');

  const subpages = [
    { key: 'scrapes', label: <Link to={`/sites/${siteId}/scrapes`}>Collections</Link> },
    {
      key: 'doc-documents',
      label: (
        <Link
          to={`/sites/${siteId}/doc-documents${
            scrapeTaskId ? `?scrape_task_id=${scrapeTaskId}` : ''
          }`}
        >
          Documents
        </Link>
      ),
    },
    {
      key: 'extraction',
      label: <Link to={`/sites/${siteId}/extraction`}>Content Extraction</Link>,
    },
    {
      key: 'lineage',
      label: (
        <div className="flex justify-between items-center">
          <Link to={`/sites/${siteId}/lineage`}>Lineage</Link>
          {/* <SelectOutlined rotate={90} onClick={() => {}} /> */}
        </div>
      ),
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
