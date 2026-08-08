"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  IconButton,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { getErrorMessage } from "@/lib/apiError";
import {
  useDeleteProductMutation,
  useListProductsQuery,
} from "@/store/api/productsApi";

function statusColor(status: string): "default" | "success" {
  return status === "published" ? "success" : "default";
}

export function ProductsList() {
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
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            Retry
          </Button>
        }
      >
        {getErrorMessage(error, "Could not load products")}
      </Alert>
    );
  }

  if (!data?.length) {
    return (
      <Box sx={{ py: 4 }}>
        <Typography color="text.secondary" gutterBottom>
          No products yet.
        </Typography>
        <Button component={Link} href="/products/new" variant="contained">
          Create product
        </Button>
      </Box>
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
