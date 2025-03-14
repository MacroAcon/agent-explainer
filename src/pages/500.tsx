import { NextPage } from 'next';
import { Box, Typography, Button, Container } from '@mui/material';
import { useRouter } from 'next/router';

const ServerError: NextPage = () => {
  const router = useRouter();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
          p: 3,
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          500
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Server Error
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Something went wrong on our end. We're working to fix the issue.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => router.push('/')}
          sx={{ mt: 2 }}
        >
          Return Home
        </Button>
      </Box>
    </Container>
  );
};

export default ServerError; 