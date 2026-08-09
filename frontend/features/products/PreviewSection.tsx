"use client";

import { Alert, Box, Button } from "@mui/material";
import Link from "next/link";

import { useT } from "@/hooks/useT";

type Props = {
  publicUuid: string | null;
};

/** Live passport preview (iframe of the public page) when published. */
export function PreviewSection({ publicUuid }: Props) {
  const t = useT();

  if (!publicUuid) {
    return <Alert severity="info">{t("products.preview.publishFirst")}</Alert>;
  }

  return (
    <Box>
      <Button
        component={Link}
        href={`/passport/${publicUuid}`}
        target="_blank"
        rel="noopener noreferrer"
        sx={{ mb: 2 }}
      >
        {t("products.preview.open")}
      </Button>
      <Box
        component="iframe"
        title={t("products.tab.preview")}
        src={`/passport/${publicUuid}`}
        sx={{
          width: "100%",
          height: "70vh",
          border: 1,
          borderColor: "divider",
          borderRadius: 1,
          bgcolor: "background.paper",
        }}
      />
    </Box>
  );
}
