"use client";

import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useEffect, useState } from "react";

import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import { triggerBlobDownload } from "@/lib/downloadBlob";
import { useGetProductQrQuery } from "@/store/api/productsApi";

type Props = {
  open: boolean;
  productId: string | null;
  productName?: string;
  onClose: () => void;
};

export function QrCodeDialog({
  open,
  productId,
  productName,
  onClose,
}: Props) {
  const t = useT();
  const {
    data: qr,
    isLoading,
    isError,
    error,
    refetch,
  } = useGetProductQrQuery(productId ?? "", { skip: !open || !productId });

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!qr?.blob) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(qr.blob);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [qr]);

  const passportPath = qr?.publicUuid ? `/passport/${qr.publicUuid}` : null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{t("products.qr.title")}</DialogTitle>
      <DialogContent
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
          pt: 1,
        }}
      >
        {productName ? (
          <Typography variant="body2" color="text.secondary" align="center">
            {productName}
          </Typography>
        ) : null}

        {isLoading ? <CircularProgress size={36} /> : null}

        {isError ? (
          <QueryError
            error={error}
            fallbackKey="publish.qrLoadError"
            onRetry={() => refetch()}
          />
        ) : null}

        {previewUrl ? (
          <Box
            component="img"
            src={previewUrl}
            alt={t("products.qr.alt")}
            sx={{
              width: 220,
              height: 220,
              border: 1,
              borderColor: "divider",
              bgcolor: "common.white",
              borderRadius: 1,
            }}
          />
        ) : null}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2, flexWrap: "wrap", gap: 1 }}>
        <Button onClick={onClose}>{t("common.cancel")}</Button>
        {passportPath ? (
          <Button
            component={Link}
            href={passportPath}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("publish.openPassport")}
          </Button>
        ) : null}
        <Button
          variant="contained"
          disabled={!qr}
          onClick={() => {
            if (!qr) return;
            triggerBlobDownload(qr.blob, qr.filename);
          }}
        >
          {t("publish.downloadQr")}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
