import React from 'react';
import { Container, Box, Typography, Tab, Tabs } from '@mui/material';
import SecurityDashboard from '../components/SecurityDashboard';
import AgentGraph from '../components/AgentGraph';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function Home() {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          CalCon - AI Agent System
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Agent Graph" />
            <Tab label="Security Dashboard" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <AgentGraph />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <SecurityDashboard />
        </TabPanel>
      </Box>
    </Container>
  );
} 