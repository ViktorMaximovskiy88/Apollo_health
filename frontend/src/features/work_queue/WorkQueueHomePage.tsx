import { Layout, Button, Table, notification } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { WorkQueue } from './types';
import {
  useGetWorkQueueCountsQuery,
  useGetWorkQueuesQuery,
  useTakeNextWorkItemMutation,
} from './workQueuesApi';

export function WorkQueueHomePage() {
  const { data: workQueues } = useGetWorkQueuesQuery();
  const { data: workQueueCounts } = useGetWorkQueueCountsQuery(undefined, {
    pollingInterval: 5000,
    refetchOnMountOrArgChange: true,
  });
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();
  const navigate = useNavigate();

  const takeNext = useCallback(
    async (queueId: string) => {
      const response = await takeNextWorkItem(queueId);
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
    [takeNextWorkItem, navigate]
  );

  const columns = [
    {
      title: 'Name',
      key: 'name',
      render: (wq: WorkQueue) => {
        return <ButtonLink to={wq._id}>{wq.name}</ButtonLink>;
      },
    },
    {
      title: 'Count',
      key: 'count',
      render: (wq: WorkQueue) => {
        const count = workQueueCounts?.find((wqc) => wqc.work_queue_id === wq._id)?.count;
        return count;
      },
    },
    {
      title: 'Actions',
      key: 'take',
      render: (wq: WorkQueue) => {
        return (
          <Button onClick={() => takeNext(wq._id)} size="small">
            Take Next
          </Button>
        );
      },
    },
  ];
  return (
    <Layout className="bg-transparent p-4">
      <div className="flex">
        <Title className="inline-block" level={4}>
          Work Queues
        </Title>
        <Link className="ml-auto" to="new">
          <Button>Create</Button>
        </Link>
      </div>
      <Table dataSource={workQueues} rowKey="_id" columns={columns} pagination={false} />
    </Layout>
  );
}
