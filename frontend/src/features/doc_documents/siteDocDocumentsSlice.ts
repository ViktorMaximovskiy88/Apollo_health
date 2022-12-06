import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LOCATION_CHANGE } from 'redux-first-history';
import { RootState } from '../../app/store';

export const initialState = {
  siteId: '',
  table: {
    sort: { name: 'final_effective_date', dir: -1 as 1 | -1 | 0 },
    selection: { selected: {}, unselected: {} },
    filter: [
      { name: 'last_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'link_text', operator: 'contains', type: 'string', value: '' },
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'internal_document', operator: 'eq', type: 'select', value: null },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'url', operator: 'contains', type: 'string', value: '' },
      { name: 'document_family_id', operator: 'eq', type: 'select', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
    forceUpdate: 0,
  },
};

export const siteDocDocuments = createSlice({
  name: 'siteDocDocuments',
  initialState,
  reducers: {
    setSiteDocDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setSiteDocDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setSiteDocDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setSiteDocDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
    setSiteDocDocumentTableSelect: (state, action: PayloadAction<any>) => {
      state.table.selection = action.payload;
    },
    setSiteDocDocumentTableForceUpdate: (state) => {
      state.table.forceUpdate += 1;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(LOCATION_CHANGE, (state, action: any) => {
      const pathname: string = action.payload.location.pathname;
      if (pathname.startsWith('/sites')) {
        const siteId = pathname.split('/')[2];
        if (state.siteId !== siteId) {
          state.table.selection = initialState.table.selection;
        }
        state.siteId = siteId;
      }
    });
  },
});

export const siteDocDocumentTableState = createSelector(
  (state: RootState) => state.siteDocDocuments.table,
  (tableState) => tableState
);

export const {
  setSiteDocDocumentTableFilter,
  setSiteDocDocumentTableSort,
  setSiteDocDocumentTableLimit,
  setSiteDocDocumentTableSkip,
  setSiteDocDocumentTableSelect,
  setSiteDocDocumentTableForceUpdate,
} = siteDocDocuments.actions;

export default siteDocDocuments.reducer;
