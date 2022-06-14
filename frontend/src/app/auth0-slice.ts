import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Auth0State {
  token: string | undefined;
}

const initialState = { token: undefined } as Auth0State;

const auth0Slice = createSlice({
  name: 'auth0',
  initialState,
  reducers: {
    setToken(state, action: PayloadAction<string>) {
      state.token = action.payload;
    },
  },
});

export const { setToken } = auth0Slice.actions;
export default auth0Slice.reducer;
