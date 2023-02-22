import { useCallback } from 'react';
import { useSelector } from 'react-redux';
import { Spin } from 'antd';

import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { MainLayout } from '../../components';
import { DocTypeUpdateModal } from './DocTypeBulkUpdateModal';
import {
  docDocumentTableState,
  setDocDocumentTableForceUpdate,
  setDocDocumentTableSelect,
} from './docDocumentsSlice';
import { useAppDispatch } from '../../app/store';
import { useLazyGetDocDocumentsQuery } from './docDocumentApi';

function SectionToolbar(props: { isFetching: boolean }) {
  const { isFetching } = props;
  const tableState = useSelector(docDocumentTableState);
  const dispatch = useAppDispatch();
  const onBulkSubmit = useCallback(() => {
    dispatch(setDocDocumentTableForceUpdate());
    dispatch(setDocDocumentTableSelect({ selected: {}, unselected: {} }));
  }, [dispatch, setDocDocumentTableForceUpdate, setDocDocumentTableSelect]);

  return (
    <>
      <Spin spinning={isFetching} />
      <DocTypeUpdateModal
        selection={tableState.selection}
        filterValue={tableState.filter}
        onBulkSubmit={onBulkSubmit}
      />
    </>
  );
}

export function DocDocumentsPage() {
  const [getDocDocumentsFn, { isFetching }] = useLazyGetDocDocumentsQuery();

  return (
    <MainLayout sectionToolbar={<SectionToolbar isFetching={isFetching} />}>
      <DocDocumentsDataTable getDocDocumentsFn={getDocDocumentsFn} />
    </MainLayout>
  );
}
