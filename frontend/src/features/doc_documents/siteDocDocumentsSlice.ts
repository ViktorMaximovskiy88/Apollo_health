import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'final_effective_date', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'last_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'link_text', operator: 'contains', type: 'string', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'internal_document', operator: 'eq', type: 'select', value: null },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'url', operator: 'contains', type: 'string', value: '' },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const siteDocDocuments = createSlice({
  name: 'siteDocDocuments',
  initialState,
  reducers: {
    setSiteDocDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setSiteDocDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setSiteDocDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setSiteDocDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const siteDocDocumentTableState = createSelector(
  (state: RootState) => state.siteDocDocuments.table,
  (tableState) => tableState
);

export const {
  setSiteDocDocumentTableFilter,
  setSiteDocDocumentTableSort,
  setSiteDocDocumentTableLimit,
  setSiteDocDocumentTableSkip,
} = siteDocDocuments.actions;

export default siteDocDocuments.reducer;
