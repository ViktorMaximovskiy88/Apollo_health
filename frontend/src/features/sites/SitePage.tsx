import { Button, Table } from 'antd';
import { useParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { SiteBreadcrumbs } from './SiteBreadcrumbs';
import { useGetSiteQuery } from './sitesApi';
import { SiteScrapeTask } from '../site_scrape_tasks/types';
import { useGetScrapeTasksForSiteQuery, useRunSiteScrapeTaskMutation } from '../site_scrape_tasks/siteScrapeTasksApi';
import { format, formatDistance, formatDistanceToNow, parseISO } from 'date-fns';

export function SitePage() {
  const params = useParams();
  const siteId  = params.siteId;
  const { data: site } = useGetSiteQuery(siteId);
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, { pollingInterval: 5000, skip: !siteId });
  const [runScrape] = useRunSiteScrapeTaskMutation();
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
        if (task.end_time) return <>{format(parseISO(task.end_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Elapsed',
      key: 'elapsed',
      render: (task: SiteScrapeTask) => {
        const startTime = parseISO(task.queued_time)
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
            return <span className="text-red-500">Failed</span>
        } else if (task.status === 'IN_PROGRESS') {
            return <span className="text-blue-500">In Progress</span>
        } else if (task.status === 'QUEUED') {
            return <span className="text-yellow-500">Queued</span>
        } else if (task.status === 'FINISHED') {
            return <span className="text-green-500">Finished</span>
        }
      },
    },
    {
      title: 'Document Count',
      key: 'documents_found',
      render: (task: SiteScrapeTask) => {
        return <ButtonLink to={`/documents?scrape_task_id=${task._id}`}>{task.documents_found} Documents</ButtonLink>;
      },
    },
  ];
  
  /*
  const pagination = { total: 200, current: 1, pageSize: 20 }
  function handleTableChange(pagination: TablePaginationConfig, filters: Record<string, FilterValue | null>, sorter: SorterResult<SiteScrapeTask> | SorterResult<SiteScrapeTask>[]) {
      setLoading(true)
      retrieve({
          sortField: sorter.field,
          sortOrder: sorter.order,
          pagination,
          ...filters
      })
      setLoading(false)
  }
  */
  return (
    <div>
      <div className="flex">
        <SiteBreadcrumbs />
        <Button onClick={() => runScrape(site._id)} className="ml-auto">Run Scrape</Button>
      </div>
      <Table
        dataSource={formattedScrapes}
        rowKey={row => row._id}
        columns={columns}
      />
    </div>
  );
}
