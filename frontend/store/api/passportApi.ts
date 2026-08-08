import type { PublicPassport } from "@/types/passport";

import { baseApi } from "./baseApi";

export type PublicPassportArg = {
  uuid: string;
  /** Forwarded once for QR scan tracking. */
  src?: "qr";
};

export const passportApi = baseApi.injectEndpoints({
  overrideExisting: process.env.NODE_ENV === "development",
  endpoints: (build) => ({
    getPublicPassport: build.query<PublicPassport, PublicPassportArg>({
      query: ({ uuid, src }) => ({
        url: `/passport/${uuid}`,
        params: src === "qr" ? { src: "qr" } : undefined,
      }),
      // Avoid focus/remount refetch re-hitting the API (and re-counting scans).
      keepUnusedDataFor: 60,
    }),
  }),
});

export const { useGetPublicPassportQuery } = passportApi;
