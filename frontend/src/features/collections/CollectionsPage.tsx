import { Button, Layout } from 'antd';
import { useParams } from 'react-router-dom';
import { useRunSiteScrapeTaskMutation } from './siteScrapeTasksApi';
import { useGetSiteQuery } from '../sites/sitesApi';
import Title from 'antd/lib/typography/Title';
import { CollectionsDataTable } from './CollectionsDataTable';
import { CollectionMethod } from "../sites/types"


export function CollectionsPage() {
  const params = useParams();
  const siteId = params.siteId;
  const { data: site } = useGetSiteQuery(siteId);
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!siteId) return null;

  return (
    <Layout className="bg-white">
      <div className="flex">
        <Title level={4}>Collections</Title>
        {
          site && site.collection_method === CollectionMethod.Automated ?
          <Button onClick={() => runScrape(site._id)} className="ml-auto">
            Run Collection
          </Button>
          :
          null
        }
      </div>
      <CollectionsDataTable siteId={siteId} />
    </Layout>
  );
}
