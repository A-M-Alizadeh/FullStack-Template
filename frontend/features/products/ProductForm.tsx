"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { Controller, useForm } from "react-hook-form";

import { useT } from "@/hooks/useT";
import { PRODUCT_CATEGORIES } from "@/types/products";

import { productSchema, type ProductFormValues } from "./productSchema";

type Props = {
  defaultValues: ProductFormValues;
  submitLabel: string;
  onSubmit: (values: ProductFormValues) => Promise<void>;
  onCancel?: () => void;
};

function labelCategory(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function ProductForm({
  defaultValues,
  submitLabel,
  onSubmit,
  onCancel,
}: Props) {
  const t = useT();
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<ProductFormValues>({
    resolver: zodResolver(productSchema),
    defaultValues,
  });

  async function submit(values: ProductFormValues) {
    try {
      await onSubmit(values);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : t("products.saveError");
      setError("root", { message });
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(submit)}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2, maxWidth: 560 }}
    >
      {errors.root?.message ? (
        <Alert severity="error">{errors.root.message}</Alert>
      ) : null}

      <TextField
        label={t("products.form.name")}
        fullWidth
        error={Boolean(errors.name)}
        helperText={errors.name?.message}
        {...register("name")}
      />

      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { sm: "1fr 1fr" } }}>
        <TextField
          label={t("products.form.sku")}
          fullWidth
          error={Boolean(errors.sku)}
          helperText={errors.sku?.message}
          {...register("sku")}
        />
        <TextField
          label={t("products.form.serial")}
          fullWidth
          error={Boolean(errors.serial_number)}
          helperText={errors.serial_number?.message}
          {...register("serial_number")}
        />
      </Box>

      <Controller
        name="category"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth error={Boolean(errors.category)}>
            <InputLabel id="product-category-label">
              {t("products.form.category")}
            </InputLabel>
            <Select
              labelId="product-category-label"
              label={t("products.form.category")}
              {...field}
            >
              {PRODUCT_CATEGORIES.map((cat) => (
                <MenuItem key={cat} value={cat}>
                  {labelCategory(cat)}
                </MenuItem>
              ))}
            </Select>
            {errors.category?.message ? (
              <FormHelperText>{errors.category.message}</FormHelperText>
            ) : null}
          </FormControl>
        )}
      />

      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { sm: "1fr 1fr" } }}>
        <TextField
          label={t("products.form.productionDate")}
          type="date"
          fullWidth
          slotProps={{ inputLabel: { shrink: true } }}
          error={Boolean(errors.production_date)}
          helperText={errors.production_date?.message}
          {...register("production_date")}
        />
        <TextField
          label={t("products.form.country")}
          placeholder="IT"
          fullWidth
          slotProps={{ htmlInput: { maxLength: 2 } }}
          error={Boolean(errors.country_of_origin)}
          helperText={
            errors.country_of_origin?.message ?? t("products.form.countryHint")
          }
          {...register("country_of_origin")}
        />
      </Box>

      <TextField
        label={t("products.form.description")}
        fullWidth
        multiline
        minRows={3}
        error={Boolean(errors.description)}
        helperText={errors.description?.message}
        {...register("description")}
      />

      <Box sx={{ display: "flex", gap: 1.5, pt: 1 }}>
        <Button type="submit" disabled={isSubmitting} variant="contained">
          {isSubmitting ? (
            <CircularProgress size={22} color="inherit" />
          ) : (
            submitLabel
          )}
        </Button>
        {onCancel ? (
          <Button type="button" onClick={onCancel} disabled={isSubmitting}>
            {t("common.cancel")}
          </Button>
        ) : null}
      </Box>
    </Box>
  );
}
