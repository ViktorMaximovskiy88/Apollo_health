import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { LineageGroup, LineageDoc } from './types';
import { lineageApi } from './lineageApi';
import _ from 'lodash';

interface InitialState {
  leftSideDoc: undefined | LineageDoc;
  rightSideDoc: undefined | LineageDoc;
  list: {
    all: LineageGroup[];
    filtered: LineageGroup[];
  };
}

export const lineageSlice = createSlice({
  name: 'lineage',
  initialState: {
    leftSideDoc: undefined,
    rightSideDoc: undefined,
    list: {
      all: [],
      filtered: [],
    },
  } as InitialState,
  reducers: {
    setLeftSide: (state, action: PayloadAction<LineageDoc>) => {
      console.log(state);
      state.leftSideDoc = action.payload;
    },
    setRightSide: (state, action: PayloadAction<LineageDoc>) => {
      state.rightSideDoc = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(lineageApi.endpoints.getSiteLineage.matchFulfilled, (state, { payload }) => {
      state.list.all = _(payload)
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
      state.list.filtered = state.list.all;
    });
  },
});

export const lineageListSelector = createSelector(
  (state: RootState) => state.lineage.list,
  (lineageState) => lineageState
);

export const lineageSelector = createSelector(
  (state: RootState) => state.lineage,
  (lineageState) => lineageState
);

export const { actions } = lineageSlice;
export default lineageSlice.reducer;
export const useLineage = () => {};
