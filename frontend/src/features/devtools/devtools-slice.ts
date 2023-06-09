import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../app/store';
import { makeActionDispatch } from '../../common/helpers';
import { DevToolsGroup, DevToolsDoc } from './types';
import { devtoolsApi } from './devtoolsApi';
import { Site } from '../../features/sites/types';
import _ from 'lodash';
import { TagComparison } from '../doc_documents/types';

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
  tag_comparison?: TagComparison;
}

interface CompareDocs {
  showModal: boolean;
  fileKeys: string[];
  tagComparison?: TagComparison;
}

interface PagedList {
  totalPages: number;
  totalCount: number;
  currentPage: number;
  perPage: number;
}

interface DevToolsState {
  docSearchQuery: string;
  searchTerm: string;
  selectedGroupBy: any;
  viewItems: ViewItem[];
  displayItems: DevToolsGroup[];
  domainItems: DevToolsDoc[];
  filters: FilterSettings;
  compareDocs: CompareDocs;
  selectedDefaultViewType: any;
  selectedSite: Site | undefined;
  siteOptions: Site[];
  selectedSortBy: any;
  sortByOptions: any[];
  groupByOptions: any[];
  viewTypeOptions: any[];
  pager: PagedList;
}

const viewTypeOptions = [
  { label: 'Info', value: 'info' },
  { label: 'Document', value: 'file' },
  { label: 'Text', value: 'text' },
  { label: 'JSON', value: 'json' },
];

const sortByOptions = [
  { label: 'Last Collected', value: '-last_collected_date' },
  { label: 'First Collected', value: '-first_collected_date' },
  { label: 'Effective Date', value: '-final_effective_date' },
  { label: 'Priority', value: '-priority' },
  { label: 'Doc Type', value: 'document_type' },
  { label: 'Status', value: 'classification_status' },
];

const groupByOptions = [
  { label: 'None' },
  { label: 'Doc Type', value: 'document_type' },
  { label: 'Lineage', value: 'lineage_id' },
  { label: 'Status', value: 'classification_status' },
];

const initialState: DevToolsState = {
  docSearchQuery: '',
  selectedDefaultViewType: viewTypeOptions[0],
  viewTypeOptions,
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
  selectedGroupBy: groupByOptions[0],
  groupByOptions,
  selectedSortBy: sortByOptions[0],
  sortByOptions,
  filters: {
    singularLineage: false,
    multipleLineage: false,
    missingLineage: false,
  },
  pager: {
    totalCount: 0,
    currentPage: 0,
    perPage: 50,
    totalPages: 0,
  },
};

export const devtoolsSlice = createSlice({
  name: 'devtools',
  initialState,
  reducers: {
    updatePager: (state, action: PayloadAction<PagedList>) => {
      state.pager.currentPage = action.payload.currentPage;
      state.pager.perPage = action.payload.perPage;
      state.pager.totalPages = Math.ceil(state.pager.totalCount / state.pager.perPage);
    },

    selectDefaultViewType: (state, action: PayloadAction<any>) => {
      state.selectedDefaultViewType = action.payload;
    },
    setDocSearchQuery: (state, action: PayloadAction<string>) => {
      state.docSearchQuery = action.payload;
    },
    selectSortBy: (state, action: PayloadAction<any>) => {
      state.selectedSortBy = action.payload;
    },
    selectGroupBy: (state, action: PayloadAction<any>) => {
      state.selectedGroupBy = action.payload;
      state.displayItems = groupItems(state.selectedGroupBy.value, state.domainItems);
    },
    setViewItem: (state, action: PayloadAction<DevToolsDoc>) => {
      const currentView = state.selectedDefaultViewType.value;
      state.viewItems = [{ item: action.payload, currentView }];
    },
    clearViewItem: (state) => {
      state.viewItems = [];
    },
    setSplitItem: (state, action: PayloadAction<DevToolsDoc>) => {
      const currentView = state.selectedDefaultViewType.value;
      const viewItem = { item: action.payload, currentView };
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
      state.compareDocs.tagComparison = action.payload.tag_comparison;
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
      const groupByKey = state.selectedGroupBy.value;
      state.displayItems = groupItems(groupByKey, filtered);
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(devtoolsApi.endpoints.getDocuments.matchFulfilled, (state, { payload }) => {
      state.domainItems = payload.items;
      state.pager.totalCount = payload.total_count;
      const groupByKey = state.selectedGroupBy.value;
      state.displayItems = groupItems(groupByKey, state.domainItems);
    });

    builder.addMatcher(devtoolsApi.endpoints.searchSites.matchFulfilled, (state, { payload }) => {
      state.siteOptions = payload.items;
      if (state.siteOptions.length === 1) {
        state.selectedSite = state.siteOptions[0];
      }
    });
  },
});

function groupItems(groupByKey: string | undefined, items: DevToolsDoc[]): DevToolsGroup[] {
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
