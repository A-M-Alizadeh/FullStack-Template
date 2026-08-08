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
  useCreateImageMutation,
  useDeleteImageMutation,
  useListImagesQuery,
} from "@/store/api/productsApi";
import { IMAGE_TYPES, type ImageType } from "@/types/products";

type Props = { productId: string };

export function ImagesSection({ productId }: Props) {
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
      setFormError("Choose an image file");
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
      setFormError(getErrorMessage(err, "Could not upload image"));
    }
  }

  async function onDelete(id: string) {
    if (!window.confirm("Remove this image?")) return;
    try {
      await deleteImage({ productId, imageId: id }).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, "Could not delete image"));
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
        {getErrorMessage(error, "Could not load images")}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {!data?.length ? (
        <Typography color="text.secondary">No images yet.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Sort</TableCell>
              <TableCell>Path</TableCell>
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
                    aria-label="Delete image"
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
          Upload image
        </Typography>
        {formError ? (
          <Alert severity="error" sx={{ width: "100%" }}>
            {formError}
          </Alert>
        ) : null}
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel id="image-type">Type</InputLabel>
          <Select
            labelId="image-type"
            label="Type"
            value={imageType}
            onChange={(e) => setImageType(e.target.value as ImageType)}
          >
            {IMAGE_TYPES.map((t) => (
              <MenuItem key={t} value={t}>
                {t}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="Sort"
          size="small"
          type="number"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          sx={{ width: 96 }}
        />
        <Button variant="outlined" component="label" size="small">
          {file ? file.name : "Choose image"}
          <input
            type="file"
            accept="image/*"
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
