"use client";

import { Box, Typography } from "@mui/material";

import { RoleGate } from "@/components/auth/RoleGate";
import { AuditList } from "@/features/audit/AuditList";
import { useT } from "@/hooks/useT";

export default function AuditPage() {
  const t = useT();

  return (
    <RoleGate roles={["admin"]}>
      <Box>
        <Typography variant="h5" component="h1" gutterBottom>
          {t("audit.title")}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {t("audit.subtitle")}
        </Typography>
        <AuditList />
      </Box>
    </RoleGate>
  );
}
