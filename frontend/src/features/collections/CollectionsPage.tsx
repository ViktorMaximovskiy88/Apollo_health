import { Button, Layout } from 'antd';
import { useParams } from 'react-router-dom';
import { useRunSiteScrapeTaskMutation } from './siteScrapeTasksApi';
import Title from 'antd/lib/typography/Title';
import { CollectionsDataTable } from './CollectionsDataTable';

export function CollectionsPage() {
  const params = useParams();
  const siteId = params.siteId;
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!siteId) return null;

  return (
    <Layout className="bg-white">
      <div className="flex">
        <Title level={4}>Collections</Title>
        <Button onClick={() => runScrape(siteId)} className="ml-auto">
          Run Collection
        </Button>
      </div>
      <CollectionsDataTable siteId={siteId} />
    </Layout>
  );
}
