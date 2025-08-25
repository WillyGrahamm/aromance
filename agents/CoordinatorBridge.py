from uagents import Agent, Context, Model, Protocol
from typing import Dict, Any, List, Optional
import json
import asyncio
import logging
import httpx
from datetime import datetime
from uuid import uuid4
from typing import Tuple

# Import chat protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# SHARED MODELS (MUST MATCH COORDINATOR AGENT)
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

class ChatRequest(Model):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponseAPI(Model):
    success: bool
    reply: str
    session_id: str
    request_id: str

class HealthResponse(Model):
    status: str
    coordinator_connected: bool
    ic_backend_connected: bool
    active_sessions: int
    timestamp: float

class MetricsResponse(Model):
    bridge_metrics: Dict[str, Any]
    coordinator_status: str
    ic_backend_status: str
    active_sessions: int
    pending_requests: int
    endpoints: List[str]

class AIRecommendation(Model):
    recommendation_id: str
    user_id: str
    product_id: str
    match_score: float
    personality_alignment: float
    lifestyle_fit: float
    occasion_match: float
    budget_compatibility: float
    reasoning: str
    confidence_level: float
    seasonal_relevance: float
    trend_factor: float
    generated_at: int
    user_feedback: Optional[float] = None

class Transaction(Model):
    transaction_id: str
    buyer_id: str
    seller_id: str
    product_id: str
    quantity: int
    unit_price_idr: int
    total_amount_idr: int
    commission_rate: float
    commission_amount: int
    transaction_tier: Dict[str, None]
    status: Dict[str, None]
    escrow_locked: bool
    payment_method: str
    shipping_address: str
    created_at: int
    completed_at: Optional[int] = None

class VerifiedReview(Model):
    review_id: str
    reviewer_id: str
    reviewer_stake: int
    reviewer_tier: Dict[str, None]
    product_id: str
    overall_rating: int
    longevity_rating: int
    sillage_rating: int
    projection_rating: int
    versatility_rating: int
    value_rating: int
    detailed_review: str
    verified_purchase: bool
    skin_type: str
    age_group: str
    wear_occasion: str
    season_tested: str
    helpful_votes: int
    reported_count: int
    ai_validated: bool
    review_date: int
    last_updated: int

# IC BACKEND MODELS (Aligned with lib.rs)
class ICUserProfile(Model):
    user_id: str
    wallet_address: Optional[str] = None
    did: Optional[str] = None
    verification_status: Dict[str, None] = {"Unverified": None}
    stake_info: Optional[Dict[str, Any]] = None
    preferences: List[Tuple[str, str]] = []
    consultation_completed: bool = False
    ai_consent: bool = False
    data_monetization_consent: bool = False
    reputation_score: float = 1.0
    total_transactions: int = 0
    created_at: int = 0
    last_active: int = 0

class ICProduct(Model):
    id: str
    seller_id: str
    seller_verification: Dict[str, None] = {"Unverified": None}
    name: str
    brand: str
    price_idr: int
    fragrance_family: str
    top_notes: List[str] = []
    middle_notes: List[str] = []
    base_notes: List[str] = []
    occasion: List[str] = []
    season: List[str] = []
    longevity: Dict[str, None] = {"Moderate": None}
    sillage: Dict[str, None] = {"Moderate": None}
    projection: Dict[str, None] = {"Moderate": None}
    versatility_score: float = 0.0
    description: str = ""
    ingredients: List[str] = []
    halal_certified: bool = False
    image_urls: List[str] = []
    stock: int = 0
    verified: bool = False
    ai_analyzed: bool = False
    personality_matches: List[str] = []
    created_at: int = 0
    updated_at: int = 0

class ICBackendRequest(Model):
    method: str
    data: Dict[str, Any]
    user_id: str
    request_id: str

class ICProductsResponse(Model):
    success: bool
    products: List[Dict[str, Any]]
    count: int
    source: str

class ICRecommendationsRequest(Model):
    user_id: Optional[str] = "anonymous"

class ICRecommendationsResponse(Model):
    success: bool
    recommendations: List[Dict[str, Any]]
    count: int
    user_id: str
    source: str

class ICUserCreateRequest(Model): # /api/ic/user/create
    user_data: Dict[str, Any]

class ICUserCreateResponse(Model):
    success: bool
    user_id: str
    message: str
    source: str

class ICProductSearchRequest(Model):
    search_params: Dict[str, Any]
    user_id: Optional[str] = "anonymous"

class ICProductSearchResponse(Model):
    success: bool
    product: List[Dict[str, Any]]
    count: int
    search_param: Dict[str, Any]
    source: str

class ICStatusResponse(Model):
    ic_backend: Dict[str, Any]
    connection_test: Dict[str, Any]
    cache_stats: Dict[str, Any]
    bridge_metrics: Dict[str, Any]

class ICStakeRequest(Model):
    user_id: str
    amount: int
    tier: Optional[str] = "BasicReviewer"

class ICStakeResponse(Model):
    success: bool
    result: Dict[str, Any]
    userId: str
    amount: int
    tier: str
    source: str

class ICHalalProductsResponse(Model):
    success: bool
    halalProducts: List[Dict[str, Any]]
    count: int
    source: str

# FRONTEND INTEGRATION CLASSES
class ICTransactionsGetRequest(Model):
    user_id: str

class ICTransactionsResponse(Model):
    success: bool
    transactions: List[Dict[str, Any]]
    count: int

class ICTransactionCreateRequest(Model):
    transaction: Dict[str, Any]

class ICTransactionCreateResponse(Model):
    success: bool
    transaction_id: str
    error: Optional[str]

class ICIdentityCreateRequest(Model):
    user_id: str
    fragrance_identity: Dict[str, Any]

class ICIdentityCreateResponse(Model):
    success: bool
    identity: Optional[Dict[str, Any]]
    error: Optional[str]

class ICReviewsGetRequest(Model):
    product_id: str

class ICReviewsResponse(Model):
    success: bool
    reviews: List[Dict[str, Any]]
    count: int

class ICReviewCreateRequest(Model):
    review: Dict[str, Any]

class ICReviewCreateResponse(Model):
    success: bool
    review_id: str
    error: Optional[str]

class ICPlatformStatsResponse(Model):
    total_users: int
    verified_users: int
    total_products: int
    verified_products: int
    total_transactions: int
    total_gmv_idr: int
    total_reviews: int
    total_staked_idr: int

# Create chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# FRONTEND BRIDGE COORDINATOR
frontend_coordinator = Agent(
    name="aromance_frontend_bridge_enhanced",
    port=8080,
    seed="aromance_frontend_bridge_enhanced_2025",
    endpoint=["http://127.0.0.1:8080/submit"],
)

# COORDINATOR AGENT CONNECTION
COORDINATOR_AGENT = {
    "address": "agent1q0c3gfhhufskvm0tfssj05y6exkfwckea9400sr2luj6l98da8n8ykxssyd",
    "endpoint": "http://127.0.0.1:8000",
    "status": "unknown",
    "name": "aromance_agent_coordinator"
}

# IC BACKEND CONNECTION - FIXED CONFIGURATION
IC_BACKEND = {
    "canister_url": None,
    "canister_id": None,
    "status": "not_configured",
    "name": "aromance_ic_backend",
    "environment": "local"
}

# Session management
frontend_sessions = {}
pending_frontend_requests = {}
ic_backend_cache = {}

# Enhanced Bridge metrics
bridge_metrics = {
    "frontend_requests": 0,
    "backend_requests": 0,
    "coordinator_forwards": 0,
    "ic_backend_calls": 0,
    "successful_responses": 0,
    "failed_requests": 0,
    "active_sessions": 0,
    "cache_hits": 0,
    "cache_misses": 0
}

# FOR IC BACKEND INTEGRATION (When the returned value is not JSON)
async def json_to_candid(data: Any) -> str:
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, (int, float)):
        return str(data)
    if isinstance(data, str):
        return f'"{data}"'
    if isinstance(data, list):
        items = '; '.join(json_to_candid(item) for item in data)
        return f"vec {{ {items} }}"
    if isinstance(data, dict):
        items = '; '.join(f'"{k}" = {json_to_candid(v)}' for k, v in data.items())
        return f"record {{ {items} }}"
    raise ValueError(f"Unsupported type for Candid: {type(data)}")

