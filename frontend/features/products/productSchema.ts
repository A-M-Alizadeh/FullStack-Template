import { z } from "zod";

import { PRODUCT_CATEGORIES } from "@/types/products";

/** Shared create/edit validation — testable without React. */
export const productSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255),
  sku: z.string().trim().min(1, "SKU is required").max(100),
  serial_number: z.string().trim().min(1, "Serial number is required").max(100),
  category: z.enum(PRODUCT_CATEGORIES),
  description: z.string(),
  production_date: z.string().min(1, "Production date is required"),
  country_of_origin: z
    .string()
    .trim()
    .toUpperCase()
    .regex(/^[A-Z]{2}$/, "Use a 2-letter country code"),
});

export type ProductFormValues = z.infer<typeof productSchema>;

export const materialSchema = z.object({
  name: z.string().trim().min(1, "Name is required"),
  percentage: z
    .string()
    .trim()
    .refine((v) => {
      const n = Number(v);
      return !Number.isNaN(n) && n >= 0 && n <= 100;
    }, "0–100"),
  country_of_origin: z
    .string()
    .trim()
    .toUpperCase()
    .regex(/^[A-Z]{2}$/, "Use a 2-letter country code"),
  recyclable: z.boolean(),
});

export type MaterialFormValues = z.infer<typeof materialSchema>;

export const sustainabilitySchema = z.object({
  carbon_footprint: z.string().trim().min(1, "Required"),
  water_consumption: z.string().trim().min(1, "Required"),
  recycled_material_percent: z
    .string()
    .trim()
    .refine((v) => {
      const n = Number(v);
      return !Number.isNaN(n) && n >= 0 && n <= 100;
    }, "0–100"),
  repairability_score: z
    .string()
    .trim()
    .refine((v) => {
      const n = Number(v);
      return !Number.isNaN(n) && n >= 0 && n <= 100;
    }, "0–100"),
  recyclable: z.boolean(),
});

export type SustainabilityFormValues = z.infer<typeof sustainabilitySchema>;
