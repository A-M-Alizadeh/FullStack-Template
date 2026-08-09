import type { AuditLogListResponse } from "@/types/audit";

import { baseApi } from "./baseApi";

export const auditApi = baseApi.injectEndpoints({
  overrideExisting: process.env.NODE_ENV === "development",
  endpoints: (build) => ({
    listAuditLogs: build.query<
      AuditLogListResponse,
      { skip?: number; limit?: number } | void
    >({
      query: (params) => ({
        url: "/audit",
        params: {
          skip: params?.skip ?? 0,
          limit: params?.limit ?? 50,
        },
      }),
      providesTags: ["Audit"],
    }),
  }),
});

export const { useListAuditLogsQuery } = auditApi;
