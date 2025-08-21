# Aromance - AI-Powered Perfume Marketplace

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)

An intelligent perfume marketplace leveraging Fetch.ai uAgents and Internet Computer Protocol for personalized fragrance recommendations and decentralized identity protection.

## Introduction

Aromance addresses three key challenges in the Indonesian perfume industry: difficulty in choosing fragrances that match personality (92.9% of consumers), fake reviews and misleading information (85.7% experience), and personal data privacy concerns (71.4% worried about data breaches).

The platform combines AI-powered personality analysis with blockchain technology to create a secure, personalized perfume shopping experience where users maintain complete control over their personal data through decentralized identity systems.

## Architecture

The platform uses a multi-layer architecture:

**Frontend Layer**: React 19 with Vite for modern UI/UX
**AI Agent Layer**: Five specialized Fetch.ai agents for different functions
**Backend Layer**: Rust canisters on Internet Computer Protocol
**Data Layer**: Decentralized storage with user-controlled access

```
Frontend (React + Vite) → AI Agents (Fetch.ai) → ICP Canisters (Rust)
```

## Tech Stack

**Frontend**
- React 19.1.1
- Vite 4.3.9
- TypeScript 5.1.3
- SCSS 1.63.6

**Backend (ICP)**
- Rust Edition 2021
- Internet Computer Protocol
- Candid Interface
- WASM32 deployment target

**AI Agents (Fetch.ai)**
- Python 3.12.3
- uAgents framework
- AsyncIO for concurrent processing
- CosmPy for blockchain integration

**Development Environment**
- Node.js 20.19.4
- DFX 0.24.3
- Ubuntu 24.04.2 LTS

## Project Structure

```
aromance/
├── .dfx/                    # ICP local deployment
├── .env                     # Environment variables
├── agents/                  # Fetch.ai AI Agents
│   ├── coordinator.py       # Main orchestrator
│   ├── consultation/        # Personality analysis
│   ├── recommendation/      # Product matching
│   ├── analytics/          # User behavior analysis
│   ├── inventory/          # Stock management
│   └── run_all_agents.py   # Agent startup script
├── src/
│   ├── aromance_backend/   # Rust ICP canister
│   │   ├── src/lib.rs      # Backend implementation
│   │   └── aromance_backend.did # Candid interface
│   └── aromance_frontend/  # React application
│       ├── src/App.jsx     # Main application
│       └── package.json    # Frontend dependencies
├── fetchai_env/            # Python virtual environment
├── install.sh             # Automated installer
├── Cargo.toml             # Rust workspace
├── dfx.json              # ICP configuration
└── package.json          # Root dependencies
```

## ICP Features Used

**Advanced Features Implemented**
- HTTP Outcalls for external API integration with Fetch.ai agents
- Timers for automated treasury management and analytics processing
- Inter-Canister Communication for modular architecture
- Stable Memory for persistent storage across upgrades
- Certified Variables for tamper-proof data integrity

**Core Canister Functions**
- User Management (create_user_profile, get_user_profile)
- Decentralized Identity (create_decentralized_identity, update_user_data_permissions)  
- Product Management (add_product, search_products_advanced, get_halal_products)
- AI Recommendations (generate_ai_recommendations, get_recommendations_for_user)
- Verification System (stake_for_verification, process_stake_rewards)
- Analytics (generate_analytics_data, get_seller_analytics)

## Fetch.ai Features Used

**Multi-Agent System**
- **Coordinator Agent**: Main orchestrator managing agent communication
- **Consultation Agent**: Personality analysis and preference extraction
- **Recommendation Agent**: AI-powered product matching algorithm
- **Analytics Agent**: User behavior tracking and market insights
- **Inventory Agent**: Stock monitoring and restock predictions

**Advanced Agent Features**
- Inter-agent communication protocol with message passing
- Agent discovery and dynamic service registration
- Blockchain integration via CosmPy for micropayments
- Event-driven architecture with pub/sub pattern
- Fault-tolerant communication with retry mechanisms

## Installation

**System Requirements**: Ubuntu 22.04+, 8GB RAM, 20GB storage

### Automated Setup

```bash
git clone https://github.com/YOUR_USERNAME/aromance.git
cd aromance
chmod +x install.sh
./install.sh
```

