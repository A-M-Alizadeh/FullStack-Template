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

import { getErrorMessage } from "@/lib/apiError";
import {
  useCreateMaterialMutation,
  useDeleteMaterialMutation,
  useListMaterialsQuery,
} from "@/store/api/productsApi";

import { materialSchema, type MaterialFormValues } from "./productSchema";

type Props = { productId: string };

export function MaterialsSection({ productId }: Props) {
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
      setFormError(getErrorMessage(err, "Could not add material"));
    }
  }

  async function onDelete(materialId: string, name: string) {
    if (!window.confirm(`Remove material “${name}”?`)) return;
    try {
      await deleteMaterial({ productId, materialId }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, "Could not delete material"));
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
            Retry
          </Button>
        }
      >
        {getErrorMessage(error, "Could not load materials")}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">No materials yet.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>%</TableCell>
              <TableCell>Origin</TableCell>
              <TableCell>Recyclable</TableCell>
              <TableCell width={56} />
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.name}</TableCell>
                <TableCell>{String(row.percentage)}</TableCell>
                <TableCell>{row.country_of_origin}</TableCell>
                <TableCell>{row.recyclable ? "Yes" : "No"}</TableCell>
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
          Add material
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
            label="Name"
            size="small"
            error={Boolean(errors.name)}
            helperText={errors.name?.message}
            {...register("name")}
          />
          <TextField
            label="%"
            size="small"
            error={Boolean(errors.percentage)}
            helperText={errors.percentage?.message}
            {...register("percentage")}
          />
          <TextField
            label="Country"
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
                  label="Recyclable"
                />
              )}
            />
            <Button type="submit" variant="contained" disabled={creating}>
              Add
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
