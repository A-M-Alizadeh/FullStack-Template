"use client";

import {
  Alert,
  Box,
  Button,
  Chip,
  Skeleton,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import {
  useGetProductQuery,
  useUpdateProductMutation,
} from "@/store/api/productsApi";

import { CertificationsSection } from "./CertificationsSection";
import { DocumentsSection } from "./DocumentsSection";
import { ImagesSection } from "./ImagesSection";
import { MaterialsSection } from "./MaterialsSection";
import { PreviewSection } from "./PreviewSection";
import { ProductForm } from "./ProductForm";
import type { ProductFormValues } from "./productSchema";
import { PublishPanel } from "./PublishPanel";
import { SustainabilitySection } from "./SustainabilitySection";

type Props = { productId: string };

export function ProductEditor({ productId }: Props) {
  const t = useT();
  const router = useRouter();
  const { data, isLoading, isError, error } = useGetProductQuery(productId);
  const [updateProduct] = useUpdateProductMutation();
  const [tab, setTab] = useState(0);

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Skeleton width={240} height={40} />
        <Skeleton variant="rounded" height={320} />
      </Box>
    );
  }

  if (isError || !data) {
    return (
      <Alert severity="error">
        {getErrorMessage(error, t("common.notFound"))}
      </Alert>
    );
  }

  async function onSave(values: ProductFormValues) {
    try {
      await updateProduct({ id: productId, body: values }).unwrap();
    } catch (err) {
      throw new Error(getErrorMessage(err, t("products.saveError")));
    }
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 2,
          mb: 2,
          flexWrap: "wrap",
        }}
      >
        <Box>
          <Typography variant="h5" component="h1">
            {data.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.sku}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Chip
            size="small"
            label={data.status}
            color={data.status === "published" ? "success" : "default"}
            variant="outlined"
          />
          <Button component={Link} href="/products" size="small">
            {t("products.editor.back")}
          </Button>
        </Box>
      </Box>

      <PublishPanel productId={productId} status={data.status} />

      <Tabs
        value={tab}
        onChange={(_e, value: number) => setTab(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 3, borderBottom: 1, borderColor: "divider" }}
      >
        <Tab label={t("products.tab.details")} />
        <Tab label={t("products.tab.materials")} />
        <Tab label={t("products.tab.sustainability")} />
        <Tab label={t("products.tab.certifications")} />
        <Tab label={t("products.tab.documents")} />
        <Tab label={t("products.tab.images")} />
        <Tab label={t("products.tab.preview")} />
      </Tabs>

      {tab === 0 ? (
        <ProductForm
          key={data.updated_at}
          defaultValues={{
            name: data.name,
            sku: data.sku,
            serial_number: data.serial_number,
            category: data.category,
            description: data.description,
            production_date: data.production_date,
            country_of_origin: data.country_of_origin,
          }}
          submitLabel={t("products.editor.save")}
          onSubmit={onSave}
          onCancel={() => router.push("/products")}
        />
      ) : null}

      {tab === 1 ? <MaterialsSection productId={productId} /> : null}
      {tab === 2 ? <SustainabilitySection productId={productId} /> : null}
      {tab === 3 ? <CertificationsSection productId={productId} /> : null}
      {tab === 4 ? <DocumentsSection productId={productId} /> : null}
      {tab === 5 ? <ImagesSection productId={productId} /> : null}
      {tab === 6 ? <PreviewSection publicUuid={data.public_uuid} /> : null}
    </Box>
  );
}
