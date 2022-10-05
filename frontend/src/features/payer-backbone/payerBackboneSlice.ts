import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'name', dir: 1 as 1 | -1 | 0 },
    filter: [{ name: 'name', operator: 'contains', type: 'string', value: '' }],
    pagination: { limit: 50, skip: 0 },
  },
};

export const payerBackbone = createSlice({
  name: 'payerBackbone',
  initialState,
  reducers: {
    setPayerBackboneTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setPayerBackboneTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setPayerBackboneTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setPayerBackboneTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const payerBackboneTableState = createSelector(
  (state: RootState) => state.payerBackbone.table,
  (tableState) => tableState
);

export const {
  setPayerBackboneTableFilter,
  setPayerBackboneTableSort,
  setPayerBackboneTableLimit,
  setPayerBackboneTableSkip,
} = payerBackbone.actions;

export default payerBackbone.reducer;
