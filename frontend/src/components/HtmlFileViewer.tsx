import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

interface HtmlFileLoaderPropTypes {
  docId: string | undefined;
}

interface HtmlFileViewerPropTypes {
  url: string | undefined;
}

export function HtmlFileLoader({ docId }: HtmlFileLoaderPropTypes) {
  const { data: viewer } = useGetDocumentViewerUrlQuery(docId);
  return <HtmlFileViewer url={viewer?.url} />;
}

export function HtmlFileViewer({ url }: HtmlFileViewerPropTypes) {
  if (!url) {
    return <></>;
  }

  return (
    <iframe
      style={{ padding: 0, margin: 0, width: '99%', height: '99%', border: '1px solid #ccc' }}
      frameBorder="0"
      src={url}
    />
  );
}
