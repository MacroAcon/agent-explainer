import { AppProps } from 'next/app';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from '../styles/theme';
import { PrivacyProvider } from '../components/PrivacyContext';
import ErrorBoundary from '../components/ErrorBoundary';
import 'reactflow/dist/style.css';
import '../styles/NodeOverrides.css';
import '../styles/DarkNodes.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <PrivacyProvider>
          <Component {...pageProps} />
        </PrivacyProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default MyApp; 