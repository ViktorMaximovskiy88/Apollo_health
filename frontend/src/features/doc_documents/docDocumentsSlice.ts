import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'last_collected_date', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'last_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'link_text', operator: 'contains', type: 'string', value: '' },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'classification_status', operator: 'eq', type: 'select', value: null },
      { name: 'url', operator: 'contains', type: 'string', value: '' },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const docDocuments = createSlice({
  name: 'docDocuments',
  initialState,
  reducers: {
    setDocDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setDocDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setDocDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setDocDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const docDocumentTableState = createSelector(
  (state: RootState) => state.docDocuments.table,
  (tableState) => tableState
);

export const {
  setDocDocumentTableFilter,
  setDocDocumentTableSort,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
} = docDocuments.actions;

export default docDocuments.reducer;