The installer will:
- Update system packages
- Install Node.js v20.x, Rust, Python 3.12
- Install DFX 0.24.3 with wasm32 target
- Create Python virtual environment with uAgents
- Install all project dependencies
- Build Rust workspace

### Verification

```bash
node -v        # v20.19.4+
npm -v         # 10.8.2+
rustc --version # Rust 2021
dfx --version   # 0.24.3
python3 -V      # Python 3.12+
```

## Development

### 1. Start ICP Network

```bash
dfx start --background --clean
```

### 2. Deploy Backend

```bash
dfx deploy aromance_backend
```

### 3. Start AI Agents

```bash
source fetchai_env/bin/activate
cd agents
python run_all_agents.py
```

### 4. Launch Frontend

```bash
cd src/aromance_frontend
npm start
```

**Access Points**
- Frontend: http://localhost:3000
- ICP Dashboard: http://localhost:4943  
- Backend Canister: http://localhost:4943/?canisterId=bkyz2-fmaaa-aaaaa-qaaaq-cai

## Testing

### Health Checks

```bash
# Test AI agents
curl http://localhost:8001/health  # Coordinator
curl http://localhost:8002/health  # Consultation
curl http://localhost:8003/health  # Recommendation

# Test ICP canister
dfx canister call aromance_backend greet '("Test")'
```

### User Journey Test

```bash
# Start consultation
curl -X POST http://localhost:8001/consultation/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_001", "session_id": "session_001"}'

# Generate recommendations  
curl -X POST http://localhost:8003/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_001",
    "fragrance_profile": {
      "personality_type": "professional",
      "preferred_families": ["woody", "citrus"]
    }
  }'
```

## Technical Difficulty

**Expert Level Features**
- Multi-agent coordination with 5 autonomous agents
- Real-time ICP-Agent synchronization via HTTP outcalls
- Advanced Rust memory management with stable storage
- Custom AI personality analysis pipeline

**Advanced Implementation**
- Inter-canister communication for modular design
- Agent discovery protocol with dynamic registration
- Blockchain micropayments between agents
- Certified query system for data integrity

## Challenges Faced

**Agent Network Connectivity**
Intermittent connection issues between agents required implementing local communication fallback mechanisms and offline development capabilities.

**ICP Memory Optimization**
Initial memory usage exceeded canister limits, requiring complete refactoring to use custom serialization with stable memory management.

**Real-time Synchronization**
Achieving consistency between AI agent decisions and ICP blockchain state required implementing event-driven architecture with HTTP outcalls.

**Critical Bug Fix**
```rust
// Fixed UserProfile schema
pub struct UserProfile {
    // ... other fields
    data_monetization_consent: bool, // REQUIRED field, not optional
}
```

## Future Plans

**Phase 1 (Q3 2025)**
- Deploy to ICP mainnet
- Mobile application development
- Enhanced ML models for better recommendations
- Social features and community building

**Phase 2 (Q4 2025)**  
- Multi-language support for regional expansion
- NFT integration for unique fragrance identities
- AR/VR virtual scent experiences
- Direct brand partnerships

**Phase 3 (2026)**
- Cross-chain support (Ethereum, Solana)
- AI Agent marketplace (Agents as a Service)
- Decentralized governance implementation
- Open-source olfactory psychology research

## Unique Value Proposition

Aromance is the first AI-powered perfume marketplace that combines decentralized identity management with specialized fragrance AI. Unlike general marketplaces, the platform understands fragrance complexity and provides personality-based recommendations while ensuring users maintain complete control over their personal data through blockchain technology.

**Key Differentiators**
- Specialized AI trained on fragrance notes and personality correlation
- Decentralized Identity giving users data ownership and monetization rights
- Economic incentive system through Proof of Stake verification
- Halal certification support for Indonesian Muslim market (85% population)

## Contributing

```bash
git clone https://github.com/YOUR_USERNAME/aromance.git
cd aromance
git checkout -b feature/your-feature
./install.sh
dfx start --background
source fetchai_env/bin/activate
```

All contributions must include tests and documentation updates. New AI agents require health check endpoint implementation.

## License

MIT License - see LICENSE file for details.

## Contact

- **Live Demo**: https://aromance-e56c8.web.app/
- **Proposal**: https://aromance-e56c8.web.app/Aromance-Resources.pdf
- **Email**: aromance@proton.me

Built for NextGen Agents Hackathon 2025

