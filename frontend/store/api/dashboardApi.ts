import type { DashboardSummary } from "@/types/dashboard";

import { baseApi } from "./baseApi";

export const dashboardApi = baseApi.injectEndpoints({
  overrideExisting: process.env.NODE_ENV === "development",
  endpoints: (build) => ({
    getDashboard: build.query<DashboardSummary, void>({
      query: () => "/dashboard",
      providesTags: ["Dashboard"],
    }),
  }),
});

export const { useGetDashboardQuery } = dashboardApi;
