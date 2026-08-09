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

import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import {
  useCreateImageMutation,
  useDeleteImageMutation,
  useListImagesQuery,
} from "@/store/api/productsApi";
import { IMAGE_TYPES, type ImageType } from "@/types/products";

type Props = { productId: string };

export function ImagesSection({ productId }: Props) {
  const t = useT();
  const { data, isLoading, isError, error, refetch } =
    useListImagesQuery(productId);
  const [createImage, { isLoading: creating }] = useCreateImageMutation();
  const [deleteImage] = useDeleteImageMutation();

  const [imageType, setImageType] = useState<ImageType>("gallery");
  const [sortOrder, setSortOrder] = useState("0");
  const [file, setFile] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  async function onAdd(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!file) {
      setFormError(t("images.chooseRequired"));
      return;
    }
    const form = new FormData();
    form.append("image_type", imageType);
    form.append("sort_order", sortOrder || "0");
    form.append("file", file);
    try {
      await createImage({ productId, form }).unwrap();
      setFile(null);
    } catch (err) {
      setFormError(getErrorMessage(err, t("images.uploadError")));
    }
  }

  async function onDelete(id: string) {
    if (!window.confirm(t("images.deleteConfirm"))) return;
    try {
      await deleteImage({ productId, imageId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("images.deleteError")));
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
        {getErrorMessage(error, t("images.loadError"))}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">{t("images.empty")}</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t("images.type")}</TableCell>
              <TableCell>{t("images.sort")}</TableCell>
              <TableCell>{t("images.path")}</TableCell>
              <TableCell width={56} />
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id}>
                <TableCell sx={{ textTransform: "capitalize" }}>
                  {row.image_type}
                </TableCell>
                <TableCell>{row.sort_order}</TableCell>
                <TableCell
                  sx={{
                    maxWidth: 280,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {row.file_path}
                </TableCell>
                <TableCell>
                  <IconButton
                    aria-label={t("images.deleteAria")}
                    size="small"
                    onClick={() => onDelete(row.id)}
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
          {t("images.upload")}
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ width: "100%" }}>
            {formError}
          </Alert>
        ) : null}
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel id="image-type">{t("images.type")}</InputLabel>
          <Select
            labelId="image-type"
            label={t("images.type")}
            value={imageType}
            onChange={(e) => setImageType(e.target.value as ImageType)}
          >
            {IMAGE_TYPES.map((item) => (
              <MenuItem key={item} value={item}>
                {item}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label={t("images.sort")}
          size="small"
          type="number"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          sx={{ width: 96 }}
        />
        <Button variant="outlined" component="label" size="small">
          {file ? file.name : t("images.choose")}
          <input
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </Button>
        <Button type="submit" variant="contained" disabled={creating}>
          {t("common.upload")}
        </Button>
      </Box>
    </Box>
  );
}
