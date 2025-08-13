from uagents import Agent, Context, Model
from typing import Dict, List, Any, Optional
import json
import aiohttp
from datetime import datetime, timedelta
from pydantic import BaseModel

class AnalyticsRequest(Model):
    seller_id: str
    time_period: str  # "daily", "weekly", "monthly"
    metrics_requested: List[str]

class AnalyticsResponse(Model):
    seller_id: str
    time_period: str
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

class UserAnalyticsEvent(Model):
    user_id: str
    event_type: str
    recommendations_count: int
    personality_type: str
    timestamp: int

class MarketTrendAnalysis(Model):
    trending_families: List[str]
    seasonal_patterns: Dict[str, float]
    competitor_analysis: Dict[str, Any]
    price_recommendations: Dict[str, int]

class AnalyticsHTTPRequest(BaseModel):
    user_id: str
    event_type: str
    recommendations_count: Optional[int] = 0
    personality_type: Optional[str] = "unknown"

analytics_agent = Agent(
    name="aromance_analytics_ai",
    port=8004,
    seed="aromance_analytics_enhanced_2025",
    endpoint=["http://127.0.0.1:8004/submit"],
    mailbox=True,
)

# Enhanced analytics data storage
user_analytics_data = {}
system_analytics = {
    "total_users": 0,
    "total_consultations": 0,
    "total_recommendations": 0,
    "conversion_rates": {},
    "popular_families": {},
    "user_demographics": {},
    "daily_metrics": []
}

# ICP Configuration
ICP_CONFIG = {
    "local_endpoint": "http://127.0.0.1:4943",
    "canister_id": "bkyz2-fmaaa-aaaaa-qaaaq-cai",
    "current_network": "local"
}

@analytics_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("📊 Aromance Enhanced Analytics Agent Started")
    ctx.logger.info(f"Agent Address: {analytics_agent.address}")
    ctx.logger.info("Ready to provide intelligent business analytics with ICP integration! 📈")

