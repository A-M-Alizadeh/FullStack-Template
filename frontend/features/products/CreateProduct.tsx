"use client";

import { Box, Typography } from "@mui/material";
import { useRouter } from "next/navigation";

import { getErrorMessage } from "@/lib/apiError";
import { useCreateProductMutation } from "@/store/api/productsApi";

import { ProductForm } from "./ProductForm";
import type { ProductFormValues } from "./productSchema";

const defaults: ProductFormValues = {
  name: "",
  sku: "",
  serial_number: "",
  category: "electronics",
  description: "",
  production_date: "",
  country_of_origin: "",
};

export function CreateProduct() {
  const router = useRouter();
  const [createProduct] = useCreateProductMutation();

  async function onSubmit(values: ProductFormValues) {
    try {
      const product = await createProduct(values).unwrap();
      router.replace(`/products/${product.id}`);
    } catch (err) {
      throw new Error(getErrorMessage(err, "Could not create product"));
    }
  }

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        New product
      </Typography>
      <ProductForm
        defaultValues={defaults}
        submitLabel="Create"
        onSubmit={onSubmit}
        onCancel={() => router.push("/products")}
      />
    </Box>
  );
}
