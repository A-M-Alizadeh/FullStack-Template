"use client";

import { Box, Button, Typography } from "@mui/material";
import Link from "next/link";

import { ProductsList } from "@/features/products/ProductsList";

export default function ProductsPage() {
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
          Products
        </Typography>
        <Button component={Link} href="/products/new" variant="contained">
          New product
        </Button>
      </Box>
      <ProductsList />
    </Box>
  );
}
