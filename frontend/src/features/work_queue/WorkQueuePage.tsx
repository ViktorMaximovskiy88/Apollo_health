import ReactDataGrid from '@inovua/reactdatagrid-community';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button, notification } from 'antd';
import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { BaseDocument } from '../../common';
import { dateDuration } from '../../common/date';
import { useInterval } from '../../common/hooks';
import { GridPaginationToolbar } from '../../components';
import { ButtonLink } from '../../components/ButtonLink';
import { TaskLock } from '../doc_documents/types';
import { useGetUsersQuery } from '../users/usersApi';
import {
  useGetWorkQueueQuery,
  useLazyGetWorkQueueItemsQuery,
  useTakeNextWorkItemMutation,
} from './workQueuesApi';
import { MainLayout } from '../../components';

export function WorkQueuePage() {
  const queueId = useParams().queueId;
  const navigate = useNavigate();
  const [getWorkItemFn] = useLazyGetWorkQueueItemsQuery();
  const { data: wq } = useGetWorkQueueQuery(queueId);
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();
  const { data: users } = useGetUsersQuery();

  const takeNext = useCallback(async () => {
    const response = await takeNextWorkItem(queueId);
    if (!('data' in response)) return;
    if (!response.data.acquired_lock) {
      notification.success({
        message: 'Queue Empty',
        description: 'Congratulations! This queue has been emptied.',
      });
      return;
    }
    navigate(`../../../../documents/${response.data.item_id}`);
  }, [takeNextWorkItem, navigate, queueId]);

  const { isActive, setActive, watermark } = useInterval(10000);
  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getWorkItemFn({ ...tableInfo, id: queueId });
      const items = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: items, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getWorkItemFn, queueId, watermark]
  );

  const renderPaginationToolbar = useCallback(
    (paginationProps: any) => {
      return (
        <GridPaginationToolbar
          paginationProps={{ ...paginationProps }}
          autoRefreshValue={isActive}
          autoRefreshClick={setActive}
        />
      );
    },
    [isActive, setActive]
  );

  const columns = [
    {
      name: 'name',
      header: 'Name',
      defaultFlex: 1,
      render: ({ data: item }: { data: { _id: string; name: string } }) => {
        return <ButtonLink to={`${item._id}/read-only`}>{item.name}</ButtonLink>;
      },
    },
    {
      name: 'locks.user_id',
      header: 'Assignee',
      defaultFlex: 1,
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

  if (!wq) return null;

  const filterValue = [
    { name: 'name', operator: 'contains', type: 'string', value: '' },
    {
      name: 'locks.user_id',
      operator: 'eq',
      type: 'select',
      value: null,
    },
  ];

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
        pagination
        defaultFilterValue={filterValue}
        renderLoadMask={() => <></>}
        renderPaginationToolbar={renderPaginationToolbar}
        activateRowOnFocus={false}
      />
    </MainLayout>
  );
}
