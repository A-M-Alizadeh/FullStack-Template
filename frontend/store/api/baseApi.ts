import { createApi } from "@reduxjs/toolkit/query/react";

import { baseQueryWithReauth } from "./baseQuery";

/**
 * Shared RTK Query API. Domain endpoints inject into this (auth, products, …).
 */
export const baseApi = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    "Me",
    "Products",
    "Product",
    "ProductMaterials",
    "ProductSustainability",
    "ProductCertifications",
    "ProductDocuments",
    "ProductImages",
    "ProductQr",
    "Lookups",
    "Dashboard",
    "Analytics",
  ],
  endpoints: () => ({}),
});
