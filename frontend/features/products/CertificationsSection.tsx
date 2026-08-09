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

import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { tFormat } from "@/lib/i18n";
import {
  useCreateCertificationMutation,
  useDeleteCertificationMutation,
  useListCertificationTypesQuery,
  useListCertificationsQuery,
  useListIssuingAuthoritiesQuery,
} from "@/store/api/productsApi";

type Props = { productId: string };

export function CertificationsSection({ productId }: Props) {
  const t = useT();
  const { locale } = usePreferences();
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
      setFormError(t("certs.required"));
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
      setFormError(getErrorMessage(err, t("certs.addError")));
    }
  }

  async function onDelete(id: string, label: string) {
    if (
      !window.confirm(tFormat("certs.deleteConfirm", locale, { name: label }))
    ) {
      return;
    }
    try {
      await deleteCert({ productId, certificationId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("certs.deleteError")));
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
        {getErrorMessage(error, t("certs.loadError"))}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">{t("certs.empty")}</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t("certs.type")}</TableCell>
              <TableCell>{t("certs.authority")}</TableCell>
              <TableCell>{t("certs.issued")}</TableCell>
              <TableCell>{t("certs.expires")}</TableCell>
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
                    aria-label={t("certs.deleteAria")}
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
          {t("certs.add")}
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
            <InputLabel id="cert-type">{t("certs.type")}</InputLabel>
            <Select
              labelId="cert-type"
              label={t("certs.type")}
              value={typeId}
              onChange={(e) => setTypeId(e.target.value)}
            >
              {(types ?? []).map((item) => (
                <MenuItem key={item.id} value={item.id}>
                  {item.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth size="small" required>
            <InputLabel id="cert-auth">{t("certs.authority")}</InputLabel>
            <Select
              labelId="cert-auth"
              label={t("certs.authority")}
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
            label={t("certs.issueDate")}
            type="date"
            size="small"
            required
            slotProps={{ inputLabel: { shrink: true } }}
            value={issueDate}
            onChange={(e) => setIssueDate(e.target.value)}
          />
          <TextField
            label={t("certs.expirationDate")}
            type="date"
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
            value={expirationDate}
            onChange={(e) => setExpirationDate(e.target.value)}
          />
          <Box sx={{ gridColumn: { md: "1 / -1" } }}>
            <Button variant="outlined" component="label" size="small">
              {pdf ? pdf.name : t("certs.choosePdf")}
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
              {t("common.add")}
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
