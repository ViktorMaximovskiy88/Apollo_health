import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { LineageGroup, LineageDoc } from './types';
import { lineageApi } from './lineageApi';
import _ from 'lodash';

interface InitialState {
  searchTerm: string;
  leftSideDoc: undefined | LineageDoc;
  rightSideDoc: undefined | LineageDoc;
  displayItems: LineageGroup[];
  domainItems: LineageDoc[];
}

export const lineageSlice = createSlice({
  name: 'lineage',
  initialState: {
    searchTerm: '',
    leftSideDoc: undefined,
    rightSideDoc: undefined,
    domainItems: [],
    displayItems: [],
  } as InitialState,
  reducers: {
    setLeftSide: (state, action: PayloadAction<LineageDoc>) => {
      state.leftSideDoc = action.payload;
    },
    setRightSide: (state, action: PayloadAction<LineageDoc>) => {
      state.rightSideDoc = action.payload;
    },
    onSearch: (state, action: PayloadAction<string>) => {
      state.searchTerm = action.payload;
      const regex = new RegExp(state.searchTerm, 'i');
      const filtered = state.domainItems.filter((doc: any) => doc.name.match(regex));
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
        const parentIndex = items.findIndex((item) => item._id == child.previous_doc_id);
        const [parent] = items.splice(parentIndex, 1);
        ordered.unshift(parent);
      }

      return {
        lineageId,
        items: ordered,
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

export const { actions } = lineageSlice;
export default lineageSlice.reducer;
