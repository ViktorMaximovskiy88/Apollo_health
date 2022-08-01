import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'first_collected_date', dir: -1 as 1 | -1 | 0 },
    filter: [
      {
        name: 'first_collected_date',
        operator: 'before',
        type: 'date',
        value: '',
      },
      {
        name: 'last_collected_date',
        operator: 'before',
        type: 'date',
        value: '',
      },
      { name: 'link_text', operator: 'contains', type: 'string', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const documents = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const documentTableState = createSelector(
  (state: RootState) => state.documents.table,
  (tableState) => tableState
);

export const {
  setDocumentTableSkip,
  setDocumentTableFilter,
  setDocumentTableSort,
  setDocumentTableLimit,
} = documents.actions;

export default documents.reducer;
