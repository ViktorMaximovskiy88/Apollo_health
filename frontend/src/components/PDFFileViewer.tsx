import { Viewer, PageChangeEvent } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

export function PDFFileLoader({ docId, onPageChange }: { docId?: string; onPageChange: Function }) {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const { data } = useGetDocumentViewerUrlQuery(docId);
  if (!data) return null;

  return (
    <Viewer
      fileUrl={data.url}
      plugins={[defaultLayoutPluginInstance]}
      onPageChange={(e: PageChangeEvent) => {
        onPageChange(e.currentPage);
      }}
    />
  );
}
