export enum ApprovalStatus {
  Queued = 'QUEUED',
  InProgress = 'IN_PROGRESS',
  Hold = 'HOLD',
  Approved = 'APPROVED',
  Pending = 'PENDING',
}

export function approvalStatusDisplayName(status: ApprovalStatus): string {
  const { name } = statusDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function approvalStatusStyledDisplay(status: ApprovalStatus): React.ReactElement {
  const { name, style } = statusDisplayAndStyle(status);
  if (!name && !style) {
    return <span />;
  }
  return <span className={style}>{name}</span>;
}

interface StatusDisplay {
  name?: string;
  style?: string;
}

function statusDisplayAndStyle(status: ApprovalStatus): StatusDisplay {
  switch (status) {
    case ApprovalStatus.Queued:
      return { name: 'Queued', style: 'text-yellow-500' };
    case ApprovalStatus.Pending:
      return { name: 'Pending', style: 'text-blue-500' };
    case ApprovalStatus.InProgress:
      return { name: 'In Progress', style: 'text-blue-500' };
    case ApprovalStatus.Hold:
      return { name: 'On Hold', style: 'text-orange-500' };
    case ApprovalStatus.Approved:
      return { name: 'Approved', style: 'text-green-500' };
    default:
      return {};
  }
}

export const statusOptions = [
  { value: ApprovalStatus.Pending, label: 'Pending' },
  { value: ApprovalStatus.Queued, label: 'Queued' },
  { value: ApprovalStatus.Hold, label: 'Hold' },
  { value: ApprovalStatus.Approved, label: 'Approved' },
];
