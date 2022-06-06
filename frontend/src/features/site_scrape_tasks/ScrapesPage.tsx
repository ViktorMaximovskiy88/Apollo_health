import { Button, Layout, Table } from 'antd';
import { useParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetSiteQuery } from '../sites/sitesApi';
import { SiteScrapeTask } from './types';
import {
  useCancelSiteScrapeTaskMutation,
  useGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from './siteScrapeTasksApi';
import {
  format,
  formatDistance,
  formatDistanceToNow,
  parseISO,
} from 'date-fns';
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
  const [cancelScrape, { isLoading: isCanceling }] =
    useCancelSiteScrapeTaskMutation();
  if (!site) return null;

  const formattedScrapes = scrapeTasks;
  const columns = [
    {
      title: 'Start Time',
      key: 'start_time',
      render: (task: SiteScrapeTask) => {
        return <>{format(parseISO(task.queued_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Stop Time',
      key: 'stop_time',
      render: (task: SiteScrapeTask) => {
        if (task.end_time)
          return <>{format(parseISO(task.end_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Elapsed',
      key: 'elapsed',
      render: (task: SiteScrapeTask) => {
        const startTime = parseISO(task.queued_time);
        if (task.end_time) {
          return formatDistance(startTime, parseISO(task.end_time));
        } else {
          return formatDistanceToNow(startTime);
        }
      },
    },
    {
      title: 'Status',
      key: 'status',
      render: (task: SiteScrapeTask) => {
        if (task.status === 'FAILED') {
          return <span className="text-red-500">Failed</span>;
        } else if (task.status === 'CANCELED') {
          return <span className="text-orange-500">Forced End</span>;
        } else if (task.status === 'CANCELING') {
          return <span className="text-amber-500">Canceling</span>;
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
        return (
          <ButtonLink
            to={`/sites/${task.site_id}/documents?scrape_task_id=${task._id}`}
          >
            {task.documents_found} Documents
          </ButtonLink>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (task: SiteScrapeTask) =>
        task.status === 'IN_PROGRESS' ? (
          <Button
            danger
            type="primary"
            disabled={isCanceling}
            onClick={() => cancelScrape(task._id)}
          >
            Cancel
          </Button>
        ) : (
          <></>
        ),
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
