import { Viewer, PageChangeEvent } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';
import { ErrorBoundary } from 'react-error-boundary';
import { Button } from 'antd';
export function PDFFileLoader({ docId, onPageChange }: { docId?: string; onPageChange: Function }) {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const { data } = useGetDocumentViewerUrlQuery(docId, { refetchOnMountOrArgChange: true });

  if (!data) return null;

  const ViewerErrorFallback = () => {
    return (
      <div className="grid place-content-center h-screen">
        <span className="mr-2 mb-2">Error Loading File, please download to view</span>

        <Button type="primary" danger>
          <a href={data.url} download>
            Download
          </a>
        </Button>
      </div>
    );
  };

  return (
    <ErrorBoundary FallbackComponent={ViewerErrorFallback}>
      <Viewer
        fileUrl={data.url}
        plugins={[defaultLayoutPluginInstance]}
        onPageChange={(e: PageChangeEvent) => {
          onPageChange(e.currentPage);
        }}
      />
    </ErrorBoundary>
  );
}
