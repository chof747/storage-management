import React, { useState } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import MenuDrawer from './Menu';

const drawerWidth = 240;

export default function Layout({ children, rightPanel }: { children: React.ReactNode, rightPanel?: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          Web App
        </Typography>
      </Toolbar>
      <MenuDrawer />
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />

      {/* Top bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap>
            Web App
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
      )}

      {/* Desktop Drawer */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
          }}
          open
        >
          {drawer}
        </Drawer>
      )}


      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          display: 'flex',
          flexDirection: 'row',
          width: { sm: '100%', },
          ml: { sm: `${drawerWidth}px` },
          gap: 2,
        }}
      >
        {/* Centered Content */}
        <Box
          sx={{
            flex: 1,
            maxWidth: isMobile ? '100%' : '900px',
          }}
        >
          <Toolbar />
          {children}
        </Box>

        {/* Optional Right Panel */}
        {rightPanel && (
          <Box
            sx={{
              display: { xs: 'none', md: 'block' }, // hide on mobile
              flexGrow: 1,
              minWidth: 50,
              maxWidth: 200,
            }}
          >
            <Toolbar />
            {rightPanel}
          </Box>
        )}

      </Box>

    </Box>
  );
}
