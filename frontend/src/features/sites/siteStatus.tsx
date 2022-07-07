export enum SiteStatus {
  New = 'NEW',
  QualityHold = 'QUALITY_HOLD',
  Inactive = 'INACTIVE',
  Online = 'ONLINE',
}

export function siteStatusDisplayName(status: SiteStatus): string {
  const { name } = statusDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function siteStatusStyledDisplay(
  status: SiteStatus
): React.ReactElement {
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

function statusDisplayAndStyle(status: SiteStatus): StatusDisplay {
  switch (status) {
    case SiteStatus.New:
      return { name: 'New', style: 'text-purple-500' };
    case SiteStatus.QualityHold:
      return { name: 'Quality Hold', style: 'text-red-500' };
    case SiteStatus.Inactive:
      return { name: 'Inactive', style: 'text-amber-500' };
    case SiteStatus.Online:
      return { name: 'Online', style: 'text-green-500' };
    default:
      return {};
  }
}
