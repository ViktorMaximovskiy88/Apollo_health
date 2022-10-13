import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

interface GoogleDocLoaderPropTypes {
  docId: string | undefined;
}

interface GoogleDocViewerPropTypes {
  url: string | undefined;
}

export function GoogleDocLoader({ docId }: GoogleDocLoaderPropTypes) {
  const { data: viewer } = useGetDocumentViewerUrlQuery(docId);
  return <GoogleDocViewer url={viewer?.url} />;
}

export function GoogleDocViewer({ url }: GoogleDocViewerPropTypes) {
  if (!url) {
    return <></>;
  }

  return (
    <iframe
      style={{ padding: 0, margin: 0, width: '99%', height: '99%', border: '1px solid #ccc' }}
      frameBorder="0"
      src={`https://docs.google.com/viewer?embedded=true&url=${encodeURIComponent(url)}`}
    />
  );
}
