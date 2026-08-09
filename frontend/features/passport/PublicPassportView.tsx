"use client";

import {
  Box,
  Chip,
  Container,
  Link as MuiLink,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useSearchParams } from "next/navigation";
import type { ReactNode } from "react";

import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import { resolveApiAssetUrl } from "@/lib/apiUrl";
import { getAppName } from "@/lib/env";
import { formatDateTime } from "@/lib/formatDate";
import { useGetPublicPassportQuery } from "@/store/api/passportApi";
import type { PublicPassport } from "@/types/passport";

type Props = { uuid: string };

export function PublicPassportView({ uuid }: Props) {
  const t = useT();
  const searchParams = useSearchParams();
  const src = searchParams.get("src") === "qr" ? ("qr" as const) : undefined;

  const { data, isLoading, isError, error } = useGetPublicPassportQuery(
    { uuid, src },
    {
      // Keep a single request per cache entry so ?src=qr is not re-counted.
      refetchOnFocus: false,
      refetchOnReconnect: false,
      refetchOnMountOrArgChange: false,
    },
  );

  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        py: { xs: 3, md: 5 },
        bgcolor: "background.default",
      }}
    >
      <Container maxWidth="md">
        {isLoading ? <PassportSkeleton /> : null}

        {isError || (!isLoading && !data) ? (
          <QueryError error={error} fallbackKey="passport.loadError" />
        ) : null}

        {data ? <PassportContent data={data} /> : null}
      </Container>
    </Box>
  );
}

function PassportContent({ data }: { data: PublicPassport }) {
  const { product } = data;
  const cover = data.images.find((img) => img.image_type === "cover");
  const gallery = data.images.filter((img) => img.id !== cover?.id);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <Box>
        <Typography variant="overline" color="text.secondary">
          {getAppName()}
        </Typography>
        <Typography variant="h4" component="h1" gutterBottom>
          {product.name}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 1 }}>
          <Chip size="small" label={data.verification_status} />
          <Chip size="small" label={`v${data.version}`} variant="outlined" />
          <Chip
            size="small"
            label={product.category}
            variant="outlined"
            sx={{ textTransform: "capitalize" }}
          />
        </Box>
        <Typography variant="body2" color="text.secondary">
          Published {formatDateTime(data.created_at)}
        </Typography>
      </Box>

      {cover ? (
        <Box
          component="img"
          src={resolveApiAssetUrl(cover.file_url)}
          alt={product.name}
          sx={{
            width: "100%",
            maxHeight: 320,
            objectFit: "contain",
            bgcolor: "grey.100",
            borderRadius: 1,
          }}
        />
      ) : null}

      <Section title="Product">
        <MetaRow label="SKU" value={product.sku} />
        <MetaRow label="Serial number" value={product.serial_number} />
        <MetaRow label="Production date" value={product.production_date} />
        <MetaRow label="Country of origin" value={product.country_of_origin} />
        {product.description ? (
          <Typography variant="body1" sx={{ mt: 1.5 }}>
            {product.description}
          </Typography>
        ) : null}
      </Section>

      <Section title="Materials">
        {!data.materials.length ? (
          <Typography color="text.secondary">No materials listed.</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>%</TableCell>
                <TableCell>Origin</TableCell>
                <TableCell>Recyclable</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.materials.map((row) => (
                <TableRow key={`${row.name}-${row.country_of_origin}`}>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{String(row.percentage)}</TableCell>
                  <TableCell>{row.country_of_origin}</TableCell>
                  <TableCell>{row.recyclable ? "Yes" : "No"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Section>

      <Section title="Sustainability">
        {!data.sustainability ? (
          <Typography color="text.secondary">Not provided.</Typography>
        ) : (
          <>
            <MetaRow
              label="Carbon footprint"
              value={data.sustainability.carbon_footprint}
            />
            <MetaRow
              label="Water consumption"
              value={data.sustainability.water_consumption}
            />
            <MetaRow
              label="Recycled material %"
              value={String(data.sustainability.recycled_material_percent)}
            />
            <MetaRow
              label="Repairability score"
              value={String(data.sustainability.repairability_score)}
            />
            <MetaRow
              label="Recyclable"
              value={data.sustainability.recyclable ? "Yes" : "No"}
            />
          </>
        )}
      </Section>

      <Section title="Certifications">
        {!data.certifications.length ? (
          <Typography color="text.secondary">None listed.</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Authority</TableCell>
                <TableCell>Issued</TableCell>
                <TableCell>Expires</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {data.certifications.map((row) => (
                <TableRow key={`${row.name}-${row.issue_date}`}>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.issuing_authority}</TableCell>
                  <TableCell>{row.issue_date}</TableCell>
                  <TableCell>{row.expiration_date ?? "—"}</TableCell>
                  <TableCell>
                    <MuiLink
                      href={resolveApiAssetUrl(row.pdf_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      PDF
                    </MuiLink>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Section>

      <Section title="Documents">
        {!data.documents.length ? (
          <Typography color="text.secondary">None listed.</Typography>
        ) : (
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            {data.documents.map((doc) => (
              <li key={`${doc.doc_type}-${doc.original_filename}`}>
                <MuiLink
                  href={resolveApiAssetUrl(doc.file_url)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {doc.original_filename}
                </MuiLink>
                <Typography
                  component="span"
                  variant="body2"
                  color="text.secondary"
                  sx={{ ml: 1, textTransform: "capitalize" }}
                >
                  ({doc.doc_type.replaceAll("_", " ")})
                </Typography>
              </li>
            ))}
          </Box>
        )}
      </Section>

      {gallery.length ? (
        <Section title="Images">
          <Box
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                xs: "1fr 1fr",
                sm: "repeat(3, 1fr)",
              },
            }}
          >
            {gallery.map((img) => (
              <Box
                key={img.id}
                component="img"
                src={resolveApiAssetUrl(img.file_url)}
                alt=""
                sx={{
                  width: "100%",
                  aspectRatio: "1",
                  objectFit: "cover",
                  bgcolor: "grey.100",
                  borderRadius: 1,
                }}
              />
            ))}
          </Box>
        </Section>
      ) : null}
    </Box>
  );
}

function PassportSkeleton() {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Skeleton width="60%" height={40} />
      <Skeleton variant="rounded" height={200} />
      <Skeleton variant="rounded" height={160} />
    </Box>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Box component="section">
      <Typography variant="h6" component="h2" gutterBottom>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: "160px 1fr",
        gap: 1,
        py: 0.5,
      }}
    >
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2">{value}</Typography>
    </Box>
  );
}