async def parse_candid_text(output: str) -> Any:
    output = output.strip()
    if output.startswith('(') and output.endswith(')'):
        content = output[1:-1].strip()
    else:
        content = output
    if content.startswith('record {'):
        content = content[8:-1].strip()
        items = [item.strip() for item in content.split(';') if item.strip()]
        result = {}
        for item in items:
            parts = item.split(' = ')
            if len(parts) == 2:
                key = parts[0].strip().strip('"')
                value_str = parts[1].strip()
                if ' : ' in value_str:
                    val, typ = value_str.split(' : ')
                    val = val.strip()
                    typ = typ.strip()
                else:
                    val = value_str
                    typ = "unknown"
                if typ in ["nat64", "nat32", "nat", "int64", "int32", "int"]:
                    result[key] = int(val)
                elif typ in ["float64", "float32"]:
                    result[key] = float(val)
                elif typ == "text":
                    result[key] = val.strip('"')
                elif typ == "bool":
                    result[key] = val == "true"
                else:
                    result[key] = val
        return result
    elif content.startswith('vec {'):
        # Simple vec parser for lists
        content = content[5:-1].strip()
        items = [parse_candid_text(item) for item in content.split(';') if item.strip()]
        return items
    elif content.startswith('"') and content.endswith('"'):
        return content.strip('"')
    elif content in ["true", "false"]:
        return content == "true"
    try:
        return int(content)
    except ValueError:
        try:
            return float(content)
        except ValueError:
            return content

method_arg_format = {
    "greet": lambda d: f'("{d["name"]}")',
    "get_platform_statistics": lambda d: '()',
    "get_user_profile": lambda d: f'("{d["user_id"]}")',
    "create_user_profile": lambda d: f'({json_to_candid(d["profile"])})',
    "get_products": lambda d: '()',
    "generate_ai_recommendations": lambda d: f'("{d["user_id"]}")',
    "search_products_advanced": lambda d: f'({json_to_candid(d.get("fragrance_family"))}, {json_to_candid(d.get("budget_min"))}, {json_to_candid(d.get("budget_max"))}, {json_to_candid(d.get("occasion"))}, {json_to_candid(d.get("season"))}, {json_to_candid(d.get("longevity"))}, {json_to_candid(d.get("verified_only"))})',
    "get_halal_products": lambda d: '()',
    "stake_for_verification": lambda d: f'("{d["user_id"]}", {d["amount"]}, {json_to_candid(d["tier"])})',
    "add_product": lambda d: f'({json_to_candid({**d, "verified": d.get("verified", True)})})',
}

# IC BACKEND INTEGRATION
async def call_ic_backend(ctx: Context, method: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    bridge_metrics["ic_backend_calls"] += 1
    try:
        cache_key = f"{method}_{json.dumps(data, sort_keys=True)}_{user_id}"
        if method.startswith("get_") and cache_key in ic_backend_cache:
            cache_entry = ic_backend_cache[cache_key]
            if datetime.now().timestamp() - cache_entry["timestamp"] < 300:
                bridge_metrics["cache_hits"] += 1
                ctx.logger.info(f"🎯 IC Backend cache hit for {method}")
                return cache_entry["data"]
        bridge_metrics["cache_misses"] += 1
        if IC_BACKEND["environment"] == "local":
            if not IC_BACKEND["canister_id"]:
                ctx.logger.warning("⚠️ IC Backend not configured - skipping call")
                return {"error": "IC Backend not configured", "simulated": True}
            candid_arg = method_arg_format.get(method, lambda d: '()' if not d else f'({json_to_candid(d)})') (data)
            cmd = ['dfx', 'canister', 'call', IC_BACKEND["canister_id"], method, candid_arg]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                output = stdout.decode().strip()
                result = parse_candid_text(output)
                ctx.logger.info(f"✅ IC Backend dfx call successful: {method}")
                IC_BACKEND["status"] = "connected"
                if method.startswith("get_"):
                    ic_backend_cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now().timestamp()
                    }
                
                # Handle variant responses
                if isinstance(result, dict) and 'Ok' in result:
                    return result['Ok']
                elif isinstance(result, dict) and 'Err' in result:
                    return {"error": result['Err']}
                return result if isinstance(result, dict) else {"result": result}
            else:
                error = stderr.decode().strip()
                ctx.logger.error(f"❌ IC Backend dfx error: {proc.returncode} - {error}")
                IC_BACKEND["status"] = "error"
                return {"error": f"IC Backend dfx error: {proc.returncode}", "details": error}
        else:
            # Mainnet implementation using HTTP client
            async with httpx.AsyncClient() as client:
                url = f"{IC_BACKEND['canister_url']}/{method}"
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    IC_BACKEND["status"] = "connected"
                    if method.startswith("get_"):
                        ic_backend_cache[cache_key] = {
                            "data": result,
                            "timestamp": datetime.now().timestamp()
                        }
                    return result
                else:
                    IC_BACKEND["status"] = "error"
                    return {"error": f"Mainnet call failed: {response.status_code}"}
    except Exception as e:
        ctx.logger.error(f"❌ IC Backend call failed: {method} - {e}")
        IC_BACKEND["status"] = "disconnected"
        return {"error": f"IC Backend connection failed: {str(e)}"}

