import { Box, Card, CardContent, Typography, Grid } from '@mui/material';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to Web App
      </Typography>

      <Grid container spacing={2}>
        {/* Hardware Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Link to="/hardware" style={{ textDecoration: 'none' }}>
            <Card sx={{ height: 150 }}>
              <CardContent>
                <Typography variant="h6">Hardware</Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage your hardware inventory
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        {/* Add more cards here */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: 150 }}>
            <CardContent>
              <Typography variant="h6">Coming Soon</Typography>
              <Typography variant="body2" color="text.secondary">
                Placeholder for future features
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
