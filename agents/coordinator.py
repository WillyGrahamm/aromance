from uagents import Agent, Context, Model, Protocol
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from dataclasses import dataclass
from uuid import uuid4

# FIXED: Import chat protocol correctly
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Enhanced Models for better integration
class UserJourney(Model):
    user_id: str
    session_id: str
    current_stage: str
    data: Dict[str, Any]
    next_action: str
    timestamp: int = None

class AgentResponse(Model):
    status: str
    message: str
    data: Dict[str, Any] = {}
    error: Optional[str] = None

class ConsultationStartRequest(Model):
    user_id: str

class ConsultationStartResponse(Model):
    success: bool
    session_id: str
    data: Dict[str, Any] = {}
    error: Optional[str] = None

class SystemHealthResponse(Model):
    status: str
    agents: Dict[str, Any]
    metrics: Dict[str, Any]
    icp_network: str
    timestamp: float

class ChatMessageLegacy(Model):
    message: str
    user_id: str

class ChatResponse(Model):
    reply: str
    success: bool

# FIXED: Agent configuration for ASI:One compatibility
coordinator_agent = Agent(
    name="aromance_system_coordinator",
    port=8000,
    seed="aromance_coordinator_real_agents_2025",
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Agent registry with REAL agent addresses - PASTIKAN INI SESUAI DENGAN AGENT ANDA
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
        "address": "agent1qvf6kv530le2glvp239rvjy6hyu3hz8jchp6y29yp2sg2nm0rwk4x9nttnd",
        "endpoint": "http://127.0.0.1:8005",
        "port": 8005,
        "status": "unknown"
    }
}

# Session storage for real agent communication
active_sessions = {}
pending_requests = {}  # Track requests waiting for agent responses
system_metrics = {
    "total_consultations": 0,
    "successful_recommendations": 0,
    "chat_interactions": 0,
    "agent_communications": 0,
    "failed_agent_calls": 0
}

# =============================================================================
# REAL AGENT COMMUNICATION MODELS
# =============================================================================

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

# =============================================================================
# CHAT PROTOCOL SETUP
# =============================================================================

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a text chat message for response"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=str(uuid4()),
        content=content,
    )

def get_aromance_welcome_message() -> str:
    """Welcome message for new chat sessions"""
    return """🌺 **Welcome to Aromance - Indonesian Fragrance AI Network!**

I'm connecting you to our specialized AI agents for the best fragrance experience:

🌸 **Consultation Agent** - Personal fragrance profiling  
🎯 **Recommendation Agent** - AI-powered suggestions
🛒 **Inventory Agent** - Real-time stock & purchasing
📊 **Analytics Agent** - Market insights & trends

Let me route your request to the right specialist! What can I help you with today? ✨"""

# Create chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# =============================================================================
# REAL AGENT COMMUNICATION HANDLERS
# =============================================================================

