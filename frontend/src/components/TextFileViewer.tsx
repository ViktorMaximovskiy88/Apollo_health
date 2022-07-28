import { useEffect, useState } from 'react';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

interface TextFileLoaderPropTypes {
  docId: string | undefined;
}

interface TextFileViewerPropTypes {
  url: string | undefined;
}

export function TextFileLoader({ docId }: TextFileLoaderPropTypes) {
  const { data: viewer } = useGetDocumentViewerUrlQuery(docId);
  return <TextFileViewer url={viewer?.url} />;
}

export function TextFileViewer({ url }: TextFileViewerPropTypes) {
  const [content, setContent] = useState('');

  useEffect(() => {
    fetch(url as string)
      .then((res) => res.text())
      .then((text) => setContent(text));
  }, [url]);

  if (!url) {
    return <></>;
  }

  return (
    <div>
      <pre>{content}</pre>
    </div>
  );
}
