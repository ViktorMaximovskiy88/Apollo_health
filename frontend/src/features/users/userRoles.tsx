export enum UserRoles {
  ScrapeAdmin = 'SCRAPE_ADMIN',
  Dashboard = 'DASHBOARD',
  Assessor = 'ASSESSOR',
  Admin = 'ADMIN',
}

export function userRoleDisplayName(status: UserRoles): string {
  const { name } = roleDisplayAndStyle(status);
  if (!name) {
    return '';
  }
  return name;
}

export function userRoleStyledDisplay(status: UserRoles): React.ReactElement {
  const { name, style } = roleDisplayAndStyle(status);
  if (!name && !style) {
    return <span />;
  }
  return <span className={style}>{name}</span>;
}

interface RoleDisplay {
  name?: string;
  style?: string;
}

function roleDisplayAndStyle(status: UserRoles): RoleDisplay {
  switch (status) {
    case UserRoles.ScrapeAdmin:
      return { name: 'Scrape Admin', style: 'text-purple-500' };
    case UserRoles.Dashboard:
      return { name: 'Dashboard', style: 'text-red-500' };
    case UserRoles.Assessor:
      return { name: 'Assessor', style: 'text-amber-500' };
    case UserRoles.Admin:
      return { name: 'Admin', style: 'text-green-500' };
    default:
      return {};
  }
}
