import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { MainLayout } from '../../components';
import { DocTypeUpdateModal } from './DocTypeBulkUpdateModal';
import { useSelector } from 'react-redux';
import {
  docDocumentTableState,
  setDocDocumentTableForceUpdate,
  setDocDocumentTableSelect,
} from './docDocumentsSlice';
import { useCallback } from 'react';
import { useAppDispatch } from '../../app/store';

function SectionToolbar() {
  const tableState = useSelector(docDocumentTableState);
  const dispatch = useAppDispatch();
  const onBulkSubmit = useCallback(() => {
    dispatch(setDocDocumentTableForceUpdate());
    dispatch(setDocDocumentTableSelect({ selected: {}, unselected: {} }));
  }, [dispatch, setDocDocumentTableForceUpdate, setDocDocumentTableSelect]);
  return (
    <DocTypeUpdateModal
      selection={tableState.selection}
      filterValue={tableState.filter}
      onBulkSubmit={onBulkSubmit}
    />
  );
}

export function DocDocumentsPage() {
  return (
    <MainLayout sectionToolbar={<SectionToolbar />}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
