import classNames from 'classnames';
import { AppBreadcrumbs } from '../app/AppLayout';

interface PropTypes {
  children: any;
  toolbar?: any;
  scrollBody?: boolean;
  sidebar?: any;
}

export function SectionLayout({ children, toolbar, sidebar, scrollBody = true }: PropTypes) {
  return (
    <div className={classNames('flex flex-col flex-1 ')}>
      <div
        className={classNames(
          'flex flex-1 h-[60px] p-4 border-gray-300 border-b-[1px] justify-between'
        )}
      >
        <div className="flex flex-1">
          <AppBreadcrumbs />
        </div>
        <div>{toolbar}</div>
      </div>
      <div className={classNames('flex flex-1')}>
        {sidebar}
        <div
          className={classNames(
            'flex flex-col app-body-layout p-4 pt-0 bg-zinc-50',
            scrollBody ? 'overflow-auto' : 'overflow-hidden'
          )}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
