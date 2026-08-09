/**
 * EN / IT message catalogs. Keys stay stable; swap catalogs via locale.
 */

import type { Locale } from "./preferences";

const en = {
  "common.retry": "Retry",
  "common.notFound": "Not found",
  "common.save": "Save",
  "common.cancel": "Cancel",
  "common.logout": "Log out",

  "nav.dashboard": "Dashboard",
  "nav.products": "Products",
  "nav.analytics": "Analytics",
  "nav.settings": "Settings",

  "auth.signIn": "Sign in",
  "auth.email": "Email",
  "auth.password": "Password",
  "auth.invalidCredentials": "Invalid email or password",

  "dashboard.title": "Dashboard",
  "dashboard.subtitle": "Overview of products, passports, and QR activity.",
  "dashboard.loadError": "Could not load dashboard",
  "dashboard.totalProducts": "Total products",
  "dashboard.publishedPassports": "Published passports",
  "dashboard.generatedQr": "Generated QR codes",
  "dashboard.passportViews": "Passport views (QR scans)",
  "dashboard.manageProducts": "Manage products",
  "dashboard.viewAnalytics": "View analytics",

  "products.title": "Products",
  "products.new": "New product",
  "products.empty": "No products yet.",
  "products.create": "Create product",
  "products.loadError": "Could not load products",

  "analytics.title": "Analytics",
  "analytics.subtitle": "QR scan activity from passport links with ?src=qr.",
  "analytics.loadError": "Could not load analytics",
  "analytics.noScans": "No QR scans yet.",
  "analytics.noLatest": "No recent scans.",
  "analytics.scansToday": "Scans today",
  "analytics.scansWeek": "Scans this week",
  "analytics.mostViewed": "Most viewed products",
  "analytics.latestScans": "Latest scans",

  "passport.loadError": "Passport not found or no longer available",
  "publish.qrLoadError": "Could not load QR code",

  "settings.title": "Settings",
  "settings.subtitle": "Appearance and language for this browser.",
  "settings.theme": "Theme",
  "settings.themeLight": "Light",
  "settings.themeDark": "Dark",
  "settings.language": "Language",
  "settings.languageEn": "English",
  "settings.languageIt": "Italiano",
} as const;

const it: Record<keyof typeof en, string> = {
  "common.retry": "Riprova",
  "common.notFound": "Non trovato",
  "common.save": "Salva",
  "common.cancel": "Annulla",
  "common.logout": "Esci",

  "nav.dashboard": "Dashboard",
  "nav.products": "Prodotti",
  "nav.analytics": "Analitiche",
  "nav.settings": "Impostazioni",

  "auth.signIn": "Accedi",
  "auth.email": "Email",
  "auth.password": "Password",
  "auth.invalidCredentials": "Email o password non validi",

  "dashboard.title": "Dashboard",
  "dashboard.subtitle": "Panoramica di prodotti, passaporti e attività QR.",
  "dashboard.loadError": "Impossibile caricare la dashboard",
  "dashboard.totalProducts": "Prodotti totali",
  "dashboard.publishedPassports": "Passaporti pubblicati",
  "dashboard.generatedQr": "Codici QR generati",
  "dashboard.passportViews": "Visualizzazioni passaporto (scan QR)",
  "dashboard.manageProducts": "Gestisci prodotti",
  "dashboard.viewAnalytics": "Vedi analitiche",

  "products.title": "Prodotti",
  "products.new": "Nuovo prodotto",
  "products.empty": "Nessun prodotto ancora.",
  "products.create": "Crea prodotto",
  "products.loadError": "Impossibile caricare i prodotti",

  "analytics.title": "Analitiche",
  "analytics.subtitle": "Attività di scan QR dai link passaporto con ?src=qr.",
  "analytics.loadError": "Impossibile caricare le analitiche",
  "analytics.noScans": "Nessuno scan QR ancora.",
  "analytics.noLatest": "Nessuno scan recente.",
  "analytics.scansToday": "Scan oggi",
  "analytics.scansWeek": "Scan questa settimana",
  "analytics.mostViewed": "Prodotti più visti",
  "analytics.latestScans": "Scan recenti",

  "passport.loadError": "Passaporto non trovato o non più disponibile",
  "publish.qrLoadError": "Impossibile caricare il codice QR",

  "settings.title": "Impostazioni",
  "settings.subtitle": "Aspetto e lingua per questo browser.",
  "settings.theme": "Tema",
  "settings.themeLight": "Chiaro",
  "settings.themeDark": "Scuro",
  "settings.language": "Lingua",
  "settings.languageEn": "English",
  "settings.languageIt": "Italiano",
};

const catalogs: Record<Locale, Record<keyof typeof en, string>> = {
  en,
  it,
};

export type MessageKey = keyof typeof en;

export function t(key: MessageKey, locale: Locale = "en"): string {
  return catalogs[locale][key] ?? catalogs.en[key] ?? key;
}
