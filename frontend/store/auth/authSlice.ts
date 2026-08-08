import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { User } from "@/types/auth";

export interface AuthState {
  accessToken: string | null;
  user: User | null;
}

const initialState: AuthState = {
  accessToken: null,
  user: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setAccessToken(state, action: PayloadAction<string>) {
      state.accessToken = action.payload;
    },
    setUser(state, action: PayloadAction<User | null>) {
      state.user = action.payload;
    },
    setSession(
      state,
      action: PayloadAction<{ accessToken: string; user: User | null }>,
    ) {
      state.accessToken = action.payload.accessToken;
      state.user = action.payload.user;
    },
    clearAuth(state) {
      state.accessToken = null;
      state.user = null;
    },
  },
});

export const { setAccessToken, setUser, setSession, clearAuth } =
  authSlice.actions;

export const selectAccessToken = (state: { auth: AuthState }) =>
  state.auth.accessToken;

export const selectUser = (state: { auth: AuthState }) => state.auth.user;

export const selectIsAuthenticated = (state: { auth: AuthState }) =>
  Boolean(state.auth.accessToken);

export default authSlice.reducer;
