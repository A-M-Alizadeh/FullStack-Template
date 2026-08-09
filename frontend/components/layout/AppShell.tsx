"use client";

import MenuIcon from "@mui/icons-material/Menu";
import {
  AppBar,
  Box,
  Button,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";

import { useT } from "@/hooks/useT";
import { getAppName } from "@/lib/env";
import { BACKOFFICE_NAV, LOGIN_PATH, navVisibleForRole } from "@/lib/navigation";
import { useLogoutMutation } from "@/store/api/authApi";
import { selectUser } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";

const DRAWER_WIDTH = 240;

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const t = useT();
  const pathname = usePathname();
  const router = useRouter();
  const user = useAppSelector(selectUser);
  const [logout, { isLoading: loggingOut }] = useLogoutMutation();
  const [mobileOpen, setMobileOpen] = useState(false);

  async function handleLogout() {
    try {
      await logout().unwrap();
    } finally {
      router.replace(LOGIN_PATH);
    }
  }

  const navItems = BACKOFFICE_NAV.filter((item) =>
    navVisibleForRole(item, user?.role),
  );

  const drawer = (
    <Box sx={{ pt: 1 }}>
      <List>
        {navItems.map((item) => (
          <ListItemButton
            key={item.href}
            component={Link}
            href={item.href}
            selected={
              pathname === item.href || pathname.startsWith(`${item.href}/`)
            }
            onClick={() => setMobileOpen(false)}
          >
            <ListItemText primary={t(item.labelKey)} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen((open) => !open)}
            sx={{ mr: 1, display: { md: "none" } }}
            aria-label="Open menu"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {getAppName()}
          </Typography>
          {user ? (
            <Typography
              variant="body2"
              sx={{ mr: 2, display: { xs: "none", sm: "block" } }}
            >
              {user.email}
            </Typography>
          ) : null}
          <Button color="inherit" onClick={handleLogout} disabled={loggingOut}>
            {t("common.logout")}
          </Button>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": { width: DRAWER_WIDTH },
          }}
        >
          <Toolbar />
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
            },
          }}
        >
          <Toolbar />
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
