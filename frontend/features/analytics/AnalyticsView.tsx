"use client";

import {
  Alert,
  Box,
  Button,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Link from "next/link";

import { getErrorMessage } from "@/lib/apiError";
import { formatDateTime } from "@/lib/formatDate";
import { useGetAnalyticsQuery } from "@/store/api/analyticsApi";

export function AnalyticsView() {
  const { data, isLoading, isError, error, refetch } = useGetAnalyticsQuery();

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Skeleton variant="rounded" height={96} />
        <Skeleton variant="rounded" height={200} />
        <Skeleton variant="rounded" height={280} />
      </Box>
    );
  }

  if (isError || !data) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            Retry
          </Button>
        }
      >
        {getErrorMessage(error, "Could not load analytics")}
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
        }}
      >
        <StatTile label="Scans today" value={data.scans_today} />
        <StatTile label="Scans this week" value={data.scans_this_week} />
      </Box>

      <Box>
        <Typography variant="h6" component="h2" gutterBottom>
          Most viewed products
        </Typography>
        {!data.most_viewed_products.length ? (
          <Typography color="text.secondary">No QR scans yet.</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell align="right">Scans</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.most_viewed_products.map((row) => (
                <TableRow key={row.product_id} hover>
                  <TableCell>
                    <MuiProductLink id={row.product_id} label={row.name} />
                  </TableCell>
                  <TableCell>{row.sku}</TableCell>
                  <TableCell align="right">{row.scan_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Box>

      <Box>
        <Typography variant="h6" component="h2" gutterBottom>
          Latest scans
        </Typography>
        {!data.latest_scans.length ? (
          <Typography color="text.secondary">No recent scans.</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>When</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Browser</TableCell>
                <TableCell>OS</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.latest_scans.map((row, index) => (
                <TableRow
                  key={`${row.product_id}-${row.scanned_at}-${index}`}
                  hover
                >
                  <TableCell>{formatDateTime(row.scanned_at)}</TableCell>
                  <TableCell>
                    <MuiProductLink
                      id={row.product_id}
                      label={`${row.product_name} (${row.sku})`}
                    />
                  </TableCell>
                  <TableCell>{row.country || "—"}</TableCell>
                  <TableCell>{row.browser || "—"}</TableCell>
                  <TableCell>{row.operating_system || "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Box>
    </Box>
  );
}

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <Box
      sx={{
        p: 2.5,
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        bgcolor: "background.paper",
      }}
    >
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Typography variant="h4" component="p">
        {value}
      </Typography>
    </Box>
  );
}

function MuiProductLink({ id, label }: { id: string; label: string }) {
  return (
    <Box
      component={Link}
      href={`/products/${id}`}
      sx={{ color: "primary.main", textDecoration: "none", "&:hover": { textDecoration: "underline" } }}
    >
      {label}
    </Box>
  );
}
