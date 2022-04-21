import { Breadcrumb } from 'antd';
import Title from 'antd/lib/typography/Title';
import { Link, useParams } from 'react-router-dom';
import { useGetSiteQuery } from './sitesApi';

export function SiteBreadcrumbs() {
  const params = useParams();
  const siteId = params.siteId;
  const { data: site } = useGetSiteQuery(siteId, { skip: !siteId });

  return (
    <Breadcrumb
      separator={
        <Title className="inline-block" level={4}>
          <span className="text-gray-400">/</span>
        </Title>
      }
    >
      <Breadcrumb.Item>
        <Title className="inline-block" level={4}>
          <Link to="/sites">Sites</Link>
        </Title>
      </Breadcrumb.Item>
      {site && (
        <Breadcrumb.Item>
          <Title className="inline-block" level={4}>
            {site.name}
          </Title>
        </Breadcrumb.Item>
      )}
    </Breadcrumb>
  );
}
