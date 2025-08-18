from uagents import Agent, Context, Model
from typing import List, Dict, Any, Optional
import json
import asyncio
import aiohttp
from datetime import datetime
from pydantic import BaseModel

class RecommendationRequest(Model):
    user_id: str
    session_id: str
    fragrance_profile: Dict[str, Any]
    budget_max: Optional[int] = None
    specific_request: Optional[str] = None

class RecommendationHTTPRequest(Model):
    user_id: str
    session_id: str
    fragrance_profile: Dict[str, Any]
    budget_max: Optional[int] = None

class ProductRecommendation(Model):
    product_id: str
    name: str
    brand: str
    price_idr: int
    fragrance_family: str
    notes: List[str]
    match_score: float
    reasoning: str
    indonesian_heritage: bool
    halal_certified: bool
    occasions: List[str]
    personality_match: str

class RecommendationResponse(Model):
    user_id: str
    session_id: str
    recommendations: List[ProductRecommendation]
    total_found: int
    explanation: str
    alternative_suggestions: List[str]
    icp_synced: bool

class UserRecommendationsResponse(Model):
    success: bool
    recommendations: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class HealthResponse(Model):
    status: str
    database_products: int
    icp_connected: bool
    timestamp: float

recommendation_agent = Agent(
    name="aromance_recommendation_ai",
    port=8002,
    seed="aromance_recommendation_enhanced_2025",
    endpoint=["http://127.0.0.1:8002/submit"]
)

# Enhanced Indonesian Product Database (Sample - will be expanded)
INDONESIAN_FRAGRANCE_DATABASE = [
#SUDAH ADA LEBIH DARI 1, INI HANYA DIPOTONG SUPAYA TIDAK KEPANJANGAN
    {
        "product_id": "IDN_034",
        "name": "Earth Love",
        "brand": "Earth Love Life",
        "price_idr": 280000,
        "fragrance_family": "green earthy",
        "top_notes": ["Green Accord", "Bergamot"],
        "middle_notes": ["Patchouli", "Vetiver"],
        "base_notes": ["Cedarwood", "Musk"],
        "occasions": ["daily", "natural"],
        "personality_match": ["grounded", "serene"],
        "longevity": "5-7 hours",
        "sillage": "light-moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Patchouli"],
        "climate_suitability": "tropical_all_day",
        "target_age": "20-40",
        "gender": "unisex",
        "description": "Earthy green scent with a calming, natural essence.",
        "tagline": "Love for the earth",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.5,
        "verified_reviews": 55,
        "image_url": "/images/IDN_034.jpg"
    }
]

# ICP Configuration
ICP_CONFIG = {
    "local_endpoint": "http://127.0.0.1:4943",
    "canister_id": "bkyz2-fmaaa-aaaaa-qaaaq-cai",
    "current_network": "local"
}

@recommendation_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🎯 Aromance Enhanced Recommendation Agent Started")
    ctx.logger.info(f"Agent Address: {recommendation_agent.address}")
    ctx.logger.info(f"Database loaded: {len(INDONESIAN_FRAGRANCE_DATABASE)} products")
    ctx.logger.info("Ready for intelligent fragrance recommendations with ICP integration! 💎")

