import classNames from 'classnames';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import tempLogoBrand from '../assets/temp-logo-brand.png';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from './use-breadcrumbs';
import { Tooltip } from 'antd';
import { breadcrumbState, menuState } from './navSlice';
import { useCurrentUser } from '../common/hooks/use-current-user';

import {
  ProjectTwoTone,
  UserOutlined,
  IdcardOutlined,
  InboxOutlined,
  FileTextTwoTone,
  MergeCellsOutlined,
  WalletOutlined,
  GroupOutlined,
  TeamOutlined,
} from '@ant-design/icons';

export function AppLayout() {
  return (
    <div className={classNames('flex h-screen flex-row')}>
      <AppBar />
      <Outlet />
    </div>
  );
}

export function AppBreadcrumbs() {
  const breadcrumbs: any = useSelector(breadcrumbState);
  useBreadcrumbs();
  return (
    <div className="flex">
      {breadcrumbs.map((crumb: any, i: number) => (
        <div
          className={classNames(
            'text-[16px]',
            i === breadcrumbs.length - 1 ? 'text-gray-900' : 'text-gray-500'
          )}
          key={`${crumb.label}`}
        >
          {i > 0 && <span className={classNames('mx-2')}>/</span>}
          <Link to={crumb.url}>{crumb.label}</Link>
        </div>
      ))}
    </div>
  );
}

export function AppUser() {
  const { user, logout } = useAuth0();

  return (
    <div
      className={classNames('flex text-[24px] cursor-pointer rounded-full bg-sky-100 p-1 mb-2')}
      onClick={() => logout()}
    >
      <Tooltip title={`${user?.given_name} ${user?.family_name}`} placement={'right'}>
        <UserOutlined style={{ color: '#5a9bc9' }} />
      </Tooltip>
    </div>
  );
}

export function AppBar() {
  return (
    <div
      className={classNames(
        'box-border flex p-1 items-center bg-blue-primary text-white flex-col w-12'
      )}
    >
      <Link to="/sites">
        <img src={tempLogoBrand} alt="SourceHub" className="w-8 h-8 mt-1" />
      </Link>
      <AppMenu />
      <div data-type="spacer" className="flex flex-1"></div>
      <AppUser />
    </div>
  );
}

function isCurrentClasses(path: string, key: string) {
  return path.startsWith(key)
    ? ['bg-white text-blue-primary hover:text-blue-primary']
    : ['text-gray-100 hover:text-blue-primary hover:bg-sky-200'];
}

function AppMenu() {
  const location = useLocation();
  const menu: any = useSelector(menuState);
  const currentUser = useCurrentUser();

  const icons: any = {
    '/document-family': <GroupOutlined />,
    '/payer-family': <TeamOutlined />,
    '/sites': <ProjectTwoTone />,
    '/work-queues': <InboxOutlined />,
    '/documents': <FileTextTwoTone />,
    '/translations': <MergeCellsOutlined />,
    '/payer-backbone': <WalletOutlined />,
    '/users': <IdcardOutlined />,
  };

  return (
    <div className={classNames('flex flex-col items-center mt-4 space-y-4')}>
      {menu.items.map(({ url, label, adminRoleRequired }: any) =>
        adminRoleRequired && !currentUser?.is_admin ? null : (
          <Tooltip key={url} placement={'right'} title={label}>
            <Link
              className={classNames(
                'cursor-pointer flex flex-col rounded-md select-none justify-center',
                isCurrentClasses(location.pathname, url),
                'text-[18px] p-2'
              )}
              to={url}
            >
              {icons[url]}
            </Link>
          </Tooltip>
        )
      )}
    </div>
  );
}
