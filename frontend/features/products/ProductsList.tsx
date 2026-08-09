"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import QrCode2Icon from "@mui/icons-material/QrCode2";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
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
  Tooltip,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";

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
} from "@/store/api/productsApi";
import type { Product } from "@/types/products";

import { QrCodeDialog } from "./QrCodeDialog";

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
  const { data, isLoading, isError, error, refetch } = useListProductsQuery();
  const [deleteProduct, { isLoading: deleting }] = useDeleteProductMutation();
  const [qrTarget, setQrTarget] = useState<{
    id: string;
    name: string;
  } | null>(null);

  async function onDelete(id: string, name: string) {
    if (!window.confirm(tFormat("products.deleteConfirm", locale, { name }))) {
      return;
    }
    try {
      await deleteProduct(id).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("products.deleteError")));
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
          {data.map((product) => (
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
                        setQrTarget({ id: product.id, name: product.name })
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

      <QrCodeDialog
        open={qrTarget !== null}
        productId={qrTarget?.id ?? null}
        productName={qrTarget?.name}
        onClose={() => setQrTarget(null)}
      />
    </>
  );
}