# HTTP Endpoints - Fixed format
@recommendation_agent.on_rest_post("/recommend", RecommendationHTTPRequest, RecommendationResponse)
async def recommend_endpoint(ctx: Context, req: RecommendationHTTPRequest) -> RecommendationResponse:
    """HTTP endpoint for generating recommendations"""
    try:
        ctx.logger.info(f"🔍 Processing recommendation for user {req.user_id}")
        ctx.logger.info(f"Profile: {req.fragrance_profile.get('personality_traits', 'Unknown')}")
        
        # Generate recommendations
        recommendations = await generate_intelligent_recommendations(ctx, req.fragrance_profile, req.budget_max)
        
        # Sync to ICP backend
        icp_sync_success = await sync_recommendations_to_icp(ctx, req.user_id, recommendations)
        
        # Create explanation and alternatives
        explanation = create_recommendation_explanation(req.fragrance_profile, recommendations)
        alternatives = generate_alternative_suggestions(req.fragrance_profile, recommendations)
        
        response = RecommendationResponse(
            user_id=req.user_id,
            session_id=req.session_id,
            recommendations=recommendations,
            total_found=len(recommendations),
            explanation=explanation,
            alternative_suggestions=alternatives,
            icp_synced=icp_sync_success
        )
        
        ctx.logger.info(f"✅ Generated {len(recommendations)} recommendations")
        
        # Notify coordinator about completion
        await notify_coordinator_recommendations_complete(req.user_id, req.session_id, {
            "recommendations": [rec.dict() for rec in recommendations],
            "total_found": len(recommendations)
        })
        
        return response
        
    except Exception as e:
        ctx.logger.error(f"⚠ Recommendation error: {e}")
        return RecommendationResponse(
            user_id=req.user_id,
            session_id=req.session_id,
            recommendations=[],
            total_found=0,
            explanation="Sorry, we encountered an error generating recommendations. Please try again.",
            alternative_suggestions=["Please refresh and try again", "Contact support if the issue persists"],
            icp_synced=False
        )

@recommendation_agent.on_rest_get("/recommendations/{user_id}", UserRecommendationsResponse)
async def get_user_recommendations_endpoint(ctx: Context, user_id: str) -> UserRecommendationsResponse:
    """Get existing recommendations for a user"""
    try:
        # Try to get from ICP first
        icp_recommendations = await get_recommendations_from_icp(ctx, user_id)
        
        if icp_recommendations:
            return UserRecommendationsResponse(
                success=True,
                recommendations=icp_recommendations
            )
        else:
            return UserRecommendationsResponse(
                success=False,
                error="No recommendations found"
            )
            
    except Exception as e:
        ctx.logger.error(f"⚠ Recommendation retrieval error: {e}")
        return UserRecommendationsResponse(
            success=False,
            error="Internal server error"
        )

@recommendation_agent.on_rest_get("/health", HealthResponse)
async def health_check_endpoint(ctx: Context) -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        database_products=len(INDONESIAN_FRAGRANCE_DATABASE),
        icp_connected=await test_icp_connection(ctx),
        timestamp=datetime.now().timestamp()
    )

# Agent Message Handling
@recommendation_agent.on_message(model=RecommendationRequest)
async def handle_recommendation_request(ctx: Context, sender: str, msg: RecommendationRequest):
    ctx.logger.info(f"🔍 Processing recommendation for user {msg.user_id}")
    
    profile = msg.fragrance_profile
    ctx.logger.info(f"Profile: {profile.get('personality_traits', 'Unknown')}")
    
    # Generate intelligent recommendations
    recommendations = await generate_intelligent_recommendations(ctx, profile, msg.budget_max)
    
    # Sync to ICP backend
    icp_synced = await sync_recommendations_to_icp(ctx, msg.user_id, recommendations)
    
    # Create explanation and alternatives
    explanation = create_recommendation_explanation(profile, recommendations)
    alternatives = generate_alternative_suggestions(profile, recommendations)
    
    response = RecommendationResponse(
        user_id=msg.user_id,
        session_id=msg.session_id,
        recommendations=recommendations,
        total_found=len(recommendations),
        explanation=explanation,
        alternative_suggestions=alternatives,
        icp_synced=icp_synced
    )
    
    ctx.logger.info(f"✅ Generated {len(recommendations)} recommendations")
    await ctx.send(sender, response)

