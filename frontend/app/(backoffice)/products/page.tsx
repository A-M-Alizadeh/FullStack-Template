"use client";

import { Box, Button, Typography } from "@mui/material";
import Link from "next/link";

import { ProductsList } from "@/features/products/ProductsList";
import { useT } from "@/hooks/useT";

export default function ProductsPage() {
  const t = useT();

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 2,
          mb: 3,
          flexWrap: "wrap",
        }}
      >
        <Typography variant="h5" component="h1">
          {t("products.title")}
        </Typography>
        <Button component={Link} href="/products/new" variant="contained">
          {t("products.new")}
        </Button>
      </Box>
      <ProductsList />
    </Box>
  );
}
