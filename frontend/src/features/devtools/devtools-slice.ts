import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../app/store';
import { makeActionDispatch } from '../../common/helpers';
import { DevToolsGroup, DevToolsDoc } from './types';
import { devtoolsApi } from './devtoolsApi';
import { Site } from '../../features/sites/types';
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
  item: DevToolsDoc;
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

interface PagedList {
  totalCount?: number;
  currentPage: number;
  perPage: number;
}

interface DevToolsState {
  docSearchQuery: string;
  searchTerm: string;
  groupByKey: string;
  viewItems: ViewItem[];
  displayItems: DevToolsGroup[];
  domainItems: DevToolsDoc[];
  filters: FilterSettings;
  compareDocs: CompareDocs;
  defaultView: string;
  selectedSite: Site | undefined;
  siteOptions: Site[];
  groupByOptions: any[];
  viewTypeOptions: any[];
  pager: PagedList;
}

const initialState: DevToolsState = {
  docSearchQuery: '',
  defaultView: 'file',
  viewTypeOptions: [
    { label: 'Info', value: 'info' },
    { label: 'Document', value: 'file' },
    { label: 'Text', value: 'text' },
    { label: 'JSON', value: 'json' },
  ],
  selectedSite: undefined,
  siteOptions: [],
  viewItems: [],
  searchTerm: '',
  domainItems: [],
  displayItems: [],
  compareDocs: {
    showModal: false,
    fileKeys: [],
  },
  groupByKey: 'document_type',
  groupByOptions: [
    { label: 'Doc Type', value: 'document_type' },
    { label: 'Lineage', value: 'lineage_id' },
    { label: 'Status', value: 'classification_status' },
  ],
  filters: {
    singularLineage: false,
    multipleLineage: false,
    missingLineage: false,
  },
  pager: {
    totalCount: 0,
    currentPage: 0,
    perPage: 50,
  },
};

export const devtoolsSlice = createSlice({
  name: 'devtools',
  initialState,
  reducers: {
    updatePager: (state, action: PayloadAction<PagedList>) => {
      state.pager.currentPage = action.payload.currentPage;
      state.pager.perPage = action.payload.perPage;
    },

    setDefaultView: (state, action: PayloadAction<string>) => {
      state.defaultView = action.payload;
    },
    setDocSearchQuery: (state, action: PayloadAction<string>) => {
      state.docSearchQuery = action.payload;
    },
    setGroupByKey: (state, action: PayloadAction<string>) => {
      state.groupByKey = action.payload;
      state.displayItems = groupItems(state.groupByKey, state.domainItems);
    },
    setViewItem: (state, action: PayloadAction<DevToolsDoc>) => {
      state.viewItems = [{ item: action.payload, currentView: state.defaultView }];
    },
    clearViewItem: (state) => {
      state.viewItems = [];
    },
    setSplitItem: (state, action: PayloadAction<DevToolsDoc>) => {
      const viewItem = { item: action.payload, currentView: state.defaultView };
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
    toggleCollapsed: (state, action: PayloadAction<DevToolsGroup>) => {
      const itemGroup = state.displayItems.find(
        (item) => item.groupByKey === action.payload.groupByKey
      );
      if (itemGroup) {
        itemGroup.collapsed = !itemGroup.collapsed;
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
    clearSiteSearch: (state) => {
      state.siteOptions = [];
    },
    selectSite: (state, action: PayloadAction<Site | undefined>) => {
      state.selectedSite = action.payload;
    },
    onDocSearch: (state, action: PayloadAction<string>) => {
      state.searchTerm = action.payload;
      const regex = new RegExp(state.searchTerm, 'i');
      const filtered = state.domainItems.filter((doc: any) => doc.name?.match(regex));
      state.displayItems = groupItems(state.groupByKey, filtered);
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(devtoolsApi.endpoints.getDocuments.matchFulfilled, (state, { payload }) => {
      state.domainItems = payload.items;
      state.pager.totalCount = payload.total_count;
      state.displayItems = groupItems(state.groupByKey, state.domainItems);
    });

    builder.addMatcher(devtoolsApi.endpoints.searchSites.matchFulfilled, (state, { payload }) => {
      state.siteOptions = payload.items;
      if (state.siteOptions.length === 1) {
        state.selectedSite = state.siteOptions[0];
      }
    });
  },
});

function groupItems(groupByKey: string, items: DevToolsDoc[]): DevToolsGroup[] {
  return _(items)
    .groupBy(groupByKey)
    .map((items, groupByKey) => {
      let groupedItems = items;
      if (groupByKey === 'lineage_id') {
        const currentIndex = items.findIndex((item) => item.is_current_version);
        const groupedItems = items.splice(currentIndex, 1);

        while (items.length > 0) {
          const child = groupedItems[0];
          const parentIndex = items.findIndex((item) => item._id === child.previous_doc_doc_id);
          const [parent] = items.splice(parentIndex, 1);
          groupedItems.unshift(parent);
        }
      }
      return {
        groupByKey,
        items: groupedItems,
        collapsed: false,
      } as DevToolsGroup;
    })
    .value();
}

export const devtoolsListSelector = createSelector(
  (state: RootState) => state.devtools.displayItems,
  (devtoolsState) => devtoolsState
);

export const devtoolsSelector = createSelector(
  (state: RootState) => state.devtools,
  (devtoolsState) => devtoolsState
);

export function useDevToolsSlice() {
  const state = useSelector(devtoolsSelector);
  const dispatch = useDispatch();
  return {
    state: state as DevToolsState,
    actions: makeActionDispatch(devtoolsSlice.actions, dispatch),
  };
}

export default devtoolsSlice.reducer;
