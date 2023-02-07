import { Viewer, PageChangeEvent, LoadError } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';
import { ErrorBoundary } from 'react-error-boundary';
import { Button } from 'antd';
import { useTaskWorker } from '../features/tasks/taskSlice';
import classNames from 'classnames';

export function PDFFileLoader({ docId, onPageChange }: { docId?: string; onPageChange: Function }) {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const { data } = useGetDocumentViewerUrlQuery(docId, { refetchOnMountOrArgChange: true });
  const enqueueTask = useTaskWorker();

  if (!data) return null;

  const renderError = (error: LoadError) => {
    let message = '';
    switch (
      error.name // https://react-pdf-viewer.dev/docs/options/
    ) {
      case 'MissingPDFException': // pdf failed to upload or not in s3.
        message = 'PDF file is missing';
        break;
      default: // should be caught by viewErrorFallback
        message = 'PDF file is missing';
        break;
    }

    return (
      <div
        className="flex items-center"
        style={{
          border: '1px solid rgba(0, 0, 0, 0.3)',
          height: '100%',
          justifyContent: 'center',
        }}
      >
        <div className={classNames('mx-2 items-center')}>
          {message}
          <br></br>

          <Button
            // disabled={isLoading}
            onClick={async () => {
              enqueueTask('RegeneratePdfTask', {
                doc_doc_id: docId,
                // retr_doc_id: docId,
              });
            }}
            className="ml-auto"
          >
            Regenerate Pdf
          </Button>
        </div>
      </div>
    );
  };

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
        renderError={renderError} // Handle invalid fileUrl (missing pdf)
        fileUrl={data.url}
        plugins={[defaultLayoutPluginInstance]}
        onPageChange={(e: PageChangeEvent) => {
          onPageChange(e.currentPage);
        }}
      />
    </ErrorBoundary>
  );
}
