from uagents import Agent, Context, Model, Bureau
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from dataclasses import dataclass

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

class ICPRequest(Model):
    method: str
    params: Dict[str, Any]
    user_id: str

class ICPResponse(Model):
    success: bool
    result: Any = None
    error: Optional[str] = None

# Enhanced Coordinator Agent
coordinator_agent = Agent(
    name="aromance_system_coordinator",
    port=8000,
    seed="aromance_coordinator_enhanced_2025",
    endpoint=["http://127.0.0.1:8000/submit"],
    mailbox=True,
)

# Agent registry with real endpoints
AGENT_REGISTRY = {
    "consultation": {
        "address": "agent1qt6klnwfrlx7zr5rvghkdwkce7vvg7mzuqfgcllvxzxclpzlsf4g0a6fpu",
        "endpoint": "http://127.0.0.1:8001",
        "port": 8001
    },
    "recommendation": {
        "address": "agent1qvxe2usgz5fddqzuqhq8rlqrnxr8l9e8xhm9g5jfn9k4d7m6q7n2p9r8s7",
        "endpoint": "http://127.0.0.1:8002", 
        "port": 8002
    },
    "analytics": {
        "address": "agent1qw8r4t2y9u1i8o0p6a5s3d1f7g9h2j4k6l8m0n3b5v7c9x1z5q7w9e3r5t7",
        "endpoint": "http://127.0.0.1:8004",
        "port": 8004
    },
    "inventory": {
        "address": "agent1qz2x4c6v8b0n2m5k7j9h1f3d5s7a9p1o3i5u7y9t1r3e5w7q9e2r4t6y8u0",
        "endpoint": "http://127.0.0.1:8005",
        "port": 8005
    }
}

# ICP Configuration
ICP_CONFIG = {
    "local_endpoint": "http://127.0.0.1:4943",
    "mainnet_endpoint": "https://ic0.app",
    "canister_ids": {
        "backend": "bkyz2-fmaaa-aaaaa-qaaaq-cai",
        "frontend": "bd3sg-teaaa-aaaaa-qaaba-cai"
    },
    "current_network": "local"  # Switch to "mainnet" when deploying
}

# Session and metrics storage
active_sessions = {}
system_metrics = {
    "total_consultations": 0,
    "successful_recommendations": 0,
    "icp_sync_success": 0,
    "icp_sync_failures": 0,
    "avg_response_time": 0.0,
    "user_satisfaction": 0.85
}

@coordinator_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🎯 Aromance Enhanced System Coordinator Started")
    ctx.logger.info(f"Coordinator Address: {coordinator_agent.address}")
    ctx.logger.info(f"Managing {len(AGENT_REGISTRY)} specialized agents")
    ctx.logger.info(f"ICP Network: {ICP_CONFIG['current_network']}")
    ctx.logger.info("Ready for intelligent fragrance discovery with full ICP integration! 🌸")
    
    await perform_system_health_check(ctx)
    await test_icp_connectivity(ctx)

@coordinator_agent.on_message(model=UserJourney)
async def handle_user_journey(ctx: Context, sender: str, msg: UserJourney):
    """Enhanced user journey handling with real agent communication"""
    ctx.logger.info(f"🎭 User journey: {msg.user_id} at stage '{msg.current_stage}'")
    
    # Initialize or update session
    if msg.session_id not in active_sessions:
        active_sessions[msg.session_id] = {
            "user_id": msg.user_id,
            "current_stage": msg.current_stage,
            "data": msg.data,
            "last_updated": datetime.now().timestamp(),
            "agents_involved": [],
            "icp_sync_status": "pending"
        }
    else:
        active_sessions[msg.session_id].update({
            "current_stage": msg.current_stage,
            "data": {**active_sessions[msg.session_id]["data"], **msg.data},
            "last_updated": datetime.now().timestamp()
        })
    
    # Route to appropriate handler
    result = await orchestrate_user_flow(ctx, msg)
    
    # Send response back
    response = AgentResponse(
        status="success" if result else "error",
        message="Journey orchestrated successfully" if result else "Journey orchestration failed",
        data={"next_stage": msg.next_action}
    )
    
    await ctx.send(sender, response)

