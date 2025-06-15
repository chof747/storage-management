import { Box, Card, CardContent, Typography, Grid } from '@mui/material';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (

    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to the Storage Manager
      </Typography>

      <Box
        sx={{
          position: 'relative',
          minHeight: '100vh',
          backgroundImage: 'url(/background.png)',
          backgroundRepeat: 'no-repeat',
          backgroundSize: 'auto 80vh',
          backgroundPosition: 'center',
          // Optional: dim the image by overlaying a transparent color
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.75)', // 50% white overlay
          },
        }}
      >
        <Box sx={{ position: 'relative', p: 4 }}>

          <Grid container spacing={2}>
            {/* Hardware Card */}
            <Grid item xs={12} sm={6} md={4}>
              <Link to="/hardware" style={{ textDecoration: 'none' }}>
                <Card sx={{ height: 150, backgroundColor: 'rgba(255, 255, 255, 0.8)' }}>
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
              <Card sx={{ height: 150, backgroundColor: 'rgba(255, 255, 255, 0.8)' }}>
                <CardContent>
                  <Typography variant="h6">Projects</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Coming soon
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Box>
  );
}
