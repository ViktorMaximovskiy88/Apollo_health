import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'final_effective_date', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'locations.site_id', operator: 'eq', type: 'select', value: '' },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'first_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'last_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'classification_status', operator: 'eq', type: 'select', value: null },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'is_current_version', operator: 'eq', type: 'boolean', value: null },
      { name: 'locations.link_text', operator: 'contains', type: 'string', value: '' },
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
