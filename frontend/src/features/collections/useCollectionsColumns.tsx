import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import {
  prettyDateDistance,
  prettyDateTimeFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
} from '../../common';
import { CollectionMethod } from '../sites/types';
import { ButtonLink } from '../../components/ButtonLink';
import { SiteScrapeTask } from './types';

interface CreateColumnsType {
  cancelScrape: (taskId: string) => void;
  isCanceling: boolean;
  openErrorModal: (errorTraceback: string) => void;
  openNewDocumentModal: () => void;
}

export const createColumns = ({
  cancelScrape,
  isCanceling,
  openErrorModal,
  openNewDocumentModal,
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
      header: 'Queued Time',
      name: 'queued',
      minWidth: 300,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        return prettyDateDistance(task.queued_time, task.start_time);
      },
    },
    {
      header: 'Collection Time',
      name: 'elapsed',
      minWidth: 300,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        if (task.start_time) {
          return prettyDateDistance(task.start_time, task.end_time);
        }
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
            id: TaskStatus.Finished,
            label: displayName(TaskStatus.Finished),
          },
          {
            id: TaskStatus.Canceled,
            label: displayName(TaskStatus.Canceled),
          },
          {
            id: TaskStatus.Canceling,
            label: displayName(TaskStatus.Canceling),
          },
          {
            id: TaskStatus.Queued,
            label: displayName(TaskStatus.Queued),
          },
          {
            id: TaskStatus.Failed,
            label: displayName(TaskStatus.Failed),
          },
          {
            id: TaskStatus.InProgress,
            label: displayName(TaskStatus.InProgress),
          },
        ],
      },
      render: ({ value: status }: { value: TaskStatus }) => styledDisplay(status),
    },
    {
      header: 'Document Count',
      name: 'documents_found',
      defaultFlex: 1,
      minWidth: 300,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        const linksFound = `(${task.links_found} Links)`;
        const showLinksFounds = task.links_found > 0;
        const docsCount = `${task.documents_found} Documents ${showLinksFounds ? linksFound : ''}`;

        return (
          <ButtonLink to={`/sites/${task.site_id}/doc-documents?scrape_task_id=${task._id}`}>
            {docsCount}
          </ButtonLink>
        );
      },
    },
    {
      header: 'Collection Method',
      name: 'collection_method',
      maxWidth: 200,
      render: ({ value: collection_method }: { value: string }) => {
        switch (collection_method) {
          case CollectionMethod.Manual:
            return <span>Manual</span>;
          case CollectionMethod.Automated:
            return <span>Automated</span>;
        }
      },
    },
    {
      name: 'action',
      header: 'Actions',
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        switch (task.status) {
          case TaskStatus.InProgress:
          case TaskStatus.Queued:
            if (task.collection_method === CollectionMethod.Automated) {
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
            } else {
              return <Button onClick={openNewDocumentModal}>Create document</Button>;
            }
          case TaskStatus.Failed:
            return (
              <Button
                danger
                onClick={() => openErrorModal(task.error_message || 'traceback not found')}
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

export const useCollectionsColumns = ({
  cancelScrape,
  isCanceling,
  openErrorModal,
  openNewDocumentModal,
}: CreateColumnsType) =>
  useMemo(
    () => createColumns({ cancelScrape, isCanceling, openErrorModal, openNewDocumentModal }),
    [cancelScrape, isCanceling, openErrorModal, openNewDocumentModal]
  );
