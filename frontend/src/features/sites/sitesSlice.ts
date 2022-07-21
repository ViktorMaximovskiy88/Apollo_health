import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'last_run_time', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'status', operator: 'eq', type: 'select', value: null },
      { name: 'last_run_time', operator: 'before', type: 'date', value: '' },
      {
        name: 'last_run_status',
        operator: 'eq',
        type: 'select',
        value: null,
      },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const sitesSlice = createSlice({
  name: 'sites',
  initialState,
  reducers: {
    setSiteTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setSiteTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setSiteTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setSiteTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const siteTableState = createSelector(
  (state: RootState) => state.sites.table,
  (tableState) => tableState
);

export const { setSiteTableFilter, setSiteTableSort, setSiteTableLimit, setSiteTableSkip } =
  sitesSlice.actions;

export default sitesSlice.reducer;
