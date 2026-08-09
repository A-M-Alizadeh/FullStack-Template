"use client";

import { Box, Typography } from "@mui/material";

import { AdminGate } from "@/components/auth/AdminGate";
import { UsersList } from "@/features/users/UsersList";
import { useT } from "@/hooks/useT";

export default function UsersPage() {
  const t = useT();

  return (
    <AdminGate>
      <Box>
        <Typography variant="h5" component="h1" gutterBottom>
          {t("users.title")}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {t("users.subtitle")}
        </Typography>
        <UsersList />
      </Box>
    </AdminGate>
  );
}