async def generate_intelligent_recommendations(ctx: Context, profile: Dict, budget_max: Optional[int]) -> List[ProductRecommendation]:
    """Generate intelligent fragrance recommendations using enhanced AI analysis"""
    
    recommendations = []
    preferred_families = profile.get("fragrance_families", ["fresh"])
    personality_traits = profile.get("personality_traits", ["versatile"])
    occasions = profile.get("occasions", ["daily"])
    budget_range = profile.get("budget_range", "moderate")
    sensitivity = profile.get("sensitivity", "normal")
    
    ctx.logger.info(f"Analyzing for families: {preferred_families}")
    
    for product in INDONESIAN_FRAGRANCE_DATABASE:
        if not product.get("stock_available", False):
            continue
            
        # Calculate comprehensive match score
        match_score = calculate_advanced_match_score(product, profile)
        
        if match_score < 0.4:  # Minimum threshold
            continue
            
        # Budget filtering
        if budget_max and product["price_idr"] > budget_max:
            continue
            
        # Sensitivity filtering
        if sensitivity == "sensitive" and product.get("sillage") == "heavy":
            continue
        if sensitivity == "allergic" and "floral" in product["fragrance_family"]:
            continue
            
        # Create reasoning
        reasoning = generate_match_reasoning(product, profile, match_score)
        
        recommendation = ProductRecommendation(
            product_id=product["product_id"],
            name=product["name"],
            brand=product["brand"],
            price_idr=product["price_idr"],
            fragrance_family=product["fragrance_family"],
            notes=product["top_notes"] + product["middle_notes"] + product["base_notes"],
            match_score=round(match_score, 2),
            reasoning=reasoning,
            indonesian_heritage=product.get("indonesian_heritage", False),
            halal_certified=product.get("halal_certified", False),
            occasions=product["occasions"],
            personality_match=", ".join(product.get("personality_match", []))
        )
        
        recommendations.append(recommendation)
    
    # Sort by match score and return top 5
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:5]

def calculate_advanced_match_score(product: Dict, profile: Dict) -> float:
    """Enhanced AI-based matching algorithm"""
    
    score = 0.0
    
    # Fragrance family matching (30% weight)
    preferred_families = profile.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        score += 0.3
    
    # Personality matching (25% weight)
    personality_traits = profile.get("personality_traits", [])
    product_personalities = product.get("personality_match", [])
    personality_overlap = len(set(personality_traits) & set(product_personalities))
    if personality_overlap > 0:
        score += 0.25 * min(personality_overlap / max(len(personality_traits), 1), 1.0)
    
    # Occasion matching (20% weight)
    user_occasions = profile.get("occasions", [])
    product_occasions = product.get("occasions", [])
    occasion_overlap = len(set(user_occasions) & set(product_occasions))
    if occasion_overlap > 0:
        score += 0.2 * min(occasion_overlap / max(len(user_occasions), 1), 1.0)
    
    # Budget compatibility (15% weight)
    budget_range = profile.get("budget_range", "moderate")
    price = product["price_idr"]
    budget_score = calculate_budget_score(price, budget_range)
    score += 0.15 * budget_score
    
    # Indonesian heritage bonus (5% weight)
    if product.get("indonesian_heritage", False):
        score += 0.05
    
    # Halal certification bonus (3% weight)
    if product.get("halal_certified", False):
        score += 0.03
    
    # Climate suitability (2% weight)
    if product.get("climate_suitability") == "tropical_all_day":
        score += 0.02
    
    return min(score, 1.0)

def calculate_budget_score(price: int, budget_range: str) -> float:
    """Calculate budget compatibility score"""
    
    if budget_range == "budget":
        if price <= 100000: return 1.0
        elif price <= 150000: return 0.7
        else: return 0.3
    elif budget_range == "moderate":
        if 100000 <= price <= 300000: return 1.0
        elif price <= 100000 or (price <= 400000): return 0.8
        else: return 0.4
    elif budget_range == "premium":
        if 300000 <= price <= 500000: return 1.0
        elif 200000 <= price <= 600000: return 0.8
        else: return 0.5
    elif budget_range == "luxury":
        if price >= 500000: return 1.0
        elif price >= 300000: return 0.7
        else: return 0.4
    
    return 0.5

