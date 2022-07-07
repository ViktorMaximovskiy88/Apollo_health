import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import {
  prettyDateDistance,
  prettyDateTimeFromISO,
  ScrapeTaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
} from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { SiteScrapeTask } from './types';

interface CreateColumnsType {
  cancelScrape: (taskId: string) => void;
  isCanceling: boolean;
  openErrorModal: (errorTraceback: string) => void;
}

export const createColumns = ({
  cancelScrape,
  isCanceling,
  openErrorModal,
}: CreateColumnsType) => {
  return [
    {
      header: 'Start Time',
      name: 'queued_time',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ value }: { value: string }) => {
        return prettyDateTimeFromISO(value);
      },
    },
    {
      header: 'Elapsed',
      minWidth: 300,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        return prettyDateDistance(task.queued_time, task.end_time);
      },
    },
    {
      header: 'Status',
      name: 'status',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: [
          {
            id: ScrapeTaskStatus.Finished,
            label: displayName(ScrapeTaskStatus.Finished),
          },
          {
            id: ScrapeTaskStatus.Canceled,
            label: displayName(ScrapeTaskStatus.Canceled),
          },
          {
            id: ScrapeTaskStatus.Canceled,
            label: displayName(ScrapeTaskStatus.Canceling),
          },
          {
            id: ScrapeTaskStatus.Queued,
            label: displayName(ScrapeTaskStatus.Queued),
          },
          {
            id: ScrapeTaskStatus.Failed,
            label: displayName(ScrapeTaskStatus.Failed),
          },
          {
            id: ScrapeTaskStatus.InProgress,
            label: displayName(ScrapeTaskStatus.InProgress),
          },
        ],
      },
      render: ({ value: status }: { value: ScrapeTaskStatus }) =>
        styledDisplay(status),
    },
    {
      header: 'Document Count',
      name: 'documents_found',
      defaultFlex: 1,
      minWidth: 300,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
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
      header: 'Actions',
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        switch (task.status) {
          case ScrapeTaskStatus.InProgress:
          case ScrapeTaskStatus.Queued:
            return (
              <Button
                danger
                type="primary"
                disabled={isCanceling}
                onClick={() => cancelScrape(task._id)}
              >
                Cancel
              </Button>
            );
          case ScrapeTaskStatus.Failed:
            return (
              <Button
                danger
                onClick={() =>
                  openErrorModal(task.error_message || 'traceback not found')
                }
              >
                Error Log
              </Button>
            );
          default:
            return null;
        }
      },
    },
  ];
};
