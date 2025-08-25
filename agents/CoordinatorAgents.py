from uagents import Agent, Context, Model
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from uuid import uuid4


# MODELS FOR AGENT COMMUNICATION
class FrontendRequest(Model):
    user_id: str
    message: str
    request_type: str
    session_id: Optional[str] = None
    data: Dict[str, Any] = {}

class FrontendResponse(Model):
    success: bool
    message: str
    data: Dict[str, Any] = {}
    session_id: str
    request_id: str
    error: Optional[str] = None

class AgentResponse(Model):
    status: str
    message: str
    data: Dict[str, Any] = {}
    error: Optional[str] = None

class ConsultationRequest(Model):
    user_id: str
    session_id: str
    message: str
    preferences: Dict[str, Any] = {}

class RecommendationRequest(Model):
    user_id: str
    session_id: str
    fragrance_profile: Dict[str, Any]
    budget_range: Optional[str] = None

class InventoryRequest(Model):
    user_id: str
    action: str  # "check_availability", "get_products", etc.
    product_ids: List[str] = []
    filters: Dict[str, Any] = {}

class AnalyticsRequest(Model):
    user_id: str
    event_type: str
    data: Dict[str, Any]

class SystemHealthResponse(Model):
    status: str
    agents: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: float


# AGENT CONFIGURATION
coordinator_agent = Agent(
    name="aromance_agent_coordinator", 
    port=8000,
    seed="aromance_agent_coordinator_2025",
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Real agent registry - UPDATE THESE ADDRESSES WITH YOUR ACTUAL AGENT ADDRESSES
AGENT_REGISTRY = {
    "consultation": {
        "address": "agent1qte4mymlf2upe79qlrjreemhcmarjndp8mh756wtruql4m45euj9wz4auz2",
        "endpoint": "http://127.0.0.1:8001",
        "port": 8001,
        "status": "unknown"
    },
    "recommendation": {
        "address": "agent1qgkurunk708n00gdawx8u0a4qcwmtzzul09lyd372e7c5whjftrsc2xn85s",
        "endpoint": "http://127.0.0.1:8002",
        "port": 8002,
        "status": "unknown"
    },
    "analytics": {
        "address": "agent1q2g2zkhqujwu6v52jlstxyeuylu8p5tvc9fp27uwunhacrj6n90tcg4nwm3",
        "endpoint": "http://127.0.0.1:8004",
        "port": 8004,
        "status": "unknown"
    },
    "inventory": {
        "address": " agent1qvf6kv530le2glvp239rvjy6hyu3hz8jchp6y29yp2sg2nm0rwk4x9nttnd",
        "endpoint": "http://127.0.0.1:8005",
        "port": 8005,
        "status": "unknown"
    }
}

# Session tracking and metrics
active_agent_sessions = {}
pending_agent_requests = {}
agent_metrics = {
    "total_agent_requests": 0,
    "successful_agent_responses": 0,
    "failed_agent_calls": 0,
    "agent_communications": 0,
    "healthy_agents": 0
}


# CORE AGENT COMMUNICATION FUNCTIONS
async def route_to_agents(ctx: Context, message: str, user_id: str, request_id: str) -> str:
    """Route message to appropriate specialized agent"""
    
    msg_lower = message.lower()
    ctx.logger.info(f"🎯 Routing '{message}' to agents for user {user_id}")
    
    # Intent detection and routing
    if any(word in msg_lower for word in ["konsultasi", "consultation", "mulai", "start", "profil", "profile"]):
        return await communicate_with_consultation_agent(ctx, user_id, message, request_id)
        
    elif any(word in msg_lower for word in ["rekomendasi", "recommend", "saran", "parfum", "fragrance"]):
        return await communicate_with_recommendation_agent(ctx, user_id, message, request_id)
        
    elif any(word in msg_lower for word in ["beli", "buy", "stok", "stock", "purchase", "inventory"]):
        return await communicate_with_inventory_agent(ctx, user_id, message, request_id)
        
    elif any(word in msg_lower for word in ["analytics", "dashboard", "laporan", "data"]):
        return await communicate_with_analytics_agent(ctx, user_id, message, request_id)
        
    else:
        # For general questions, try consultation agent first
        return await communicate_with_consultation_agent(ctx, user_id, message, request_id)

async def communicate_with_consultation_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with consultation agent"""
    
    agent_info = AGENT_REGISTRY["consultation"]
    ctx.logger.info(f"📞 Calling consultation agent at {agent_info['address']}")
    
    try:
        session_id = f"consul_{request_id}"
        
        consultation_request = ConsultationRequest(
            user_id=user_id,
            session_id=session_id,
            message=message,
            preferences={"source": "coordinator", "language": "indonesian"}
        )
        
        agent_metrics["agent_communications"] += 1
        
        try:
            await ctx.send(agent_info["address"], consultation_request)
            ctx.logger.info(f"✅ Sent request to consultation agent")
            
            # Track session
            active_agent_sessions[session_id] = {
                "user_id": user_id,
                "agent_type": "consultation",
                "request_id": request_id,
                "status": "pending_response",
                "timestamp": datetime.now().timestamp()
            }
            
            AGENT_REGISTRY["consultation"]["status"] = "active"
            
            return f"""🌸 **Consultation Agent Processing...**

✅ Successfully connected to Consultation Specialist
📋 Request forwarded for fragrance profile analysis
🎯 Agent analyzing your preferences and lifestyle

**Session:** {session_id}
**Agent Status:** Connected
**Processing:** Consultation analysis in progress"""

        except Exception as messaging_error:
            ctx.logger.error(f"❌ uAgent messaging failed: {messaging_error}")
            return await fallback_http_consultation(ctx, agent_info, user_id, message, session_id)
            
    except Exception as e:
        ctx.logger.error(f"❌ Consultation agent communication failed: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["consultation"]["status"] = "error"
        
        return f"""⚠️ **Consultation Agent Error**

Connection failed: {str(e)[:100]}

**Status:** Agent temporarily unavailable
**Action:** Trying alternative connection methods
**Request ID:** {request_id}"""

async def fallback_http_consultation(ctx: Context, agent_info: Dict, user_id: str, message: str, session_id: str) -> str:
    """HTTP fallback for consultation agent"""
    
    try:
        ctx.logger.info(f"🔄 HTTP fallback to {agent_info['endpoint']}")
        
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "source": "agent_coordinator"
            }
            
            async with session.post(
                f"{agent_info['endpoint']}/consultation/start",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    ctx.logger.info(f"✅ HTTP consultation success")
                    
                    AGENT_REGISTRY["consultation"]["status"] = "healthy"
                    agent_metrics["successful_agent_responses"] += 1
                    
                    return f"""✅ **Consultation Agent Connected (HTTP)**

{result.get('message', 'Consultation request processed successfully')}

**Method:** HTTP Fallback
**Status:** {result.get('status', 'Processing')}
**Session:** {session_id}"""

                else:
                    AGENT_REGISTRY["consultation"]["status"] = "error"
                    return f"""❌ **Consultation Agent HTTP Error**

Status Code: {response.status}
**Session:** {session_id}
**Action Required:** Check agent availability"""
                    
    except Exception as e:
        AGENT_REGISTRY["consultation"]["status"] = "unreachable"
        return f"""❌ **Consultation Agent Unreachable**

HTTP Error: {str(e)[:100]}
**Status:** Connection failed
**Session:** {session_id}"""

async def communicate_with_recommendation_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with recommendation agent"""
    
    agent_info = AGENT_REGISTRY["recommendation"]
    ctx.logger.info(f"📞 Calling recommendation agent at {agent_info['address']}")
    
    try:
        session_id = f"rec_{request_id}"
        
        recommendation_request = RecommendationRequest(
            user_id=user_id,
            session_id=session_id,
            fragrance_profile={},
            budget_range="moderate"
        )
        
        agent_metrics["agent_communications"] += 1
        
        try:
            await ctx.send(agent_info["address"], recommendation_request)
            ctx.logger.info(f"✅ Sent to recommendation agent")
            
            active_agent_sessions[session_id] = {
                "user_id": user_id,
                "agent_type": "recommendation",
                "request_id": request_id,
                "status": "pending_response",
                "timestamp": datetime.now().timestamp()
            }
            
            AGENT_REGISTRY["recommendation"]["status"] = "active"
            
            return f"""🎯 **Recommendation Agent Processing...**

✅ Connected to Recommendation Specialist
🔍 Analyzing fragrance preferences
💡 Generating personalized suggestions

**Session:** {session_id}
**Agent Status:** Active
**Processing:** Recommendation analysis"""

        except Exception as messaging_error:
            ctx.logger.error(f"❌ Recommendation messaging failed: {messaging_error}")
            return await fallback_http_recommendation(ctx, agent_info, user_id, message, session_id)
            
    except Exception as e:
        ctx.logger.error(f"❌ Recommendation agent error: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["recommendation"]["status"] = "error"
        return f"""❌ **Recommendation Agent Error**

{str(e)[:100]}

**Session:** {session_id}
**Status:** Connection failed"""

async def fallback_http_recommendation(ctx: Context, agent_info: Dict, user_id: str, message: str, session_id: str) -> str:
    """HTTP fallback for recommendation agent"""
    
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "message": message
            }
            
            async with session.post(
                f"{agent_info['endpoint']}/recommend",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    AGENT_REGISTRY["recommendation"]["status"] = "healthy"
                    agent_metrics["successful_agent_responses"] += 1
                    
                    return f"""✅ **Recommendation Agent Connected (HTTP)**

{result.get('message', 'Recommendations generated successfully')}

**Method:** HTTP Fallback
**Session:** {session_id}"""
                else:
                    AGENT_REGISTRY["recommendation"]["status"] = "error"
                    return f"""❌ **Recommendation Agent HTTP Error {response.status}**

**Session:** {session_id}"""
                    
    except Exception as e:
        AGENT_REGISTRY["recommendation"]["status"] = "unreachable"
        return f"""❌ **Recommendation Agent Unreachable**

HTTP Error: {str(e)[:100]}
**Session:** {session_id}"""

async def communicate_with_inventory_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with inventory agent"""
    
    agent_info = AGENT_REGISTRY["inventory"]
    ctx.logger.info(f"📞 Calling inventory agent at {agent_info['address']}")
    
    try:
        session_id = f"inv_{request_id}"
        
        inventory_request = InventoryRequest(
            user_id=user_id,
            action="check_availability",
            product_ids=[],
            filters={"region": "indonesia"}
        )
        
        agent_metrics["agent_communications"] += 1
        
        await ctx.send(agent_info["address"], inventory_request)
        ctx.logger.info(f"✅ Sent to inventory agent")
        
        active_agent_sessions[session_id] = {
            "user_id": user_id,
            "agent_type": "inventory",
            "request_id": request_id,
            "status": "pending_response",
            "timestamp": datetime.now().timestamp()
        }
        
        AGENT_REGISTRY["inventory"]["status"] = "active"
        
        return f"""🛒 **Inventory Agent Processing...**

✅ Connected to Inventory Specialist
📦 Checking product availability
💳 Preparing transaction options

**Session:** {session_id}
**Agent Status:** Active"""

    except Exception as e:
        ctx.logger.error(f"❌ Inventory agent error: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["inventory"]["status"] = "error"
        return f"""❌ **Inventory Agent Error**

{str(e)[:100]}

**Session:** {session_id}"""

async def communicate_with_analytics_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with analytics agent"""
    
    agent_info = AGENT_REGISTRY["analytics"]
    ctx.logger.info(f"📞 Calling analytics agent at {agent_info['address']}")
    
    try:
        session_id = f"ana_{request_id}"
        
        analytics_request = AnalyticsRequest(
            user_id=user_id,
            event_type="data_request",
            data={"message": message, "timestamp": datetime.now().timestamp()}
        )
        
        agent_metrics["agent_communications"] += 1
        
        await ctx.send(agent_info["address"], analytics_request)
        ctx.logger.info(f"✅ Sent to analytics agent")
        
        active_agent_sessions[session_id] = {
            "user_id": user_id,
            "agent_type": "analytics",
            "request_id": request_id,
            "status": "pending_response",
            "timestamp": datetime.now().timestamp()
        }
        
        AGENT_REGISTRY["analytics"]["status"] = "active"
        
        return f"""📊 **Analytics Agent Processing...**

✅ Connected to Analytics Specialist
📈 Generating market insights
📋 Compiling performance data

**Session:** {session_id}
**Agent Status:** Active"""

    except Exception as e:
        ctx.logger.error(f"❌ Analytics agent error: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["analytics"]["status"] = "error"
        return f"""❌ **Analytics Agent Error**

{str(e)[:100]}

**Session:** {session_id}"""


# AGENT HEALTH MONITORING
async def check_agent_health(ctx: Context):
    """Check health of all registered agents"""
    ctx.logger.info("🏥 Checking agent network health...")
    
    healthy_count = 0
    for agent_name, agent_info in AGENT_REGISTRY.items():
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{agent_info['endpoint']}/health") as response:
                    if response.status == 200:
                        AGENT_REGISTRY[agent_name]["status"] = "healthy"
                        healthy_count += 1
                        ctx.logger.info(f"✅ {agent_name} agent: Healthy")
                    else:
                        AGENT_REGISTRY[agent_name]["status"] = f"error_{response.status}"
                        ctx.logger.error(f"❌ {agent_name} agent: HTTP {response.status}")
        except Exception as e:
            AGENT_REGISTRY[agent_name]["status"] = "unreachable"
            ctx.logger.error(f"❌ {agent_name} agent: {e}")
    
    agent_metrics["healthy_agents"] = healthy_count
    total_count = len(AGENT_REGISTRY)
    
    ctx.logger.info(f"🏥 Agent Health: {healthy_count}/{total_count} agents healthy")


# REQUEST HANDLERS FROM BRIDGE
@coordinator_agent.on_message(model=FrontendRequest)
async def handle_bridge_request(ctx: Context, sender: str, msg: FrontendRequest):
    """Handle requests from CoordinatorBridge.py"""
    ctx.logger.info(f"📨 Request from bridge: {sender}")
    
    request_id = msg.session_id or str(uuid4())
    agent_metrics["total_agent_requests"] += 1
    
    try:
        # Route to appropriate agent
        response_message = await route_to_agents(ctx, msg.message, msg.user_id, request_id)
        
        # Send response back to bridge
        response = FrontendResponse(
            success=True,
            message=response_message,
            data={"agent_routing": "completed", "timestamp": datetime.now().timestamp()},
            session_id=request_id,
            request_id=request_id,
            error=None
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Response sent to bridge")
        agent_metrics["successful_agent_responses"] += 1
        
    except Exception as e:
        ctx.logger.error(f"❌ Bridge request processing failed: {e}")
        
        # Send error response back to bridge
        error_response = FrontendResponse(
            success=False,
            message="Agent coordination system encountered an error",
            data={"error_details": str(e)[:200]},
            session_id=request_id,
            request_id=request_id,
            error=str(e)
        )
        
        try:
            await ctx.send(sender, error_response)
        except:
            ctx.logger.error("❌ Failed to send error response to bridge")
        
        agent_metrics["failed_agent_calls"] += 1


# AGENT RESPONSE HANDLERS
@coordinator_agent.on_message(model=AgentResponse)
async def handle_agent_response(ctx: Context, sender: str, msg: AgentResponse):
    """Handle responses from specialized agents"""
    ctx.logger.info(f"📥 Response from agent {sender}: {msg.status}")
    
    # Find matching session
    matching_session = None
    for session_id, session_data in active_agent_sessions.items():
        if session_data.get("status") == "pending_response":
            matching_session = (session_id, session_data)
            break
    
    if matching_session:
        session_id, session_data = matching_session
        
        # Update session
        active_agent_sessions[session_id]["status"] = "completed"
        active_agent_sessions[session_id]["agent_response"] = {
            "status": msg.status,
            "message": msg.message,
            "data": msg.data,
            "timestamp": datetime.now().timestamp()
        }
        
        ctx.logger.info(f"✅ Agent response stored for session {session_id}")
        agent_metrics["successful_agent_responses"] += 1
        
        # Note: The bridge will handle forwarding to end users
        
    else:
        ctx.logger.warning("⚠️ Received agent response with no matching session")


# REST ENDPOINTS
@coordinator_agent.on_rest_get("/api/health", SystemHealthResponse)
async def agent_system_health(ctx: Context) -> SystemHealthResponse:
    """System health focused on agent network"""
    await check_agent_health(ctx)
    
    return SystemHealthResponse(
        status="healthy" if agent_metrics["healthy_agents"] > 0 else "degraded",
        agents=AGENT_REGISTRY,
        metrics=agent_metrics,
        timestamp=datetime.now().timestamp()
    )


# MAINTENANCE
@coordinator_agent.on_interval(period=120.0)  # Every 2 minutes
async def periodic_agent_maintenance(ctx: Context):
    """Regular agent health checks and cleanup"""
    await check_agent_health(ctx)
    
    # Clean old sessions (older than 10 minutes)
    current_time = datetime.now().timestamp()
    expired_sessions = [
        session_id for session_id, session_data in active_agent_sessions.items()
        if current_time - session_data["timestamp"] > 600
    ]
    
    for session_id in expired_sessions:
        del active_agent_sessions[session_id]
    
    if expired_sessions:
        ctx.logger.info(f"🧹 Cleaned {len(expired_sessions)} expired agent sessions")
    
    # Log agent metrics
    ctx.logger.info(f"📊 Agent Metrics:")
    ctx.logger.info(f"  • Active sessions: {len(active_agent_sessions)}")
    ctx.logger.info(f"  • Total requests: {agent_metrics['total_agent_requests']}")
    ctx.logger.info(f"  • Successful responses: {agent_metrics['successful_agent_responses']}")
    ctx.logger.info(f"  • Failed calls: {agent_metrics['failed_agent_calls']}")
    ctx.logger.info(f"  • Healthy agents: {agent_metrics['healthy_agents']}/{len(AGENT_REGISTRY)}")


# STARTUP
@coordinator_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🤖 Aromance Agent Coordinator Started!")
    ctx.logger.info(f"📍 Coordinator Address: {coordinator_agent.address}")
    ctx.logger.info(f"🔗 Endpoint: http://127.0.0.1:8000")
    ctx.logger.info(f"🌐 Managing {len(AGENT_REGISTRY)} specialized agents:")
    
    for agent_name, agent_info in AGENT_REGISTRY.items():
        ctx.logger.info(f"  • {agent_name}: {agent_info['address']} ({agent_info['endpoint']})")
    
    ctx.logger.info("✅ Ready for agent coordination! 🌺")
    
    # Initial health check
    await check_agent_health(ctx)
    
    # Set startup metrics
    agent_metrics["startup_time"] = datetime.now().timestamp()
    agent_metrics["coordinator_address"] = str(coordinator_agent.address)

def update_agent_address(agent_name: str, address: str):
    """Helper function to update agent addresses"""
    if agent_name in AGENT_REGISTRY:
        AGENT_REGISTRY[agent_name]["address"] = address
        print(f"✅ {agent_name} agent address updated: {address}")
    else:
        print(f"❌ Agent {agent_name} not found in registry")

if __name__ == "__main__":
    print("🤖 Starting Aromance Agent Coordinator...")
    print(f"📍 Coordinator Address: {coordinator_agent.address}")
    print()
    print("🔧 Agent Registry:")
    for name, info in AGENT_REGISTRY.items():
        print(f"  • {name}: {info['address']} -> {info['endpoint']}")
    print()
    print("⚠️  Update agent addresses in AGENT_REGISTRY with your actual agent addresses!")
    
    coordinator_agent.run()