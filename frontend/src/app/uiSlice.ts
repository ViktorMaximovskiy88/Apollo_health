import { createSelector, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { LOCATION_CHANGE } from "redux-first-history";
import { RootState } from "./store";

const initialState = {
  extractions: {
    table: {
      sort: [
        { name: 'collection_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'collection_time', operator: 'before', type: 'date', value: '' },
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'select', value: null },
      ],
    }
  },
  extraction_tasks: {
    table: {
      sort: [
        { name: 'queued_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'queued_time', operator: 'before', type: 'date', value: '' },
        { name: 'status', operator: 'eq', type: 'select', value: null },
      ],
    }
  },
  extracted_documents: {
    table: {
      sort: [
        { name: 'collection_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'collection_time', operator: 'before', type: 'date', value: '' },
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'select', value: null },
      ],
    }
  },
  documents: {
    table: {
      sort: [
        { name: 'collection_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'collection_time', operator: 'before', type: 'date', value: '' },
        { name: 'last_seen', operator: 'before', type: 'date', value: '' },
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'select', value: null },
      ],
    }
  },
  collections: {
    table: {
      sort: [
        { name: 'queued_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'queued_time', operator: 'before', type: 'date', value: '' },
        { name: 'status', operator: 'eq', type: 'select', value: null },
      ],
    }
  },
  sites: {
    table: {
      sort: [
        { name: 'last_run_time', dir: -1 as 1 | -1 | 0 },
      ],
      filter: [
        { name: 'name', operator: 'contains', type: 'string', value: '' },
        { name: 'last_run_time', operator: 'before', type: 'date', value: '' },
        { name: 'last_status', operator: 'eq', type: 'select', value: null },
      ],
    }
  }
}

export const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setSiteTableFilter: (state, action: PayloadAction<any>) => {
      state.sites.table.filter = action.payload
    },
    setSiteTableSort: (state, action: PayloadAction<any>) => {
      state.sites.table.sort = action.payload
    },
    setCollectionTableFilter: (state, action: PayloadAction<any>) => {
      state.collections.table.filter = action.payload
    },
    setCollectionTableSort: (state, action: PayloadAction<any>) => {
      state.collections.table.sort = action.payload
    },
    setDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.documents.table.filter = action.payload
    },
    setDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.documents.table.sort = action.payload
    },
    setExtractedDocumentTableFilter: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.filter = action.payload
    },
    setExtractedDocumentTableSort: (state, action: PayloadAction<any>) => {
      state.extracted_documents.table.sort = action.payload
    },
    setExtractionTaskTableFilter: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.filter = action.payload
    },
    setExtractionTaskTableSort: (state, action: PayloadAction<any>) => {
      state.extraction_tasks.table.sort = action.payload
    },
    setExtractionTableFilter: (state, action: PayloadAction<any>) => {
      state.extractions.table.filter = action.payload
    },
    setExtractionTableSort: (state, action: PayloadAction<any>) => {
      state.extractions.table.sort = action.payload
    },
  },
  extraReducers: (builder) => {
    builder.addCase(LOCATION_CHANGE, (state, action: any) => {
      const path: string = action.payload.location.pathname
      if (!path.startsWith('/sites/')) {
        state.documents.table = initialState.documents.table
        state.collections.table = initialState.collections.table
        state.extracted_documents.table = initialState.extracted_documents.table
        state.extraction_tasks.table = initialState.extraction_tasks.table
        state.extractions.table = initialState.extractions.table
      }
    })
  }
})

export const siteTableState = createSelector(
  (state: RootState) => state.ui.sites.table,
  (tableState) => tableState
);

export const collectionTableState = createSelector(
  (state: RootState) => state.ui.collections.table,
  (tableState) => tableState
);

export const documentTableState = createSelector(
  (state: RootState) => state.ui.documents.table,
  (tableState) => tableState
);

export const extractedDocumentTableState = createSelector(
  (state: RootState) => state.ui.extracted_documents.table,
  (tableState) => tableState
);

export const extractionTaskTableState = createSelector(
  (state: RootState) => state.ui.extraction_tasks.table,
  (tableState) => tableState
);

export const extractionTableState = createSelector(
  (state: RootState) => state.ui.extractions.table,
  (tableState) => tableState
);

export const {
  setSiteTableFilter,
  setSiteTableSort,
  setCollectionTableFilter,
  setCollectionTableSort,
  setDocumentTableFilter,
  setDocumentTableSort,
  setExtractedDocumentTableFilter,
  setExtractedDocumentTableSort,
  setExtractionTaskTableFilter,
  setExtractionTaskTableSort,
  setExtractionTableFilter,
  setExtractionTableSort,
} = uiSlice.actions;

export default uiSlice.reducer