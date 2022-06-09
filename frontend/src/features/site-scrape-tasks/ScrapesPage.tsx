import { Button, Layout, Spin, Table } from 'antd';
import { useParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { useGetSiteQuery } from '../sites/sitesApi';
import { SiteScrapeTask, Status } from './types';
import {
  useCancelSiteScrapeTaskMutation,
  useGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from './siteScrapeTasksApi';
import { prettyDate, prettyRelativeDate } from '../../common';
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
        return prettyDate(task.queued_time);
      },
    },
    {
      title: 'Stop Time',
      key: 'stop_time',
      render: (task: SiteScrapeTask) => {
        if (task.end_time) return prettyDate(task.end_time);
      },
    },
    {
      title: 'Elapsed',
      key: 'elapsed',
      render: (task: SiteScrapeTask) => {
        return prettyRelativeDate(task.queued_time, task.end_time);
      },
    },
    {
      title: 'Status',
      key: 'status',
      render: (task: SiteScrapeTask) => {
        switch (task.status) {
          case Status.Failed:
            return <span className="text-red-500">Failed</span>;
          case Status.Canceled:
            return <span className="text-orange-500">Canceled</span>;
          case Status.Canceling:
            return (
              <>
                <span className="text-amber-500 mr-2">Canceling</span>
                <Spin size="small" />
              </>
            );
          case Status.InProgress:
            return <span className="text-blue-500">In Progress</span>;
          case Status.Queued:
            return <span className="text-yellow-500">Queued</span>;
          case Status.Finished:
            return <span className="text-green-500">Finished</span>;
          default:
            return <></>;
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
