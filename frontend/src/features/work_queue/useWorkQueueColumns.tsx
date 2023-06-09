import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback } from 'react';
import { BaseDocument } from '../../common';
import { dateDuration, prettyDateTimeFromISO, prettyDateUTCFromISO } from '../../common/date';
import { ButtonLink } from '../../components/ButtonLink';
import { TaskLock } from '../doc_documents/types';
import { useGetUsersQuery } from '../users/usersApi';
import { DocumentTypes } from '../retrieved_documents/types';
import { useGetSiteQuery, useLazyGetSitesQuery } from '../sites/sitesApi';
import { RemoteColumnFilter } from '../../components/RemoteColumnFilter';
import { workQueueTableState } from './workQueueSlice';
import { useSelector } from 'react-redux';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import { priorityOptions, priorityStyle } from '../doc_documents/useSiteDocDocumentColumns';
import { TypeFilterValue } from '@inovua/reactdatagrid-community/types';
import { useGetWorkQueueQuery } from './workQueuesApi';
import { WorkQueue } from './types';

function useSiteSelectOptions() {
  const [getSites] = useLazyGetSitesQuery();
  const siteOptions = useCallback(
    async (search: string) => {
      const { data } = await getSites({
        limit: 150,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((site) => ({ label: site.name, value: site._id }));
    },
    [getSites]
  );
  return { siteOptions };
}

const useHoldTypes = (queueId?: string) => {
  const { data: holdWorkQueue } = useGetWorkQueueQuery(queueId);
  const holdTypes = holdWorkQueue?.hold_types?.map((holdType) => ({
    id: holdType,
    label: holdType,
  }));
  return holdTypes ?? null;
};

export function useWorkQueueColumns(
  queueId: string | undefined,
  siteNamesById: { [key: string]: string },
  wq: WorkQueue | undefined
) {
  const { data: users } = useGetUsersQuery();
  const { siteOptions } = useSiteSelectOptions();

  const res = useSelector(workQueueTableState);
  const siteFilter = res.filter?.find((f) => f.name === 'locations.site_id');
  const { data: site } = useGetSiteQuery(siteFilter?.value, { skip: !siteFilter?.value });
  const initialOptions = site ? [{ value: site._id, label: site.name }] : [];
  const holdTypes = useHoldTypes(queueId);
  let columns = [
    {
      name: 'name',
      header: 'Name',
      defaultFlex: 1,
      minWidth: 300,
      render: ({ data: item }: { data: { _id: string; name: string } }) => {
        return <ButtonLink to={`${item._id}/process`}>{item.name}</ButtonLink>;
      },
    },
    {
      name: 'locations.link_text',
      header: 'Link Text',
      defaultFlex: 1,
      minWidth: 300,
      render: ({ data }: { data: { locations: { link_text: string }[] } }) => {
        return data.locations.map((s) => s.link_text).join(', ');
      },
    },
    {
      name: 'locations.site_id',
      header: 'Sites',
      minWidth: 200,
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: siteOptions,
        initialOptions,
      },
      defaultFlex: 1,
      render: ({ data }: { data: { locations: { site_id: string }[] } }) => {
        return data.locations.map((s) => siteNamesById[s.site_id]).join(', ');
      },
    },
    {
      name: 'locks.user_id',
      header: 'Assignee',
      defaultFlex: 1,
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource:
          users?.map((u) => ({
            id: u._id,
            label: u.full_name,
          })) || [],
      },
      render: ({ data: item }: { data: { _id: string; locks: TaskLock[] } }) => {
        if (!users) return;
        const lock = item.locks.find((l) => l.work_queue_id === queueId);
        if (lock) {
          const tillExpiry = dateDuration(lock.expires).toMillis();
          if (tillExpiry < 0) {
            const u = users.find((u) => u._id === lock.user_id);
            if (u) return u.full_name;
          }
        }
      },
    },
    {
      name: 'document_type',
      header: 'Document Type',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: ({ filterValue }: { filterValue: TypeFilterValue }) => ({
        placeholder: filterValue ? null : 'All',
        multiple: true,
        wrapMultiple: false,
        dataSource: DocumentTypes,
      }),
      render: ({ value: document_type }: { value: string }) => {
        return <>{document_type}</>;
      },
    },
    {
      name: 'final_effective_date',
      header: 'Final Effective Date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ value: finalEffectiveDate }: { value: string }) => {
        if (finalEffectiveDate) {
          return prettyDateUTCFromISO(finalEffectiveDate);
        }
      },
    },
    {
      name: 'first_collected_date',
      header: 'First Collected Date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ value: firstCollectedDate }: { value: string }) => {
        if (firstCollectedDate) {
          return prettyDateUTCFromISO(firstCollectedDate);
        }
      },
    },
    {
      header: 'Priority',
      name: 'priority',
      width: 130,
      filterEditor: SelectFilter,
      filterEditorProps: {
        dataSource: priorityOptions,
      },
      render: ({ value: priority }: { value: number }) => {
        return priorityStyle(priority);
      },
    },
    {
      header: 'Hold Type',
      name: 'hold_type',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        dataSource: holdTypes,
      },
      visible: !!holdTypes,
      render: ({ value: holdType }: { value: string }) => <>{holdType}</>,
    },
    {
      name: 'hold_comment',
      header: 'Hold Comment',
      defaultFlex: 0,
      minWidth: 200,
      render: ({ data: item }: { data: { hold_comment: string } }) => {
        return <>{item.hold_comment}</>;
      },
    },
    {
      name: 'hold_time',
      header: 'Hold Time',
      render: ({ value: holdComment }: { value: string }) => {
        return prettyDateTimeFromISO(holdComment);
      },
      defaultFlex: 0,
      minWidth: 200,
    },
    {
      name: 'action',
      header: 'Actions',
      render: ({ data: item }: { data: BaseDocument }) => {
        return (
          <ButtonLink type="default" to={`${item._id}/process`}>
            Take
          </ButtonLink>
        );
      },
      defaultFlex: 0,
      minWidth: 200,
    },
  ];

  //remove the comment and time columns if not a hold queue
  if (!wq?.name.includes('Hold')) {
    columns = columns.filter((col) => !col.name.includes('hold'));
  }
  return { columns };
}
