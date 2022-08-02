import classNames from 'classnames';
import { useDispatch } from 'react-redux';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import tempLogoBrand from '../assets/temp-logo-brand.png';
import tempLogo from '../assets/temp-logo.png';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from './use-breadcrumbs';
import { Tooltip } from 'antd';
import { breadcrumbState, menuState, layoutState, toggleAppBarPosition } from './navSlice';
import { ProjectTwoTone, IdcardOutlined, InboxOutlined, FileTextTwoTone } from '@ant-design/icons';

export function AppLayout() {
  const layout: any = useSelector(layoutState);
  const vertical: boolean = layout.appBarPosition == 'left';

  return (
    <div className={classNames('flex h-screen', vertical ? 'flex-row' : 'flex-col')}>
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
            i == breadcrumbs.length - 1 ? 'text-gray-900' : 'text-gray-500'
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
    <div className="flex cursor-pointer" onClick={() => logout()}>
      {user?.given_name} {user?.family_name}
    </div>
  );
}

export function AppBar() {
  const layout: any = useSelector(layoutState);
  const vertical: boolean = layout.appBarPosition == 'left';
  const dispatch = useDispatch();

  return (
    <div
      className={classNames(
        'box-border flex p-1 items-center bg-blue-primary text-white',
        vertical ? 'flex-col w-12' : 'flex-row h-12 px-2'
      )}
    >
      <Link
        to="/sites"
        onDoubleClick={() => {
          dispatch(toggleAppBarPosition());
        }}
      >
        {vertical ? (
          <img src={tempLogoBrand} alt="SourceHub" className="w-8 h-8 mt-1" />
        ) : (
          <>
            <img src={tempLogo} alt="SourceHub" className="" />
          </>
        )}
      </Link>
      {!vertical && <div data-type="spacer" className="flex flex-1"></div>}
      <AppMenu />
      {vertical && <div data-type="spacer" className="flex flex-1"></div>}
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
  const layout: any = useSelector(layoutState);
  const vertical: boolean = layout.appBarPosition == 'left';

  const icons: any = {
    '/sites': <ProjectTwoTone />,
    '/work-queues': <InboxOutlined />,
    '/documents': <FileTextTwoTone />,
    '/users': <IdcardOutlined />,
  };

  return (
    <div
      className={classNames(
        'flex',
        vertical ? 'flex-col items-center mt-4 space-y-4' : 'space-x-2 mr-2'
      )}
    >
      {menu.items.map(({ url, label }: any) => (
        <Tooltip key={url} placement="right" title={label}>
          <Link
            className={classNames(
              'cursor-pointer flex rounded-md select-none',
              isCurrentClasses(location.pathname, url),
              vertical ? 'text-[18px] p-2' : 'px-2 py-1'
            )}
            to={url}
          >
            {vertical ? icons[url] : label}
          </Link>
        </Tooltip>
      ))}
    </div>
  );
}
