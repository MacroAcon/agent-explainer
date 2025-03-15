import React from 'react';
import { Container, Box, Typography, Tab, Tabs, useMediaQuery, useTheme } from '@mui/material';
import AgentGraph from '../components/AgentGraph';
import HealthAgentGraph from '../components/HealthAgentGraph';
import PrivacySettings from '../components/PrivacySettings';
import MarketingDemo from '../components/MarketingDemo';
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
  let readmeContent = '';
  
  try {
    const readmePath = path.join(process.cwd(), 'README.md');
    readmeContent = await fs.readFile(readmePath, 'utf8');
  } catch (error) {
    console.error('Error loading README.md:', error);
    readmeContent = '# Documentation\n\nDocumentation content will be available soon.';
  }
  
  return {
    props: {
      readmeContent
    }
  };
};

export default function Home({ readmeContent }: HomeProps) {
  const [value, setValue] = React.useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        CalCon Agent Framework
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3, width: '100%' }}>
        <Tabs 
          value={value} 
          onChange={handleChange} 
          aria-label="agent tabs"
          variant={isMobile ? "scrollable" : "standard"}
          scrollButtons="auto"
          allowScrollButtonsMobile
          sx={{ 
            maxWidth: '100%',
            '& .MuiTabs-flexContainer': {
              flexWrap: isMobile ? 'nowrap' : 'wrap'
            }
          }}
        >
          <Tab label="Restaurant Operations" {...a11yProps(0)} />
          <Tab label="Healthcare Operations" {...a11yProps(1)} />
          <Tab label="Marketing Demo" {...a11yProps(2)} />
          <Tab label="Documentation" {...a11yProps(3)} />
        </Tabs>
      </Box>
      
      <TabPanel value={value} index={0}>
        <AgentGraph />
      </TabPanel>
      
      <TabPanel value={value} index={1}>
        <HealthAgentGraph />
      </TabPanel>
      
      <TabPanel value={value} index={2}>
        <MarketingDemo />
      </TabPanel>
      
      <TabPanel value={value} index={3}>
        <ReadmeContent content={readmeContent} />
      </TabPanel>
      
      <PrivacySettings />
    </Container>
  );
} 