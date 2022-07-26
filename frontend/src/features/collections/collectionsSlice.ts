import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'queued_time', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'queued_time', operator: 'before', type: 'date', value: '' },
      { name: 'status', operator: 'eq', type: 'select', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const collectionsSlice = createSlice({
  name: 'collections',
  initialState,
  reducers: {
    setCollectionTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setCollectionTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setCollectionTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setCollectionTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const collectionTableState = createSelector(
  (state: RootState) => state.collections.table,
  (tableState) => tableState
);

export const {
  setCollectionTableFilter,
  setCollectionTableSort,
  setCollectionTableLimit,
  setCollectionTableSkip,
} = collectionsSlice.actions;

export default collectionsSlice.reducer;
