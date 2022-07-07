import { Spin } from 'antd';

export enum ScrapeTaskStatus {
  Queued = 'QUEUED',
  Pending = 'PENDING',
  InProgress = 'IN_PROGRESS',
  Finished = 'FINISHED',
  Canceling = 'CANCELING',
  Canceled = 'CANCELED',
  Failed = 'FAILED',
}

export function scrapeTaskStatusDisplayName(status: ScrapeTaskStatus): string {
  const { name } = statusDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function scrapeTaskStatusStyledDisplay(
  status: ScrapeTaskStatus
): React.ReactElement {
  const { name, style } = statusDisplayAndStyle(status);
  if (!name && !style) {
    return <span />;
  }
  if (status === ScrapeTaskStatus.Canceling) {
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

function statusDisplayAndStyle(status: ScrapeTaskStatus): StatusDisplay {
  switch (status) {
    case ScrapeTaskStatus.Failed:
      return { name: 'Failed', style: 'text-red-500' };
    case ScrapeTaskStatus.Canceled:
      return { name: 'Canceled', style: 'text-orange-500' };
    case ScrapeTaskStatus.Canceling:
      return { name: 'Canceling', style: 'text-amber-500' };
    case ScrapeTaskStatus.InProgress:
      return { name: 'In Progress', style: 'text-blue-500' };
    case ScrapeTaskStatus.Queued:
      return { name: 'Queued', style: 'text-yellow-500' };
    case ScrapeTaskStatus.Finished:
      return { name: 'Finished', style: 'text-green-500' };
    default:
      return {};
  }
}
