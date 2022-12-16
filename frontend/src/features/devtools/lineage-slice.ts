import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../app/store';
import { makeActionDispatch } from '../../common/helpers';
import { LineageGroup, LineageDoc } from './types';
import { lineageApi } from './lineageApi';
import _ from 'lodash';

interface FilterSettings {
  singularLineage: boolean;
  multipleLineage: boolean;
  missingLineage: boolean;
}

interface ChangeDisplayView {
  index: number;
  viewKey: string;
}

interface ViewItem {
  item: LineageDoc;
  currentView: string;
}

interface CompareResult {
  new_key: string;
  prev_key: string;
}

interface CompareDocs {
  showModal: boolean;
  fileKeys: string[];
}

interface LineageState {
  searchTerm: string;
  viewItems: ViewItem[];
  displayItems: LineageGroup[];
  domainItems: LineageDoc[];
  filters: FilterSettings;
  compareDocs: CompareDocs;
}

export const lineageSlice = createSlice({
  name: 'lineage',
  initialState: {
    viewItems: [],
    searchTerm: '',
    domainItems: [],
    displayItems: [],
    compareDocs: {
      showModal: false,
      fileKeys: [],
    },
    filters: {
      singularLineage: false,
      multipleLineage: false,
      missingLineage: false,
    },
  } as LineageState,
  reducers: {
    setViewItem: (state, action: PayloadAction<LineageDoc>) => {
      state.viewItems = [{ item: action.payload, currentView: 'file' }];
    },
    setSplitItem: (state, action: PayloadAction<LineageDoc>) => {
      const viewItem = { item: action.payload, currentView: 'file' };
      state.viewItems = [...state.viewItems, viewItem];
    },
    removeViewItemByIndex: (state, action: PayloadAction<number>) => {
      state.viewItems.splice(action.payload, 1);
      state.viewItems = [...state.viewItems];
    },
    setViewItemDisplay: (state, action: PayloadAction<ChangeDisplayView>) => {
      state.viewItems[action.payload.index].currentView = action.payload.viewKey;
    },
    setCompareResult: (state, action: PayloadAction<CompareResult>) => {
      state.compareDocs.fileKeys = [action.payload.new_key, action.payload.prev_key];
    },
    toggleCompareModal: (state, action: PayloadAction<boolean | undefined>) => {
      if (action.payload !== undefined) {
        state.compareDocs.showModal = action.payload;
      } else {
        state.compareDocs.showModal = !state.compareDocs.showModal;
      }
    },

    toggleCollapsed: (state, action: PayloadAction<LineageGroup>) => {
      const lineageGroup = state.displayItems.find(
        (item) => item.lineageId === action.payload.lineageId
      );
      if (lineageGroup) {
        lineageGroup.collapsed = !lineageGroup.collapsed;
      }
    },
    setCollapsed: (state, action: PayloadAction<boolean>) => {
      const collapsed = action.payload;
      for (const item of state.displayItems) {
        item.collapsed = collapsed;
      }
    },
    toggleSingularLineage: (state) => {
      state.filters.singularLineage = !state.filters.singularLineage;
    },
    toggleMultipleLineage: (state) => {
      state.filters.multipleLineage = !state.filters.multipleLineage;
    },
    toggleMissingLineage: (state) => {
      state.filters.missingLineage = !state.filters.missingLineage;
    },
    onSearch: (state, action: PayloadAction<string>) => {
      state.searchTerm = action.payload;
      const regex = new RegExp(state.searchTerm, 'i');
      const filtered = state.domainItems.filter((doc: any) => doc.name?.match(regex));
      state.displayItems = groupItems(filtered);
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(lineageApi.endpoints.getSiteLineage.matchFulfilled, (state, { payload }) => {
      state.domainItems = payload;
      state.displayItems = groupItems(state.domainItems);
    });
  },
});

function groupItems(items: LineageDoc[]): LineageGroup[] {
  return _(items)
    .groupBy('lineage_id')
    .map((items, lineageId) => {
      const currentIndex = items.findIndex((item) => item.is_current_version);
      const ordered = items.splice(currentIndex, 1);

      while (items.length > 0) {
        const child = ordered[0];
        const parentIndex = items.findIndex((item) => item._id === child.previous_doc_id);
        const [parent] = items.splice(parentIndex, 1);
        ordered.unshift(parent);
      }

      return {
        lineageId,
        items: ordered,
        collapsed: false,
      } as LineageGroup;
    })
    .value();
}

export const lineageListSelector = createSelector(
  (state: RootState) => state.lineage.displayItems,
  (lineageState) => lineageState
);

export const lineageSelector = createSelector(
  (state: RootState) => state.lineage,
  (lineageState) => lineageState
);

export function useLineageSlice() {
  const state = useSelector(lineageSelector);
  const dispatch = useDispatch();
  return {
    state: state as LineageState,
    actions: makeActionDispatch(lineageSlice.actions, dispatch),
  };
}

export default lineageSlice.reducer;