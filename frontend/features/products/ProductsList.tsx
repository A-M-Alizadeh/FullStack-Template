"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import {
  Box,
  Chip,
  CircularProgress,
  IconButton,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@mui/material";
import { useRouter } from "next/navigation";

import { EmptyState } from "@/components/feedback/EmptyState";
import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import {
  useDeleteProductMutation,
  useListProductsQuery,
} from "@/store/api/productsApi";

function statusColor(status: string): "default" | "success" {
  return status === "published" ? "success" : "default";
}

export function ProductsList() {
  const t = useT();
  const router = useRouter();
  const { data, isLoading, isError, error, refetch } = useListProductsQuery();
  const [deleteProduct, { isLoading: deleting }] = useDeleteProductMutation();

  async function onDelete(id: string, name: string) {
    if (!window.confirm(`Delete “${name}”? This cannot be undone.`)) {
      return;
    }
    try {
      await deleteProduct(id).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, "Could not delete product"));
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} variant="rounded" height={48} />
        ))}
      </Box>
    );
  }

  if (isError) {
    return (
      <QueryError
        error={error}
        fallbackKey="products.loadError"
        onRetry={() => refetch()}
      />
    );
  }

  if (!data?.length) {
    return (
      <EmptyState
        message={t("products.empty")}
        actionHref="/products/new"
        actionLabel={t("products.create")}
      />
    );
  }

  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>SKU</TableCell>
          <TableCell>Category</TableCell>
          <TableCell>Status</TableCell>
          <TableCell align="right" width={96} />
        </TableRow>
      </TableHead>
      <TableBody>
        {data.map((product) => (
          <TableRow
            key={product.id}
            hover
            sx={{ cursor: "pointer" }}
            onClick={() => router.push(`/products/${product.id}`)}
          >
            <TableCell>{product.name}</TableCell>
            <TableCell>{product.sku}</TableCell>
            <TableCell sx={{ textTransform: "capitalize" }}>
              {product.category}
            </TableCell>
            <TableCell>
              <Chip
                size="small"
                label={product.status}
                color={statusColor(product.status)}
                variant="outlined"
              />
            </TableCell>
            <TableCell align="right" onClick={(e) => e.stopPropagation()}>
              <IconButton
                aria-label={`Delete ${product.name}`}
                size="small"
                disabled={deleting}
                onClick={() => onDelete(product.id, product.name)}
              >
                {deleting ? (
                  <CircularProgress size={18} />
                ) : (
                  <DeleteOutlinedIcon fontSize="small" />
                )}
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
