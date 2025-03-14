import { Node, Edge } from 'reactflow';
import { NodeData } from '../types/agent';

export const initialNodes: Node<NodeData>[] = [
  {
    id: 'base',
    type: 'default',
    position: { x: 100, y: 400 },
    data: {
      label: 'Base Health Agent',
      description: 'Core healthcare automation agent',
      type: 'default',
      channels: ['email', 'sms', 'web'],
      tools: ['scheduling', 'records', 'analytics']
    }
  },
  {
    id: 'coordinator',
    type: 'default',
    position: { x: 500, y: 400 },
    data: {
      label: 'Healthcare Coordinator',
      description: 'Coordinates healthcare operations',
      type: 'coordinator',
      channels: ['email', 'sms', 'web', 'phone'],
      tools: ['scheduling', 'records', 'analytics', 'coordination']
    }
  },
  {
    id: 'swarm_coordinator',
    type: 'default',
    position: { x: 500, y: 700 },
    data: {
      label: 'Compliance Swarm Coordinator',
      description: 'Manages compliance swarm agents',
      type: 'swarm_coordinator',
      channels: ['email', 'web', 'internal'],
      tools: ['compliance', 'monitoring', 'reporting']
    }
  },
  {
    id: 'patient',
    type: 'default',
    position: { x: 900, y: 200 },
    data: {
      label: 'Patient Care Operations',
      description: 'Handles patient care services',
      type: 'operations',
      channels: ['email', 'sms', 'web', 'phone'],
      tools: ['scheduling', 'records', 'care']
    }
  },
  {
    id: 'pharmacy',
    type: 'default',
    position: { x: 900, y: 400 },
    data: {
      label: 'Pharmacy Operations',
      description: 'Manages pharmacy services',
      type: 'operations',
      channels: ['email', 'web', 'internal'],
      tools: ['prescriptions', 'inventory', 'dispensing']
    }
  },
  {
    id: 'lab',
    type: 'default',
    position: { x: 900, y: 600 },
    data: {
      label: 'Laboratory Services',
      description: 'Handles lab operations',
      type: 'operations',
      channels: ['email', 'web', 'internal'],
      tools: ['testing', 'results', 'analysis']
    }
  },
  {
    id: 'clinic',
    type: 'default',
    position: { x: 1300, y: 400 },
    data: {
      label: 'Calhoun Clinic',
      description: 'Physical location for services',
      type: 'location',
      channels: ['email', 'sms', 'web', 'phone'],
      tools: ['scheduling', 'records', 'location']
    }
  },
  {
    id: 'privacy',
    type: 'default',
    position: { x: 1300, y: 800 },
    data: {
      label: 'Data Privacy Agent',
      description: 'Ensures data privacy compliance',
      type: 'swarm_agent',
      channels: ['internal'],
      tools: ['privacy', 'compliance', 'monitoring']
    }
  },
  {
    id: 'audit',
    type: 'default',
    position: { x: 1300, y: 900 },
    data: {
      label: 'Audit Agent',
      description: 'Performs compliance audits',
      type: 'swarm_agent',
      channels: ['internal'],
      tools: ['audit', 'compliance', 'reporting']
    }
  },
  {
    id: 'breach',
    type: 'default',
    position: { x: 1300, y: 1000 },
    data: {
      label: 'Breach Detection Agent',
      description: 'Monitors for data breaches',
      type: 'swarm_agent',
      channels: ['internal'],
      tools: ['monitoring', 'alerts', 'response']
    }
  },
  {
    id: 'insurance',
    type: 'default',
    position: { x: 1700, y: 300 },
    data: {
      label: 'Insurance Processing',
      description: 'Handles insurance operations',
      type: 'service',
      channels: ['email', 'web', 'internal'],
      tools: ['claims', 'billing', 'verification']
    }
  },
  {
    id: 'telemedicine',
    type: 'default',
    position: { x: 1700, y: 500 },
    data: {
      label: 'Telemedicine Operations',
      description: 'Manages virtual healthcare',
      type: 'service',
      channels: ['email', 'web', 'video'],
      tools: ['scheduling', 'video', 'records']
    }
  },
  {
    id: 'emergency',
    type: 'default',
    position: { x: 1700, y: 700 },
    data: {
      label: 'Emergency Response Coordinator',
      description: 'Coordinates emergency services',
      type: 'coordinator',
      channels: ['phone', 'sms', 'radio'],
      tools: ['dispatch', 'coordination', 'response']
    }
  }
];

export const initialEdges: Edge[] = [
  {
    id: 'base-coordinator',
    source: 'base',
    target: 'coordinator',
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  {
    id: 'base-swarm-coordinator',
    source: 'base',
    target: 'swarm_coordinator',
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  {
    id: 'coordinator-patient',
    source: 'coordinator',
    target: 'patient',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  {
    id: 'coordinator-pharmacy',
    source: 'coordinator',
    target: 'pharmacy',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  {
    id: 'coordinator-lab',
    source: 'coordinator',
    target: 'lab',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  {
    id: 'swarm-privacy',
    source: 'swarm_coordinator',
    target: 'privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'swarm-audit',
    source: 'swarm_coordinator',
    target: 'audit',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'swarm-breach',
    source: 'swarm_coordinator',
    target: 'breach',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'privacy-patient',
    source: 'privacy',
    target: 'patient',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'privacy-pharmacy',
    source: 'privacy',
    target: 'pharmacy',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'privacy-lab',
    source: 'privacy',
    target: 'lab',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'patient-clinic',
    source: 'patient',
    target: 'clinic',
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'pharmacy-clinic',
    source: 'pharmacy',
    target: 'clinic',
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'lab-clinic',
    source: 'lab',
    target: 'clinic',
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'clinic-insurance',
    source: 'clinic',
    target: 'insurance',
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  {
    id: 'clinic-telemedicine',
    source: 'clinic',
    target: 'telemedicine',
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  {
    id: 'clinic-emergency',
    source: 'clinic',
    target: 'emergency',
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  }
]; 