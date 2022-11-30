import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: undefined,
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'locations.site_id', operator: 'eq', type: 'select', value: '' },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'classification_status', operator: 'eq', type: 'select', value: null },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'locations.payer_family_id', operator: 'eq', type: 'select', value: '' },
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
