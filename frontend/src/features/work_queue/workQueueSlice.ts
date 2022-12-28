import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export interface TableState {
  sort?: TypeSortInfo;
  filter: TypeFilterValue;
  pagination: {
    limit: number;
    skip: number;
  };
}

export const initialState: { table: TableState } = {
  table: {
    sort: { name: 'priority', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'locations.site_id', operator: 'eq', type: 'string', value: '' },
      {
        name: 'locks.user_id',
        operator: 'eq',
        type: 'select',
        value: null,
      },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'final_effective_date', operator: 'after', type: 'date', value: '' },
      { name: 'first_collected_date', operator: 'after', type: 'date', value: '' },
      { name: 'priority', operator: 'eq', type: 'number', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const workQueues = createSlice({
  name: 'workQueues',
  initialState,
  reducers: {
    setWorkQueueTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setWorkQueueTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setWorkQueueTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setWorkQueueTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const workQueueTableState = createSelector(
  (state: RootState) => state.workQueues.table,
  (tableState) => tableState
);

export const {
  setWorkQueueTableSkip,
  setWorkQueueTableFilter,
  setWorkQueueTableSort,
  setWorkQueueTableLimit,
} = workQueues.actions;

export default workQueues.reducer;
