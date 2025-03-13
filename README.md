# Calhoun Business Automation Framework

A specialized automation framework for small businesses in Calhoun, GA, powered by AG2 (Autonomous Group 2) technology.

## Core Components

### Business Swarm Coordinator
The central coordinator that manages all specialized agents using AG2's CaptainAgent architecture. Responsible for:
- Task delegation and coordination through dedicated communication channels
- Priority-based task queue management
- Real-time performance monitoring and metrics
- Multi-channel agent communication
- Compliance oversight
- Local market optimization

## Specialized Agents

### Restaurant Operations Agent
Manages day-to-day restaurant operations including:
- Menu management and pricing
- Kitchen operations and food prep
- Quality control and food safety
- Table and seating management
- Bar operations and compliance
- Food cost analysis
- Kitchen staff coordination
- Equipment maintenance
- Food waste management
- Catering operations
- Local ingredient sourcing

### Retail Operations Agent
Handles retail business operations including:
- Inventory management
- Order processing
- Employee scheduling
- Customer loyalty programs
- Payment processing
- Sales analytics
- Supplier management
- Delivery coordination
- Compliance monitoring
- Peak time tracking

### Local Marketing Agent
Specializes in local marketing and community engagement:
- Social media management
- Local event coordination
- Community promotions
- Customer review management
- Local partnership development
- Seasonal campaign creation
- Competitor analysis
- Business organization engagement
- Community event planning
- Email marketing
- Local media coordination

### Local Supplier Integration Agent
Manages relationships with local suppliers and community:
- Supplier relationship management
- Seasonal ingredient tracking
- Community event monitoring
- Farm-to-table program coordination
- Supplier compliance management
- Bulk purchasing coordination
- Sustainability initiatives
- Community engagement
- Food education programs
- Market price analysis

## Base Classes

### BaseBusinessAgent
Foundation class that provides:
- AG2 SwarmAgent integration
- Tool registration and management
- Task processing capabilities
- Conversation memory management
- Error handling
- Response formatting

### HIPAACompliantAgent
Extended base class that ensures:
- HIPAA privacy standards
- PHI protection
- Access logging
- Authorization verification
- Data encryption
- Minimum necessary principle

## Technical Details

### AG2 Integration
The framework leverages AG2's advanced features:
- CaptainAgent for intelligent task coordination
- SwarmAgent for specialized operations
- GroupChat with dedicated communication channels
- Advanced memory management systems
- Tool chain for complex operations
- Task delegation with priority management
- Real-time metrics and analytics

### Security & Compliance
Built-in security features include:
- Access level management (admin/write/read)
- Activity logging
- Data protection
- Authorization verification
- Privacy controls

### Local Market Focus
Specialized for Calhoun, GA businesses:
- Local supplier integration
- Community event tracking
- Market-specific pricing
- Local compliance management
- Community engagement

## Getting Started

1. Initialize the swarm coordinator:
```python
coordinator = BusinessSwarmCoordinator()
```

2. Process business tasks:
```python
result = await coordinator.process_task(
    task="your task description",
    context={
        "business_type": "restaurant/retail",
        "business_name": "Your Business Name",
        "user_id": "USER_ID",
        "access_level": "admin/write/read"
    }
)
```

3. Review results:
- Task status and timestamp
- Agent responses
- Captain's analysis
- Recommended next steps
- Task completion status

## Configuration

Key settings can be configured in `src/config/config.py`:
- Model settings
- API keys
- Business information
- Security parameters
- Logging preferences

## Features

- Multi-agent framework with advanced memory systems
- Priority-based task management
- Dedicated communication channels
- Real-time performance monitoring
- Customizable for different business types
- Built-in customer service capabilities
- Easy to extend with new agent types
- Secure and privacy-focused

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Running the Example

```bash
python src/example.py
```

### Creating Custom Agents

1. Create a new agent class in `src/agents/` inheriting from `BaseBusinessAgent`
2. Define the agent's system message and tools
3. Implement the `generate_response()` method

Example:
```python
from agents.base_agent import BaseBusinessAgent

class MyCustomAgent(BaseBusinessAgent):
    def __init__(self, name: str = "MyCustomAgent"):
        system_message = """Your custom system message here"""
        tools = [
            {
                "name": "custom_tool",
                "description": "Tool description",
                "func": self.custom_tool
            }
        ]
        super().__init__(name=name, system_message=system_message, tools=tools)
    
    async def generate_response(self, task: str, context: Dict[str, Any]) -> str:
        # Implement your custom response generation logic here
        pass
```

## Project Structure

```
src/
├── agents/          # Agent implementations
├── tools/           # Custom tools and utilities
├── templates/       # Response templates
├── config/          # Configuration files
└── example.py       # Example usage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Agent Network Visualizer

An interactive visualization of the business automation agent network. This web-based tool provides a visual representation of:

- Agent hierarchy and inheritance
- Agent capabilities and tools
- Inter-agent communication patterns
- Business process flows

### Visualizer Features

- Interactive node-based visualization
- Detailed agent information display
- Tool and capability exploration
- Real-time network manipulation
- Responsive design

### Technology Stack

- Next.js 14
- React Flow
- TypeScript
- Tailwind CSS

### Visualizer Setup

1. Install dependencies:
   ```bash
   cd agent-visualizer
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Deployment

The visualizer is deployed on Netlify:
1. Push code to GitHub
2. Connect GitHub repository to Netlify
3. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `.next`

### Project Structure

```
.
├── src/                 # Framework source code
│   ├── agents/         # Agent implementations
│   ├── tools/          # Custom tools and utilities
│   ├── templates/      # Response templates
│   └── config/         # Configuration files
│
└── agent-visualizer/   # Interactive visualization
    ├── src/
    │   ├── app/       # Next.js app
    │   └── components/# React components
    └── public/        # Static assets
```

## License

MIT License 