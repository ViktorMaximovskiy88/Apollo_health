import ReactDataGrid from '@inovua/reactdatagrid-community';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button, notification } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { BaseDocument } from '../../common';
import { dateDuration } from '../../common/date';
import {
  useDataTableFilter,
  useDataTablePagination,
  useDataTableSort,
  useInterval,
} from '../../common/hooks';
import { ButtonLink } from '../../components/ButtonLink';
import { DocDocument, TaskLock } from '../doc_documents/types';
import { useGetUsersQuery } from '../users/usersApi';
import { useGetWorkQueueQuery } from './workQueuesApi';
import { MainLayout } from '../../components';
import { DocumentTypes } from '../retrieved_documents/types';
import { useGetSiteQuery, useGetSitesQuery, useLazyGetSitesQuery } from '../sites/sitesApi';
import { RemoteColumnFilter } from '../../components/RemoteColumnFilter';
import {
  workQueueTableState,
  setWorkQueueTableFilter,
  setWorkQueueTableSort,
  setWorkQueueTableLimit,
  setWorkQueueTableSkip,
} from './workQueueSlice';
import { useSelector } from 'react-redux';
import {
  useLazyGetWorkQueueItemsQuery,
  useTakeNextWorkItemMutation,
} from '../doc_documents/docDocumentApi';

function useSiteSelectOptions() {
  const [getSites] = useLazyGetSitesQuery();
  const siteOptions = useCallback(
    async (search: string) => {
      const { data } = await getSites({
        limit: 20,
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

function useGetSiteNamesById() {
  const [siteIds, setSiteIds] = useState<string[]>([]);
  const { data: sites } = useGetSitesQuery(
    {
      filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: siteIds }],
    },
    { skip: siteIds.length === 0 }
  );
  const siteNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    sites?.data.forEach((site) => {
      map[site._id] = site.name;
    });
    return map;
  }, [sites]);
  return { setSiteIds, siteNamesById };
}

function uniqueSiteIds(items: DocDocument[]) {
  const usedSiteIds: { [key: string]: boolean } = {};
  items.forEach((item) => item.locations.forEach((l) => (usedSiteIds[l.site_id] = true)));
  return Object.keys(usedSiteIds);
}

function useWorkQueueColumns(
  queueId: string | undefined,
  siteNamesById: { [key: string]: string }
) {
  const { data: users } = useGetUsersQuery();
  const { siteOptions } = useSiteSelectOptions();

  const res = useSelector(workQueueTableState);
  const siteFilter = res.filter.find((f) => f.name === 'locations.site_id');
  const { data: site } = useGetSiteQuery(siteFilter?.value, { skip: !siteFilter?.value });
  const initialOptions = site ? [{ value: site._id, label: site.name }] : [];
  const columns = [
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
      minWidth: 300,
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
      defaultFlex: 1,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: DocumentTypes,
      },
      render: ({ value: document_type }: { value: string }) => {
        return <>{document_type}</>;
      },
    },
    {
      header: 'Actions',
      render: ({ data: item }: { data: BaseDocument }) => {
        return (
          <ButtonLink type="default" to={`${item._id}/process`}>
            Take
          </ButtonLink>
        );
      },
    },
  ];
  return { columns };
}

export function WorkQueuePage() {
  const queueId = useParams().queueId;
  const navigate = useNavigate();
  const [getWorkItemFn] = useLazyGetWorkQueueItemsQuery();
  const { data: wq } = useGetWorkQueueQuery(queueId);
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();

  const tableState = useSelector(workQueueTableState);
  const takeNext = useCallback(async () => {
    const response = await takeNextWorkItem({ queueId, tableState });
    if ('data' in response) {
      if (!response.data.acquired_lock) {
        notification.success({
          message: 'Queue Empty',
          description: 'Congratulations! This queue has been emptied.',
        });
      } else {
        navigate(`../${response.data.item_id}/process`);
      }
    }
  }, [takeNextWorkItem, navigate, queueId, tableState]);

  const { isActive, setActive, watermark } = useInterval(10000);
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();
  const { columns } = useWorkQueueColumns(queueId, siteNamesById);

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getWorkItemFn({ ...tableInfo, id: queueId });
      const items = data?.data ?? [];
      const count = data?.total ?? 0;
      if (items) setSiteIds(uniqueSiteIds(items));
      return { data: items, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getWorkItemFn, queueId, watermark]
  );

  const filterProps = useDataTableFilter(workQueueTableState, setWorkQueueTableFilter);
  const sortProps = useDataTableSort(workQueueTableState, setWorkQueueTableSort);
  const paginationProps = useDataTablePagination(
    workQueueTableState,
    setWorkQueueTableLimit,
    setWorkQueueTableSkip,
    { isActive, setActive }
  );

  if (!wq) return null;

  return (
    <MainLayout
      sectionToolbar={
        <>
          <Button onClick={takeNext}>Take Next</Button>
        </>
      }
    >
      <ReactDataGrid
        dataSource={loadData}
        columns={columns}
        rowHeight={50}
        renderLoadMask={() => <></>}
        {...filterProps}
        {...sortProps}
        {...paginationProps}
        columnUserSelect
      />
    </MainLayout>
  );
}
