"use client";

import { Alert, Button } from "@mui/material";

import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import type { MessageKey } from "@/lib/i18n";

type Props = {
  error: unknown;
  fallbackKey: MessageKey;
  onRetry?: () => void;
};

/** Shared load-error alert with optional retry. */
export function QueryError({ error, fallbackKey, onRetry }: Props) {
  const t = useT();

  return (
    <Alert
      severity="error"
      action={
        onRetry ? (
          <Button color="inherit" size="small" onClick={onRetry}>
            {t("common.retry")}
          </Button>
        ) : undefined
      }
    >
      {getErrorMessage(error, t(fallbackKey))}
    </Alert>
  );
}
