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

import { getErrorMessage } from "@/lib/apiError";
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
      setFormError("Choose a PDF file");
      return;
    }
    const form = new FormData();
    form.append("doc_type", docType);
    form.append("file", file);
    try {
      await createDoc({ productId, form }).unwrap();
      setFile(null);
    } catch (err) {
      setFormError(getErrorMessage(err, "Could not upload document"));
    }
  }

  async function onDelete(id: string, name: string) {
    if (!window.confirm(`Remove document “${name}”?`)) return;
    try {
      await deleteDoc({ productId, documentId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, "Could not delete document"));
    }
  }

  if (isLoading) return <Skeleton variant="rounded" height={160} />;

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
        {getErrorMessage(error, "Could not load documents")}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">No documents yet.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>File</TableCell>
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
                    aria-label={`Delete ${row.original_filename}`}
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
          Upload document
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ width: "100%" }}>
            {formError}
          </Alert>
        ) : null}
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="doc-type">Type</InputLabel>
          <Select
            labelId="doc-type"
            label="Type"
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
          >
            {DOCUMENT_TYPES.map((t) => (
              <MenuItem key={t} value={t}>
                {labelDocType(t)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button variant="outlined" component="label" size="small">
          {file ? file.name : "Choose PDF"}
          <input
            type="file"
            accept="application/pdf"
            hidden
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </Button>
        <Button type="submit" variant="contained" disabled={creating}>
          Upload
        </Button>
      </Box>
    </Box>
  );
}
