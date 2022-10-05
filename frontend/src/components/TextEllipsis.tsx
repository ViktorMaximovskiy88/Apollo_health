export const TextEllipsis = ({ text, rtl = false }: { text: string; rtl?: boolean }) => {
  return (
    <div
      className="flex-inline"
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