def generate_match_reasoning(product: Dict, profile: Dict, match_score: float) -> str:
    """Generate intelligent reasoning for the match"""
    
    reasons = []
    
    # Match score interpretation
    if match_score > 0.8:
        reasons.append("✨ PERFECT MATCH! Highly recommended for your profile")
    elif match_score > 0.6:
        reasons.append("💫 Excellent choice that suits your personality")
    else:
        reasons.append("✅ Good alternative option to consider")
    
    # Fragrance family match
    preferred_families = profile.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        reasons.append(f"Perfect match for your {product['fragrance_family']} preference")
    
    # Personality alignment
    personality_traits = profile.get("personality_traits", [])
    product_personalities = product.get("personality_match", [])
    if set(personality_traits) & set(product_personalities):
        matching_traits = list(set(personality_traits) & set(product_personalities))
        reasons.append(f"Matches your {', '.join(matching_traits)} character")
    
    # Indonesian heritage
    if product.get("indonesian_heritage", False):
        reasons.append("🇮🇩 Proudly Indonesian brand supporting local industry")
    
    # Halal certification
    if product.get("halal_certified", False):
        reasons.append("☪️ Halal certified and safe for Muslim consumers")
    
    # Local ingredients
    local_ingredients = product.get("local_ingredients", [])
    if local_ingredients:
        reasons.append(f"Features authentic Indonesian ingredients: {', '.join(local_ingredients[:2])}")
    
    # Climate suitability
    if product.get("climate_suitability") == "tropical_all_day":
        reasons.append("🌴 Specially formulated for Indonesia's tropical climate")
    
    return " • ".join(reasons)

def create_recommendation_explanation(profile: Dict, recommendations: List[ProductRecommendation]) -> str:
    """Create overall explanation for the recommendations"""
    
    if not recommendations:
        return "I apologize, but no products currently match your specific criteria. Try adjusting your budget or preferences, or contact us for personalized assistance!"
    
    personality_traits = profile.get("personality_traits", ["unique character"])
    preferred_families = profile.get("fragrance_families", ["fresh"])
    
    explanation = f"Based on your {', '.join(personality_traits)} personality and love for {', '.join(preferred_families)} fragrances, "
    explanation += f"I've carefully selected {len(recommendations)} perfect matches from our Indonesian collection! ✨\n\n"
    
    top_match = recommendations[0]
    explanation += f"🎯 Top recommendation: **{top_match.name}** with {int(top_match.match_score*100)}% compatibility! "
    
    # Add insights about the selection
    indonesian_count = sum(1 for rec in recommendations if rec.indonesian_heritage)
    halal_count = sum(1 for rec in recommendations if rec.halal_certified)
    
    if indonesian_count > 0:
        explanation += f"\n\n🇮🇩 {indonesian_count} of these recommendations are authentic Indonesian brands, supporting our local fragrance industry."
    if halal_count > 0:
        explanation += f"\n☪️ {halal_count} products are halal certified for your peace of mind."
    
    explanation += f"\n\n🌴 All recommendations are specially curated for Indonesia's tropical climate and tested by local fragrance enthusiasts!"
    
    return explanation

def generate_alternative_suggestions(profile: Dict, recommendations: List[ProductRecommendation]) -> List[str]:
    """Generate alternative suggestions for broader exploration"""
    
    alternatives = []
    
    # Suggest exploring different families
    current_families = profile.get("fragrance_families", [])
    if "fresh" in current_families:
        alternatives.append("🌸 Also explore Floral category for elegant variations")
    if "floral" in current_families:
        alternatives.append("🌿 Consider Oriental scents for evening sophistication")
    
    # Budget suggestions
    budget_range = profile.get("budget_range", "moderate")
    if budget_range == "budget":
        alternatives.append("💰 Consider mid-range brands for enhanced longevity and complexity")
    elif budget_range == "luxury":
        alternatives.append("🎨 Explore artisanal Indonesian niche brands for unique signature scents")
    
    # Lifestyle suggestions
    alternatives.append("🔄 Consider building a fragrance wardrobe with 2-3 scents for different moods")
    alternatives.append("🌡️ Try fragrance layering techniques to adjust intensity for our tropical weather")
    alternatives.append("⭐ Join our community reviews to discover hidden gems from fellow Indonesian fragrance lovers")
    
    return alternatives

