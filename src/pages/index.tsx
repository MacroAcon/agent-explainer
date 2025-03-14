import React from 'react';
import { Container, Box, Typography, Tab, Tabs } from '@mui/material';
import AgentGraph from '../components/AgentGraph';
import HealthAgentGraph from '../components/HealthAgentGraph';
import ReactMarkdown from 'react-markdown';
import { GetStaticProps } from 'next';
import fs from 'fs/promises';
import path from 'path';

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
      id={`agent-tabpanel-${index}`}
      aria-labelledby={`agent-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `agent-tab-${index}`,
    'aria-controls': `agent-tabpanel-${index}`,
  };
}

interface ReadmeContentProps {
  content: string;
}

const ReadmeContent = ({ content }: ReadmeContentProps) => {
  return (
    <Box sx={{ 
      p: 3, 
      color: '#fff',
      maxWidth: '1200px', 
      margin: '0 auto',
      '& h1, & h2, & h3, & h4, & h5, & h6': {
        color: '#90caf9',
        marginTop: '1.5em',
        marginBottom: '0.5em'
      },
      '& p': {
        color: '#fff',
        marginBottom: '1em'
      },
      '& ul, & ol': {
        color: '#fff',
        marginBottom: '1em'
      },
      '& li': {
        marginBottom: '0.5em'
      },
      '& strong': {
        color: '#81c784'
      }
    }}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </Box>
  );
};

interface HomeProps {
  readmeContent: string;
}

export const getStaticProps: GetStaticProps<HomeProps> = async () => {
  const readmePath = path.join(process.cwd(), 'README.md');
  const readmeContent = await fs.readFile(readmePath, 'utf8');
  
  return {
    props: {
      readmeContent
    }
  };
};

export default function Home({ readmeContent }: HomeProps) {
  const [value, setValue] = React.useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      backgroundColor: '#121212',
      pb: 4
    }}>
      <Container maxWidth="xl">
        <Box sx={{ width: '100%', pt: 4 }}>
          <Typography 
            variant="h4" 
            component="h1" 
            gutterBottom 
            sx={{ 
              color: '#90caf9', 
              textAlign: 'center', 
              mb: 4,
              fontWeight: 500
            }}
          >
            A&A Calhoun Automation Consultancy - AI Agent System Examples
          </Typography>

          <Box sx={{ 
            borderBottom: 1, 
            borderColor: 'rgba(255, 255, 255, 0.12)',
            mb: 3
          }}>
            <Tabs 
              value={value} 
              onChange={handleChange} 
              aria-label="agent system tabs"
              sx={{
                '& .MuiTab-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&.Mui-selected': {
                    color: '#90caf9'
                  }
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: '#90caf9'
                }
              }}
            >
              <Tab label="Retail Example" {...a11yProps(0)} />
              <Tab label="Health Service Example" {...a11yProps(1)} />
              <Tab label="Documentation" {...a11yProps(2)} />
            </Tabs>
          </Box>

          <TabPanel value={value} index={0}>
            <AgentGraph />
          </TabPanel>

          <TabPanel value={value} index={1}>
            <HealthAgentGraph />
          </TabPanel>

          <TabPanel value={value} index={2}>
            <ReadmeContent content={readmeContent} />
          </TabPanel>
        </Box>
      </Container>
    </Box>
  );
} 