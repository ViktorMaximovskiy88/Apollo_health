import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

interface OfficeFileLoaderPropTypes {
  docId: string | undefined;
}

interface OfficeFileViewerPropTypes {
  url: string | undefined;
}

export function OfficeFileLoader({ docId }: OfficeFileLoaderPropTypes) {
  const { data: viewer } = useGetDocumentViewerUrlQuery(docId);
  return <OfficeFileViewer url={viewer?.url} />;
}

export function OfficeFileViewer({ url }: OfficeFileViewerPropTypes) {
  if (!url) {
    return <></>;
  }

  return (
    <iframe
      style={{ padding: 0, margin: 0, width: '99%', height: '99%', border: '1px solid #ccc' }}
      title="Office File Viewer"
      frameBorder="0"
      src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(url)}`}
    />
  );
}
