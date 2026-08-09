"use client";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import {
  Box,
  Button,
  Chip,
  IconButton,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
} from "@mui/material";
import { useState } from "react";

import { QueryError } from "@/components/feedback/QueryError";
import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { formatDateTime } from "@/lib/formatDate";
import { tFormat } from "@/lib/i18n";
import { selectUser } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";
import {
  useDeleteUserMutation,
  useListUsersQuery,
} from "@/store/api/usersApi";
import type { User } from "@/types/auth";

import { UserFormDialog } from "./UserFormDialog";

export function UsersList() {
  const t = useT();
  const { locale } = usePreferences();
  const me = useAppSelector(selectUser);
  const { data, isLoading, isError, error, refetch } = useListUsersQuery();
  const [deleteUser, { isLoading: deleting }] = useDeleteUserMutation();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);

  async function onDelete(user: User) {
    if (me?.id === user.id) {
      window.alert(t("users.deleteSelf"));
      return;
    }
    if (
      !window.confirm(
        tFormat("users.deleteConfirm", locale, { email: user.email }),
      )
    ) {
      return;
    }
    try {
      await deleteUser(user.id).unwrap();
    } catch (err) {
      window.alert(getErrorMessage(err, t("users.deleteError")));
    }
  }

  if (isLoading) {
    return <Skeleton variant="rounded" height={200} />;
  }

  if (isError || !data) {
    return (
      <QueryError
        error={error}
        fallbackKey="users.loadError"
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2 }}>
        <Button
          variant="contained"
          onClick={() => {
            setEditing(null);
            setDialogOpen(true);
          }}
        >
          {t("users.create")}
        </Button>
      </Box>

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t("users.col.email")}</TableCell>
            <TableCell>{t("users.col.role")}</TableCell>
            <TableCell>{t("users.col.created")}</TableCell>
            <TableCell align="right">{t("common.actions")}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((user) => (
            <TableRow key={user.id} hover>
              <TableCell>{user.email}</TableCell>
              <TableCell>
                <Chip size="small" label={user.role} variant="outlined" />
              </TableCell>
              <TableCell>{formatDateTime(user.created_at)}</TableCell>
              <TableCell align="right">
                <Tooltip title={t("common.edit")}>
                  <IconButton
                    size="small"
                    aria-label={t("common.edit")}
                    onClick={() => {
                      setEditing(user);
                      setDialogOpen(true);
                    }}
                  >
                    <EditOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title={t("common.delete")}>
                  <span>
                    <IconButton
                      size="small"
                      aria-label={t("common.delete")}
                      disabled={deleting || me?.id === user.id}
                      onClick={() => onDelete(user)}
                    >
                      <DeleteOutlinedIcon fontSize="small" />
                    </IconButton>
                  </span>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <UserFormDialog
        open={dialogOpen}
        user={editing}
        onClose={() => {
          setDialogOpen(false);
          setEditing(null);
        }}
      />
    </Box>
  );
}
