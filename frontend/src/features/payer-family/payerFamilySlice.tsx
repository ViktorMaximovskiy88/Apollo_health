import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'name', dir: 1 as 1 | -1 | 0 },
    filter: [
      { name: 'document_type', operator: 'eq', type: 'select', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'doc_doc_count', operator: 'gte', type: 'number', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const payerFamilies = createSlice({
  name: 'payerFamilies',
  initialState,
  reducers: {
    setPayerFamilyFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setPayerFamilyTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setPayerTableFamilyLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setPayerFamilyTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const payerFamilyTableState = createSelector(
  (state: RootState) => state.payerFamilies.table,
  (tableState) => tableState
);

export const {
  setPayerFamilyFilter,
  setPayerTableFamilyLimit,
  setPayerFamilyTableSort,
  setPayerFamilyTableSkip,
} = payerFamilies.actions;

export default payerFamilies.reducer;
