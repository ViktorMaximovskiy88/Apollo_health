import { Layout, Button, Popconfirm, Table, Tag } from 'antd';
import Title from 'antd/lib/typography/Title';
import { Link } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { WorkQueue } from './types';
import {
  useDeleteWorkQueueMutation,
  useGetChangeLogQuery,
  useGetWorkQueueCountsQuery,
  useGetWorkQueuesQuery,
} from './workQueuesApi';

export function WorkQueueHomePage() {
  const { data: workQueues } = useGetWorkQueuesQuery();
  const { data: workQueueCounts } = useGetWorkQueueCountsQuery(undefined, {
    pollingInterval: 5000,
    refetchOnMountOrArgChange: true,
  });
  const [deleteWorkQueue] = useDeleteWorkQueueMutation();
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
        const count = workQueueCounts?.find((wqc) => wqc.work_queue_id === wq._id)?.count
        return count
      }
    },
    {
      title: 'Actions',
      key: 'action',
      render: (wq: WorkQueue) => {
        return (
          <>
            <ButtonLink to={`${wq._id}/edit`}>Edit</ButtonLink>
            <ChangeLogModal
              target={wq}
              useChangeLogQuery={useGetChangeLogQuery}
            />
            <Popconfirm
              title={`Are you sure you want to delete '${wq.name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => deleteWorkQueue(wq)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
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
      <Table dataSource={workQueues} columns={columns} />
    </Layout>
  );
}
