"use client";

import {
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { EmptyState } from "@/components/feedback/EmptyState";
import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import { formatDateTime } from "@/lib/formatDate";
import { useListAuditLogsQuery } from "@/store/api/auditApi";

export function AuditList() {
  const t = useT();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const { data, isLoading, isError, error, refetch } = useListAuditLogsQuery({
    skip: page * rowsPerPage,
    limit: rowsPerPage,
  });

  if (isLoading) {
    return <Skeleton variant="rounded" height={280} />;
  }

  if (isError || !data) {
    return (
      <QueryError
        error={error}
        fallbackKey="audit.loadError"
        onRetry={() => refetch()}
      />
    );
  }

  if (!data.items.length) {
    return <EmptyState message={t("audit.empty")} />;
  }

  return (
    <>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t("audit.col.when")}</TableCell>
            <TableCell>{t("audit.col.actor")}</TableCell>
            <TableCell>{t("audit.col.action")}</TableCell>
            <TableCell>{t("audit.col.entity")}</TableCell>
            <TableCell>{t("audit.col.details")}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.items.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell>{formatDateTime(row.created_at)}</TableCell>
              <TableCell>{row.actor_email ?? "—"}</TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                  {row.action}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                  {row.entity_type}
                  {row.entity_id ? `:${row.entity_id.slice(0, 8)}` : ""}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography
                  variant="caption"
                  component="pre"
                  sx={{ m: 0, whiteSpace: "pre-wrap", maxWidth: 280 }}
                >
                  {row.details ? JSON.stringify(row.details) : "—"}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={data.total}
        page={page}
        onPageChange={(_e, next) => setPage(next)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        rowsPerPageOptions={[25, 50, 100]}
      />
    </>
  );
}
