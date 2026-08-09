"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import {
  Alert,
  Box,
  Button,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { FileDropZone } from "@/components/feedback/FileDropZone";
import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { tFormat } from "@/lib/i18n";
import {
  useCreateDocumentMutation,
  useDeleteDocumentMutation,
  useListDocumentsQuery,
} from "@/store/api/productsApi";
import { DOCUMENT_TYPES, type DocumentType } from "@/types/products";

type Props = { productId: string };

function labelDocType(value: string) {
  return value.replaceAll("_", " ");
}

export function DocumentsSection({ productId }: Props) {
  const t = useT();
  const { locale } = usePreferences();
  const { data, isLoading, isError, error, refetch } =
    useListDocumentsQuery(productId);
  const [createDoc, { isLoading: creating }] = useCreateDocumentMutation();
  const [deleteDoc] = useDeleteDocumentMutation();

  const [docType, setDocType] = useState<DocumentType>("user_manual");
  const [file, setFile] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  async function onAdd(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!file) {
      setFormError(t("docs.chooseRequired"));
      return;
    }
    const form = new FormData();
    form.append("doc_type", docType);
    form.append("file", file);
    try {
      await createDoc({ productId, form }).unwrap();
      setFile(null);
    } catch (err) {
      setFormError(getErrorMessage(err, t("docs.uploadError")));
    }
  }

  async function onDelete(id: string, name: string) {
    if (!window.confirm(tFormat("docs.deleteConfirm", locale, { name }))) {
      return;
    }
    try {
      await deleteDoc({ productId, documentId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("docs.deleteError")));
    }
  }

  if (isLoading) return <Skeleton variant="rounded" height={160} />;

  if (isError) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            {t("common.retry")}
          </Button>
        }
      >
        {getErrorMessage(error, t("docs.loadError"))}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">{t("docs.empty")}</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t("docs.type")}</TableCell>
              <TableCell>{t("docs.file")}</TableCell>
              <TableCell width={56} />
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id}>
                <TableCell sx={{ textTransform: "capitalize" }}>
                  {labelDocType(row.doc_type)}
                </TableCell>
                <TableCell>{row.original_filename}</TableCell>
                <TableCell>
                  <IconButton
                    aria-label={`${t("common.delete")} ${row.original_filename}`}
                    size="small"
                    onClick={() => onDelete(row.id, row.original_filename)}
                  >
                    <DeleteOutlinedIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Box
        component="form"
        onSubmit={onAdd}
        sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}
      >
        <Typography variant="subtitle2" sx={{ width: "100%" }}>
          {t("docs.upload")}
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ width: "100%" }}>
            {formError}
          </Alert>
        ) : null}
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="doc-type">{t("docs.type")}</InputLabel>
          <Select
            labelId="doc-type"
            label={t("docs.type")}
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
          >
            {DOCUMENT_TYPES.map((item) => (
              <MenuItem key={item} value={item}>
                {labelDocType(item)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Box sx={{ width: "100%", maxWidth: 480 }}>
          <FileDropZone
            accept="application/pdf"
            label={t("docs.choosePdf")}
            fileName={file?.name}
            onFile={setFile}
            disabled={creating}
          />
        </Box>
        <Button type="submit" variant="contained" disabled={creating}>
          {t("common.upload")}
        </Button>
      </Box>
    </Box>
  );
}