# MOCK IC BACKEND FOR DEVELOPMENT (when not configured)
async def mock_ic_backend_call(ctx: Context, method: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Mock IC backend responses for development when canister is not available"""
    ctx.logger.info(f"🔧 Mock IC Backend call: {method}")
    
    # Simulate different responses based on method
    if method == "greet":
        return {"message": f"Hello {data.get('name', 'User')} from Mock IC Backend!"}
    
    elif method == "get_products":
        return {
            "products": [
                {
                    "id": "mock_product_1",
                    "name": "Mock Fragrance 1",
                    "brand": "Mock Brand",
                    "price_idr": 150000,
                    "fragrance_family": "Fresh",
                    "halal_certified": True,
                    "stock": 10
                },
                {
                    "id": "mock_product_2", 
                    "name": "Mock Fragrance 2",
                    "brand": "Mock Brand Premium",
                    "price_idr": 350000,
                    "fragrance_family": "Oriental",
                    "halal_certified": True,
                    "stock": 5
                }
            ]
        }
    
    elif method == "generate_ai_recommendations":
        return {
            "recommendations": [
                {
                    "product_id": "mock_rec_1",
                    "name": "Recommended Mock Fragrance",
                    "match_score": 0.95,
                    "reason": "Perfect match for your preferences"
                }
            ]
        }
    
    elif method == "get_user_profile":
        return {
            "user_id": user_id,
            "verification_status": "Unverified",
            "reputation_score": 1.0,
            "preferences": {}
        }
    
    elif method == "create_user_profile":
        return {
            "success": True,
            "user_id": user_id,
            "message": "Mock user created"
        }
    
    elif method == "get_platform_statistics":
        return {
            "total_users": 100,
            "total_products": 50,
            "total_transactions": 25,
            "mock": True
        }
    
    else:
        return {"success": True, "mock": True, "method": method, "data": data}

async def ensure_user_exists_in_ic(ctx: Context, user_id: str) -> bool:
    """Ensure user profile exists in IC backend"""
    try:
        # Check if IC backend is configured
        if not IC_BACKEND["canister_id"]:
            ctx.logger.info(f"👤 Mock user creation for {user_id}")
            return True
        
        # Check if user exists
        result = await call_ic_backend(ctx, "get_user_profile", {"user_id": user_id}, user_id)
        
        if "error" in result or not result:
            # Create user profile
            profile_data = {
                "user_id": user_id,
                "wallet_address": None,
                "did": None,
                "verification_status": "Unverified",
                "preferences": {},
                "consultation_completed": False,
                "ai_consent": True, 
                "data_monetization_consent": False,
                "reputation_score": 1.0,
                "total_transactions": 0,
                "created_at": int(datetime.now().timestamp() * 1_000_000_000),
                "last_active": int(datetime.now().timestamp() * 1_000_000_000)
            }
            
            create_result = await call_ic_backend(ctx, "create_user_profile", {"profile": profile_data}, user_id)
            ctx.logger.info(f"👤 Created IC user profile: {user_id}")
            return "error" not in create_result
        else:
            ctx.logger.info(f"👤 IC user profile exists: {user_id}")
            return True
            
    except Exception as e:
        ctx.logger.error(f"❌ User creation in IC failed: {e}")
        return False

async def get_user_products_from_ic(ctx: Context, user_id: str) -> List[Dict[str, Any]]:
    """Get user's products from IC backend"""
    try:
        if not IC_BACKEND["canister_id"]:
            return await mock_ic_backend_call(ctx, "get_products", {}, user_id)
            
        result = await call_ic_backend(ctx, "get_products", {}, user_id)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "products" in result:
            return result["products"]
        else:
            return []
            
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get products from IC: {e}")
        return []

async def search_products_in_ic(ctx: Context, search_params: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
    """Search products in IC backend"""
    try:
        if not IC_BACKEND["canister_id"]:
            mock_result = await mock_ic_backend_call(ctx, "get_products", {}, user_id)
            return mock_result.get("products", [])
            
        result = await call_ic_backend(ctx, "search_products_advanced", search_params, user_id)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "products" in result:
            return result["products"]
        else:
            return []
            
    except Exception as e:
        ctx.logger.error(f"❌ Failed to search products in IC: {e}")
        return []

async def get_user_recommendations_from_ic(ctx: Context, user_id: str) -> List[Dict[str, Any]]:
    """Get AI recommendations from IC backend"""
    try:
        if not IC_BACKEND["canister_id"]:
            mock_result = await mock_ic_backend_call(ctx, "generate_ai_recommendations", {"user_id": user_id}, user_id)
            return mock_result.get("recommendations", [])
            
        # First ensure user exists
        await ensure_user_exists_in_ic(ctx, user_id)
        
        # Generate or get recommendations
        result = await call_ic_backend(ctx, "generate_ai_recommendations", {"user_id": user_id}, user_id)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "recommendations" in result:
            return result["recommendations"]
        else:
            # Fallback to getting existing recommendations
            existing = await call_ic_backend(ctx, "get_recommendations_for_user", {"user_id": user_id}, user_id)
            return existing if isinstance(existing, list) else []
            
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get recommendations from IC: {e}")
        return []


# CHAT PROTOCOL FOR ASI:ONE
def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create ASI:One chat message"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=str(uuid4()),
        content=content,
    )

def get_frontend_welcome_message() -> str:
    """Enhanced welcome message with IC backend integration status"""
    ic_status = "✅ Connected" if IC_BACKEND["status"] == "connected" else ("⚙️ Mock Mode" if IC_BACKEND["status"] == "not_configured" else "❌ Error")
    
    return f"""🌺 **Welcome to Aromance - Indonesian Fragrance AI**

I'm your enhanced frontend bridge connecting you to our complete ecosystem!

🚀 **Available Services:**
• 💬 **Chat** - Natural conversation with AI agents
• 🌸 **Consultation** - Personal fragrance profiling  
• 🎯 **Recommendations** - AI-powered suggestions from IC backend
• 🛍️ **Inventory** - Product search & availability via IC canister
• 📊 **Analytics** - Market insights & user analytics
• 🔐 **Web3 Identity** - Decentralized identity management

**Connected Systems:**
✅ Agent Coordinator → Specialist Agent Network
{ic_status} IC Backend Canister → Decentralized Data Storage
✅ AI Recommendation Engine → Smart Matching

How can I assist you today? ✨"""

# ASI:ONE CHAT HANDLERS WITH IC INTEGRATION
@chat_proto.on_message(ChatMessage)
async def handle_frontend_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle ASI:One chat messages with IC backend integration"""
    ctx.logger.info(f"💬 Frontend message from {sender}")
    
    # Send acknowledgment
    try:
        ack = ChatAcknowledgement(
            timestamp=datetime.utcnow(), 
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)
    except Exception as e:
        ctx.logger.error(f"❌ ACK failed: {e}")
    
    # Process content
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🚀 Starting enhanced session with {sender}")
            welcome_msg = get_frontend_welcome_message()
            
            # Create session with IC backend integration
            session_id = f"frontend_{str(uuid4())}"
            user_id = f"frontend_{sender}"
            
            # Ensure user exists in IC backend
            ic_user_created = await ensure_user_exists_in_ic(ctx, user_id)
            
            frontend_sessions[session_id] = {
                "sender": sender,
                "user_id": user_id,
                "start_time": datetime.now().timestamp(),
                "status": "active",
                "ic_backend_integrated": ic_user_created
            }
            bridge_metrics["active_sessions"] += 1
            
            try:
                response = create_text_chat(welcome_msg)
                await ctx.send(sender, response)
            except Exception as e:
                ctx.logger.error(f"❌ Welcome failed: {e}")
                
        elif isinstance(item, TextContent):
            ctx.logger.info(f"💭 Processing with IC integration: '{item.text}'")
            bridge_metrics["frontend_requests"] += 1
            
            request_id = str(uuid4())
            user_id = f"frontend_{sender}"
            
            # Store pending request
            pending_frontend_requests[request_id] = {
                "sender": sender,
                "user_id": user_id,
                "message": item.text,
                "timestamp": datetime.now().timestamp(),
                "status": "processing_with_ic_backend"
            }
            
            try:
                # Enhanced processing with IC backend integration
                response_text = await process_message_with_ic_backend(ctx, item.text, user_id, request_id)
                response_msg = create_text_chat(response_text)
                await ctx.send(sender, response_msg)
                
                if request_id in pending_frontend_requests:
                    pending_frontend_requests[request_id]["status"] = "completed"
                bridge_metrics["successful_responses"] += 1
                
            except Exception as e:
                ctx.logger.error(f"❌ Processing error: {e}")
                error_msg = create_text_chat(
                    f"I'm having trouble connecting to our systems (Agent Coordinator + IC Backend). Please try again shortly... 🔄"
                )
                try:
                    await ctx.send(sender, error_msg)
                except:
                    pass
                
                if request_id in pending_frontend_requests:
                    pending_frontend_requests[request_id]["status"] = "failed"
                bridge_metrics["failed_requests"] += 1
                    
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"👋 Ending enhanced session with {sender}")
            
            # Clean up sessions
            sessions_to_remove = [sid for sid, sdata in frontend_sessions.items() if sdata["sender"] == sender]
            for sid in sessions_to_remove:
                del frontend_sessions[sid]
                bridge_metrics["active_sessions"] = max(0, bridge_metrics["active_sessions"] - 1)
            
            goodbye_msg = "Thank you for using Aromance! Our AI agents and IC backend are always ready to help! 🌺"
            try:
                response = create_text_chat(goodbye_msg, end_session=True)
                await ctx.send(sender, response)
            except Exception as e:
                ctx.logger.error(f"❌ Goodbye failed: {e}")


# ENHANCED MESSAGE PROCESSING WITH IC BACKEND
async def process_message_with_ic_backend(ctx: Context, message: str, user_id: str, request_id: str) -> str:
    """Process message with both Agent Coordinator and IC Backend integration"""
    
    message_lower = message.lower()
    
    # Determine if this needs IC backend data
    needs_ic_data = any(keyword in message_lower for keyword in [
        "product", "fragrance", "perfume", "recommendation", "search", 
        "buy", "purchase", "inventory", "stock", "brand", "price", "consultation", "identity"
    ])
    
    if needs_ic_data:
        ctx.logger.info(f"🔗 Processing with IC Backend integration")
        
        try:
            # Get user data from IC if needed
            user_products = []
            recommendations = []
            consultation_response = None
            
            if any(word in message_lower for word in ["recommend", "suggest", "match"]):
                recommendations = await get_user_recommendations_from_ic(ctx, user_id)
            
            if any(word in message_lower for word in ["search", "find", "product", "fragrance"]):
                search_params = {}
                if "budget" in message_lower or "price" in message_lower:
                    search_params["budget_max"] = 500000
                if "halal" in message_lower:
                    search_params["halal_certified"] = True
                user_products = await search_products_in_ic(ctx, search_params, user_id)
            
            if any(word in message_lower for word in ["consultation", "identity"]):
                # Extract consultation data from message if provided
                consultation_data = {}
                if "lifestyle" in message_lower:
                    consultation_data["lifestyle"] = message_lower.split("lifestyle")[1].split()[0]
                if "budget" in message_lower:
                    consultation_data["budget_range"] = message_lower.split("budget")[1].split()[0]
                if "fragrance family" in message_lower:
                    consultation_data["preferred_families"] = [f.strip() for f in message_lower.split("fragrance family")[1].split(",")]
                
                if consultation_data:
                    result = await call_ic_backend(ctx, "create_decentralized_identity", {
                        "user_id": user_id,
                        "fragrance_identity": consultation_data
                    }, user_id)
                    consultation_response = result.get('Ok', result.get('Err', 'Failed to create identity'))
            
            # Combine IC data with coordinator response
            ic_data = {
                "products": user_products[:5],  # Limit to 5 products
                "recommendations": recommendations[:3],  # Limit to 3 recommendations
                "consultation_response": consultation_response,
                "ic_backend_status": IC_BACKEND["status"]
            }
            
            # Forward to coordinator with IC data
            enhanced_response = await forward_to_coordinator_with_ic_data(
                ctx, message, user_id, request_id, ic_data
            )
            
            return enhanced_response
            
        except Exception as e:
            ctx.logger.error(f"❌ IC Backend integration error: {e}")
            # Fallback to coordinator only
            return await forward_to_coordinator_agent(ctx, message, user_id, request_id)
    else:
        # Forward to coordinator without IC data
        return await forward_to_coordinator_agent(ctx, message, user_id, request_id)

async def forward_to_coordinator_with_ic_data(ctx: Context, message: str, user_id: str, request_id: str, ic_data: Dict[str, Any]) -> str:
    """Forward request to CoordinatorAgent.py with IC backend data"""
    
    if COORDINATOR_AGENT["address"] is None:
        return f"""❌ **Agent Coordinator Not Connected**

However, I can provide some information from our IC Backend:

**Products Available:** {len(ic_data.get('products', []))}
**Your Recommendations:** {len(ic_data.get('recommendations', []))}
**IC Backend:** {ic_data['ic_backend_status'].title()}

Please contact system administrator to configure the agent coordinator."""
    
    ctx.logger.info(f"📡 Forwarding to coordinator with IC data: '{message}'")
    
    try:
        coordinator_request = FrontendRequest(
            user_id=user_id,
            message=message,
            request_type="chat_with_ic_data",
            session_id=request_id,
            data={
                "source": "frontend_bridge_enhanced", 
                "timestamp": datetime.now().timestamp(),
                "bridge_session": request_id,
                "ic_backend_data": ic_data,
                "ic_integration": True
            }
        )
        
        bridge_metrics["coordinator_forwards"] += 1
        
        # Send to CoordinatorAgent.py
        await ctx.send(COORDINATOR_AGENT["address"], coordinator_request)
        ctx.logger.info(f"✅ Forwarded to agent coordinator with IC data")
        
        COORDINATOR_AGENT["status"] = "connected"
        
        # Enhanced response with IC data summary
        ic_summary = ""
        if ic_data.get("products"):
            ic_summary += f"\n📦 **Found {len(ic_data['products'])} Products** from IC Backend"
        if ic_data.get("recommendations"):
            ic_summary += f"\n🎯 **{len(ic_data['recommendations'])} AI Recommendations** available"
        
        return f"""📤 **Request Sent to Enhanced Agent Network**

Your message has been forwarded to our specialized agent coordination system with IC backend data:

📋 **Request Details:**
• Message: "{message[:50]}{'...' if len(message) > 50 else ''}"
• User ID: {user_id}
• Request ID: {request_id}
• IC Backend: {IC_BACKEND['status'].title()}
• Status: Processing with full ecosystem integration

{ic_summary}

⚡ **Agent Coordinator is processing with IC backend data...**

The coordinator will use the IC backend data along with specialist agents (consultation, recommendation, inventory, analytics) to provide the most comprehensive response!

*Bridge Status: Enhanced - IC Backend Integrated*
*Coordinator: {COORDINATOR_AGENT['status'].title()}*
*IC Backend: {IC_BACKEND['status'].title()}*
*Agent Network: Active*"""

    except Exception as e:
        ctx.logger.error(f"❌ Enhanced forward failed: {e}")
        COORDINATOR_AGENT["status"] = "error"
        bridge_metrics["failed_requests"] += 1
        
        return f"""❌ **Connection Error to Enhanced Agent Network**

Unable to reach the agent coordination system, but IC backend data is available:

🔧 **Technical Details:**
• Error: {str(e)[:100]}
• Coordinator: {COORDINATOR_AGENT['endpoint']}
• IC Backend: {IC_BACKEND['status'].title()}
• Status: Coordinator Connection Failed

{f"📦 Available Products: {len(ic_data.get('products', []))}" if ic_data.get('products') else ""}
{f"🎯 Available Recommendations: {len(ic_data.get('recommendations', []))}" if ic_data.get('recommendations') else ""}

*Request ID: {request_id}*"""


# FALLBACK COORDINATOR COMMUNICATION (Original function)
async def forward_to_coordinator_agent(ctx: Context, message: str, user_id: str, request_id: str) -> str:
    """Original forward function without IC data"""
    
    if COORDINATOR_AGENT["address"] is None:
        return """❌ **Agent Coordinator Not Connected**

The agent coordination system address is not configured. 

🔧 **Setup Required:**
1. Start the CoordinatorAgent.py first
2. Copy its address to this bridge
3. Restart the bridge coordinator

*Please contact system administrator*"""
    
    try:
        coordinator_request = FrontendRequest(
            user_id=user_id,
            message=message,
            request_type="chat",
            session_id=request_id,
            data={
                "source": "frontend_bridge", 
                "timestamp": datetime.now().timestamp(),
                "bridge_session": request_id
            }
        )
        
        await ctx.send(COORDINATOR_AGENT["address"], coordinator_request)
        COORDINATOR_AGENT["status"] = "connected"
        
        return f"""📤 **Request Sent to Agent Coordinator**

Your message has been forwarded to our agent coordination system.

*Standard processing without IC backend integration*"""

    except Exception as e:
        ctx.logger.error(f"❌ Forward failed: {e}")
        COORDINATOR_AGENT["status"] = "error"
        return f"❌ Connection error: {str(e)[:100]}"


@chat_proto.on_message(ChatAcknowledgement)
async def handle_frontend_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle ACKs"""
    ctx.logger.info(f"✅ ACK from {sender}")


# ENHANCED RESPONSE HANDLERS
@frontend_coordinator.on_message(model=FrontendResponse)
async def handle_coordinator_response(ctx: Context, sender: str, msg: FrontendResponse):
    """Handle responses from CoordinatorAgent.py with IC data awareness"""
    ctx.logger.info(f"📥 Enhanced response from agent coordinator: {msg.success}")
    
    request_id = msg.request_id
    if request_id in pending_frontend_requests:
        req_data = pending_frontend_requests[request_id]
        original_sender = req_data["sender"]
        
        try:
            if msg.success:
                # Enhanced response formatting
                ic_data_note = ""
                if "ic_backend_data" in msg.data:
                    ic_data_note = "\n🔗 *Response enhanced with IC Backend data*"
                
                response_text = f"""✅ **Response from Enhanced Agent Network**

{msg.message}

**Processing Status:** {msg.success}
**Session ID:** {msg.session_id}
{ic_data_note}

{json.dumps(msg.data, indent=2) if msg.data and len(json.dumps(msg.data)) < 500 else ''}

*Processed by: Agent Coordinator + IC Backend → Specialist Agents → Your Response*"""
            else:
                response_text = f"""❌ **Processing Error from Enhanced Agent Network**

{msg.message}

**Error Details:** {msg.error or 'Unknown error occurred'}
**Session:** {msg.session_id}

Please try rephrasing your request or try again in a moment."""
            
            # Send back to frontend user
            response_msg = create_text_chat(response_text)
            await ctx.send(original_sender, response_msg)
            
            del pending_frontend_requests[request_id]
            ctx.logger.info(f"✅ Enhanced response forwarded to frontend user")
            
        except Exception as e:
            ctx.logger.error(f"❌ Failed to forward response: {e}")
    else:
        ctx.logger.warning("⚠️ Response received with no matching request")


# ENHANCED REST ENDPOINTS
@frontend_coordinator.on_rest_post("/api/chat", ChatRequest, ChatResponseAPI)
async def enhanced_backend_chat_endpoint(ctx: Context, req: ChatRequest) -> ChatResponseAPI:
    """Enhanced REST chat endpoint with IC backend integration"""
    try:
        bridge_metrics["backend_requests"] += 1
        request_id = str(uuid4())
        session_id = req.session_id or f"backend_{request_id}"
        
        # Ensure user exists in IC backend
        ic_integrated = await ensure_user_exists_in_ic(ctx, req.user_id)
        
        frontend_sessions[session_id] = {
            "user_id": req.user_id,
            "request_id": request_id,
            "source": "backend_rest",
            "timestamp": datetime.now().timestamp(),
            "ic_backend_integrated": ic_integrated
        }
        
        try:
            response_text = await process_message_with_ic_backend(ctx, req.message, req.user_id, request_id)
            bridge_metrics["successful_responses"] += 1
            
            return ChatResponseAPI(
                success=True,
                reply=response_text,
                session_id=session_id,
                request_id=request_id
            )
        except Exception as forward_error:
            bridge_metrics["failed_requests"] += 1
            return ChatResponseAPI(
                success=False,
                reply=f"Enhanced agent network error: {str(forward_error)[:100]}",
                session_id=session_id,
                request_id=request_id
            )
        
    except Exception as e:
        bridge_metrics["failed_requests"] += 1
        return ChatResponseAPI(
            success=False,
            reply=f"Enhanced backend error: {str(e)[:100]}",
            session_id="error",
            request_id="error"
        )

@frontend_coordinator.on_rest_get("/api/health", HealthResponse)
async def enhanced_health_check(ctx: Context) -> HealthResponse:
    """Enhanced health check with IC backend status"""
    return HealthResponse(
        status="healthy",
        coordinator_connected=COORDINATOR_AGENT["status"] == "connected",
        ic_backend_connected=IC_BACKEND["status"] == "connected",
        active_sessions=len(frontend_sessions),
        timestamp=datetime.now().timestamp()
    )

@frontend_coordinator.on_rest_get("/api/metrics", MetricsResponse)
async def get_enhanced_bridge_metrics(ctx: Context) -> MetricsResponse:
    """Enhanced bridge metrics with IC backend statistics"""
    return MetricsResponse(
        bridge_metrics=bridge_metrics,
        coordinator_status=COORDINATOR_AGENT["status"],
        ic_backend_status=IC_BACKEND["status"],
        active_sessions=len(frontend_sessions),
        pending_requests=len(pending_frontend_requests),
        endpoints=[
            "GET /api/health - Enhanced health check",
            "GET /api/metrics - Enhanced bridge metrics", 
            "POST /api/chat - Chat with enhanced agent network + IC backend",
            "GET /api/ic/products - Direct IC backend product access",
            "POST /api/ic/recommendations - Direct IC backend recommendations"
        ]
    )

# MAINTENANCE WITH IC BACKEND CACHE CLEANUP
@frontend_coordinator.on_interval(period=60.0)
async def enhanced_periodic_cleanup(ctx: Context):
    """Enhanced cleanup with IC backend cache management"""
    current_time = datetime.now().timestamp()
    
    # Clean sessions older than 30 minutes
    expired_sessions = [
        sid for sid, sdata in frontend_sessions.items()
        if current_time - sdata.get("timestamp", current_time) > 1800
    ]
    
    for sid in expired_sessions:
        del frontend_sessions[sid]
        bridge_metrics["active_sessions"] = max(0, bridge_metrics["active_sessions"] - 1)
    
    # Clean requests older than 5 minutes
    expired_requests = [
        req_id for req_id, req_data in pending_frontend_requests.items()
        if current_time - req_data["timestamp"] > 300
    ]
    
    for req_id in expired_requests:
        del pending_frontend_requests[req_id]
    
    # Clean IC backend cache older than 10 minutes
    expired_cache = [
        cache_key for cache_key, cache_data in ic_backend_cache.items()
        if current_time - cache_data["timestamp"] > 600
    ]
    
    for cache_key in expired_cache:
        del ic_backend_cache[cache_key]
    
    if expired_sessions or expired_requests or expired_cache:
        ctx.logger.info(f"🧹 Enhanced cleanup: {len(expired_sessions)} sessions, {len(expired_requests)} requests, {len(expired_cache)} cache entries")

@frontend_coordinator.on_interval(period=300.0)  # Every 5 minutes
async def ic_backend_health_check(ctx: Context):
    """Periodic IC backend health check"""
    if not IC_BACKEND["canister_id"]:
        return  # Skip if not configured
        
    try:
        # Simple health check to IC backend
        result = await call_ic_backend(ctx, "get_platform_statistics", {}, "health_check")
        
        if "error" not in result:
            IC_BACKEND["status"] = "connected"
            ctx.logger.info("💚 IC Backend health check: OK")
        else:
            IC_BACKEND["status"] = "error"
            ctx.logger.warning("💛 IC Backend health check: Error")
            
    except Exception as e:
        IC_BACKEND["status"] = "disconnected"
        ctx.logger.warning(f"💔 IC Backend health check failed: {e}")


# ADDITIONAL IC BACKEND HELPER FUNCTIONS
async def create_product_in_ic(ctx: Context, product_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Create a new product in IC backend"""
    try:
        product_data = {
            **product_data,
            "seller_verification": product_data.get("verified", True)
        }
        result = await call_ic_backend(ctx, "add_product", {"product": product_data}, user_id)
        return result
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create product in IC: {e}")
        return {"error": str(e)}

    # User analytics
async def get_user_analytics_from_ic(ctx: Context, seller_id: str) -> List[Dict[str, Any]]:
    """Get seller analytics from IC backend"""
    try:
        result = await call_ic_backend(ctx, "get_seller_analytics", {"seller_id": seller_id}, seller_id)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "analytics" in result:
            return result["analytics"]
        else:
            return []
            
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get analytics from IC: {e}")
        return []

    # Create Review
async def create_review_in_ic(ctx: Context, review_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Create a verified review in IC backend"""
    try:
        result = await call_ic_backend(ctx, "create_verified_review", {"review": review_data}, user_id)
        return result
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create review in IC: {e}")
        return {"error": str(e)}

    # Get Halal Products
async def get_halal_products_from_ic(ctx: Context, user_id: str) -> List[Dict[str, Any]]:
    """Get halal certified products from IC backend"""
    try:
        if not IC_BACKEND["canister_id"]:
            mock_result = await mock_ic_backend_call(ctx, "get_products", {}, user_id)
            # Filter for halal products in mock
            products = mock_result.get("products", [])
            return [p for p in products if p.get("halal_certified", False)]
            
        result = await call_ic_backend(ctx, "get_halal_products", {}, user_id)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "products" in result:
            return result["products"]
        else:
            return []
            
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get halal products from IC: {e}")
        return []

async def stake_for_verification_in_ic(ctx: Context, user_id: str, amount: int, tier: str) -> Dict[str, Any]:
    """Stake for verification in IC backend"""
    try:
        stake_data = {
            "user_id": user_id,
            "amount": amount,
            "tier": tier
        }
        
        if not IC_BACKEND["canister_id"]:
            return await mock_ic_backend_call(ctx, "stake_for_verification", stake_data, user_id)
            
        result = await call_ic_backend(ctx, "stake_for_verification", stake_data, user_id)
        return result
    except Exception as e:
        ctx.logger.error(f"❌ Failed to stake in IC: {e}")
        return {"error": str(e)}

# STARTUP WITH IC BACKEND INTEGRATION
frontend_coordinator.include(chat_proto, publish_manifest=True)

@frontend_coordinator.on_event("startup")
async def enhanced_startup_handler(ctx: Context):
    ctx.logger.info("🌉 Aromance Enhanced Frontend-Backend Bridge Started!")
    ctx.logger.info(f"🏠 Bridge Address: {frontend_coordinator.address}")
    ctx.logger.info(f"🔗 Bridge Endpoint: http://127.0.0.1:8080")
    ctx.logger.info("🌐 Enhanced REST Endpoints:")
    ctx.logger.info("  • GET  http://127.0.0.1:8080/api/health")
    ctx.logger.info("  • GET  http://127.0.0.1:8080/api/metrics") 
    ctx.logger.info("  • POST http://127.0.0.1:8080/api/chat")
    ctx.logger.info("  • GET  http://127.0.0.1:8080/api/ic/products")
    ctx.logger.info("  • POST http://127.0.0.1:8080/api/ic/recommendations")
    ctx.logger.info("  • POST http://127.0.0.1:8080/api/ic/user/create")
    ctx.logger.info("  • POST http://127.0.0.1:8080/api/ic/products/search")
    ctx.logger.info("  • GET  http://127.0.0.1:8080/api/ic/status")
    
    # Coordinator Agent Status
    if COORDINATOR_AGENT["address"] is None:
        ctx.logger.warning("⚠️ COORDINATOR AGENT ADDRESS NOT SET!")
        ctx.logger.warning("📋 TODO: Copy the CoordinatorAgent.py address and update COORDINATOR_AGENT['address']")
        ctx.logger.warning(f"📡 Expected Agent Coordinator: {COORDINATOR_AGENT['endpoint']}")
    else:
        ctx.logger.info(f"📡 Agent Coordinator: {COORDINATOR_AGENT['address']}")
    
    # IC Backend Status
    ctx.logger.info("🔗 IC Backend Integration:")
    if IC_BACKEND["canister_id"] is None:
        ctx.logger.warning("⚠️ IC BACKEND NOT CONFIGURED - RUNNING IN MOCK MODE")
        ctx.logger.warning("📋 TODO: Configure IC backend with:")
        ctx.logger.warning("   • configure_for_local_dfx('YOUR_CANISTER_ID')")
        ctx.logger.warning("   • configure_for_mainnet('YOUR_CANISTER_ID')")
        IC_BACKEND["status"] = "not_configured"
    else:
        ctx.logger.info(f"  • Canister URL: {IC_BACKEND['canister_url']}")
        ctx.logger.info(f"  • Canister ID: {IC_BACKEND['canister_id']}")
        ctx.logger.info(f"  • Environment: {IC_BACKEND['environment']}")
        ctx.logger.info(f"  • Status: {IC_BACKEND['status'].title()}")
    
    ctx.logger.info("✅ Enhanced bridge ready with full ecosystem integration! 🌺")
    ctx.logger.info("🔗 Systems: Frontend ↔ Bridge ↔ Agent Coordinator ↔ IC Backend")
    
    # Initialize metrics
    bridge_metrics["startup_time"] = datetime.now().timestamp()
    bridge_metrics["bridge_address"] = str(frontend_coordinator.address)
    bridge_metrics["ic_backend_enabled"] = IC_BACKEND["canister_id"] is not None
    
    # Initial IC backend connection test
    if IC_BACKEND["canister_id"]:
        try:
            ctx.logger.info("🧪 Testing initial IC backend connection...")
            test_result = await call_ic_backend(ctx, "greet", {"name": "Enhanced Bridge"}, "startup_test")
            if "error" not in test_result:
                ctx.logger.info("✅ IC Backend initial connection successful!")
                ctx.logger.info(f"🎉 IC Response: {test_result}")
            else:
                ctx.logger.warning("⚠️ IC Backend initial connection failed")
                ctx.logger.warning(f"🔧 Error: {test_result.get('error', 'Unknown error')}")
        except Exception as e:
            ctx.logger.warning(f"⚠️ IC Backend startup test error: {e}")
    else:
        ctx.logger.info("🔧 Running in MOCK MODE - IC Backend calls will be simulated")

def set_ic_backend_config(canister_id: str, canister_url: str = None):
    """Helper function to set IC backend configuration"""
    global IC_BACKEND
    IC_BACKEND["canister_id"] = canister_id
    if canister_url:
        IC_BACKEND["canister_url"] = canister_url
        IC_BACKEND["environment"] = "custom"
    else:
        # Default local dfx setup
        IC_BACKEND["canister_url"] = f"http://127.0.0.1:4943/?canisterId={canister_id}"
        IC_BACKEND["environment"] = "local"
    
    IC_BACKEND["status"] = "configured"
    
    print(f"✅ IC Backend configured:")
    print(f"   Canister ID: {canister_id}")
    print(f"   Canister URL: {IC_BACKEND['canister_url']}")
    print(f"   Environment: {IC_BACKEND['environment']}")

def configure_for_mainnet(canister_id: str):
    """Quick configuration for IC mainnet deployment"""
    global IC_BACKEND
    IC_BACKEND["canister_id"] = canister_id
    IC_BACKEND["canister_url"] = f"https://{canister_id}.ic0.app"
    IC_BACKEND["environment"] = "mainnet"
    IC_BACKEND["status"] = "configured"
    
    print(f"✅ Configured for IC mainnet:")
    print(f"   Canister ID: {canister_id}")
    print(f"   Mainnet URL: {IC_BACKEND['canister_url']}")

def configure_for_local_dfx(canister_id: str, port: int = 4943):
    """Quick configuration for local dfx development"""
    global IC_BACKEND
    IC_BACKEND["canister_id"] = canister_id
    IC_BACKEND["canister_url"] = f"http://127.0.0.1:{port}/?canisterId={canister_id}"
    IC_BACKEND["environment"] = "local"
    IC_BACKEND["status"] = "configured"
    
    print(f"✅ Configured for local dfx:")
    print(f"   Canister ID: {canister_id}")
    print(f"   Local URL: {IC_BACKEND['canister_url']}")

def get_bridge_status():
    """Get current bridge status"""
    return {
        "coordinator_agent": COORDINATOR_AGENT,
        "ic_backend": IC_BACKEND,
        "metrics": bridge_metrics,
        "active_sessions": len(frontend_sessions),
        "pending_requests": len(pending_frontend_requests),
        "cache_entries": len(ic_backend_cache)
    }

def reset_ic_backend_config():
    """Reset IC backend to unconfigured state"""
    global IC_BACKEND
    IC_BACKEND["canister_id"] = None
    IC_BACKEND["canister_url"] = None
    IC_BACKEND["environment"] = "local"
    IC_BACKEND["status"] = "not_configured"
    print("✅ IC Backend configuration reset - now running in MOCK MODE")

# ENHANCED ERROR HANDLING AND RECOVERY
async def test_ic_backend_connection(ctx: Context) -> Dict[str, Any]:
    """Test IC backend connection and return status"""
    if not IC_BACKEND["canister_id"]:
        return {
            "connected": False,
            "error": "IC Backend not configured",
            "status": "not_configured",
            "mock_mode": True
        }
        
    try:
        # Test with simple greet function
        result = await call_ic_backend(ctx, "greet", {"name": "Connection Test"}, "test")
        
        if "error" not in result:
            # Test with platform statistics
            stats_result = await call_ic_backend(ctx, "get_platform_statistics", {}, "test")
            
            return {
                "connected": True,
                "greet_response": result,
                "platform_stats": stats_result,
                "status": "healthy"
            }
        else:
            return {
                "connected": False,
                "error": result.get("error", "Unknown error"),
                "status": "error"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "status": "disconnected"
        }

async def sync_user_data_with_ic(ctx: Context, user_id: str, session_data: Dict[str, Any]) -> bool:
    """Sync user session data with IC backend"""
    try:
        if not IC_BACKEND["canister_id"]:
            return True  # Skip sync in mock mode
            
        # Update last active timestamp
        update_data = {
            "user_id": user_id,
            "last_active": int(datetime.now().timestamp() * 1_000_000_000),
            "session_info": session_data
        }
        
        result = await call_ic_backend(ctx, "update_user_activity", update_data, user_id)
        return "error" not in result
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to sync user data with IC: {e}")
        return False

# DIRECT IC BACKEND ENDPOINTS
@frontend_coordinator.on_rest_post("/api/ic/product/create", ICProduct, ICProductsResponse)
async def create_product_in_ic_direct(ctx: Context, req: ICProduct) -> ICProductsResponse:
    try:
        product_data = req.dict()
        product_data["seller_verification"] = product_data.get("seller_verification", "verified")  # Adjust type
        result = await create_product_in_ic(ctx, product_data, req.seller_id)

        if "error" not in result:
            return ICProductsResponse(
                success=True,
                products=[result],
                count=1,
                source="ic_backend_direct"
            )
        return ICProductsResponse(
            success=False,
            products=[],
            count=0,
            source="ic_backend_direct"
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create product: {e}")
        return ICProductsResponse(
            success=False,
            products=[],
            count=0,
            source="ic_backend_direct"
        )
    
@frontend_coordinator.on_rest_get("/api/ic/products", ICProductsResponse)
async def get_ic_products_direct(ctx: Context) -> ICProductsResponse:
    try:
        products = await call_ic_backend(ctx, "get_products", {}, "direct_api")

        if isinstance(products, list):
            return ICProductsResponse(
                success=True,
                products=products,
                count=len(products),
                source="ic_backend_direct"
            )
        elif isinstance(products, dict) and "products" in products:
            return ICProductsResponse(
                success=True,
                products=products["products"],
                count=len(products["products"]),
                source="ic_backend_direct"
            )
        else:
            return ICProductsResponse(
                success=False,
                products=[],
                count=0,
                source="ic_backend_direct"
            )
    except Exception as e:
        ctx.logger.error(f"❌ Failed direct IC products call: {e}")
        return ICProductsResponse(
            success=False,
            products=[],
            count=0,
            source="ic_backend_direct"
        )

@frontend_coordinator.on_rest_post("/api/ic/recommendations", ICRecommendationsRequest, ICRecommendationsResponse)
async def get_ic_recommendations_direct(ctx: Context, req: ICRecommendationsRequest) -> ICRecommendationsResponse:
    try:
        user_id = req.user_id or "anonymous"
        recommendations = await get_user_recommendations_from_ic(ctx, user_id)

        return ICRecommendationsResponse(
            success=True,
            recommendations=recommendations,
            count=len(recommendations),
            user_id=user_id,
            source="ic_backend_direct"
        )
    
    except Exception as e:
        ctx.logger.error(f"❌ Failed direct IC recommendations call: {e}")
        return ICRecommendationsResponse(
            success=False,
            recommendations=[],
            count=0,
            user_id=req.user_id or "anonymous",
            source="ic_backend_direct"
        )

@frontend_coordinator.on_rest_post("/api/ic/user/create", ICUserCreateRequest, ICUserCreateResponse)
async def create_user_in_ic_direct(ctx: Context, req: ICUserCreateRequest) -> ICUserCreateResponse:
    try:
        user_data = req.user_data
        user_id = user_data.get("user_id", f"user_{str(uuid4())}")
        success = await ensure_user_exists_in_ic(ctx, user_id)

        return ICUserCreateResponse(
            success=success,
            user_id=user_id,
            message="User created in IC backend" if success else "Failed to create user",
            source="ic_backend_direct"
        )
    
    except Exception as e:
        return ICUserCreateResponse(
            success=False,
            user_id="",
            message=f"Error: {str(e)}",
            source="ic_backend_direct"
        )

@frontend_coordinator.on_rest_post("/api/ic/products/search", ICProductSearchRequest, ICProductSearchResponse)
async def search_products_in_ic_direct(ctx: Context, req: ICProductSearchRequest) -> ICProductSearchResponse:
    try:
        search_params = req.search_params
        user_id = req.user_id or "anonymous"

        products = await search_products_in_ic(ctx, search_params, user_id)

        return ICProductSearchResponse(
            success=True,
            product=products,
            count=len(products),
            search_param=search_params,
            source="ic_backend_direct"
        )
    
    except Exception as e:
        return ICProductSearchResponse(
            success=False,
            product=[],
            count=0,
            search_param=req.search_params,
            source="ic_backend_direct"
        )

@frontend_coordinator.on_rest_get("/api/ic/status", ICStatusResponse)
async def get_ic_backend_status(ctx: Context) -> ICStatusResponse:
    try:
        connection_test = await test_ic_backend_connection(ctx)

        return ICStatusResponse(
            ic_backend=IC_BACKEND,
            connection_test=connection_test,

            cache_stats={
                "entries": len(ic_backend_cache),
                "oldest_entry": min([entry["timestamp"] for entry in ic_backend_cache.values()]) if ic_backend_cache else None,
                "newest_entry": max([entry["timestamp"] for entry in ic_backend_cache.values()]) if ic_backend_cache else None
            },

            bridge_metrics={
                "ic_backend_calls": bridge_metrics["ic_backend_calls"],
                "cache_hits": bridge_metrics["cache_hits"],
                "cache_misses": bridge_metrics["cache_misses"]
            }
        )
    except Exception as e:
        return ICStatusResponse(
            ic_backend=IC_BACKEND,
            connection_test={"error": str(e)},
            cache_stats={},
            bridge_metrics={}
        )

@frontend_coordinator.on_rest_post("/api/ic/stake", ICStakeRequest, ICStakeResponse)
async def stake_verification_direct(ctx: Context, req: ICStakeRequest) -> ICStakeResponse:
    try:
        user_id = req.user_id
        amount = req.amount
        tier = req.tier or "BasicReviewer"

        if not user_id or amount <= 0:
            return ICStakeResponse(
                success=False,
                result={"error": "Invalid user_id or amount"},
                userId=user_id,
                amount=amount,
                tier=tier,
                source="ic_backend_direct"
            )
        
        result = await stake_for_verification_in_ic(ctx, user_id, amount, tier)

        return ICStakeResponse(
            success="error" not in result,
            result=result,
            userId=user_id,
            amount=amount,
            tier=tier,
            source="ic_backend_direct"
        )
    except Exception as e:
        return ICStakeResponse(
            success=False,
            result={"error": str(e)},
            userId=req.user_id if hasattr(req, 'user_id') else "",
            amount=req.amount if hasattr(req, 'amount') else 0,
            tier=req.tier if hasattr(req, 'tier') else "BasicReviewer",
            source="ic_backend_direct"
        )

@frontend_coordinator.on_rest_get("/api/ic/halal", ICHalalProductsResponse)
async def get_halal_products_direct(ctx: Context) -> ICHalalProductsResponse:
    try:
        halal_products = await get_halal_products_from_ic(ctx, "halal_query")

        return ICHalalProductsResponse(
            success=True,
            halalProducts=halal_products,
            count=len(halal_products),
            source="ic_backend_direct"
        )
    except Exception as e:
        return ICHalalProductsResponse(
            success=False,
            halalProducts=[],
            count=0,
            source="ic_backend_direct"
        )
    
    # FROM FRONTEND
@frontend_coordinator.on_rest_post("/api/ic/identity/create", ICIdentityCreateRequest, ICIdentityCreateResponse)
async def create_identity_in_ic_direct(ctx: Context, req: ICIdentityCreateRequest) -> ICIdentityCreateResponse:
    try:
        result = await call_ic_backend(ctx, "create_decentralized_identity", {
            "user_id": req.user_id,
            "fragrance_identity": req.fragrance_identity
        }, req.user_id)
        
        if isinstance(result, dict) and 'Ok' in result:
            return ICIdentityCreateResponse(
                success=True,
                identity=result['Ok'],
                error=None
            )
        return ICIdentityCreateResponse(
            success=False,
            identity=None,
            error=result.get('Err', 'Unknown error')
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create identity: {e}")
        return ICIdentityCreateResponse(
            success=False,
            identity=None,
            error=str(e)
        )

@frontend_coordinator.on_rest_post("/api/ic/reviews/create", ICReviewCreateRequest, ICReviewCreateResponse)
async def create_review_in_ic_direct(ctx: Context, req: ICReviewCreateRequest) -> ICReviewCreateResponse:
    try:
        result = await call_ic_backend(ctx, "create_verified_review", {"review": req.review}, req.review.get('reviewer_id', 'anonymous'))
        
        if isinstance(result, dict) and 'Ok' in result:
            return ICReviewCreateResponse(
                success=True,
                review_id=result['Ok'],
                error=None
            )
        return ICReviewCreateResponse(
            success=False,
            review_id="",
            error=result.get('Err', 'Unknown error')
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create review: {e}")
        return ICReviewCreateResponse(
            success=False,
            review_id="",
            error=str(e)
        )

@frontend_coordinator.on_rest_post("/api/ic/reviews/get", ICReviewsGetRequest, ICReviewsResponse)
async def get_reviews_in_ic_direct(ctx: Context, req: ICReviewsGetRequest) -> ICReviewsResponse:
    try:
        result = await call_ic_backend(ctx, "get_product_reviews", {"product_id": req.product_id}, "anonymous")
        
        if isinstance(result, list):
            return ICReviewsResponse(
                success=True,
                reviews=result,
                count=len(result)
            )
        return ICReviewsResponse(
            success=False,
            reviews=[],
            count=0
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get reviews: {e}")
        return ICReviewsResponse(
            success=False,
            reviews=[],
            count=0
        )

@frontend_coordinator.on_rest_post("/api/ic/transactions/create", ICTransactionCreateRequest, ICTransactionCreateResponse)
async def create_transaction_in_ic_direct(ctx: Context, req: ICTransactionCreateRequest) -> ICTransactionCreateResponse:
    try:
        result = await call_ic_backend(ctx, "create_transaction", {"transaction": req.transaction}, req.transaction.get('buyer_id', 'anonymous'))
        
        if isinstance(result, dict) and 'Ok' in result:
            return ICTransactionCreateResponse(
                success=True,
                transaction_id=result['Ok'],
                error=None
            )
        return ICTransactionCreateResponse(
            success=False,
            transaction_id="",
            error=result.get('Err', 'Unknown error')
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to create transaction: {e}")
        return ICTransactionCreateResponse(
            success=False,
            transaction_id="",
            error=str(e)
        )

@frontend_coordinator.on_rest_post("/api/ic/transactions/get", ICTransactionsGetRequest, ICTransactionsResponse)
async def get_transactions_in_ic_direct(ctx: Context, req: ICTransactionsGetRequest) -> ICTransactionsResponse:
    try:
        result = await call_ic_backend(ctx, "get_user_transactions", {"user_id": req.user_id}, req.user_id)
        
        if isinstance(result, list):
            return ICTransactionsResponse(
                success=True,
                transactions=result,
                count=len(result)
            )
        return ICTransactionsResponse(
            success=False,
            transactions=[],
            count=0
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get transactions: {e}")
        return ICTransactionsResponse(
            success=False,
            transactions=[],
            count=0
        )

@frontend_coordinator.on_rest_get("/api/ic/platform_stats", ICPlatformStatsResponse)
async def get_platform_stats_direct(ctx: Context) -> ICPlatformStatsResponse:
    try:
        result = await call_ic_backend(ctx, "get_platform_statistics", {}, "anonymous")
        
        if isinstance(result, dict):
            return ICPlatformStatsResponse(
                total_users=result.get('total_users', 0),
                verified_users=result.get('verified_users', 0),
                total_products=result.get('total_products', 0),
                verified_products=result.get('verified_products', 0),
                total_transactions=result.get('total_transactions', 0),
                total_gmv_idr=result.get('total_gmv_idr', 0),
                total_reviews=result.get('total_reviews', 0),
                total_staked_idr=result.get('total_staked_idr', 0)
            )
        return ICPlatformStatsResponse(
            total_users=0,
            verified_users=0,
            total_products=0,
            verified_products=0,
            total_transactions=0,
            total_gmv_idr=0,
            total_reviews=0,
            total_staked_idr=0
        )
    except Exception as e:
        ctx.logger.error(f"❌ Failed to get platform stats: {e}")
        return ICPlatformStatsResponse(
            total_users=0,
            verified_users=0,
            total_products=0,
            verified_products=0,
            total_transactions=0,
            total_gmv_idr=0,
            total_reviews=0,
            total_staked_idr=0
        )

@frontend_coordinator.on_interval(period=60.0)
async def periodic_cleanup(ctx: Context):
    current_time = datetime.now().timestamp()
    expired_sessions = [
        sid for sid, sdata in frontend_sessions.items()
        if current_time - sdata.get("timestamp", current_time) > 1800
    ]
    for sid in expired_sessions:
        del frontend_sessions[sid]
        bridge_metrics["active_sessions"] = max(0, bridge_metrics["active_sessions"] - 1)
    
    expired_requests = [
        req_id for req_id, req_data in pending_frontend_requests.items()
        if current_time - req_data["timestamp"] > 300
    ]
    for req_id in expired_requests:
        del pending_frontend_requests[req_id]
    
    expired_cache = [
        cache_key for cache_key, cache_data in ic_backend_cache.items()
        if current_time - cache_data["timestamp"] > 600
    ]
    for cache_key in expired_cache:
        del ic_backend_cache[cache_key]
    
    if expired_sessions or expired_requests or expired_cache:
        ctx.logger.info(f"🧹 Cleanup: {len(expired_sessions)} sessions, {len(expired_requests)} requests, {len(expired_cache)} cache entries")

# DECLARE THE COORDINATOR AGENTS' ADDRESS
def set_coordinator_agent_address(address: str):
    """Helper function to set coordinator agent address"""
    global COORDINATOR_AGENT
    COORDINATOR_AGENT["address"] = address
    print(f"✅ Agent coordinator address updated: {address}")

call_ic_backend
if __name__ == "__main__":
    print("🌉 Starting Aromance Enhanced Frontend Bridge...")
    print(f"🔧 Bridge Address: {frontend_coordinator.address}")
    print()
    print("🚀 Available Configuration Functions:")
    print("   • set_coordinator_agent_address(address)")
    print("   • configure_for_local_dfx(canister_id)")
    print("   • configure_for_mainnet(canister_id)")
    print("   • reset_ic_backend_config()  # Run in mock mode")
    print("   • get_bridge_status()")
    print()
    
    set_coordinator_agent_address("agent1q0c3gfhhufskvm0tfssj05y6exkfwckea9400sr2luj6l98da8n8ykxssyd")
    
    # Configure IC backend (OPTIONAL - will run in mock mode if not configured)
    configure_for_local_dfx("bkyz2-fmaaa-aaaaa-qaaaq-cai")
    # OR
    # configure_for_mainnet("YOUR_MAINNET_CANISTER_ID")
    
    print("🚀 Starting enhanced bridge with current configuration...")
    print("📊 Bridge Status:")
    status = get_bridge_status()
    for key, value in status.items():
        if key != "metrics":
            print(f"   {key}: {value}")
    
    print()
    if IC_BACKEND["canister_id"] is None:
        print("🔧 IC Backend: MOCK MODE - All IC calls will be simulated")
        print("   To enable real IC backend, use:")
        print("   configure_for_local_dfx('your_canister_id')")
    else:
        print(f"🔗 IC Backend: {IC_BACKEND['environment'].upper()} - {IC_BACKEND['canister_id']}")
    
    print("\n✅ Starting bridge...")
    
    frontend_coordinator.run()