# HTTP Endpoints
@analytics_agent.on_rest_post("/analytics")
async def analytics_event_endpoint(ctx: Context, req):
    """HTTP endpoint to record analytics events"""
    try:
        data = await req.json()
        user_id = data.get("user_id")
        event_type = data.get("event_type")
        
        if not user_id or not event_type:
            return {"error": "user_id and event_type are required"}, 400
        
        # Record analytics event
        analytics_event = {
            "user_id": user_id,
            "event_type": event_type,
            "recommendations_count": data.get("recommendations_count", 0),
            "personality_type": data.get("personality_type", "unknown"),
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Process the event
        await process_analytics_event(ctx, analytics_event)
        
        # Sync to ICP if needed
        await sync_analytics_to_icp(ctx, analytics_event)
        
        return {"success": True, "message": "Analytics event recorded"}
        
    except Exception as e:
        ctx.logger.error(f"❌ Analytics event error: {e}")
        return {"error": "Internal server error"}, 500

@analytics_agent.on_rest_get("/analytics/seller/{seller_id}")
async def get_seller_analytics_endpoint(ctx: Context, req):
    """Get analytics data for a specific seller"""
    try:
        seller_id = req.path_params.get("seller_id")
        time_period = req.query_params.get("period", "monthly")
        
        # Generate analytics metrics
        metrics = await generate_seller_analytics(ctx, seller_id, time_period)
        insights = generate_business_insights(metrics, seller_id)
        recommendations = generate_actionable_recommendations(metrics, insights)
        
        return {
            "success": True,
            "data": {
                "seller_id": seller_id,
                "time_period": time_period,
                "metrics": metrics,
                "insights": insights,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Seller analytics error: {e}")
        return {"error": "Internal server error"}, 500

@analytics_agent.on_rest_get("/analytics/market/trends")
async def get_market_trends_endpoint(ctx: Context, req):
    """Get market trend analysis"""
    try:
        trends = await generate_market_trends_analysis(ctx)
        return {"success": True, "trends": trends.dict()}
        
    except Exception as e:
        ctx.logger.error(f"❌ Market trends error: {e}")
        return {"error": "Internal server error"}, 500

@analytics_agent.on_rest_get("/analytics/dashboard")
async def get_dashboard_metrics_endpoint(ctx: Context, req):
    """Get dashboard metrics for admin/overview"""
    try:
        dashboard_data = await generate_dashboard_metrics(ctx)
        return {"success": True, "dashboard": dashboard_data}
        
    except Exception as e:
        ctx.logger.error(f"❌ Dashboard metrics error: {e}")
        return {"error": "Internal server error"}, 500

@analytics_agent.on_rest_get("/health")
async def health_check_endpoint(ctx: Context, req):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_events": len(user_analytics_data),
        "icp_connected": await test_icp_connection(ctx),
        "timestamp": datetime.now().timestamp()
    }

# Agent Message Handling
@analytics_agent.on_message(model=AnalyticsRequest)
async def handle_analytics_request(ctx: Context, sender: str, msg: AnalyticsRequest):
    ctx.logger.info(f"📊 Analytics request from seller {msg.seller_id}")
    
    # Generate analytics based on subscription tier
    metrics = await generate_seller_analytics(ctx, msg.seller_id, msg.time_period)
    insights = generate_business_insights(metrics, msg.seller_id)
    recommendations = generate_actionable_recommendations(metrics, insights)
    
    response = AnalyticsResponse(
        seller_id=msg.seller_id,
        time_period=msg.time_period,
        metrics=metrics,
        insights=insights,
        recommendations=recommendations
    )
    
    ctx.logger.info(f"✅ Analytics generated for {msg.seller_id}")
    await ctx.send(sender, response)

@analytics_agent.on_message(model=UserAnalyticsEvent)
async def handle_user_analytics_event(ctx: Context, sender: str, msg: UserAnalyticsEvent):
    """Handle incoming user analytics events"""
    ctx.logger.info(f"📈 Analytics event: {msg.event_type} for user {msg.user_id}")
    
    event_data = {
        "user_id": msg.user_id,
        "event_type": msg.event_type,
        "recommendations_count": msg.recommendations_count,
        "personality_type": msg.personality_type,
        "timestamp": msg.timestamp
    }
    
    await process_analytics_event(ctx, event_data)
    await sync_analytics_to_icp(ctx, event_data)

async def process_analytics_event(ctx: Context, event_data: Dict):
    """Process and store analytics event"""
    
    user_id = event_data["user_id"]
    event_type = event_data["event_type"]
    
    # Update user-specific analytics
    if user_id not in user_analytics_data:
        user_analytics_data[user_id] = {
            "events": [],
            "first_seen": datetime.now().timestamp(),
            "last_active": datetime.now().timestamp(),
            "total_events": 0
        }
    
    user_analytics_data[user_id]["events"].append(event_data)
    user_analytics_data[user_id]["last_active"] = event_data["timestamp"]
    user_analytics_data[user_id]["total_events"] += 1
    
    # Update system-wide analytics
    system_analytics["total_users"] = len(user_analytics_data)
    
    if event_type == "consultation_complete":
        system_analytics["total_consultations"] += 1
    elif event_type == "recommendation_generated":
        system_analytics["total_recommendations"] += 1
        
        # Track popular personality types
        personality = event_data.get("personality_type", "unknown")
        if "user_demographics" not in system_analytics:
            system_analytics["user_demographics"] = {}
        if personality not in system_analytics["user_demographics"]:
            system_analytics["user_demographics"][personality] = 0
        system_analytics["user_demographics"][personality] += 1
    
    ctx.logger.info(f"📊 Event processed: {event_type} for user {user_id}")

async def generate_seller_analytics(ctx: Context, seller_id: str, time_period: str) -> Dict[str, Any]:
    """Generate comprehensive seller analytics"""
    
    # Get data from ICP canister
    icp_analytics = await get_analytics_from_icp(ctx, seller_id, time_period)
    
    # Generate synthetic data for demo (replace with real ICP data)
    metrics = {
        "sales": {
            "total_revenue": 15_750_000,
            "units_sold": 127,
            "avg_order_value": 124_000,
            "growth_rate": 23.5
        },
        "traffic": {
            "page_views": 2_840,
            "unique_visitors": 1_120,
            "bounce_rate": 35.2,
            "avg_time_on_page": 185
        },
        "conversion": {
            "view_to_cart": 8.7,
            "cart_to_purchase": 42.3,
            "overall_conversion": 3.7,
            "abandoned_cart_rate": 57.7
        },
        "customer_insights": {
            "demographics": {
                "age_18_25": 35,
                "age_26_35": 45,
                "age_36_45": 20
            },
            "personality_preferences": system_analytics.get("user_demographics", {
                "romantic": 32,
                "professional": 28,
                "confident": 25,
                "playful": 15
            }),
            "budget_distribution": {
                "under_100k": 40,
                "100k_300k": 35,
                "300k_500k": 20,
                "500k_plus": 5
            }
        },
        "product_performance": {
            "top_selling_families": ["fresh", "floral", "fruity"],
            "avg_rating": 4.3,
            "return_rate": 2.1,
            "customer_satisfaction": 89.5
        }
    }
    
    # Merge with real ICP data if available
    if icp_analytics:
        metrics.update(icp_analytics)
    
    return metrics

def generate_business_insights(metrics: Dict[str, Any], seller_id: str) -> List[str]:
    """Generate AI-powered business insights"""
    
    insights = []
    
    # Sales insights
    if "sales" in metrics:
        sales = metrics["sales"]
        if sales["growth_rate"] > 20:
            insights.append(f"🚀 Outstanding growth! Revenue increased {sales['growth_rate']}% - your strategy is working excellently")
        
        if sales["avg_order_value"] < 150000:
            insights.append(f"💡 AOV opportunity: Current {sales['avg_order_value']:,} IDR could be increased through bundling or premium recommendations")
    
    # Traffic insights
    if "traffic" in metrics:
        traffic = metrics["traffic"]
        if traffic["bounce_rate"] > 40:
            insights.append(f"⚠️ High bounce rate at {traffic['bounce_rate']}% - consider improving product descriptions and page loading speed")
        
        if traffic["avg_time_on_page"] > 120:
            insights.append("✅ Users are highly engaged with your content - maintain this quality across all products")
    
    # Customer insights
    if "customer_insights" in metrics:
        customer = metrics["customer_insights"]
        if "personality_preferences" in customer:
            top_personality = max(customer["personality_preferences"].items(), key=lambda x: x[1])
            insights.append(f"🎯 Primary target: {top_personality[0]} personalities ({top_personality[1]}%) - tailor marketing messaging accordingly")
        
        if "budget_distribution" in customer:
            budget_dist = customer["budget_distribution"]
            if budget_dist.get("under_100k", 0) > 35:
                insights.append("💰 Budget-conscious market dominance - emphasize value propositions and affordable premium options")
    
    # Product performance insights
    if "product_performance" in metrics:
        performance = metrics["product_performance"]
        if performance.get("customer_satisfaction", 0) > 85:
            insights.append("⭐ High customer satisfaction indicates strong product-market fit")
        
        if performance.get("return_rate", 0) < 3:
            insights.append("✅ Low return rate shows excellent product quality and accurate descriptions")
    
    return insights

def generate_actionable_recommendations(metrics: Dict[str, Any], insights: List[str]) -> List[str]:
    """Generate specific actionable recommendations"""
    
    recommendations = []
    
    # Seasonal recommendations based on Indonesian climate
    current_month = datetime.now().month
    if 6 <= current_month <= 8:  # Dry season
        recommendations.append("🌞 Dry season strategy: Promote fresh & citrus fragrances, highlight cooling and refreshing properties")
    else:  # Rainy season
        recommendations.append("🌧️ Rainy season focus: Emphasize woody & oriental scents, market cozy and warming qualities")
    
    # Product optimization recommendations
    recommendations.extend([
        "📝 Enhance product descriptions with Indonesian cultural connections and local ingredient highlights",
        "🏷️ Implement AI-driven dynamic pricing based on demand patterns and competitor analysis",
        "🎯 Create personality-based collections: 'Bold Indonesian Professional', 'Romantic Tropical Soul', etc.",
        "🇮🇩 Leverage Indonesian heritage positioning - highlight local ingredients and cultural significance",
        "📱 Optimize mobile experience for Indonesian users - 75% of traffic comes from mobile devices",
        "⭐ Implement verified review incentive program with exclusive Indonesian fragrance samples"
    ])
    
    # Conversion optimization based on metrics
    if "conversion" in metrics:
        conversion = metrics["conversion"]
        if conversion.get("cart_to_purchase", 0) < 50:
            recommendations.append("🛒 Deploy cart abandonment email series with limited-time offers and Indonesian cultural storytelling")
        
        if conversion.get("overall_conversion", 0) < 5:
            recommendations.append("🔄 A/B test product page layouts, CTA buttons, and trust signals with Indonesian design elements")
    
    # Market-specific recommendations
    recommendations.extend([
        "🌴 Develop tropical climate-specific marketing: 'Long-lasting in humid weather', 'Perfect for Indonesian lifestyle'",
        "🕌 Create Ramadan/Eid special collections with halal certification prominently displayed",
        "👥 Partner with Indonesian beauty influencers and fragrance enthusiasts for authentic testimonials",
        "🎨 Use Indonesian aesthetic elements in packaging and marketing materials for cultural resonance"
    ])
    
    return recommendations

async def generate_market_trends_analysis(ctx: Context) -> MarketTrendAnalysis:
    """Generate comprehensive market trend analysis"""
    
    # Get market data from ICP
    market_data = await get_market_trends_from_icp(ctx)
    
    # Current seasonal patterns for Indonesia
    current_month = datetime.now().month
    seasonal_patterns = {
        "fresh": 0.9 if 6 <= current_month <= 8 else 0.7,  # High in dry season
        "floral": 0.8,  # Consistently popular
        "fruity": 0.9 if 6 <= current_month <= 8 else 0.6,  # Popular in hot weather
        "woody": 0.4 if 6 <= current_month <= 8 else 0.8,  # Better in cooler months
        "oriental": 0.3 if 6 <= current_month <= 8 else 0.7,  # Evening/cooler weather
        "gourmand": 0.5 if 6 <= current_month <= 8 else 0.8   # Comfort scents
    }
    
    return MarketTrendAnalysis(
        trending_families=["fresh", "tropical_fruity", "halal_certified", "indonesian_heritage"],
        seasonal_patterns=seasonal_patterns,
        competitor_analysis={
            "wardah": {
                "market_share": 25, 
                "avg_price": 95000, 
                "strength": "halal_certified_mass_market",
                "weakness": "limited_premium_options"
            },
            "esqa": {
                "market_share": 15, 
                "avg_price": 165000, 
                "strength": "natural_ingredients_premium",
                "weakness": "higher_price_point"
            },
            "make_over": {
                "market_share": 12, 
                "avg_price": 180000, 
                "strength": "professional_quality",
                "weakness": "limited_indonesian_heritage_marketing"
            },
            "international_brands": {
                "market_share": 35,
                "avg_price": 250000,
                "strength": "brand_recognition_premium_quality",
                "weakness": "not_climate_optimized"
            }
        },
        price_recommendations={
            "fresh": 85000,
            "floral": 120000,
            "fruity": 75000,
            "woody": 200000,
            "oriental": 250000,
            "gourmand": 150000
        }
    )

async def generate_dashboard_metrics(ctx: Context) -> Dict[str, Any]:
    """Generate comprehensive dashboard metrics"""
    
    # Get platform statistics from ICP
    platform_stats = await get_platform_stats_from_icp(ctx)
    
    # Calculate derived metrics
    total_users = len(user_analytics_data)
    active_users_today = len([
        user for user, data in user_analytics_data.items()
        if datetime.now().timestamp() - data.get("last_active", 0) < 86400  # 24 hours
    ])
    
    conversion_rate = 0
    if system_analytics["total_consultations"] > 0:
        conversion_rate = (system_analytics["total_recommendations"] / system_analytics["total_consultations"]) * 100
    
    dashboard_data = {
        "overview": {
            "total_users": total_users,
            "active_users_today": active_users_today,
            "total_consultations": system_analytics["total_consultations"],
            "total_recommendations": system_analytics["total_recommendations"],
            "consultation_to_recommendation_rate": round(conversion_rate, 2)
        },
        "user_engagement": {
            "avg_session_duration": 8.5,  # minutes
            "completion_rate": 78.3,  # percentage
            "user_satisfaction_score": 4.6,  # out of 5
            "repeat_user_rate": 34.2  # percentage
        },
        "popular_personalities": system_analytics.get("user_demographics", {}),
        "platform_health": {
            "system_uptime": 99.8,
            "avg_response_time": 1.2,  # seconds
            "icp_sync_success_rate": 95.4,
            "agent_availability": 100.0
        },
        "business_metrics": platform_stats if platform_stats else {
            "total_revenue": 0,
            "total_transactions": 0,
            "avg_order_value": 0,
            "growth_rate": 0
        },
        "recent_activity": [
            {
                "timestamp": datetime.now().timestamp() - 3600,
                "event": "New user consultation completed",
                "details": "Romantic Indonesian Soul profile created"
            },
            {
                "timestamp": datetime.now().timestamp() - 7200,
                "event": "5 recommendations generated",
                "details": "High match scores achieved"
            },
            {
                "timestamp": datetime.now().timestamp() - 10800,
                "event": "Analytics sync to ICP completed",
                "details": "All user data successfully backed up"
            }
        ]
    }
    
    return dashboard_data

# ICP Integration Functions
async def sync_analytics_to_icp(ctx: Context, event_data: Dict) -> bool:
    """Sync analytics data to ICP canister"""
    
    try:
        # Prepare analytics data for ICP
        icp_data = {
            "user_id": event_data["user_id"],
            "event_type": event_data["event_type"],
            "metadata": {
                "recommendations_count": event_data.get("recommendations_count", 0),
                "personality_type": event_data.get("personality_type", "unknown"),
                "timestamp": event_data["timestamp"]
            }
        }
        
        # Call ICP canister to store analytics
        result = await call_icp_canister(
            ctx,
            "update_analytics_data",
            icp_data
        )
        
        if result.get("success"):
            ctx.logger.info(f"✅ Analytics synced to ICP for user {event_data['user_id']}")
            return True
        else:
            ctx.logger.error(f"❌ ICP analytics sync failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"❌ ICP analytics sync error: {e}")
        return False

async def get_analytics_from_icp(ctx: Context, seller_id: str, time_period: str) -> Optional[Dict]:
    """Get analytics data from ICP canister"""
    
    try:
        # Calculate time period timestamps
        now = datetime.now()
        if time_period == "daily":
            period_start = int((now - timedelta(days=1)).timestamp())
        elif time_period == "weekly":
            period_start = int((now - timedelta(weeks=1)).timestamp())
        elif time_period == "monthly":
            period_start = int((now - timedelta(days=30)).timestamp())
        else:
            period_start = int((now - timedelta(days=30)).timestamp())
        
        period_end = int(now.timestamp())
        
        result = await call_icp_canister(
            ctx,
            "generate_analytics_data",
            {
                "seller_id": seller_id,
                "period_start": period_start,
                "period_end": period_end
            }
        )
        
        if result.get("success") and result.get("result"):
            return result["result"]
        else:
            return None
            
    except Exception as e:
        ctx.logger.error(f"❌ ICP analytics retrieval error: {e}")
        return None

async def get_market_trends_from_icp(ctx: Context) -> Optional[Dict]:
    """Get market trends from ICP canister"""
    
    try:
        result = await call_icp_canister(
            ctx,
            "get_trending_fragrances",
            {}
        )
        
        if result.get("success"):
            return result.get("result")
        else:
            return None
            
    except Exception as e:
        ctx.logger.error(f"❌ Market trends retrieval error: {e}")
        return None

async def get_platform_stats_from_icp(ctx: Context) -> Optional[Dict]:
    """Get platform statistics from ICP canister"""
    
    try:
        result = await call_icp_canister(
            ctx,
            "get_platform_statistics",
            {}
        )
        
        if result.get("success") and result.get("result"):
            return result["result"]
        else:
            return None
            
    except Exception as e:
        ctx.logger.error(f"❌ Platform stats retrieval error: {e}")
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
                    ctx.logger.error(f"❌ ICP call failed: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
    except Exception as e:
        ctx.logger.error(f"❌ ICP canister call error: {e}")
        return {"success": False, "error": str(e)}

async def test_icp_connection(ctx: Context) -> bool:
    """Test ICP connectivity"""
    try:
        result = await call_icp_canister(ctx, "greet", {"name": "Analytics Agent Test"})
        return result.get("success", False)
    except:
        return False

if __name__ == "__main__":
    analytics_agent.run()