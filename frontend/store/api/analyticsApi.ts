import type { AnalyticsSummary } from "@/types/analytics";

import { baseApi } from "./baseApi";

export const analyticsApi = baseApi.injectEndpoints({
  overrideExisting: process.env.NODE_ENV === "development",
  endpoints: (build) => ({
    getAnalytics: build.query<AnalyticsSummary, void>({
      query: () => "/analytics",
      providesTags: ["Analytics"],
    }),
  }),
});

export const { useGetAnalyticsQuery } = analyticsApi;
