import classNames from 'classnames';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import tempLogo from '../assets/temp-logo.png';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from './use-breadcrumbs';
import { breadcrumbState, menuState } from './navSlice';

export function AppLayout() {
  return (
    <div className={classNames('flex flex-col h-screen')}>
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
  return (
    <div
      className={classNames(
        'flex h-[70px] px-4 justify-between items-center bg-blue-primary text-white'
      )}
    >
      <Link to="/sites">
        <img src={tempLogo} alt="SourceHub" className="mr-4" />
      </Link>
      <div data-type="spacer" className="flex flex-1"></div>
      <AppMenu />
      <AppUser />
    </div>
  );
}

function isCurrentClasses(path: string, key: string) {
  return path.startsWith(key)
    ? ['bg-white text-blue-primary hover:text-blue-primary']
    : ['text-gray-100 hover:text-white'];
}

function AppMenu() {
  const location = useLocation();
  const menu: any = useSelector(menuState);

  return (
    <div className="flex flex-row">
      {menu.items.map((menuItem: any) => (
        <Link
          key={menuItem.url}
          className={classNames(
            'cursor-pointer flex px-3 py-2 rounded-md mr-2 select-none',
            isCurrentClasses(location.pathname, menuItem.url)
          )}
          to={menuItem.url}
        >
          {menuItem.label}
        </Link>
      ))}
    </div>
  );
}
