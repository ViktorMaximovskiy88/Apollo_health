import classNames from 'classnames';
export const TextEllipsis = ({
  className = '',
  text,
  rtl = false,
}: {
  className?: string;
  text: string | JSX.Element;
  rtl?: boolean;
}) => {
  return (
    <div
      className={classNames('flex-inline', className)}
      style={{
        textAlign: 'left',
        direction: rtl ? 'rtl' : 'initial',
        textOverflow: 'ellipsis',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
      }}
    >
      {text}
    </div>
  );
};
