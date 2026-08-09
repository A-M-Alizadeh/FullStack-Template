"use client";

import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import QrCode2Icon from "@mui/icons-material/QrCode2";
import {
  IconButton,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { EmptyState } from "@/components/feedback/EmptyState";
import { QueryError } from "@/components/feedback/QueryError";
import { QrCodeDialog } from "@/features/products/QrCodeDialog";
import { useT } from "@/hooks/useT";
import { useListProductsQuery } from "@/store/api/productsApi";

export function PassportsList() {
  const t = useT();
  const { data, isLoading, isError, error, refetch } = useListProductsQuery({
    skip: 0,
    limit: 100,
    status: "published",
  });
  const [qrTarget, setQrTarget] = useState<{
    id: string;
    name: string;
  } | null>(null);

  const published = (data?.items ?? []).filter((p) => p.public_uuid);

  if (isLoading) {
    return <Skeleton variant="rounded" height={200} />;
  }

  if (isError) {
    return (
      <QueryError
        error={error}
        fallbackKey="passports.loadError"
        onRetry={() => refetch()}
      />
    );
  }

  if (!published.length) {
    return (
      <EmptyState
        message={t("passports.empty")}
        actionHref="/products"
        actionLabel={t("nav.products")}
      />
    );
  }

  return (
    <>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t("passports.col.product")}</TableCell>
            <TableCell>{t("products.col.sku")}</TableCell>
            <TableCell>{t("passports.col.uuid")}</TableCell>
            <TableCell align="right">{t("passports.col.views")}</TableCell>
            <TableCell align="right">{t("common.actions")}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {published.map((product) => (
            <TableRow key={product.id} hover>
              <TableCell>{product.name}</TableCell>
              <TableCell>{product.sku}</TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                  {product.public_uuid}
                </Typography>
              </TableCell>
              <TableCell align="right">{product.scan_count}</TableCell>
              <TableCell align="right">
                <Tooltip title={t("products.action.viewQr")}>
                  <IconButton
                    size="small"
                    onClick={() =>
                      setQrTarget({ id: product.id, name: product.name })
                    }
                    aria-label={t("products.action.viewQr")}
                  >
                    <QrCode2Icon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title={t("products.action.openPassport")}>
                  <IconButton
                    size="small"
                    component="a"
                    href={`/passport/${product.public_uuid}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={t("products.action.openPassport")}
                  >
                    <OpenInNewIcon fontSize="small" />
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
