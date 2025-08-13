"""
🌸 Aromance Fetch.ai Agents System
================================

Intelligent AI agents untuk NextGen Agents Hackathon
Built with Fetch.ai uAgents framework

## Agent Architecture

### 1. System Coordinator (Port 8000)
- Orchestrates multi-agent workflows
- Manages user journey across agents
- Handles ICP canister integration
- Monitors system health

### 2. Consultation AI (Port 8001) 
- Natural language conversation for fragrance discovery
- Personality-based preference analysis
- Indonesian market context understanding
- Creates personalized fragrance profiles

### 3. Recommendation AI (Port 8002)
- AI-powered product matching algorithm
- Indonesian fragrance database integration
- Multi-factor scoring (personality, budget, occasion)
- Halal certification & local brand prioritization

### 4. Analytics AI (Port 8004)
- Business intelligence for sellers
- Market trend analysis
- Performance optimization recommendations
- Seasonal demand prediction

### 5. Inventory AI (Port 8005)
- Smart stock management
- Low stock alerts & restock recommendations
- Demand forecasting
- Product performance tracking

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install uagents requests asyncio
   ```

2. Start all agents:
   ```bash
   python agents/run_all_agents.py
   ```

3. Individual agent startup:
   ```bash
   python agents/consultation/consultation_agent.py
   python agents/recommendation/recommendation_agent.py
   # etc...
   ```

## Integration Checklist

### Frontend Integration
- [ ] Connect to Coordinator agent (port 8000)
- [ ] Implement chat interface for Consultation AI
- [ ] Display recommendations from Recommendation AI
- [ ] Add analytics dashboard for sellers

### Backend Integration  
- [ ] Configure ICP canister endpoints
- [ ] Implement authentication middleware
- [ ] Add rate limiting
- [ ] Set up monitoring & logging

### Data Integration
- [ ] Add Indonesian perfume products database
- [ ] Import halal certification data
- [ ] Configure local brand information
- [ ] Set up user preference storage

### Production Deployment
- [ ] Deploy agents to separate containers/servers
- [ ] Configure load balancing
- [ ] Set up monitoring & alerting
- [ ] Implement backup & recovery

## Agent Communication Flow

```
User Request → Coordinator → Consultation AI
                    ↓
              Creates Profile → Recommendation AI
                    ↓
              Generates Recs → Analytics AI (tracking)
                    ↓
              Check Stock → Inventory AI
                    ↓
              Return Results → Frontend
```

## Hackathon Submission

This system demonstrates:
✅ Multi-agent coordination
✅ Autonomous decision making  
✅ Real-world business application
✅ Indonesian market localization
✅ AI-powered personalization
✅ Blockchain integration (ICP)

## NOTE untuk Tim Development

1. **Data Population**: Tambahkan produk parfum Indonesia di `recommendation_agent.py`
2. **ICP Integration**: Configure canister endpoints di semua agent files
3. **Testing**: Gunakan `test_agent.py` untuk testing individual agents
4. **Monitoring**: Check logs untuk debugging dan performance monitoring
5. **Scaling**: Setiap agent bisa di-scale independent sesuai load

Happy coding! 🚀
"""