@chat_proto.on_message(ChatMessage)
async def handle_asi_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle ASI:One chat messages and route to real agents"""
    ctx.logger.info(f"🔵 ASI:One message from {sender}")
    
    # Store session
    session_key = f"session_{str(ctx.session)}"
    ctx.storage.set(session_key, sender)
    
    # Send acknowledgment
    try:
        ack = ChatAcknowledgement(
            timestamp=datetime.utcnow(), 
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)
        ctx.logger.info(f"✅ ACK sent to {sender}")
    except Exception as e:
        ctx.logger.error(f"❌ Failed ACK: {e}")
    
    # Process content
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🚀 Starting session with {sender}")
            welcome_msg = get_aromance_welcome_message()
            
            try:
                response = create_text_chat(welcome_msg)
                await ctx.send(sender, response)
            except Exception as e:
                ctx.logger.error(f"❌ Welcome send failed: {e}")
                
        elif isinstance(item, TextContent):
            ctx.logger.info(f"💬 Processing: '{item.text}'")
            system_metrics["chat_interactions"] += 1
            
            # Create user session for tracking
            user_id = f"asi_{sender}_{int(datetime.now().timestamp())}"
            request_id = str(uuid4())
            
            # Store pending request
            pending_requests[request_id] = {
                "sender": sender,
                "user_id": user_id,
                "message": item.text,
                "timestamp": datetime.now().timestamp(),
                "status": "processing"
            }
            
            try:
                # Route to appropriate REAL agent
                response_text = await route_to_real_agents(ctx, item.text, user_id, request_id, sender)
                
                # Send response
                response_msg = create_text_chat(response_text)
                await ctx.send(sender, response_msg)
                
                # Update request status
                if request_id in pending_requests:
                    pending_requests[request_id]["status"] = "completed"
                
            except Exception as e:
                ctx.logger.error(f"❌ Processing error: {e}")
                error_msg = create_text_chat(
                    f"I'm having trouble connecting to my specialist agents. Let me try a different approach... 🔄"
                )
                try:
                    await ctx.send(sender, error_msg)
                except:
                    pass
                
                # Mark request as failed
                if request_id in pending_requests:
                    pending_requests[request_id]["status"] = "failed"
                    
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"👋 Ending session with {sender}")
            goodbye_msg = "Thank you for using Aromance! Our agents are always here to help! 🌺"
            try:
                response = create_text_chat(goodbye_msg, end_session=True)
                await ctx.send(sender, response)
            except Exception as e:
                ctx.logger.error(f"❌ Goodbye failed: {e}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_asi_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements"""
    ctx.logger.info(f"✅ ACK from {sender} for {msg.acknowledged_msg_id}")

# =============================================================================
# REAL AGENT ROUTING AND COMMUNICATION
# =============================================================================

async def route_to_real_agents(ctx: Context, message: str, user_id: str, request_id: str, sender: str) -> str:
    """Route message to REAL specialized agents"""
    
    msg_lower = message.lower()
    ctx.logger.info(f"🎯 Routing '{message}' to real agents for user {user_id}")
    
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
    """Communicate with REAL consultation agent"""
    
    agent_info = AGENT_REGISTRY["consultation"]
    ctx.logger.info(f"📞 Calling consultation agent at {agent_info['address']}")
    
    try:
        # First try via uAgent messaging
        session_id = f"req_{request_id}"
        
        consultation_request = ConsultationRequest(
            user_id=user_id,
            session_id=session_id,
            message=message,
            preferences={"source": "asi_one", "language": "indonesian"}
        )
        
        # Send to real consultation agent
        system_metrics["agent_communications"] += 1
        
        try:
            await ctx.send(agent_info["address"], consultation_request)
            ctx.logger.info(f"✅ Sent request to consultation agent {agent_info['address']}")
            
            # Store session for tracking
            active_sessions[session_id] = {
                "user_id": user_id,
                "agent_type": "consultation",
                "request_id": request_id,
                "status": "pending_agent_response",
                "timestamp": datetime.now().timestamp()
            }
            
            return f"""🌸 **Connecting to Consultation Specialist...**

I've forwarded your request to our expert Consultation Agent who will analyze your fragrance preferences and lifestyle.

📋 **What our specialist will do:**
• Analyze your personality and lifestyle
• Map your scent preferences  
• Consider Indonesian climate factors
• Create your personal fragrance profile

⏰ **Processing your request...**
Our agent is working on your consultation right now!

*Session: {session_id}*
*Request ID: {request_id}*"""

        except Exception as messaging_error:
            ctx.logger.error(f"❌ uAgent messaging failed: {messaging_error}")
            
            # Fallback to HTTP if messaging fails
            return await fallback_http_consultation(ctx, agent_info, user_id, message, session_id)
            
    except Exception as e:
        ctx.logger.error(f"❌ Consultation agent communication failed: {e}")
        system_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["consultation"]["status"] = "error"
        
        return f"""⚠️ **Consultation Agent Temporarily Unavailable**

I'm having trouble connecting to our Consultation specialist. 

🔄 **Trying alternative approach:**
Let me help you directly with basic fragrance guidance while our specialist comes back online.

**Quick questions to get started:**
1. What's your daily activity level? (Active/Moderate/Calm)
2. Preferred scent strength? (Light/Medium/Strong)  
3. Favorite scents so far? (If any)

Our full consultation service will be restored shortly! 
*Error: {str(e)[:100]}*"""

