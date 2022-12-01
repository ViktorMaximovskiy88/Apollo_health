import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../../app/store';

export const initialState = {
  table: {
    sort: { name: 'name', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'document_type', operator: 'eq', type: 'select', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'site_ids', operator: 'eq', type: 'select', value: [] },
      { name: 'legacy_relevance', operator: 'eq', type: 'select', value: '' },
      { name: 'field_groups', operator: 'eq', type: 'select', value: '' },
      { name: 'doc_doc_count', operator: 'gte', type: 'number', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const documentFamilies = createSlice({
  name: 'documentFamilies',
  initialState,
  reducers: {
    setDocumentFamilyFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setDocumentFamilyTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setDocumentTableFamilyLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setDocumentFamilyTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const documentFamilyTableState = createSelector(
  (state: RootState) => state.documentFamilies.table,
  (tableState) => tableState
);

export const {
  setDocumentFamilyFilter,
  setDocumentTableFamilyLimit,
  setDocumentFamilyTableSort,
  setDocumentFamilyTableSkip,
} = documentFamilies.actions;

export default documentFamilies.reducer;
