import { Spin } from 'antd';

export enum TaskStatus {
  Queued = 'QUEUED',
  Pending = 'PENDING',
  InProgress = 'IN_PROGRESS',
  Finished = 'FINISHED',
  Canceling = 'CANCELING',
  Canceled = 'CANCELED',
  Failed = 'FAILED',
}

export function scrapeTaskStatusDisplayName(status: TaskStatus): string {
  const { name } = statusDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function scrapeTaskStatusStyledDisplay(status: TaskStatus): React.ReactElement {
  const { name, style } = statusDisplayAndStyle(status);
  if (!name && !style) {
    return <span />;
  }
  if (status === TaskStatus.Canceling) {
    return (
      <>
        <span className={`${style} mr-2`}>Canceling</span>
        <Spin size="small" />
      </>
    );
  }
  return <span className={style}>{name}</span>;
}

interface StatusDisplay {
  name?: string;
  style?: string;
}

export function statusDisplayAndStyle(status: TaskStatus): StatusDisplay {
  switch (status) {
    case TaskStatus.Failed:
      return { name: 'Failed', style: 'text-red-500' };
    case TaskStatus.Canceled:
      return { name: 'Canceled', style: 'text-orange-500' };
    case TaskStatus.Canceling:
      return { name: 'Canceling', style: 'text-amber-500' };
    case TaskStatus.InProgress:
      return { name: 'In Progress', style: 'text-blue-500' };
    case TaskStatus.Queued:
      return { name: 'Queued', style: 'text-yellow-500' };
    case TaskStatus.Finished:
      return { name: 'Last Collected', style: 'text-green-500' };
    default:
      return {};
  }
}
