import { Spin } from 'antd';

export enum Status {
  Queued = 'QUEUED',
  Pending = 'PENDING',
  InProgress = 'IN_PROGRESS',
  Finished = 'FINISHED',
  Canceling = 'CANCELING',
  Canceled = 'CANCELED',
  Failed = 'FAILED',
}

export function statusDisplayName(status: Status): string {
  const { name } = statusDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function statusStyledDisplay(status: Status): React.ReactElement {
  const { name, style } = statusDisplayAndStyle(status);
  if (!name && !style) {
    return <span />;
  }
  if (status === Status.Canceling) {
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

function statusDisplayAndStyle(status: Status): StatusDisplay {
  switch (status) {
    case Status.Failed:
      return { name: 'Failed', style: 'text-red-500' };
    case Status.Canceled:
      return { name: 'Canceled', style: 'text-orange-500' };
    case Status.Canceling:
      return { name: 'Canceling', style: 'text-amber-500' };
    case Status.InProgress:
      return { name: 'In Progress', style: 'text-blue-500' };
    case Status.Queued:
      return { name: 'Queued', style: 'text-yellow-500' };
    case Status.Finished:
      return { name: 'Finished', style: 'text-green-500' };
    default:
      return {};
  }
}
