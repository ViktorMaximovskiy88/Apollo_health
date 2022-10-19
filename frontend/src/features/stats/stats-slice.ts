import { createSelector, createSlice } from '@reduxjs/toolkit';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../app/store';
import { CollectionStats } from './types';
import { statsApi } from './statsApi';
import { makeActionDispatch } from '../../common/helpers';
import _ from 'lodash';

export interface StatsState {
  collectionStats: CollectionStats[];
}

export const statsSlice = createSlice({
  name: 'stats',
  initialState: {
    collectionStats: [],
  } as StatsState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addMatcher(
      statsApi.endpoints.getCollectionStats.matchFulfilled,
      (state, { payload }) => {
        state.collectionStats = payload;
      }
    );
  },
});

const statsSelector: any = createSelector(
  (state: RootState) => state.stats,
  (statsState) => statsState
);

export function useStatsSlice() {
  const state = useSelector(statsSelector);
  const dispatch = useDispatch();
  return {
    state: state as StatsState,
    actions: makeActionDispatch(statsSlice.actions, dispatch),
  };
}

export default statsSlice.reducer;
