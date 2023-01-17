import { Viewer, PageChangeEvent, DocumentLoadEvent } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin, DefaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import '@react-pdf-viewer/page-navigation/lib/styles/index.css';

import { useAccessToken } from '../../../common/hooks';
import { baseApiUrl } from '../../../app/base-api';

interface PropTypes {
  fileKey?: string;
  onPageChange?: (currentPage: number) => void;
  defaultLayoutPluginInstance?: DefaultLayoutPlugin;
  onDocLoad: (e: DocumentLoadEvent) => void;
}

export function CompareDocViewer({
  fileKey,
  defaultLayoutPluginInstance,
  onPageChange = () => {},
  onDocLoad = () => {
    return 0;
  },
}: PropTypes) {
  const token = useAccessToken();
  const layoutPlugin = defaultLayoutPluginInstance
    ? defaultLayoutPluginInstance
    : defaultLayoutPlugin();
  if (!token && fileKey) return null;
  return (
    <Viewer
      withCredentials={true}
      fileUrl={`${baseApiUrl}/doc-documents/diff/${fileKey}`}
      plugins={[layoutPlugin]}
      onPageChange={(e: PageChangeEvent) => {
        onPageChange(e.currentPage);
      }}
      onDocumentLoad={onDocLoad}
      httpHeaders={{
        Authorization: `Bearer ${token}`,
      }}
    />
  );
}
