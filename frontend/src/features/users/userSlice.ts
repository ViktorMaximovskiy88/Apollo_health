import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'full_name', dir: -1 as 1 | -1 | 0 },
    filter: [
      { name: 'full_name', operator: 'contains', type: 'string', value: '' },
      { name: 'email', operator: 'contains', type: 'string', value: '' },
      { name: 'is_admin', operator: 'eq', type: 'select', value: null },
      { name: 'roles', operator: 'eq', type: 'select', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
  },
};

export const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    setUserTableFilter: (state, action: PayloadAction<any>) => {
      console.log(state, initialState.table.filter);
      state.table.filter = action.payload;
    },
    setUserTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setUserTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setUserTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const userTableState = createSelector(
  (state: RootState) => {
    return state.users.table;
  },
  (tableState) => tableState
);

export const { setUserTableFilter, setUserTableSort, setUserTableLimit, setUserTableSkip } =
  userSlice.actions;

export default userSlice.reducer;
