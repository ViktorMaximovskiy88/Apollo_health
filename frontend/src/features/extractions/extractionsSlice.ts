import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LOCATION_CHANGE } from 'redux-first-history';
import { RootState } from '../../app/store';

export const initialState = {
  extractions: {
    table: {
      sort: { name: 'first_collected_date', dir: -1 as 1 | -1 | 0 },
      filter: [
        {
          name: 'first_collected_date',
          operator: 'before',
          type: 'date',
          value: '',
        },
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'select', value: null },
      ],
      pagination: { limit: 50, skip: 0 },
    },
  },
  extraction_tasks: {
    table: {
      sort: { name: 'queued_time', dir: -1 as 1 | -1 | 0 },
      filter: [
        { name: 'queued_time', operator: 'before', type: 'date', value: '' },
        { name: 'status', operator: 'eq', type: 'select', value: null },
      ],
      pagination: { limit: 50, skip: 0 },
    },
  },
  extracted_documents: {
    table: {
      sort: { name: 'first_collected_date', dir: -1 as 1 | -1 | 0 },
      filter: [
        {
          name: 'first_collected_date',
          operator: 'before',
          type: 'date',
          value: '',
        },
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'select', value: null },
      ],
      pagination: { limit: 50, skip: 0 },
    },
  },
};

export const extractions = createSlice({
  name: 'extractions',
  initialState,
  reducers: {
    setExtractedDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.filter = action.payload;
    },
    setExtractedDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.sort = action.payload;
    },
    setExtractedDocumentTableLimit: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.pagination.limit = action.payload;
    },
    setExtractedDocumentTableSkip: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.pagination.skip = action.payload;
    },
    setExtractionTaskTableFilter: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.filter = action.payload;
    },
    setExtractionTaskTableSort: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.sort = action.payload;
    },
    setExtractionTaskTableLimit: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.pagination.limit = action.payload;
    },
    setExtractionTaskTableSkip: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.pagination.skip = action.payload;
    },
    setExtractionTableFilter: (state, action: PayloadAction<any>) => {
      state.extractions.table.filter = action.payload;
    },
    setExtractionTableSort: (state, action: PayloadAction<any>) => {
      state.extractions.table.sort = action.payload;
    },
    setExtractionTableLimit: (state, action: PayloadAction<any>) => {
      state.extractions.table.pagination.limit = action.payload;
    },
    setExtractionTableSkip: (state, action: PayloadAction<any>) => {
      state.extractions.table.pagination.skip = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(LOCATION_CHANGE, (state, action: any) => {
      const path: string = action.payload.location.pathname;
      if (!path.startsWith('/sites/')) {
        state.extracted_documents.table = initialState.extracted_documents.table;
        state.extraction_tasks.table = initialState.extraction_tasks.table;
        state.extractions.table = initialState.extractions.table;
      }
    });
  },
});

export const extractedDocumentTableState = createSelector(
  (state: RootState) => state.extractions.extracted_documents.table,
  (tableState) => tableState
);

export const extractionTaskTableState = createSelector(
  (state: RootState) => state.extractions.extraction_tasks.table,
  (tableState) => tableState
);

export const extractionTableState = createSelector(
  (state: RootState) => state.extractions.extractions.table,
  (tableState) => tableState
);

export const {
  setExtractedDocumentTableFilter,
  setExtractedDocumentTableSort,
  setExtractedDocumentTableLimit,
  setExtractedDocumentTableSkip,
  setExtractionTaskTableFilter,
  setExtractionTaskTableSort,
  setExtractionTaskTableLimit,
  setExtractionTaskTableSkip,
  setExtractionTableFilter,
  setExtractionTableSort,
  setExtractionTableLimit,
  setExtractionTableSkip,
} = extractions.actions;

export default extractions.reducer;
