"use client";

import { Box, Button, Typography } from "@mui/material";
import { useState } from "react";

import { useT } from "@/hooks/useT";

type Props = {
  accept: string;
  label: string;
  fileName?: string | null;
  onFile: (file: File | null) => void;
  disabled?: boolean;
};

/** Click-to-pick + drag-and-drop file target. */
export function FileDropZone({
  accept,
  label,
  fileName,
  onFile,
  disabled,
}: Props) {
  const t = useT();
  const [dragging, setDragging] = useState(false);

  function takeFile(fileList: FileList | null) {
    const file = fileList?.[0] ?? null;
    onFile(file);
  }

  return (
    <Box
      onDragEnter={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setDragging(false);
      }}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (disabled) return;
        takeFile(e.dataTransfer.files);
      }}
      sx={{
        border: 1,
        borderStyle: "dashed",
        borderColor: dragging ? "primary.main" : "divider",
        bgcolor: dragging ? "action.hover" : "transparent",
        borderRadius: 1,
        p: 2,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: 1.5,
      }}
    >
      <Button
        variant="outlined"
        component="label"
        size="small"
        disabled={disabled}
      >
        {fileName || label}
        <input
          type="file"
          accept={accept}
          hidden
          disabled={disabled}
          onChange={(e) => {
            takeFile(e.target.files);
            e.target.value = "";
          }}
        />
      </Button>
      <Typography variant="body2" color="text.secondary">
        {t("common.dropHint")}
      </Typography>
    </Box>
  );
}
