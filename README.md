<<<<<<< HEAD
# Calhoun Business Agent Network Visualizer

An interactive visualization of the business automation agent network for Calhoun, GA businesses. This project provides a visual representation of:

- Agent hierarchy and inheritance
- Agent capabilities and tools
- Inter-agent communication patterns
- Business process flows

## Features

- Interactive node-based visualization
- Detailed agent information display
- Tool and capability exploration
- Real-time network manipulation
- Responsive design

## Technology Stack

- Next.js 14
- React Flow
- TypeScript
- Tailwind CSS

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Netlify

1. Push your code to GitHub
2. Connect your GitHub repository to Netlify
3. Configure the build settings:
   - Build command: `npm run build`
   - Publish directory: `.next`
4. Deploy!

## Project Structure

```
agent-visualizer/
├── src/
│   ├── app/
│   │   ├── page.tsx       # Main page component
│   │   └── layout.tsx     # Root layout with styles
│   └── components/
│       ├── AgentGraph.tsx # Graph visualization
│       └── AgentNode.tsx  # Custom node component
├── public/
└── package.json
```

## Development

- The agent network is defined in `src/components/AgentGraph.tsx`
- Agent node styling is in `src/components/AgentNode.tsx`
- Add new agents by extending the `initialNodes` array
- Define new connections in the `initialEdges` array

## License

MIT
=======
# agent-explainer
>>>>>>> 6ecde929039ee60cfea5a6c4d67222250a4058a5
