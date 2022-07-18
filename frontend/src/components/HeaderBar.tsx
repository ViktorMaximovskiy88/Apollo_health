import classNames from 'classnames';

interface PropTypes {
  children: any;
  header?: any;
}

export function HeaderBar({ header, children }: PropTypes) {
  return (
    <div className={classNames('flex items-center', header ? 'justify-between' : 'justify-end')}>
      {header}
      <div className="py-2 items-center space-x-2">{children}</div>
    </div>
  );
}
