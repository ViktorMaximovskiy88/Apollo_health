import classNames from 'classnames';

interface PropTypes {
  children?: any;
  title?: any;
  toolbar?: any;
  section?: boolean;
}

export function PageLayout({ title, toolbar, children, section = false }: PropTypes) {
  const showPageHeader = !!(title || toolbar);
  return (
    <div className={classNames('flex flex-col flex-1 overflow-hidden')}>
      {showPageHeader && (
        <div
          className={classNames(
            'box-border h-[72px] p-4 flex items-center',
            title ? 'justify-between' : 'justify-end',
            section ? '' : 'border-gray-300 border-b-[1px]'
          )}
        >
          {title && <h4>{title}</h4>}
          <div className="space-x-2">{toolbar}</div>
        </div>
      )}
      <div className={classNames('flex flex-1 flex-col')}>
        <div
          className={classNames(
            'flex flex-col p-4 bg-zinc-50 overflow-auto',
            section && showPageHeader
              ? 'section-page-body-layout'
              : section && !showPageHeader
              ? 'section-body-layout'
              : 'page-body-layout'
          )}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