# ICP Integration Functions
async def sync_recommendations_to_icp(ctx: Context, user_id: str, recommendations: List[ProductRecommendation]) -> bool:
    """Sync recommendations to ICP canister backend"""
    
    try:
        # Prepare data for ICP canister
        recommendation_data = {
            "user_id": user_id,
            "recommendations": [
                {
                    "recommendation_id": f"rec_{user_id}_{rec.product_id}",
                    "user_id": user_id,
                    "product_id": rec.product_id,
                    "match_score": rec.match_score,
                    "personality_alignment": rec.match_score * 0.9,  # Simulated
                    "lifestyle_fit": rec.match_score * 0.85,  # Simulated
                    "occasion_match": rec.match_score * 0.8,  # Simulated
                    "budget_compatibility": rec.match_score * 0.95,  # Simulated
                    "reasoning": rec.reasoning,
                    "confidence_level": rec.match_score * 0.9,
                    "seasonal_relevance": 0.9,  # High for tropical climate
                    "trend_factor": 0.8,
                    "generated_at": int(datetime.now().timestamp()),
                    "user_feedback": None
                }
                for rec in recommendations
            ],
            "generated_at": datetime.now().timestamp()
        }
        
        # Call ICP canister
        result = await call_icp_canister(
            ctx, 
            "generate_ai_recommendations", 
            {"user_id": user_id}
        )
        
        if result.get("success"):
            ctx.logger.info(f"✅ Recommendations synced to ICP for user {user_id}")
            return True
        else:
            ctx.logger.error(f"⚠ ICP sync failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"⚠ ICP sync error: {e}")
        return False

async def get_recommendations_from_icp(ctx: Context, user_id: str) -> Optional[List[Dict]]:
    """Get recommendations from ICP canister"""
    
    try:
        result = await call_icp_canister(
            ctx,
            "get_recommendations_for_user",
            {"user_id": user_id}
        )
        
        if result.get("success") and result.get("result"):
            return result["result"]
        else:
            return None
            
    except Exception as e:
        ctx.logger.error(f"⚠ ICP retrieval error: {e}")
        return None

async def call_icp_canister(ctx: Context, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generic ICP canister call function"""
    
    try:
        endpoint = ICP_CONFIG["local_endpoint"]
        canister_id = ICP_CONFIG["canister_id"]
        
        # For local development, use DFX HTTP gateway
        dfx_url = f"{endpoint}/?canisterId={canister_id}"
        
        payload = {
            "type": "call",
            "method_name": method,
            "args": params
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
                    ctx.logger.error(f"⚠ ICP call failed: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
    except Exception as e:
        ctx.logger.error(f"⚠ ICP canister call error: {e}")
        return {"success": False, "error": str(e)}

async def test_icp_connection(ctx: Context) -> bool:
    """Test ICP connectivity"""
    try:
        result = await call_icp_canister(ctx, "greet", {"name": "Recommendation Agent Test"})
        return result.get("success", False)
    except:
        return False

async def notify_coordinator_recommendations_complete(user_id: str, session_id: str, response_data: Dict):
    """Notify coordinator that recommendations are complete"""
    try:
        coordinator_endpoint = "http://127.0.0.1:8000"
        
        journey_data = {
            "user_id": user_id,
            "session_id": session_id,
            "current_stage": "recommendations_generated",
            "data": {
                "recommendations": response_data["recommendations"],
                "total_found": response_data["total_found"]
            },
            "next_action": "show_recommendations",
            "timestamp": int(datetime.now().timestamp())
        }
        
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f"{coordinator_endpoint}/user_journey",
                json=journey_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    print(f"✅ Coordinator notified for user {user_id}")
                else:
                    print(f"⚠ Failed to notify coordinator: {response.status}")
                    
    except Exception as e:
        print(f"⚠ Coordinator notification error: {e}")

if __name__ == "__main__":
    recommendation_agent.run()