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
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { getErrorMessage } from "@/lib/apiError";
import {
  useCreateCertificationMutation,
  useDeleteCertificationMutation,
  useListCertificationTypesQuery,
  useListCertificationsQuery,
  useListIssuingAuthoritiesQuery,
} from "@/store/api/productsApi";

type Props = { productId: string };

export function CertificationsSection({ productId }: Props) {
  const { data, isLoading, isError, error, refetch } =
    useListCertificationsQuery(productId);
  const { data: types } = useListCertificationTypesQuery();
  const { data: authorities } = useListIssuingAuthoritiesQuery();
  const [createCert, { isLoading: creating }] = useCreateCertificationMutation();
  const [deleteCert] = useDeleteCertificationMutation();

  const [typeId, setTypeId] = useState("");
  const [authorityId, setAuthorityId] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [expirationDate, setExpirationDate] = useState("");
  const [pdf, setPdf] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  async function onAdd(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!typeId || !authorityId || !issueDate || !pdf) {
      setFormError("Type, authority, issue date, and PDF are required");
      return;
    }
    const form = new FormData();
    form.append("certification_type_id", typeId);
    form.append("issuing_authority_id", authorityId);
    form.append("issue_date", issueDate);
    if (expirationDate) form.append("expiration_date", expirationDate);
    form.append("pdf", pdf);
    try {
      await createCert({ productId, form }).unwrap();
      setTypeId("");
      setAuthorityId("");
      setIssueDate("");
      setExpirationDate("");
      setPdf(null);
    } catch (err) {
      setFormError(getErrorMessage(err, "Could not add certification"));
    }
  }

  async function onDelete(id: string, label: string) {
    if (!window.confirm(`Remove certification “${label}”?`)) return;
    try {
      await deleteCert({ productId, certificationId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, "Could not delete certification"));
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
        {getErrorMessage(error, "Could not load certifications")}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">No certifications yet.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Authority</TableCell>
              <TableCell>Issued</TableCell>
              <TableCell>Expires</TableCell>
              <TableCell width={56} />
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.certification_type.name}</TableCell>
                <TableCell>{row.issuing_authority.name}</TableCell>
                <TableCell>{row.issue_date}</TableCell>
                <TableCell>{row.expiration_date ?? "—"}</TableCell>
                <TableCell>
                  <IconButton
                    aria-label="Delete certification"
                    size="small"
                    onClick={() =>
                      onDelete(row.id, row.certification_type.name)
                    }
                  >
                    <DeleteOutlinedIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Add certification
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {formError}
          </Alert>
        ) : null}
        <Box
          component="form"
          onSubmit={onAdd}
          sx={{
            display: "grid",
            gap: 2,
            gridTemplateColumns: { md: "1fr 1fr" },
            maxWidth: 720,
          }}
        >
          <FormControl fullWidth size="small" required>
            <InputLabel id="cert-type">Type</InputLabel>
            <Select
              labelId="cert-type"
              label="Type"
              value={typeId}
              onChange={(e) => setTypeId(e.target.value)}
            >
              {(types ?? []).map((t) => (
                <MenuItem key={t.id} value={t.id}>
                  {t.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth size="small" required>
            <InputLabel id="cert-auth">Authority</InputLabel>
            <Select
              labelId="cert-auth"
              label="Authority"
              value={authorityId}
              onChange={(e) => setAuthorityId(e.target.value)}
            >
              {(authorities ?? []).map((a) => (
                <MenuItem key={a.id} value={a.id}>
                  {a.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Issue date"
            type="date"
            size="small"
            required
            slotProps={{ inputLabel: { shrink: true } }}
            value={issueDate}
            onChange={(e) => setIssueDate(e.target.value)}
          />
          <TextField
            label="Expiration date"
            type="date"
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
            value={expirationDate}
            onChange={(e) => setExpirationDate(e.target.value)}
          />
          <Box sx={{ gridColumn: { md: "1 / -1" } }}>
            <Button variant="outlined" component="label" size="small">
              {pdf ? pdf.name : "Choose PDF"}
              <input
                type="file"
                accept="application/pdf"
                hidden
                onChange={(e) => setPdf(e.target.files?.[0] ?? null)}
              />
            </Button>
          </Box>
          <Box>
            <Button type="submit" variant="contained" disabled={creating}>
              Add
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
