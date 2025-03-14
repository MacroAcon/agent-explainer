import { NextPage } from 'next';
import { Box, Typography, Button, Container } from '@mui/material';
import { useRouter } from 'next/router';
import { GetServerSideProps } from 'next';

interface ErrorProps {
  statusCode?: number;
}

const Error: NextPage<ErrorProps> = ({ statusCode }) => {
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
          {statusCode || 'Error'}
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          {statusCode ? 'An error occurred on server' : 'An error occurred on client'}
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          {statusCode
            ? `The server returned an error with status code ${statusCode}.`
            : 'Something went wrong while loading this page.'}
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

export const getServerSideProps: GetServerSideProps = async ({ res }) => {
  const statusCode = res ? res.statusCode : 404;
  return { props: { statusCode } };
};

export default Error; 