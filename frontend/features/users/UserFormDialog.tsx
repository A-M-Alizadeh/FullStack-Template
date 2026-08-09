"use client";

import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import {
  useCreateUserMutation,
  useUpdateUserMutation,
} from "@/store/api/usersApi";
import type { User, UserRole } from "@/types/auth";

type Props = {
  open: boolean;
  user: User | null;
  onClose: () => void;
};

const ROLES: UserRole[] = ["admin", "editor"];

export function UserFormDialog({ open, user, onClose }: Props) {
  const t = useT();
  const isEdit = user !== null;
  const [createUser, { isLoading: creating }] = useCreateUserMutation();
  const [updateUser, { isLoading: updating }] = useUpdateUserMutation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("editor");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setEmail(user?.email ?? "");
    setPassword("");
    setRole(user?.role ?? "editor");
    setFormError(null);
  }, [open, user]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    if (!email.trim()) {
      setFormError(t("users.form.emailRequired"));
      return;
    }
    if (!isEdit && password.length < 8) {
      setFormError(t("users.form.passwordMin"));
      return;
    }
    if (isEdit && password && password.length < 8) {
      setFormError(t("users.form.passwordMin"));
      return;
    }

    try {
      if (isEdit && user) {
        const body: { email: string; role: UserRole; password?: string } = {
          email: email.trim(),
          role,
        };
        if (password) body.password = password;
        await updateUser({ id: user.id, body }).unwrap();
      } else {
        await createUser({
          email: email.trim(),
          password,
          role,
        }).unwrap();
      }
      onClose();
    } catch (err) {
      setFormError(
        getErrorMessage(
          err,
          isEdit ? t("users.updateError") : t("users.createError"),
        ),
      );
    }
  }

  const saving = creating || updating;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>
        {isEdit ? t("users.edit") : t("users.create")}
      </DialogTitle>
      <Box component="form" onSubmit={onSubmit} noValidate>
        <DialogContent
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          {formError ? <Alert severity="error">{formError}</Alert> : null}
          <TextField
            label={t("users.col.email")}
            type="email"
            required
            fullWidth
            autoComplete="off"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label={
              isEdit
                ? t("users.form.passwordOptional")
                : t("auth.password")
            }
            type="password"
            required={!isEdit}
            fullWidth
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            helperText={isEdit ? t("users.form.passwordHint") : undefined}
          />
          <FormControl fullWidth>
            <InputLabel id="user-role">{t("users.col.role")}</InputLabel>
            <Select
              labelId="user-role"
              label={t("users.col.role")}
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
            >
              {ROLES.map((r) => (
                <MenuItem key={r} value={r}>
                  {r}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={onClose} disabled={saving}>
            {t("common.cancel")}
          </Button>
          <Button type="submit" variant="contained" disabled={saving}>
            {isEdit ? t("common.save") : t("users.create")}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
