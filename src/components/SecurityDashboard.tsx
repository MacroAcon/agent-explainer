import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { SecurityMetrics } from '@/types/security';

const SecurityDashboard: React.FC = () => {
  const theme = useTheme();
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/security/metrics');
        if (!response.ok) {
          throw new Error('Failed to fetch security metrics');
        }
        const data = await response.json();
        if (!data.data) {
          throw new Error('Invalid metrics data format');
        }
        setMetrics(data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!metrics) {
    return (
      <Alert severity="warning" sx={{ m: 2 }}>
        No metrics data available
      </Alert>
    );
  }

  const getSeverityColor = (value: number, threshold: number) => {
    if (value > threshold * 1.2) return 'error';
    if (value > threshold) return 'warning';
    return 'success';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Security State */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security State
              </Typography>
              <Box sx={{ mb: 2 }}>
                {metrics.security_state.last_audit && (
                  <Typography variant="body2">
                    Last Audit: {new Date(metrics.security_state.last_audit).toLocaleString()}
                  </Typography>
                )}
                <Typography variant="body2">
                  Failed Attempts: {metrics.security_state.failed_attempts}
                </Typography>
                <Typography variant="body2">
                  Active Sessions: {metrics.security_state.active_sessions.length}
                </Typography>
              </Box>
              {metrics.security_state.locked_until && (
                <Alert severity="warning">
                  Account locked until: {new Date(metrics.security_state.locked_until).toLocaleString()}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2">CPU Usage</Typography>
                  <Chip
                    label={`${metrics.performance_metrics.system.cpu_percent.toFixed(1)}%`}
                    color={getSeverityColor(metrics.performance_metrics.system.cpu_percent, 80)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Memory Usage</Typography>
                  <Chip
                    label={`${metrics.performance_metrics.system.memory_percent.toFixed(1)}%`}
                    color={getSeverityColor(metrics.performance_metrics.system.memory_percent, 80)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Disk Usage</Typography>
                  <Chip
                    label={`${metrics.performance_metrics.system.disk_usage.toFixed(1)}%`}
                    color={getSeverityColor(metrics.performance_metrics.system.disk_usage, 90)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Process Count</Typography>
                  <Chip
                    label={metrics.performance_metrics.system.process_count}
                    color="primary"
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Audit Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2">Total Events</Typography>
                  <Typography variant="h6">{metrics.audit_metrics.total_events}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2">Events (24h)</Typography>
                  <Typography variant="h6">{metrics.audit_metrics.events_last_24h}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2">Events by Type</Typography>
                  {Object.entries(metrics.audit_metrics.events_by_type).map(([type, count]) => (
                    <Typography key={type} variant="body2">
                      {type}: {count}
                    </Typography>
                  ))}
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2">Events by Severity</Typography>
                  {Object.entries(metrics.audit_metrics.events_by_severity).map(([severity, count]) => (
                    <Typography key={severity} variant="body2">
                      {severity}: {count}
                    </Typography>
                  ))}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Alerts
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Category</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Threshold</TableCell>
                      <TableCell>Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {metrics.performance_metrics.alerts.map((alert, index) => (
                      <TableRow key={index}>
                        <TableCell>{alert.category}</TableCell>
                        <TableCell>{alert.type}</TableCell>
                        <TableCell>{alert.value.toFixed(2)}</TableCell>
                        <TableCell>{alert.threshold.toFixed(2)}</TableCell>
                        <TableCell>
                          {new Date(alert.timestamp).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SecurityDashboard; 