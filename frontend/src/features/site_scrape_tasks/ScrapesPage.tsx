import { Button, Layout, Table } from 'antd';
import { useParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetSiteQuery } from '../sites/sitesApi';
import { SiteScrapeTask } from './types';
import {
  useGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from './siteScrapeTasksApi';
import { prettyDateFromISO, prettyDateDistance } from '../../common';
import Title from 'antd/lib/typography/Title';

export function ScrapesPage() {
  const params = useParams();
  const siteId = params.siteId;
  const { data: site } = useGetSiteQuery(siteId);
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, {
    pollingInterval: 1000,
    skip: !siteId,
  });
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!site) return null;

  const formattedScrapes = scrapeTasks;
  const columns = [
    {
      title: 'Start Time',
      key: 'start_time',
      render: (task: SiteScrapeTask) => {
        return prettyDateFromISO(task.queued_time);
      },
    },
    {
      title: 'Stop Time',
      key: 'stop_time',
      render: (task: SiteScrapeTask) => {
        if (task.end_time)
          return prettyDateFromISO(task.end_time);
      },
    },
    {
      title: 'Elapsed',
      key: 'elapsed',
      render: (task: SiteScrapeTask) => {
        return prettyDateDistance(task.queued_time, task.end_time)
      },
    },
    {
      title: 'Status',
      key: 'status',
      render: (task: SiteScrapeTask) => {
        if (task.status === 'FAILED') {
          return <span className="text-red-500">Failed</span>;
        } else if (task.status === 'IN_PROGRESS') {
          return <span className="text-blue-500">In Progress</span>;
        } else if (task.status === 'QUEUED') {
          return <span className="text-yellow-500">Queued</span>;
        } else if (task.status === 'FINISHED') {
          return <span className="text-green-500">Finished</span>;
        }
      },
    },
    {
      title: 'Document Count',
      key: 'documents_found',
      render: (task: SiteScrapeTask) => {
        const linksFound = `(${task.links_found} Links)`;
        const showLinksFounds =
          task.links_found > 0 && task.documents_found !== task.links_found;
        const docsCount = `${task.documents_found} Documents ${
          showLinksFounds ? linksFound : ''
        }`;

        return (
          <ButtonLink
            to={`/sites/${task.site_id}/documents?scrape_task_id=${task._id}`}
          >
            {docsCount}
          </ButtonLink>
        );
      },
    },
  ];

  return (
    <Layout className="bg-white">
      <div className="flex">
        <Title level={4}>Collections</Title>
        <Button onClick={() => runScrape(site._id)} className="ml-auto">
          Run Collection
        </Button>
      </div>
      <Table
        dataSource={formattedScrapes}
        rowKey={(row) => row._id}
        columns={columns}
      />
    </Layout>
  );
}
