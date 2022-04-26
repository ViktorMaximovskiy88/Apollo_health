import { Button, Table } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useParams, useSearchParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import {
  useGetExtractionTasksForDocQuery,
  useRunExtractionTaskMutation,
} from '../extractions/extractionsApi';
import {
  format,
  formatDistance,
  formatDistanceToNow,
  parseISO,
} from 'date-fns';
import { ExtractionTask } from '../extractions/types';
import { useGetDocumentQuery } from '../documents/documentsApi';

export function DocExtractionPage() {
  const params = useParams();
  const docId = params.docId;
  const [runExtractionForDoc] = useRunExtractionTaskMutation();
  const { data: documents } = useGetExtractionTasksForDocQuery(docId, {
    skip: !docId,
    pollingInterval: 5000,
  });
  const { data: doc } = useGetDocumentQuery(docId, { skip: !docId });

  if (!docId || !doc) return null;

  const columns = [
    {
      title: 'Start Time',
      key: 'start_time',
      render: (task: ExtractionTask) => {
        return <>{format(new Date(task.queued_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Stop Time',
      key: 'stop_time',
      render: (task: ExtractionTask) => {
        if (task.end_time)
          return <>{format(new Date(task.end_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Elapsed',
      key: 'elapsed',
      render: (task: ExtractionTask) => {
        const startTime = parseISO(task.queued_time);
        if (task.end_time) {
          return formatDistance(startTime, new Date(task.end_time));
        } else {
          return formatDistanceToNow(startTime);
        }
      },
    },
    {
      title: 'Status',
      key: 'status',
      render: (task: ExtractionTask) => {
        if (task.status === 'FAILED') {
          return <span className="text-red-500">Failed</span>;
        } else if (task.status === 'IN_PROGRESS') {
          return <span className="text-blue-500">In Progress</span>;
        } else if (task.status === 'QUEUED') {
          return <span className="text-yellow-500">Queued</span>;
        } else if (task.status === 'FINISHED') {
          return <span className="text-green-500">Finished</span>;
        }
      },
    },
    {
      title: 'Extracted Count',
      key: 'extraction_count',
      render: (task: ExtractionTask) => {
        return (
          <ButtonLink to={task._id}>
            {task.extraction_count} Extractions
          </ButtonLink>
        );
      },
    },
  ];
  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extractions - {doc.name}
        </Title>
        <Button className="ml-auto" onClick={() => runExtractionForDoc(docId)}>
          Run Extraction
        </Button>
      </div>
      <Table
        dataSource={documents}
        columns={columns}
        rowKey={(task) => task._id}
      />
    </div>
  );
}