async def orchestrate_user_flow(ctx: Context, journey: UserJourney) -> bool:
    """Enhanced orchestration with real agent communication and ICP sync"""
    
    stage = journey.current_stage
    session = active_sessions[journey.session_id]
    
    try:
        if stage == "consultation_complete":
            ctx.logger.info(f"🔄 Routing to recommendation agent for {journey.user_id}")
            
            # Create DID in ICP backend first
            did_result = await sync_create_decentralized_identity(ctx, journey)
            if not did_result:
                ctx.logger.error("❌ Failed to create DID in ICP")
                return False
            
            # Send to recommendation agent
            recommendation_success = await route_to_recommendation_agent(ctx, journey)
            if recommendation_success:
                session["agents_involved"].append("recommendation")
                system_metrics["total_consultations"] += 1
            
            return recommendation_success
            
        elif stage == "recommendations_generated":
            ctx.logger.info(f"💾 Syncing recommendations to ICP backend")
            
            # Sync recommendations to ICP
            sync_success = await sync_recommendations_to_icp(ctx, journey)
            if sync_success:
                session["icp_sync_status"] = "success"
                system_metrics["icp_sync_success"] += 1
            else:
                session["icp_sync_status"] = "failed"
                system_metrics["icp_sync_failures"] += 1
            
            # Update analytics
            await route_to_analytics_agent(ctx, journey)
            session["agents_involved"].append("analytics")
            system_metrics["successful_recommendations"] += 1
            
            return sync_success
            
        elif stage == "purchase_initiated":
            ctx.logger.info(f"📦 Coordinating inventory and transaction")
            
            # Check inventory and create transaction
            inventory_success = await route_to_inventory_agent(ctx, journey)
            if inventory_success:
                transaction_success = await sync_create_transaction(ctx, journey)
                session["agents_involved"].append("inventory")
                return transaction_success
            
            return inventory_success
            
        else:
            ctx.logger.warning(f"⚠️ Unknown stage: {stage}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"❌ Orchestration error: {e}")
        return False

async def route_to_recommendation_agent(ctx: Context, journey: UserJourney) -> bool:
    """Route consultation results to recommendation agent"""
    try:
        agent_info = AGENT_REGISTRY["recommendation"]
        
        # Prepare recommendation request
        request_data = {
            "user_id": journey.user_id,
            "session_id": journey.session_id,
            "fragrance_profile": journey.data,
            "timestamp": datetime.now().timestamp()
        }
        
        # Send via HTTP to recommendation agent
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{agent_info['endpoint']}/recommend",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ctx.logger.info(f"✅ Recommendation request sent successfully")
                    return True
                else:
                    ctx.logger.error(f"❌ Recommendation agent error: {response.status}")
                    return False
                    
    except Exception as e:
        ctx.logger.error(f"❌ Failed to route to recommendation agent: {e}")
        return False

async def route_to_analytics_agent(ctx: Context, journey: UserJourney) -> bool:
    """Route data to analytics agent"""
    try:
        agent_info = AGENT_REGISTRY["analytics"]
        
        analytics_data = {
            "user_id": journey.user_id,
            "event_type": "recommendation_generated",
            "recommendations_count": len(journey.data.get("recommendations", [])),
            "personality_type": journey.data.get("profile", {}).get("personality_type"),
            "timestamp": datetime.now().timestamp()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{agent_info['endpoint']}/analytics",
                json=analytics_data,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                return response.status == 200
                
    except Exception as e:
        ctx.logger.error(f"❌ Analytics routing failed: {e}")
        return False

async def route_to_inventory_agent(ctx: Context, journey: UserJourney) -> bool:
    """Route to inventory agent for stock check"""
    try:
        agent_info = AGENT_REGISTRY["inventory"]
        
        inventory_request = {
            "user_id": journey.user_id,
            "product_ids": journey.data.get("selected_products", []),
            "action": "check_availability"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{agent_info['endpoint']}/inventory",
                json=inventory_request,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                return response.status == 200
                
    except Exception as e:
        ctx.logger.error(f"❌ Inventory routing failed: {e}")
        return False

# ICP Integration Functions
async def sync_create_decentralized_identity(ctx: Context, journey: UserJourney) -> bool:
    """Create decentralized identity in ICP canister"""
    try:
        fragrance_identity = {
            "personality_type": journey.data.get("personality_type", "Versatile Indonesian Character"),
            "lifestyle": journey.data.get("lifestyle", "balanced"),
            "preferred_families": journey.data.get("fragrance_families", ["fresh"]),
            "occasion_preferences": journey.data.get("occasions", ["daily"]),
            "season_preferences": ["tropical_year_round"],
            "sensitivity_level": journey.data.get("sensitivity", "normal"),
            "budget_range": journey.data.get("budget_range", "moderate"),
            "scent_journey": [{
                "date": datetime.now().timestamp(),
                "preference_change": "Initial consultation completed",
                "trigger_event": "AI consultation",
                "confidence_score": 0.85
            }]
        }
        
        icp_request = {
            "method": "create_decentralized_identity",
            "params": {
                "user_id": journey.user_id,
                "personality_data": fragrance_identity
            }
        }
        
        result = await call_icp_canister(ctx, icp_request)
        if result and result.get("success"):
            ctx.logger.info(f"✅ DID created for user {journey.user_id}")
            return True
        else:
            ctx.logger.error(f"❌ DID creation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"❌ DID creation error: {e}")
        return False

async def sync_recommendations_to_icp(ctx: Context, journey: UserJourney) -> bool:
    """Sync AI recommendations to ICP canister"""
    try:
        icp_request = {
            "method": "generate_ai_recommendations",
            "params": {
                "user_id": journey.user_id
            }
        }
        
        result = await call_icp_canister(ctx, icp_request)
        if result and result.get("success"):
            ctx.logger.info(f"✅ Recommendations synced for user {journey.user_id}")
            return True
        else:
            ctx.logger.error(f"❌ Recommendations sync failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"❌ Recommendations sync error: {e}")
        return False

async def sync_create_transaction(ctx: Context, journey: UserJourney) -> bool:
    """Create transaction in ICP canister"""
    try:
        transaction_data = {
            "transaction_id": f"txn_{journey.user_id}_{int(datetime.now().timestamp())}",
            "buyer_id": journey.user_id,
            "seller_id": journey.data.get("seller_id", "default_seller"),
            "product_id": journey.data.get("selected_products", [""])[0],
            "quantity": journey.data.get("quantity", 1),
            "unit_price_idr": journey.data.get("price", 100000),
            "total_amount_idr": journey.data.get("total_amount", 100000),
            "commission_rate": 0.02,
            "commission_amount": 0,
            "transaction_tier": "Standard",
            "status": "Pending",
            "escrow_locked": False,
            "payment_method": "bank_transfer",
            "shipping_address": journey.data.get("address", "Jakarta, Indonesia"),
            "created_at": int(datetime.now().timestamp()),
            "completed_at": None
        }
        
        icp_request = {
            "method": "create_transaction",
            "params": transaction_data
        }
        
        result = await call_icp_canister(ctx, icp_request)
        return result and result.get("success", False)
        
    except Exception as e:
        ctx.logger.error(f"❌ Transaction creation error: {e}")
        return False

async def call_icp_canister(ctx: Context, request: Dict[str, Any]) -> Dict[str, Any]:
    """Generic ICP canister call function"""
    try:
        endpoint = ICP_CONFIG["local_endpoint"] if ICP_CONFIG["current_network"] == "local" else ICP_CONFIG["mainnet_endpoint"]
        canister_id = ICP_CONFIG["canister_ids"]["backend"]
        
        # For local development, use DFX HTTP gateway
        if ICP_CONFIG["current_network"] == "local":
            dfx_url = f"{endpoint}/?canisterId={canister_id}"
        else:
            dfx_url = f"{endpoint}/api/v2/canister/{canister_id}/call"
        
        payload = {
            "type": "call",
            "method_name": request["method"],
            "args": request["params"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                dfx_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "result": result}
                else:
                    error_text = await response.text()
                    ctx.logger.error(f"❌ ICP call failed: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
    except Exception as e:
        ctx.logger.error(f"❌ ICP canister call error: {e}")
        return {"success": False, "error": str(e)}

async def test_icp_connectivity(ctx: Context):
    """Test ICP connectivity on startup"""
    try:
        test_request = {
            "method": "greet",
            "params": {"name": "System Test"}
        }
        
        result = await call_icp_canister(ctx, test_request)
        if result.get("success"):
            ctx.logger.info("✅ ICP connectivity test successful")
        else:
            ctx.logger.warning(f"⚠️ ICP connectivity issue: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        ctx.logger.error(f"❌ ICP connectivity test failed: {e}")

async def perform_system_health_check(ctx: Context):
    """Enhanced system health check"""
    ctx.logger.info("🏥 Performing enhanced system health check...")
    
    healthy_agents = []
    
    for agent_name, agent_info in AGENT_REGISTRY.items():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{agent_info['endpoint']}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        healthy_agents.append(agent_name)
                        ctx.logger.info(f"✅ {agent_name} agent: Healthy")
                    else:
                        ctx.logger.error(f"❌ {agent_name} agent: HTTP {response.status}")
        except Exception as e:
            ctx.logger.error(f"❌ {agent_name} agent: Unreachable - {e}")
    
    health_percentage = len(healthy_agents) / len(AGENT_REGISTRY) * 100
    ctx.logger.info(f"🏥 System Health: {len(healthy_agents)}/{len(AGENT_REGISTRY)} agents ({health_percentage:.1f}%)")

# HTTP Endpoints for Frontend Integration
@coordinator_agent.on_rest_post("/api/consultation/start")
async def start_consultation_endpoint(ctx: Context, req):
    """HTTP endpoint to start consultation process"""
    try:
        data = await req.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return {"error": "user_id is required"}, 400
        
        session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
        
        journey = UserJourney(
            user_id=user_id,
            session_id=session_id,
            current_stage="consultation_start",
            data={"started_at": datetime.now().timestamp()},
            next_action="begin_consultation"
        )
        
        # Route to consultation agent
        agent_info = AGENT_REGISTRY["consultation"]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{agent_info['endpoint']}/consultation/start",
                json={"user_id": user_id, "session_id": session_id}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "session_id": session_id, "data": result}
                else:
                    return {"error": "Consultation agent unavailable"}, 503
                    
    except Exception as e:
        ctx.logger.error(f"❌ Consultation start error: {e}")
        return {"error": "Internal server error"}, 500

@coordinator_agent.on_rest_get("/api/system/health")
async def system_health_endpoint(ctx: Context, req):
    """HTTP endpoint for system health"""
    try:
        await perform_system_health_check(ctx)
        
        return {
            "status": "healthy",
            "agents": AGENT_REGISTRY,
            "metrics": system_metrics,
            "icp_network": ICP_CONFIG["current_network"],
            "timestamp": datetime.now().timestamp()
        }
    except Exception as e:
        return {"error": str(e)}, 500

@coordinator_agent.on_rest_get("/api/system/metrics")
async def system_metrics_endpoint(ctx: Context, req):
    """HTTP endpoint for system metrics"""
    return {
        "metrics": system_metrics,
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().timestamp()
    }

@coordinator_agent.on_interval(period=300.0)  # Every 5 minutes
async def periodic_maintenance(ctx: Context):
    """Periodic system maintenance and monitoring"""
    
    # Health check
    await perform_system_health_check(ctx)
    
    # Clean expired sessions (older than 2 hours)
    current_time = datetime.now().timestamp()
    expired_sessions = [
        session_id for session_id, session in active_sessions.items()
        if current_time - session["last_updated"] > 7200  # 2 hours
    ]
    
    for session_id in expired_sessions:
        del active_sessions[session_id]
    
    if expired_sessions:
        ctx.logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    # Log system metrics
    ctx.logger.info(f"📊 Active sessions: {len(active_sessions)}")
    ctx.logger.info(f"📈 Total consultations: {system_metrics['total_consultations']}")
    ctx.logger.info(f"💾 ICP sync success rate: {system_metrics['icp_sync_success']}/{system_metrics['icp_sync_success'] + system_metrics['icp_sync_failures']}")

if __name__ == "__main__":
    coordinator_agent.run()