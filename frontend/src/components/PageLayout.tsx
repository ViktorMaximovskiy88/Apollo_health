import classNames from 'classnames';

interface PropTypes {
  children?: any;
  title?: any;
  toolbar?: any;
}

export function PageLayout({ title, toolbar, children }: PropTypes) {
  return (
    <div className={classNames('flex flex-col flex-1 ')}>
      <div
        className={classNames(
          'box-border min-h-[72px] py-2 flex items-center',
          title ? 'justify-between' : 'justify-end'
        )}
      >
        {title && <h4>{title}</h4>}
        <div>{toolbar}</div>
      </div>
      <div className={classNames('flex flex-1')}>
        <div className={classNames('flex flex-col app-body-layout p-4 pt-0 bg-zinc-50')}>
          {children}
        </div>
      </div>
    </div>
  );
}
