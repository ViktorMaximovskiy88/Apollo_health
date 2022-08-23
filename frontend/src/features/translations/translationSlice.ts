import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'name', dir: -1 as 1 | -1 | 0 },
    filter: [{ name: 'name', operator: 'contains', type: 'string', value: '' }],
    pagination: { limit: 50, skip: 0 },
  },
};

export const translations = createSlice({
  name: 'translations',
  initialState,
  reducers: {
    setTranslationTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setTranslationTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setTranslationTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setTranslationTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
  },
});

export const translationTableState = createSelector(
  (state: RootState) => state.translations.table,
  (tableState) => tableState
);

export const {
  setTranslationTableFilter,
  setTranslationTableSort,
  setTranslationTableLimit,
  setTranslationTableSkip,
} = translations.actions;

export default translations.reducer;
