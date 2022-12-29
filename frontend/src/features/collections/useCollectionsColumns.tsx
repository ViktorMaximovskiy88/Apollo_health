import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import {
  prettyDateTimeFromISO,
  TaskStatus,
  scrapeTaskStatusDisplayName as displayName,
  scrapeTaskStatusStyledDisplay as styledDisplay,
  prettyDateDistanceSingle,
} from '../../common';
import { CollectionMethod, Site } from '../sites/types';
import { ButtonLink } from '../../components/ButtonLink';
import { SiteScrapeTask } from './types';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';

interface CreateColumnsType {
  cancelScrape: (taskId: string) => void;
  isCanceling: boolean;
  openErrorModal: (errorTraceback: string) => void;
  openNewDocumentModal: () => void;
  site: Site;
}

export const createColumns = ({
  cancelScrape,
  isCanceling,
  openErrorModal,
  openNewDocumentModal,
  site,
}: CreateColumnsType) => {
  const columns = [
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
      header: 'Collection Time',
      name: 'elapsed',
      minWidth: 150,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        if (task.start_time) {
          return prettyDateDistanceSingle(task.start_time, task.end_time);
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
      filterEditor: NumberFilter,
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
      header: 'Actions',
      name: 'action',
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

  if (site.collection_method === CollectionMethod.Automated) {
    columns.splice(2, 0, {
      header: 'Queued Time',
      name: 'queued',
      minWidth: 150,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        return prettyDateDistanceSingle(task.queued_time, task.start_time);
      },
    });
  }

  return columns;
};

export const useCollectionsColumns = ({
  cancelScrape,
  isCanceling,
  openErrorModal,
  openNewDocumentModal,
  site,
}: CreateColumnsType) =>
  useMemo(
    () => createColumns({ cancelScrape, isCanceling, openErrorModal, openNewDocumentModal, site }),
    [cancelScrape, isCanceling, openErrorModal, openNewDocumentModal, site]
  );
