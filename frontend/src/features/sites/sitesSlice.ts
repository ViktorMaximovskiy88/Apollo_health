import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'last_run_time', dir: -1 as 1 | -1 | 0 },
    selection: { selected: {}, unselected: {} },
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'status', operator: 'eq', type: 'select', value: null },
      { name: 'last_run_time', operator: 'before', type: 'date', value: '' },
      { name: 'last_run_documents', operator: 'contains', type: 'number', value: '' },
      {
        name: 'last_run_status',
        operator: 'eq',
        type: 'select',
        value: null,
      },
      {
        name: 'assignee',
        operator: 'eq',
        type: 'select',
        value: '',
      },
      { name: 'tags', operator: 'contains', type: 'string', value: '' },
      {
        name: 'collection_method',
        operator: 'eq',
        type: 'select',
        value: '',
      },
    ],
    pagination: { limit: 50, skip: 0 },
    forceUpdate: 0,
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
    setSiteTableSelect: (state, action: PayloadAction<any>) => {
      state.table.selection = action.payload;
    },
    setSiteTableForceUpdate: (state) => {
      state.table.forceUpdate += 1;
    },
  },
});

export const siteTableState = createSelector(
  (state: RootState) => state.sites.table,
  (tableState) => tableState
);

export const {
  setSiteTableFilter,
  setSiteTableSort,
  setSiteTableLimit,
  setSiteTableSkip,
  setSiteTableSelect,
  setSiteTableForceUpdate,
} = sitesSlice.actions;

export default sitesSlice.reducer;
