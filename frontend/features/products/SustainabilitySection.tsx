"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Skeleton,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";

import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import {
  useGetSustainabilityQuery,
  useUpsertSustainabilityMutation,
} from "@/store/api/productsApi";

import {
  sustainabilitySchema,
  type SustainabilityFormValues,
} from "./productSchema";

type Props = { productId: string };

const emptyValues: SustainabilityFormValues = {
  carbon_footprint: "",
  water_consumption: "",
  recycled_material_percent: "",
  repairability_score: "",
  recyclable: false,
};

export function SustainabilitySection({ productId }: Props) {
  const t = useT();
  const { data, isLoading, isError, error } =
    useGetSustainabilityQuery(productId);
  const [upsert, { isLoading: saving }] = useUpsertSustainabilityMutation();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const missing = isError && isNotFound(error);

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SustainabilityFormValues>({
    resolver: zodResolver(sustainabilitySchema),
    defaultValues: emptyValues,
  });

  useEffect(() => {
    if (data) {
      reset({
        carbon_footprint: data.carbon_footprint,
        water_consumption: data.water_consumption,
        recycled_material_percent: String(data.recycled_material_percent),
        repairability_score: String(data.repairability_score),
        recyclable: data.recyclable,
      });
    } else if (missing) {
      reset(emptyValues);
    }
  }, [data, missing, reset]);

  async function onSave(values: SustainabilityFormValues) {
    setSubmitError(null);
    setSaved(false);
    try {
      await upsert({ productId, body: values }).unwrap();
      setSaved(true);
    } catch (err) {
      setSubmitError(getErrorMessage(err, t("sustainability.saveError")));
    }
  }

  if (isLoading) {
    return <Skeleton variant="rounded" height={220} />;
  }

  if (isError && !missing) {
    return (
      <Alert severity="error">
        {getErrorMessage(error, t("sustainability.loadError"))}
      </Alert>
    );
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSave)}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2, maxWidth: 560 }}
    >
      {missing ? (
        <Typography color="text.secondary">
          {t("sustainability.empty")}
        </Typography>
      ) : null}

      {submitError ? <Alert severity="error">{submitError}</Alert> : null}
      {saved ? (
        <Alert severity="success">{t("sustainability.saved")}</Alert>
      ) : null}

      <TextField
        label={t("sustainability.carbon")}
        fullWidth
        error={Boolean(errors.carbon_footprint)}
        helperText={errors.carbon_footprint?.message}
        {...register("carbon_footprint")}
      />
      <TextField
        label={t("sustainability.water")}
        fullWidth
        error={Boolean(errors.water_consumption)}
        helperText={errors.water_consumption?.message}
        {...register("water_consumption")}
      />
      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { sm: "1fr 1fr" } }}>
        <TextField
          label={t("sustainability.recycled")}
          fullWidth
          error={Boolean(errors.recycled_material_percent)}
          helperText={errors.recycled_material_percent?.message}
          {...register("recycled_material_percent")}
        />
        <TextField
          label={t("sustainability.repair")}
          fullWidth
          error={Boolean(errors.repairability_score)}
          helperText={errors.repairability_score?.message}
          {...register("repairability_score")}
        />
      </Box>
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
            label={t("sustainability.recyclable")}
          />
        )}
      />

      <Box>
        <Button type="submit" variant="contained" disabled={saving}>
          {saving ? (
            <CircularProgress size={22} color="inherit" />
          ) : (
            t("common.save")
          )}
        </Button>
      </Box>
    </Box>
  );
}

function isNotFound(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    (error as { status: unknown }).status === 404
  );
}
