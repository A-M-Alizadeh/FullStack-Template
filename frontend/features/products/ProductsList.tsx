"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import QrCode2Icon from "@mui/icons-material/QrCode2";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/feedback/EmptyState";
import { QueryError } from "@/components/feedback/QueryError";
import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useAuthedObjectUrl } from "@/hooks/useAuthedObjectUrl";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { tFormat } from "@/lib/i18n";
import {
  useDeleteProductMutation,
  useListProductsQuery,
  useRestoreProductMutation,
} from "@/store/api/productsApi";
import type { Product, ProductStatus } from "@/types/products";

import { QrCodeDialog } from "./QrCodeDialog";

const PAGE_SIZE_OPTIONS = [10, 20, 50];

function statusColor(status: string): "default" | "success" {
  return status === "published" ? "success" : "default";
}

function CoverThumb({ product }: { product: Product }) {
  const src = useAuthedObjectUrl(product.cover_image?.url);
  const [broken, setBroken] = useState(false);

  if (!src || broken) {
    return (
      <Box
        sx={{
          width: 40,
          height: 40,
          bgcolor: "action.hover",
          borderRadius: 1,
        }}
      />
    );
  }
  return (
    <Box
      component="img"
      src={src}
      alt=""
      onError={() => setBroken(true)}
      sx={{ width: 40, height: 40, objectFit: "cover", borderRadius: 1 }}
    />
  );
}

export function ProductsList() {
  const t = useT();
  const { locale } = usePreferences();
  const router = useRouter();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [searchInput, setSearchInput] = useState("");
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<ProductStatus | "">("");

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setQ(searchInput.trim());
      setPage(0);
    }, 300);
    return () => window.clearTimeout(handle);
  }, [searchInput]);

  const { data, isLoading, isError, error, refetch, isFetching } =
    useListProductsQuery({
      skip: page * rowsPerPage,
      limit: rowsPerPage,
      q: q || undefined,
      status: status || undefined,
    });
  const [deleteProduct, { isLoading: deleting }] = useDeleteProductMutation();
  const [restoreProduct, { isLoading: restoring }] = useRestoreProductMutation();
  const [qrTarget, setQrTarget] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [undoToast, setUndoToast] = useState<{
    id: string;
    name: string;
  } | null>(null);

  async function onDelete(id: string, name: string) {
    if (!window.confirm(tFormat("products.deleteConfirm", locale, { name }))) {
      return;
    }
    try {
      await deleteProduct(id).unwrap();
      setUndoToast({ id, name });
    } catch (err) {
      window.alert(getErrorMessage(err, t("products.deleteError")));
    }
  }

  async function onUndo() {
    if (!undoToast) return;
    const { id } = undoToast;
    setUndoToast(null);
    try {
      await restoreProduct(id).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("products.restoreError")));
    }
  }

  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 2,
          mb: 2,
          alignItems: "center",
        }}
      >
        <TextField
          size="small"
          label={t("products.search")}
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          sx={{ minWidth: 220, flex: "1 1 200px" }}
        />
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel id="product-status-filter">
            {t("products.col.status")}
          </InputLabel>
          <Select
            labelId="product-status-filter"
            label={t("products.col.status")}
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as ProductStatus | "");
              setPage(0);
            }}
          >
            <MenuItem value="">{t("products.filter.allStatuses")}</MenuItem>
            <MenuItem value="draft">{t("products.filter.draft")}</MenuItem>
            <MenuItem value="published">
              {t("products.filter.published")}
            </MenuItem>
          </Select>
        </FormControl>
        {isFetching && !isLoading ? <CircularProgress size={20} /> : null}
      </Box>

      {isLoading ? (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="rounded" height={48} />
          ))}
        </Box>
      ) : null}

      {isError ? (
        <QueryError
          error={error}
          fallbackKey="products.loadError"
          onRetry={() => refetch()}
        />
      ) : null}

      {!isLoading && !isError && items.length === 0 ? (
        <EmptyState
          message={q || status ? t("products.emptyFiltered") : t("products.empty")}
          actionHref={q || status ? undefined : "/products/new"}
          actionLabel={q || status ? undefined : t("products.create")}
        />
      ) : null}

      {!isLoading && !isError && items.length > 0 ? (
        <>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width={56}>{t("products.col.image")}</TableCell>
                <TableCell>{t("products.col.name")}</TableCell>
                <TableCell>{t("products.col.sku")}</TableCell>
                <TableCell>{t("products.col.status")}</TableCell>
                <TableCell>{t("products.col.qr")}</TableCell>
                <TableCell align="right">{t("products.col.views")}</TableCell>
                <TableCell align="right">{t("common.actions")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>
                    <CoverThumb product={product} />
                  </TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.sku}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={product.status}
                      color={statusColor(product.status)}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {product.status === "published" ? (
                      <Tooltip title={t("products.action.viewQr")}>
                        <IconButton
                          size="small"
                          aria-label={t("products.action.viewQr")}
                          onClick={() =>
                            setQrTarget({
                              id: product.id,
                              name: product.name,
                            })
                          }
                        >
                          <QrCode2Icon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell align="right">{product.scan_count}</TableCell>
                  <TableCell align="right">
                    <Tooltip title={t("common.view")}>
                      <IconButton
                        size="small"
                        aria-label={t("common.view")}
                        onClick={() => router.push(`/products/${product.id}`)}
                      >
                        <VisibilityOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t("common.edit")}>
                      <IconButton
                        size="small"
                        aria-label={t("common.edit")}
                        onClick={() => router.push(`/products/${product.id}`)}
                      >
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {product.public_uuid ? (
                      <Tooltip title={t("products.action.openPassport")}>
                        <IconButton
                          size="small"
                          aria-label={t("products.action.openPassport")}
                          href={`/passport/${product.public_uuid}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          component="a"
                        >
                          <OpenInNewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ) : null}
                    <Tooltip title={t("common.delete")}>
                      <IconButton
                        aria-label={t("common.delete")}
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
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={(_e, next) => setPage(next)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={PAGE_SIZE_OPTIONS}
            labelRowsPerPage={t("products.rowsPerPage")}
          />
        </>
      ) : null}

      <QrCodeDialog
        open={qrTarget !== null}
        productId={qrTarget?.id ?? null}
        productName={qrTarget?.name}
        onClose={() => setQrTarget(null)}
      />

      <Snackbar
        open={undoToast !== null}
        autoHideDuration={8000}
        onClose={(_e, reason) => {
          if (reason === "clickaway") return;
          setUndoToast(null);
        }}
        message={
          undoToast
            ? tFormat("products.deletedToast", locale, { name: undoToast.name })
            : ""
        }
        action={
          <Button
            color="secondary"
            size="small"
            disabled={restoring}
            onClick={onUndo}
          >
            {t("products.undo")}
          </Button>
        }
      />
    </Box>
  );
}
