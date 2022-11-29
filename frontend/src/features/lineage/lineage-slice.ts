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

interface LineageState {
  searchTerm: string;
  leftSideDoc: undefined | LineageDoc;
  rightSideDoc: undefined | LineageDoc;
  displayItems: LineageGroup[];
  domainItems: LineageDoc[];
  filters: FilterSettings;
}

export const lineageSlice = createSlice({
  name: 'lineage',
  initialState: {
    searchTerm: '',
    leftSideDoc: undefined,
    rightSideDoc: undefined,
    domainItems: [],
    displayItems: [],
    filters: {
      singularLineage: false,
      multipleLineage: false,
      missingLineage: false,
    },
  } as LineageState,
  reducers: {
    setLeftSide: (state, action: PayloadAction<LineageDoc>) => {
      state.leftSideDoc = action.payload;
    },
    setRightSide: (state, action: PayloadAction<LineageDoc>) => {
      state.rightSideDoc = action.payload;
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
