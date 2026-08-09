import { configureStore } from "@reduxjs/toolkit";

import { baseApi } from "./api/baseApi";
import "./api/authApi";
import "./api/usersApi";
import "./api/productsApi";
import "./api/dashboardApi";
import "./api/analyticsApi";
import "./api/passportApi";
import authReducer from "./auth/authSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [baseApi.reducerPath]: baseApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
