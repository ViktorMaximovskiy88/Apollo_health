import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../../app/store';

export const initialState = {
  table: {
    sort: { name: 'final_effective_date', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const lineageDocDocuments = createSlice({
  name: 'lineageDocDocuments',
  initialState,
  reducers: {
    setLineageDocDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setLineageDocDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setLineageDocDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setLineageDocDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const lineageDocDocumentTableState = createSelector(
  (state: RootState) => state.lineageDocDocuments.table,
  (tableState) => tableState
);

export const {
  setLineageDocDocumentTableFilter,
  setLineageDocDocumentTableSort,
  setLineageDocDocumentTableLimit,
  setLineageDocDocumentTableSkip,
} = lineageDocDocuments.actions;

export default lineageDocDocuments.reducer;
