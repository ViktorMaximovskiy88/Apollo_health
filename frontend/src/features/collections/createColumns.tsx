import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import {
  prettyDateDistance,
  prettyDateTimeFromISO,
  Status,
  statusDisplayName,
  statusStyledDisplay,
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
          { id: Status.Finished, label: statusDisplayName(Status.Finished) },
          { id: Status.Canceled, label: statusDisplayName(Status.Canceled) },
          { id: Status.Canceled, label: statusDisplayName(Status.Canceling) },
          { id: Status.Queued, label: statusDisplayName(Status.Queued) },
          { id: Status.Failed, label: statusDisplayName(Status.Failed) },
          {
            id: Status.InProgress,
            label: statusDisplayName(Status.InProgress),
          },
        ],
      },
      render: ({ value: status }: { value: Status }) =>
        statusStyledDisplay(status),
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
          case Status.InProgress:
          case Status.Queued:
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
          case Status.Failed:
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