async def fallback_http_consultation(ctx: Context, agent_info: Dict, user_id: str, message: str, session_id: str) -> str:
    """Fallback HTTP communication with consultation agent"""
    
    try:
        ctx.logger.info(f"🔄 Trying HTTP fallback to {agent_info['endpoint']}")
        
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "source": "asi_one_coordinator"
            }
            
            async with session.post(
                f"{agent_info['endpoint']}/consultation/start",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    ctx.logger.info(f"✅ HTTP consultation success")
                    
                    AGENT_REGISTRY["consultation"]["status"] = "healthy"
                    system_metrics["total_consultations"] += 1
                    
                    agent_response = result.get("response", {})
                    return f"""✅ **Consultation Agent Connected!**

{agent_response.get('message', 'Our specialist has received your request!')}

🎯 **Current Status:** {agent_response.get('status', 'Processing')}

{agent_response.get('next_steps', 'Please wait for detailed analysis...')}

*Session: {session_id}*
*Agent Response: HTTP Success*"""

                else:
                    ctx.logger.error(f"❌ HTTP consultation failed: {response.status}")
                    response_text = await response.text()
                    AGENT_REGISTRY["consultation"]["status"] = "error"
                    
                    return f"""❌ **Consultation Agent Error**

HTTP Error {response.status} when connecting to consultation specialist.

🔧 **Technical Details:**
• Agent: {agent_info['endpoint']}
• Status: {response.status}
• Error: {response_text[:100] if response_text else 'Unknown'}

Please try again or contact support if this persists."""
                    
    except asyncio.TimeoutError:
        ctx.logger.error("⏰ HTTP consultation timeout")
        AGENT_REGISTRY["consultation"]["status"] = "timeout"
        return f"""⏰ **Consultation Agent Timeout**

Our consultation specialist is taking longer than expected to respond.

This could be due to:
• High demand for consultation services
• Agent performing complex analysis  
• Network connectivity issues

Please try again in a few moments."""
        
    except Exception as http_error:
        ctx.logger.error(f"❌ HTTP consultation error: {http_error}")
        AGENT_REGISTRY["consultation"]["status"] = "error"
        return f"""❌ **Unable to Connect to Consultation Agent**

Technical error: {str(http_error)[:100]}

Our team has been notified and is working to restore the connection."""

async def communicate_with_recommendation_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with REAL recommendation agent"""
    
    agent_info = AGENT_REGISTRY["recommendation"]
    ctx.logger.info(f"📞 Calling recommendation agent at {agent_info['address']}")
    
    try:
        session_id = f"rec_{request_id}"
        
        # Check if user has existing consultation data
        user_sessions = [s for s in active_sessions.values() if s.get('user_id') == user_id]
        fragrance_profile = {}
        
        if user_sessions:
            fragrance_profile = user_sessions[0].get('data', {})
        
        recommendation_request = RecommendationRequest(
            user_id=user_id,
            session_id=session_id,
            fragrance_profile=fragrance_profile,
            budget_range="moderate"
        )
        
        system_metrics["agent_communications"] += 1
        
        try:
            await ctx.send(agent_info["address"], recommendation_request)
            ctx.logger.info(f"✅ Sent to recommendation agent {agent_info['address']}")
            
            active_sessions[session_id] = {
                "user_id": user_id,
                "agent_type": "recommendation", 
                "request_id": request_id,
                "status": "pending_agent_response"
            }
            
            return f"""🎯 **Connecting to Recommendation Specialist...**

I've sent your request to our AI Recommendation Agent who will:

🔍 **Analyze Your Profile:**
• Current fragrance preferences
• Lifestyle compatibility
• Indonesian climate factors
• Budget considerations

🌺 **Generate Personalized Suggestions:**
• Top 3-5 fragrance matches
• Indonesian brand prioritization  
• Price and availability info
• Match confidence scores

⚡ **Processing your recommendations...**

*Session: {session_id}*
*Request: {request_id}*"""

        except Exception as messaging_error:
            ctx.logger.error(f"❌ Recommendation messaging failed: {messaging_error}")
            return await fallback_http_recommendation(ctx, agent_info, user_id, message, session_id, fragrance_profile)
            
    except Exception as e:
        ctx.logger.error(f"❌ Recommendation agent error: {e}")
        system_metrics["failed_agent_calls"] += 1
        return f"""❌ **Recommendation Agent Unavailable**

Connection error: {str(e)[:100]}

🔄 **Trying backup recommendation system...**"""

async def fallback_http_recommendation(ctx: Context, agent_info: Dict, user_id: str, message: str, session_id: str, profile: Dict) -> str:
    """HTTP fallback for recommendation agent"""
    
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "fragrance_profile": profile,
                "message": message
            }
            
            async with session.post(
                f"{agent_info['endpoint']}/recommend",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    ctx.logger.info("✅ HTTP recommendation success")
                    
                    AGENT_REGISTRY["recommendation"]["status"] = "healthy"
                    system_metrics["successful_recommendations"] += 1
                    
                    recommendations = result.get("recommendations", [])
                    
                    if recommendations:
                        rec_text = "✅ **Recommendations from Specialist Agent:**\n\n"
                        
                        for i, rec in enumerate(recommendations[:3], 1):
                            rec_text += f"**{i}. {rec.get('name', 'Indonesian Fragrance')}**\n"
                            rec_text += f"• {rec.get('description', 'Premium Indonesian fragrance')}\n"
                            rec_text += f"• Price: IDR {rec.get('price', 0):,}\n"
                            rec_text += f"• Match Score: {rec.get('match_score', 0)*100:.0f}%\n"
                            rec_text += f"• Agent Notes: {rec.get('agent_notes', 'Recommended for you')}\n\n"
                        
                        rec_text += f"*Powered by Recommendation Agent*\n*Session: {session_id}*"
                        return rec_text
                    else:
                        return f"🔍 **Agent Analysis Complete**\n\nOur recommendation specialist has processed your request but needs more specific preferences to provide personalized suggestions.\n\n*Session: {session_id}*"
                else:
                    return f"❌ **Recommendation Agent Error {response.status}**\n\nPlease try again."
                    
    except Exception as e:
        return f"❌ **Recommendation Service Temporarily Down**\n\nError: {str(e)[:100]}"

async def communicate_with_inventory_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with REAL inventory agent"""
    
    agent_info = AGENT_REGISTRY["inventory"]
    ctx.logger.info(f"📞 Calling inventory agent at {agent_info['address']}")
    
    try:
        session_id = f"inv_{request_id}"
        
        inventory_request = InventoryRequest(
            user_id=user_id,
            action="check_availability",
            product_ids=[],
            filters={"region": "indonesia", "source": "asi_one"}
        )
        
        system_metrics["agent_communications"] += 1
        
        await ctx.send(agent_info["address"], inventory_request)
        ctx.logger.info(f"✅ Sent to inventory agent {agent_info['address']}")
        
        return f"""🛒 **Connecting to Inventory Specialist...**

I've contacted our Inventory Agent who will provide:

📦 **Real-Time Stock Information:**
• Current product availability
• Indonesian seller verification
• Price comparisons
• Shipping options

💳 **Secure Transaction Setup:**
• Escrow payment protection
• Buyer guarantees
• Authentic product verification

⏳ **Checking inventory systems...**

*Session: {session_id}*
*Agent: Inventory Specialist*"""

    except Exception as e:
        ctx.logger.error(f"❌ Inventory agent error: {e}")
        return f"""❌ **Inventory Agent Connection Failed**

Error: {str(e)[:100]}

🔄 **Backup inventory info available on request.**"""

async def communicate_with_analytics_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with REAL analytics agent"""
    
    agent_info = AGENT_REGISTRY["analytics"]
    ctx.logger.info(f"📞 Calling analytics agent at {agent_info['address']}")
    
    try:
        session_id = f"ana_{request_id}"
        
        analytics_request = AnalyticsRequest(
            user_id=user_id,
            event_type="dashboard_request",
            data={"message": message, "source": "asi_one", "timestamp": datetime.now().timestamp()}
        )
        
        system_metrics["agent_communications"] += 1
        
        await ctx.send(agent_info["address"], analytics_request)
        ctx.logger.info(f"✅ Sent to analytics agent {agent_info['address']}")
        
        return f"""📊 **Connecting to Analytics Specialist...**

I've requested data from our Analytics Agent who will provide:

📈 **Real-Time Market Data:**
• Indonesian fragrance trends
• Popular products and brands
• Regional preferences
• Price analysis

🎯 **System Performance:**
• Agent network status
• User engagement metrics
• Success rates

⚡ **Generating analytics report...**

*Session: {session_id}*
*Specialist: Analytics Agent*"""

    except Exception as e:
        ctx.logger.error(f"❌ Analytics agent error: {e}")
        return f"""❌ **Analytics Agent Unavailable**

Error: {str(e)[:100]}

📊 Basic metrics available on request."""

# =============================================================================
# RESPONSE HANDLERS FROM REAL AGENTS
# =============================================================================

@coordinator_agent.on_message(model=AgentResponse)
async def handle_agent_response(ctx: Context, sender: str, msg: AgentResponse):
    """Handle responses from real specialized agents"""
    ctx.logger.info(f"📥 Response from agent {sender}: {msg.status}")
    
    # Find pending request this response belongs to
    matching_requests = []
    for req_id, req_data in pending_requests.items():
        if req_data.get("status") == "processing":
            matching_requests.append((req_id, req_data))
    
    if matching_requests:
        req_id, req_data = matching_requests[0]  # Take first pending
        original_sender = req_data["sender"]
        
        try:
            # Format response from specialized agent
            response_text = f"""✅ **Response from {sender}:**

{msg.message}

**Agent Status:** {msg.status}
**Data:** {json.dumps(msg.data, indent=2) if msg.data else 'None'}

*Processed by specialized agent network*"""
            
            # Send back to original ASI:One user
            response_msg = create_text_chat(response_text)
            await ctx.send(original_sender, response_msg)
            
            # Mark request as completed
            pending_requests[req_id]["status"] = "completed"
            ctx.logger.info(f"✅ Forwarded agent response to {original_sender}")
            
        except Exception as e:
            ctx.logger.error(f"❌ Failed to forward agent response: {e}")
    
    else:
        ctx.logger.warning("⚠️ Received agent response with no matching pending request")

# =============================================================================
# SYSTEM HEALTH AND AGENT MONITORING
# =============================================================================

async def check_agent_health(ctx: Context):
    """Check health of all registered agents"""
    ctx.logger.info("🏥 Checking agent network health...")
    
    for agent_name, agent_info in AGENT_REGISTRY.items():
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{agent_info['endpoint']}/health") as response:
                    if response.status == 200:
                        AGENT_REGISTRY[agent_name]["status"] = "healthy"
                        ctx.logger.info(f"✅ {agent_name} agent: Healthy")
                    else:
                        AGENT_REGISTRY[agent_name]["status"] = f"error_{response.status}"
                        ctx.logger.error(f"❌ {agent_name} agent: HTTP {response.status}")
        except Exception as e:
            AGENT_REGISTRY[agent_name]["status"] = "unreachable"
            ctx.logger.error(f"❌ {agent_name} agent: {e}")
    
    healthy_count = sum(1 for agent in AGENT_REGISTRY.values() if agent["status"] == "healthy")
    total_count = len(AGENT_REGISTRY)
    
    ctx.logger.info(f"🏥 Agent Health: {healthy_count}/{total_count} agents healthy")

# =============================================================================
# REST ENDPOINTS
# =============================================================================

@coordinator_agent.on_rest_get("/api/system/health", SystemHealthResponse)
async def system_health_endpoint(ctx: Context) -> SystemHealthResponse:
    """System health including real agent status"""
    await check_agent_health(ctx)
    
    return SystemHealthResponse(
        status="healthy" if any(agent["status"] == "healthy" for agent in AGENT_REGISTRY.values()) else "degraded",
        agents=AGENT_REGISTRY,
        metrics=system_metrics,
        icp_network="local",
        timestamp=datetime.now().timestamp()
    )

@coordinator_agent.on_rest_post("/chat", ChatMessageLegacy, ChatResponse)
async def handle_legacy_chat(ctx: Context, req: ChatMessageLegacy) -> ChatResponse:
    """Legacy chat endpoint"""
    try:
        ctx.logger.info(f"📱 Legacy chat: {req.message}")
        
        request_id = str(uuid4())
        user_id = f"legacy_{req.user_id}"
        
        response = await route_to_real_agents(ctx, req.message, user_id, request_id, f"legacy_{req.user_id}")
        return ChatResponse(reply=response, success=True)
        
    except Exception as e:
        ctx.logger.error(f"❌ Legacy chat error: {e}")
        return ChatResponse(reply=f"System error: {str(e)[:100]}", success=False)

# =============================================================================
# PERIODIC MAINTENANCE
# =============================================================================

@coordinator_agent.on_interval(period=120.0)  # Every 2 minutes
async def periodic_agent_health_check(ctx: Context):
    """Regularly check agent health"""
    await check_agent_health(ctx)
    
    # Clean old pending requests (older than 5 minutes)
    current_time = datetime.now().timestamp()
    expired_requests = [
        req_id for req_id, req_data in pending_requests.items()
        if current_time - req_data["timestamp"] > 300
    ]
    
    for req_id in expired_requests:
        del pending_requests[req_id]
    
    if expired_requests:
        ctx.logger.info(f"🧹 Cleaned {len(expired_requests)} expired requests")
    
    # Log metrics
    ctx.logger.info(f"📊 Active sessions: {len(active_sessions)}")
    ctx.logger.info(f"⏳ Pending requests: {len(pending_requests)}")
    ctx.logger.info(f"🤝 Agent communications: {system_metrics['agent_communications']}")
    ctx.logger.info(f"❌ Failed agent calls: {system_metrics['failed_agent_calls']}")

# =============================================================================
# STARTUP AND PROTOCOL INCLUSION
# =============================================================================

coordinator_agent.include(chat_proto, publish_manifest=True)

@coordinator_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🚀 Aromance Real Agent Coordinator Started!")
    ctx.logger.info(f"📍 Coordinator Address: {coordinator_agent.address}")
    ctx.logger.info(f"🔗 Endpoint: http://127.0.0.1:8000")
    ctx.logger.info(f"🌐 Managing {len(AGENT_REGISTRY)} real specialized agents:")
    
    for agent_name, agent_info in AGENT_REGISTRY.items():
        ctx.logger.info(f"  • {agent_name}: {agent_info['address']} ({agent_info['endpoint']})")
    
    ctx.logger.info("✅ Ready for REAL agent communication via ASI:One! 🌺")
    
    # Initial health check
    await check_agent_health(ctx)
    
    # Set startup metrics
    system_metrics["startup_time"] = datetime.now().timestamp()
    system_metrics["coordinator_address"] = str(coordinator_agent.address)

if __name__ == "__main__":
    coordinator_agent.run()