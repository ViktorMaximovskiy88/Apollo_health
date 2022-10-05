import { Button, notification } from 'antd';
import { useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { WorkQueue } from './types';
import {
  useGetWorkQueueCountsQuery,
  useGetWorkQueuesQuery,
  useTakeNextWorkItemMutation,
} from './workQueuesApi';
import { MainLayout } from '../../components';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { useSelector } from 'react-redux';
import { workQueueTableState } from './workQueueSlice';

export function WorkQueueHomePage() {
  const { data: workQueues } = useGetWorkQueuesQuery();
  const { data: workQueueCounts } = useGetWorkQueueCountsQuery(undefined, {
    pollingInterval: 5000,
    refetchOnMountOrArgChange: true,
  });
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();
  const navigate = useNavigate();
  const tableState = useSelector(workQueueTableState);

  const takeNext = useCallback(
    async (queueId: string) => {
      const response = await takeNextWorkItem({ queueId, tableState });
      if ('data' in response) {
        if (!response.data.acquired_lock) {
          notification.success({
            message: 'Queue Empty',
            description: 'Congratulations! This queue has been emptied.',
          });
        } else {
          navigate(`${queueId}/${response.data.item_id}/process`);
        }
      }
    },
    [takeNextWorkItem, navigate, tableState]
  );

  const columns: TypeColumn[] = [
    {
      header: 'Name',
      name: 'name',
      defaultFlex: 1,
      render: ({ data: wq }: { data: WorkQueue }) => {
        return <ButtonLink to={wq._id}>{wq.name}</ButtonLink>;
      },
    },
    {
      header: 'Count',
      name: 'count',
      render: ({ data: wq }: { data: WorkQueue }) => {
        const count = workQueueCounts?.find((wqc) => wqc.work_queue_id === wq._id)?.count;
        return count;
      },
    },
    {
      header: 'Actions',
      name: 'take',
      render: ({ data: wq }: { data: WorkQueue }) => {
        return (
          <Button onClick={() => takeNext(wq._id)} size="small">
            Take Next
          </Button>
        );
      },
    },
  ];
  const filters = [{ name: 'name', operator: 'contains', type: 'string', value: '' }];
  return (
    <MainLayout
      sectionToolbar={
        <>
          <Link className="ml-auto" to="new">
            <Button>Create</Button>
          </Link>
        </>
      }
    >
      <ReactDataGrid
        dataSource={workQueues || []}
        defaultFilterValue={filters}
        columns={columns}
        rowHeight={50}
      />
    </MainLayout>
  );
}
