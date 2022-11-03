import { Viewer, PageChangeEvent } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import { useAccessToken } from '../../../common/hooks';
import { baseApiUrl } from '../../../app/base-api';

interface PropTypes {
  fileKey?: string;
  onPageChange?: Function;
}

export function CompareDocViewer({ fileKey, onPageChange = () => {} }: PropTypes) {
  const token = useAccessToken();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  if (!token && fileKey) return null;
  return (
    <Viewer
      withCredentials={true}
      fileUrl={`${baseApiUrl}/doc-documents/diff/${fileKey}`}
      plugins={[defaultLayoutPluginInstance]}
      onPageChange={(e: PageChangeEvent) => {
        onPageChange(e.currentPage);
      }}
      httpHeaders={{
        Authorization: `Bearer ${token}`,
      }}
    />
  );
}
