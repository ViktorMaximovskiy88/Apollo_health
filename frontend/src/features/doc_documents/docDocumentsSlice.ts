import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LOCATION_CHANGE } from 'redux-first-history';
import { RootState } from '../../app/store';

export const initialState = {
  table: {
    sort: { name: 'locations.link_text', dir: 1 as 1 | -1 | 0 },
    selection: undefined,
    filter: [
      { name: 'name', operator: 'contains', type: 'string', value: '' },
      { name: 'locations.site_id', operator: 'eq', type: 'select', value: '' },
      { name: 'final_effective_date', operator: 'before', type: 'date', value: '' },
      { name: 'status', operator: 'eq', type: 'select', value: null },
      { name: 'classification_status', operator: 'eq', type: 'select', value: null },
      { name: 'family_status', operator: 'eq', type: 'select', value: null },
      { name: 'content_extraction_status', operator: 'eq', type: 'select', value: null },
      { name: 'document_type', operator: 'eq', type: 'select', value: null },
      { name: 'locations.payer_family_id', operator: 'eq', type: 'select', value: '' },
      { name: 'document_family_id', operator: 'eq', type: 'select', value: null },
      { name: 'first_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'last_collected_date', operator: 'before', type: 'date', value: '' },
      { name: 'priority', operator: 'eq', type: 'number', value: null },
    ],
    pagination: { limit: 50, skip: 0 },
    forceUpdate: 0,
  },
};

export const docDocuments = createSlice({
  name: 'docDocuments',
  initialState,
  reducers: {
    setDocDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.table.filter = action.payload;
    },
    setDocDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.table.sort = action.payload;
    },
    setDocDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.table.pagination.limit = action.payload;
    },
    setDocDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.table.pagination.skip = action.payload;
    },
    setDocDocumentTableSelect: (state, action: PayloadAction<any>) => {
      state.table.selection = action.payload;
    },
    setDocDocumentTableForceUpdate: (state) => {
      state.table.forceUpdate += 1;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(LOCATION_CHANGE, (state, action: any) => {
      const pathname: string = action.payload.location.pathname;
      if (!pathname.startsWith('/documents')) {
        state.table.selection = initialState.table.selection;
      }
    });
  },
});

export const docDocumentTableState = createSelector(
  (state: RootState) => state.docDocuments.table,
  (tableState) => tableState
);

export const {
  setDocDocumentTableFilter,
  setDocDocumentTableSort,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
  setDocDocumentTableSelect,
  setDocDocumentTableForceUpdate,
} = docDocuments.actions;

export default docDocuments.reducer;
