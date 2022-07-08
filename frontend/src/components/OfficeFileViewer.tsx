interface PropTypes {
  url: string;
}

export function OfficeFileViewer({ url }: PropTypes) {
  return (
    <iframe
      style={{ width: '100%', height: '100%' }}
      src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(
        url
      )}`}
    />
  );
}
