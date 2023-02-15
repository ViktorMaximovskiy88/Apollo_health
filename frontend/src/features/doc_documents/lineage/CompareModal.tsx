import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import { defaultLayoutPlugin, DefaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { DocumentLoadEvent } from '@react-pdf-viewer/core';

import { CompareDocViewer } from './CompareDocumentViewer';
import { CompareModalFooter } from './CompareModalFooter';
import { FullScreenModal } from '../../../components/FullScreenModal';
import { TagComparison } from '../types';

interface DocPages {
  docPageCount: number | undefined;
  updateDocPageCount: (e: DocumentLoadEvent) => void;
  docPage: number | undefined;
  setDocPage: Dispatch<SetStateAction<number | undefined>>;
}

function useDocPages(): DocPages {
  const [docPageCount, setDocPageCount] = useState<number>();
  const [docPage, setDocPage] = useState<number>();

  useEffect(() => {
    setDocPage(0);
  }, [docPageCount]);

  const updateDocPageCount = (e: DocumentLoadEvent) => {
    setDocPageCount(e.doc.numPages);
  };

  return { docPageCount, updateDocPageCount, docPage, setDocPage };
}

function CompareModalBody({
  newFileKey,
  prevFileKey,
  currentDocLayoutPlugin,
  previousDocLayoutPlugin,
  currentDocPages,
  prevDocPages,
  setLatestPage,
}: {
  newFileKey?: string;
  prevFileKey?: string;
  currentDocLayoutPlugin: DefaultLayoutPlugin;
  previousDocLayoutPlugin: DefaultLayoutPlugin;
  currentDocPages: DocPages;
  prevDocPages: DocPages;
  setLatestPage: Dispatch<SetStateAction<number>>;
}) {
  const handleCurrentPageChange = (page: number) => {
    setLatestPage(page);
    currentDocPages.setDocPage(page);
  };

  const handlePrevPageChange = (page: number) => {
    setLatestPage(page);
    prevDocPages.setDocPage(page);
  };

  return (
    <div className="flex h-full">
      <div className="mr-2 flex-grow flex flex-col">
        <h3>Previous Document</h3>
        <div className="overflow-auto">
          <CompareDocViewer
            fileKey={prevFileKey}
            defaultLayoutPluginInstance={previousDocLayoutPlugin}
            onDocLoad={prevDocPages.updateDocPageCount}
            onPageChange={handlePrevPageChange}
          />
        </div>
      </div>
      <div className="mr-2 flex-grow flex flex-col">
        <h3>Current Document</h3>
        <div className="overflow-auto">
          <CompareDocViewer
            fileKey={newFileKey}
            defaultLayoutPluginInstance={currentDocLayoutPlugin}
            onDocLoad={currentDocPages.updateDocPageCount}
            onPageChange={handleCurrentPageChange}
          />
        </div>
      </div>
    </div>
  );
}

export function CompareModal(props: {
  newFileKey?: string;
  prevFileKey?: string;
  modalOpen: boolean;
  handleCloseModal: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
  tagComparison?: TagComparison;
  processCompare?: () => void;
}) {
  const currentDocPages = useDocPages();
  const prevDocPages = useDocPages();
  const [latestPage, setLatestPage] = useState<number>(0);
  const currentDocLayoutPlugin = defaultLayoutPlugin();
  const previousDocLayoutPlugin = defaultLayoutPlugin();

  const updateCurrentPdfPage = (page: number) => {
    currentDocPages.setDocPage(page);
    setLatestPage(page);
    currentDocLayoutPlugin.toolbarPluginInstance.pageNavigationPluginInstance.jumpToPage(page);
  };
  const updatePreviousPdfPage = (page: number) => {
    prevDocPages.setDocPage(page);
    setLatestPage(page);
    previousDocLayoutPlugin.toolbarPluginInstance.pageNavigationPluginInstance.jumpToPage(page);
  };

  let maxPage: undefined | number;
  if (currentDocPages.docPageCount !== undefined && prevDocPages.docPageCount !== undefined) {
    maxPage = Math.max(currentDocPages.docPageCount, prevDocPages.docPageCount);
  }

  return (
    <FullScreenModal
      title="Previous Document Compare"
      footer={
        <CompareModalFooter
          tagComparison={props.tagComparison}
          updateCurrentPdfPage={updateCurrentPdfPage}
          updatePreviousPdfPage={updatePreviousPdfPage}
          hasDocPages={maxPage !== undefined}
          maxPage={maxPage}
          latestPage={latestPage}
          processCompare={props.processCompare}
        />
      }
      open={props.modalOpen}
      onCancel={props.handleCloseModal}
    >
      {props.newFileKey && props.prevFileKey ? (
        <CompareModalBody
          newFileKey={props.newFileKey}
          prevFileKey={props.prevFileKey}
          currentDocLayoutPlugin={currentDocLayoutPlugin}
          previousDocLayoutPlugin={previousDocLayoutPlugin}
          currentDocPages={currentDocPages}
          prevDocPages={prevDocPages}
          setLatestPage={setLatestPage}
        />
      ) : (
        <div>Loading...</div>
      )}
    </FullScreenModal>
  );
}
