import { filenameFromContentDisposition } from "@/lib/downloadBlob";
import type { ProductQrPayload, PublishResponse } from "@/types/passport";
import type {
  Certification,
  LookupItem,
  Material,
  MaterialWrite,
  Product,
  ProductDocument,
  ProductImage,
  ProductWrite,
  Sustainability,
  SustainabilityWrite,
} from "@/types/products";

import { baseApi } from "./baseApi";

export const productsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    listProducts: build.query<Product[], void>({
      query: () => "/products",
      providesTags: (result) =>
        result
          ? [
              ...result.map((p) => ({ type: "Product" as const, id: p.id })),
              { type: "Products", id: "LIST" },
            ]
          : [{ type: "Products", id: "LIST" }],
    }),
    getProduct: build.query<Product, string>({
      query: (id) => `/products/${id}`,
      providesTags: (_r, _e, id) => [{ type: "Product", id }],
    }),
    createProduct: build.mutation<Product, ProductWrite>({
      query: (body) => ({ url: "/products", method: "POST", body }),
      invalidatesTags: [{ type: "Products", id: "LIST" }],
    }),
    updateProduct: build.mutation<
      Product,
      { id: string; body: Partial<ProductWrite> }
    >({
      query: ({ id, body }) => ({
        url: `/products/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_r, _e, { id }) => [
        { type: "Product", id },
        { type: "Products", id: "LIST" },
      ],
    }),
    deleteProduct: build.mutation<void, string>({
      query: (id) => ({ url: `/products/${id}`, method: "DELETE" }),
      invalidatesTags: [{ type: "Products", id: "LIST" }],
    }),

    publishProduct: build.mutation<PublishResponse, string>({
      query: (id) => ({
        url: `/products/${id}/publish`,
        method: "POST",
      }),
      invalidatesTags: (_r, _e, id) => [
        { type: "Product", id },
        { type: "Products", id: "LIST" },
        { type: "ProductQr", id },
      ],
    }),

    getProductQr: build.query<ProductQrPayload, string>({
      query: (productId) => ({
        url: `/products/${productId}/passport/qr`,
        responseHandler: async (response: Response) => {
          const blob = await response.blob();
          const filename = filenameFromContentDisposition(
            response.headers.get("Content-Disposition"),
            "qr.png",
          );
          const publicUuid = filename.replace(/\.png$/i, "");
          return { blob, publicUuid, filename } satisfies ProductQrPayload;
        },
      }),
      providesTags: (_r, _e, productId) => [
        { type: "ProductQr", id: productId },
      ],
    }),

    listMaterials: build.query<Material[], string>({
      query: (productId) => `/products/${productId}/materials`,
      providesTags: (_r, _e, productId) => [
        { type: "ProductMaterials", id: productId },
      ],
    }),
    createMaterial: build.mutation<
      Material,
      { productId: string; body: MaterialWrite }
    >({
      query: ({ productId, body }) => ({
        url: `/products/${productId}/materials`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductMaterials", id: productId },
      ],
    }),
    deleteMaterial: build.mutation<
      void,
      { productId: string; materialId: string }
    >({
      query: ({ productId, materialId }) => ({
        url: `/products/${productId}/materials/${materialId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductMaterials", id: productId },
      ],
    }),

    getSustainability: build.query<Sustainability, string>({
      query: (productId) => `/products/${productId}/sustainability`,
      providesTags: (_r, _e, productId) => [
        { type: "ProductSustainability", id: productId },
      ],
    }),
    upsertSustainability: build.mutation<
      Sustainability,
      { productId: string; body: SustainabilityWrite }
    >({
      query: ({ productId, body }) => ({
        url: `/products/${productId}/sustainability`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductSustainability", id: productId },
      ],
    }),

    listCertificationTypes: build.query<LookupItem[], void>({
      query: () => "/products/certification-types",
      providesTags: [{ type: "Lookups", id: "cert-types" }],
    }),
    listIssuingAuthorities: build.query<LookupItem[], void>({
      query: () => "/products/issuing-authorities",
      providesTags: [{ type: "Lookups", id: "authorities" }],
    }),
    listCertifications: build.query<Certification[], string>({
      query: (productId) => `/products/${productId}/certifications`,
      providesTags: (_r, _e, productId) => [
        { type: "ProductCertifications", id: productId },
      ],
    }),
    createCertification: build.mutation<
      Certification,
      { productId: string; form: FormData }
    >({
      query: ({ productId, form }) => ({
        url: `/products/${productId}/certifications`,
        method: "POST",
        body: form,
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductCertifications", id: productId },
      ],
    }),
    deleteCertification: build.mutation<
      void,
      { productId: string; certificationId: string }
    >({
      query: ({ productId, certificationId }) => ({
        url: `/products/${productId}/certifications/${certificationId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductCertifications", id: productId },
      ],
    }),

    listDocuments: build.query<ProductDocument[], string>({
      query: (productId) => `/products/${productId}/documents`,
      providesTags: (_r, _e, productId) => [
        { type: "ProductDocuments", id: productId },
      ],
    }),
    createDocument: build.mutation<
      ProductDocument,
      { productId: string; form: FormData }
    >({
      query: ({ productId, form }) => ({
        url: `/products/${productId}/documents`,
        method: "POST",
        body: form,
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductDocuments", id: productId },
      ],
    }),
    deleteDocument: build.mutation<
      void,
      { productId: string; documentId: string }
    >({
      query: ({ productId, documentId }) => ({
        url: `/products/${productId}/documents/${documentId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductDocuments", id: productId },
      ],
    }),

    listImages: build.query<ProductImage[], string>({
      query: (productId) => `/products/${productId}/images`,
      providesTags: (_r, _e, productId) => [
        { type: "ProductImages", id: productId },
      ],
    }),
    createImage: build.mutation<
      ProductImage,
      { productId: string; form: FormData }
    >({
      query: ({ productId, form }) => ({
        url: `/products/${productId}/images`,
        method: "POST",
        body: form,
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductImages", id: productId },
        { type: "Product", id: productId },
        { type: "Products", id: "LIST" },
      ],
    }),
    deleteImage: build.mutation<
      void,
      { productId: string; imageId: string }
    >({
      query: ({ productId, imageId }) => ({
        url: `/products/${productId}/images/${imageId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_r, _e, { productId }) => [
        { type: "ProductImages", id: productId },
        { type: "Product", id: productId },
        { type: "Products", id: "LIST" },
      ],
    }),
  }),
  // Next.js HMR re-runs this module; allow re-inject into the same baseApi.
  overrideExisting: process.env.NODE_ENV === "development",
});

export const {
  useListProductsQuery,
  useGetProductQuery,
  useCreateProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
  usePublishProductMutation,
  useGetProductQrQuery,
  useLazyGetProductQrQuery,
  useListMaterialsQuery,
  useCreateMaterialMutation,
  useDeleteMaterialMutation,
  useGetSustainabilityQuery,
  useUpsertSustainabilityMutation,
  useListCertificationTypesQuery,
  useListIssuingAuthoritiesQuery,
  useListCertificationsQuery,
  useCreateCertificationMutation,
  useDeleteCertificationMutation,
  useListDocumentsQuery,
  useCreateDocumentMutation,
  useDeleteDocumentMutation,
  useListImagesQuery,
  useCreateImageMutation,
  useDeleteImageMutation,
} = productsApi;
