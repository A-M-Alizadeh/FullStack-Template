"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  IconButton,
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
import { Controller, useForm } from "react-hook-form";

import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { tFormat } from "@/lib/i18n";
import {
  useCreateMaterialMutation,
  useDeleteMaterialMutation,
  useListMaterialsQuery,
} from "@/store/api/productsApi";

import { materialSchema, type MaterialFormValues } from "./productSchema";

type Props = { productId: string };

export function MaterialsSection({ productId }: Props) {
  const t = useT();
  const { locale } = usePreferences();
  const { data, isLoading, isError, error, refetch } =
    useListMaterialsQuery(productId);
  const [createMaterial, { isLoading: creating }] = useCreateMaterialMutation();
  const [deleteMaterial] = useDeleteMaterialMutation();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MaterialFormValues>({
    resolver: zodResolver(materialSchema),
    defaultValues: {
      name: "",
      percentage: "",
      country_of_origin: "",
      recyclable: false,
    },
  });

  async function onAdd(values: MaterialFormValues) {
    setFormError(null);
    try {
      await createMaterial({ productId, body: values }).unwrap();
      reset();
    } catch (err) {
      setFormError(getErrorMessage(err, t("materials.addError")));
    }
  }

  async function onDelete(materialId: string, name: string) {
    if (!window.confirm(tFormat("materials.deleteConfirm", locale, { name }))) {
      return;
    }
    try {
      await deleteMaterial({ productId, materialId }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("materials.deleteError")));
    }
  }

  if (isLoading) {
    return <Skeleton variant="rounded" height={160} />;
  }

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
        {getErrorMessage(error, t("materials.loadError"))}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">{t("materials.empty")}</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t("materials.name")}</TableCell>
              <TableCell>{t("materials.percent")}</TableCell>
              <TableCell>{t("materials.country")}</TableCell>
              <TableCell>{t("materials.recyclable")}</TableCell>
              <TableCell width={56} />
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.name}</TableCell>
                <TableCell>{String(row.percentage)}</TableCell>
                <TableCell>{row.country_of_origin}</TableCell>
                <TableCell>
                  {row.recyclable ? t("common.yes") : t("common.no")}
                </TableCell>
                <TableCell>
                  <IconButton
                    aria-label={`Delete ${row.name}`}
                    size="small"
                    onClick={() => onDelete(row.id, row.name)}
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
          {t("materials.add")}
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {formError}
          </Alert>
        ) : null}
        <Box
          component="form"
          onSubmit={handleSubmit(onAdd)}
          noValidate
          sx={{
            display: "grid",
            gap: 2,
            gridTemplateColumns: { sm: "2fr 1fr 1fr auto" },
            alignItems: "start",
          }}
        >
          <TextField
            label={t("materials.name")}
            size="small"
            error={Boolean(errors.name)}
            helperText={errors.name?.message}
            {...register("name")}
          />
          <TextField
            label={t("materials.percent")}
            size="small"
            error={Boolean(errors.percentage)}
            helperText={errors.percentage?.message}
            {...register("percentage")}
          />
          <TextField
            label={t("materials.country")}
            size="small"
            placeholder="IT"
            slotProps={{ htmlInput: { maxLength: 2 } }}
            error={Boolean(errors.country_of_origin)}
            helperText={errors.country_of_origin?.message}
            {...register("country_of_origin")}
          />
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Controller
              name="recyclable"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={field.value}
                      onChange={(e) => field.onChange(e.target.checked)}
                    />
                  }
                  label={t("materials.recyclable")}
                />
              )}
            />
            <Button type="submit" variant="contained" disabled={creating}>
              {t("common.add")}
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
