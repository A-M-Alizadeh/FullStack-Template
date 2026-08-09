"use client";

import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Link as MuiLink,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useEffect, useState } from "react";

import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { triggerBlobDownload } from "@/lib/downloadBlob";
import { formatDateTime } from "@/lib/formatDate";
import {
  useGetProductQrQuery,
  useListPassportVersionsQuery,
  usePublishProductMutation,
} from "@/store/api/productsApi";
import type { ProductStatus } from "@/types/products";

type Props = {
  productId: string;
  status: ProductStatus;
};

export function PublishPanel({ productId, status }: Props) {
  const t = useT();
  const isPublished = status === "published";
  const [publish, { isLoading: publishing }] = usePublishProductMutation();
  const [publishError, setPublishError] = useState<string | null>(null);
  const [publicUrlFromPublish, setPublicUrlFromPublish] = useState<
    string | null
  >(null);

  const {
    data: qr,
    isLoading: qrLoading,
    isError: qrError,
    error: qrErr,
    refetch: refetchQr,
  } = useGetProductQrQuery(productId, { skip: !isPublished });

  const { data: versions } = useListPassportVersionsQuery(productId, {
    skip: !isPublished,
  });

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

  async function onPublish() {
    const confirmKey = isPublished ? "publish.confirmRepublish" : "publish.confirm";
    if (!window.confirm(t(confirmKey))) {
      return;
    }
    setPublishError(null);
    try {
      const result = await publish(productId).unwrap();
      setPublicUrlFromPublish(result.passport.public_url);
    } catch (err) {
      setPublishError(getErrorMessage(err, t("publish.error")));
    }
  }

  function onDownloadQr() {
    if (!qr) return;
    triggerBlobDownload(qr.blob, qr.filename);
  }

  const passportPath = qr?.publicUuid ? `/passport/${qr.publicUuid}` : null;
  const [origin, setOrigin] = useState("");
  useEffect(() => {
    setOrigin(window.location.origin);
  }, []);
  const publicUrl =
    publicUrlFromPublish ??
    (passportPath && origin ? `${origin}${passportPath}` : passportPath);

  return (
    <Box
      sx={{
        mb: 3,
        p: 2,
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Typography variant="subtitle1">{t("publish.title")}</Typography>

      {!isPublished ? (
        <>
          <Typography variant="body2" color="text.secondary">
            {t("publish.draftHint")}
          </Typography>
          {publishError ? <Alert severity="error">{publishError}</Alert> : null}
          <Box>
            <Button
              variant="contained"
              onClick={onPublish}
              disabled={publishing}
            >
              {publishing ? (
                <CircularProgress size={22} color="inherit" />
              ) : (
                t("publish.cta")
              )}
            </Button>
          </Box>
        </>
      ) : (
        <>
          <Typography variant="body2" color="text.secondary">
            {t("publish.live")}
          </Typography>

          {publicUrl ? (
            <Typography variant="body2">
              Passport:{" "}
              <MuiLink
                component={Link}
                href={passportPath ?? publicUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                {publicUrl}
              </MuiLink>
            </Typography>
          ) : null}

          {qrLoading ? <Skeleton variant="rounded" width={180} height={180} /> : null}

          {qrError ? (
            <QueryError
              error={qrErr}
              fallbackKey="publish.qrLoadError"
              onRetry={() => refetchQr()}
            />
          ) : null}

          {previewUrl ? (
            <Box
              component="img"
              src={previewUrl}
              alt="Product passport QR code"
              sx={{
                width: 180,
                height: 180,
                border: 1,
                borderColor: "divider",
                bgcolor: "common.white",
              }}
            />
          ) : null}

          {publishError ? <Alert severity="error">{publishError}</Alert> : null}

          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            <Button
              variant="contained"
              onClick={onDownloadQr}
              disabled={!qr}
            >
              {t("publish.downloadQr")}
            </Button>
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
              variant="outlined"
              onClick={onPublish}
              disabled={publishing}
            >
              {publishing ? (
                <CircularProgress size={22} color="inherit" />
              ) : (
                t("publish.republish")
              )}
            </Button>
          </Box>

          {versions && versions.length > 0 ? (
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                {t("publish.versions")}
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("publish.col.version")}</TableCell>
                    <TableCell>{t("publish.col.status")}</TableCell>
                    <TableCell>{t("publish.col.created")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {versions.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>v{row.version}</TableCell>
                      <TableCell sx={{ textTransform: "capitalize" }}>
                        {row.status}
                      </TableCell>
                      <TableCell>{formatDateTime(row.created_at)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          ) : null}
        </>
      )}
    </Box>
  );
}
