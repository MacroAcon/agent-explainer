import { Node, Edge } from 'reactflow';
import { NodeData } from '../types/agent';

export const initialNodes: Node<NodeData>[] = [
  {
    id: 'base',
    type: 'default',
    position: { x: 100, y: 400 },
    data: {
      label: 'Base Business Agent',
      description: 'Base agent class for business automation tasks',
      type: 'default',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy'],
      tools: ['process_task', 'register_tools', 'generate_response']
    }
  },
  {
    id: 'coordinator',
    type: 'default',
    position: { x: 500, y: 400 },
    data: {
      label: 'Business Swarm Coordinator',
      description: 'Coordinates business automation agents',
      type: 'coordinator',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['delegate_task', 'monitor_performance', 'manage_channels', 'track_metrics', 'manage_group_discussions']
    }
  },
  {
    id: 'privacy_coordinator',
    type: 'default',
    position: { x: 500, y: 700 },
    data: {
      label: 'Privacy Swarm Coordinator',
      description: 'Coordinates temporary privacy-focused agents',
      type: 'swarm_coordinator',
      channels: ['privacy', 'customer_relations', 'audit'],
      tools: ['spawn_privacy_agent', 'monitor_compliance', 'coordinate_audits']
    }
  },
  {
    id: 'restaurant',
    type: 'default',
    position: { x: 900, y: 200 },
    data: {
      label: 'Restaurant Operations',
      description: 'Manages global restaurant operations and standards',
      type: 'operations',
      channels: ['operations', 'supply_chain', 'privacy', 'group_chat'],
      tools: ['manage_menu', 'manage_kitchen', 'monitor_quality', 'manage_inventory', 'coordinate_staff_discussions']
    }
  },
  {
    id: 'retail',
    type: 'default',
    position: { x: 900, y: 400 },
    data: {
      label: 'Retail Operations',
      description: 'Manages global retail operations and standards',
      type: 'operations',
      channels: ['operations', 'supply_chain', 'privacy', 'group_chat'],
      tools: ['manage_inventory', 'process_orders', 'track_sales', 'manage_logistics', 'coordinate_team_discussions']
    }
  },
  {
    id: 'marketing',
    type: 'default',
    position: { x: 900, y: 600 },
    data: {
      label: 'Marketing Operations',
      description: 'Manages global marketing strategy and standards',
      type: 'marketing',
      channels: ['marketing', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['create_promotions', 'track_events', 'manage_reviews', 'coordinate_campaign_discussions']
    }
  },
  {
    id: 'loyalty_privacy',
    type: 'default',
    position: { x: 1300, y: 800 },
    data: {
      label: 'Loyalty Data Privacy Agent',
      description: 'Temporary agent for customer loyalty data protection',
      type: 'swarm_agent',
      channels: ['privacy', 'customer_relations'],
      tools: ['encrypt_data', 'manage_consent', 'anonymize_analytics']
    }
  },
  {
    id: 'payment_privacy',
    type: 'default',
    position: { x: 1300, y: 900 },
    data: {
      label: 'Payment Privacy Agent',
      description: 'Temporary agent for payment data security',
      type: 'swarm_agent',
      channels: ['privacy', 'operations'],
      tools: ['secure_transactions', 'mask_card_data', 'audit_access']
    }
  },
  {
    id: 'marketing_privacy',
    type: 'default',
    position: { x: 1300, y: 1000 },
    data: {
      label: 'Marketing Privacy Agent',
      description: 'Temporary agent for marketing data compliance',
      type: 'swarm_agent',
      channels: ['privacy', 'marketing'],
      tools: ['manage_preferences', 'verify_consent', 'clean_analytics']
    }
  },
  {
    id: 'calhoun',
    type: 'default',
    position: { x: 1300, y: 400 },
    data: {
      label: 'Calhoun Location',
      description: 'Manages all operations for Calhoun, GA location',
      type: 'location',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['manage_local_ops', 'track_performance', 'coordinate_services', 'manage_group_channels']
    }
  },
  {
    id: 'supplier',
    type: 'default',
    position: { x: 1700, y: 300 },
    data: {
      label: 'Local Supplier Integration',
      description: 'Manages supplier relationships and contracts',
      type: 'service',
      channels: ['supply_chain', 'operations', 'group_chat'],
      tools: ['manage_suppliers', 'track_ingredients', 'monitor_costs', 'coordinate_supply_discussions']
    }
  },
  {
    id: 'customer',
    type: 'default',
    position: { x: 1700, y: 500 },
    data: {
      label: 'Customer Service',
      description: 'Handles customer service tasks',
      type: 'service',
      channels: ['customer_relations', 'marketing', 'privacy', 'group_chat'],
      tools: ['handle_inquiries', 'manage_complaints', 'manage_feedback', 'coordinate_service_discussions']
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
    id: 'base-privacy-coordinator',
    source: 'base',
    target: 'privacy_coordinator',
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-restaurant', 
    source: 'coordinator', 
    target: 'restaurant', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-retail', 
    source: 'coordinator', 
    target: 'retail', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-marketing', 
    source: 'coordinator', 
    target: 'marketing', 
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-calhoun', 
    source: 'coordinator', 
    target: 'calhoun', 
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-loyalty',
    source: 'privacy_coordinator',
    target: 'loyalty_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-payment',
    source: 'privacy_coordinator',
    target: 'payment_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-marketing',
    source: 'privacy_coordinator',
    target: 'marketing_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'loyalty-retail',
    source: 'loyalty_privacy',
    target: 'retail',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'loyalty-customer',
    source: 'loyalty_privacy',
    target: 'customer',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'payment-restaurant',
    source: 'payment_privacy',
    target: 'restaurant',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'payment-retail',
    source: 'payment_privacy',
    target: 'retail',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'marketing-privacy-marketing',
    source: 'marketing_privacy',
    target: 'marketing',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'restaurant-calhoun', 
    source: 'restaurant', 
    target: 'calhoun',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'retail-calhoun', 
    source: 'retail', 
    target: 'calhoun',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'marketing-calhoun', 
    source: 'marketing', 
    target: 'calhoun',
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  { 
    id: 'calhoun-supplier', 
    source: 'calhoun', 
    target: 'supplier',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  { 
    id: 'calhoun-customer', 
    source: 'calhoun', 
    target: 'customer',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  }
]; 