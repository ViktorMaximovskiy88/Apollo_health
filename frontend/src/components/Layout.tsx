import classNames from 'classnames';

interface PropTypes {
  children?: any;
  title?: any;
  toolbar?: any;
  sidebar?: any;
  gap?: boolean;
  className?: string;
  border?: boolean;
}

export function Layout({
  title,
  toolbar,
  sidebar,
  children,
  gap = true,
  border = false,
}: PropTypes) {
  const showPageHeader = !!(title || toolbar);

  return (
    <div className={classNames('flex flex-col flex-1 overflow-hidden h-full')}>
      {showPageHeader && (
        <div
          className={classNames(
            'box-border h-12 flex items-center p-2',
            title ? 'justify-between' : 'justify-end',
            border ? 'border border-zinc-100' : ''
          )}
        >
          {title}
          <div className={classNames('space-x-2')}>{toolbar}</div>
        </div>
      )}
      <div className={classNames('flex flex-1', showPageHeader ? 'layout-with-header' : 'layout')}>
        {sidebar}
        <div
          className={classNames(
            'flex flex-1 flex-col bg-zinc-50 overflow-auto',
            gap && 'p-2',
            showPageHeader && 'pt-0'
          )}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
