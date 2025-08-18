from uagents import Agent, Context, Model
from typing import Dict, List, Any, Optional
import json
import aiohttp
from datetime import datetime
from pydantic import BaseModel

class InventoryUpdate(Model):
    product_id: str
    action: str  # "add", "update", "remove", "restock", "check_availability"
    data: Dict[str, Any]

class InventoryQuery(Model):
    seller_id: str
    filters: Optional[Dict[str, Any]] = None

class InventoryResponse(Model):
    products: List[Dict[str, Any]]
    total_count: int
    low_stock_alerts: List[str]
    recommendations: List[str]

class StockAlert(Model):
    product_id: str
    current_stock: int
    recommended_restock: int
    urgency_level: str

# NEW: REST endpoint models using new uAgents syntax
class InventoryActionRequest(Model):
    user_id: str
    product_ids: List[str]
    action: str
    quantity: Optional[int] = 1

class InventoryActionResponse(Model):
    success: bool
    availability: Optional[Dict[str, Any]] = None
    reservation: Optional[Dict[str, Any]] = None
    release: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SellerInventoryResponse(Model):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class InventoryAlertsResponse(Model):
    success: bool
    alerts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class InventoryRecommendationsResponse(Model):
    success: bool
    recommendations: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class HealthCheckResponse(Model):
    status: str
    total_products: int
    low_stock_products: int
    icp_connected: bool
    timestamp: float

inventory_agent = Agent(
    name="aromance_inventory_ai",
    port=8005,
    seed="aromance_inventory_enhanced_2025",
    endpoint=["http://127.0.0.1:8005/submit"],
    mailbox=True,
)

# Enhanced inventory database - synced with recommendation agent
inventory_database = {
    "IDN_001": {
        "product_id": "IDN_001",
        "seller_id": "wardah_official",
        "name": "Wardah Scentsations Wonder Bloom",
        "brand": "Wardah",
        "price_idr": 89000,
        "fragrance_family": "floral",
        "stock_quantity": 150,
        "min_stock_threshold": 20,
        "max_stock_capacity": 500,
        "reserved_quantity": 5,
        "available_quantity": 145,
        "last_restocked": int(datetime.now().timestamp()) - 86400 * 7,  # 7 days ago
        "supplier_info": {
            "supplier_name": "PT Wardah Kosmetik Indonesia",
            "lead_time_days": 14,
            "minimum_order_quantity": 50
        },
        "sales_velocity": {
            "daily_avg": 3.2,
            "weekly_avg": 22.4,
            "monthly_avg": 89.6
        },
        "seasonal_demand": {
            "high_season": ["march", "april", "may", "june"],
            "low_season": ["august", "september"]
        },
        "location": "Jakarta Warehouse",
        "status": "active"
    },
    "IDN_002": {
        "product_id": "IDN_002",
        "seller_id": "esqa_official",
        "name": "Esqa Natural Bergamot & Neroli",
        "brand": "Esqa",
        "price_idr": 165000,
        "fragrance_family": "fresh",
        "stock_quantity": 75,
        "min_stock_threshold": 15,
        "max_stock_capacity": 200,
        "reserved_quantity": 3,
        "available_quantity": 72,
        "last_restocked": int(datetime.now().timestamp()) - 86400 * 5,  # 5 days ago
        "supplier_info": {
            "supplier_name": "Esqa Beauty Indonesia",
            "lead_time_days": 10,
            "minimum_order_quantity": 25
        },
        "sales_velocity": {
            "daily_avg": 2.1,
            "weekly_avg": 14.7,
            "monthly_avg": 58.8
        },
        "seasonal_demand": {
            "high_season": ["june", "july", "august"],
            "low_season": ["november", "december", "january"]
        },
        "location": "Surabaya Warehouse",
        "status": "active"
    },
    "IDN_003": {
        "product_id": "IDN_003",
        "seller_id": "makeover_official",
        "name": "Make Over Eau De Toilette Blooming Garden",
        "brand": "Make Over",
        "price_idr": 175000,
        "fragrance_family": "floral",
        "stock_quantity": 8,  # Low stock for testing alerts
        "min_stock_threshold": 10,
        "max_stock_capacity": 150,
        "reserved_quantity": 2,
        "available_quantity": 6,
        "last_restocked": int(datetime.now().timestamp()) - 86400 * 12,  # 12 days ago
        "supplier_info": {
            "supplier_name": "Make Over Indonesia",
            "lead_time_days": 7,
            "minimum_order_quantity": 30
        },
        "sales_velocity": {
            "daily_avg": 1.8,
            "weekly_avg": 12.6,
            "monthly_avg": 50.4
        },
        "seasonal_demand": {
            "high_season": ["february", "march", "april", "may"],
            "low_season": ["september", "october"]
        },
        "location": "Bandung Warehouse",
        "status": "low_stock"
    }
}

# ICP Configuration
ICP_CONFIG = {
    "local_endpoint": "http://127.0.0.1:4943",
    "canister_id": "bkyz2-fmaaa-aaaaa-qaaaq-cai",
    "current_network": "local"
}

@inventory_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("📦 Aromance Enhanced Inventory Agent Started")
    ctx.logger.info(f"Agent Address: {inventory_agent.address}")
    ctx.logger.info(f"Managing {len(inventory_database)} products")
    ctx.logger.info("Ready for intelligent inventory management with ICP integration! 📋")
    
    # Perform initial stock check
    await perform_stock_health_check(ctx)

# FIXED: HTTP Endpoints using new uAgents syntax
@inventory_agent.on_rest_post("/inventory", InventoryActionRequest, InventoryActionResponse)
async def inventory_action_endpoint(ctx: Context, req: InventoryActionRequest) -> InventoryActionResponse:
    """HTTP endpoint for inventory actions"""
    try:
        user_id = req.user_id
        product_ids = req.product_ids
        action = req.action
        quantity = req.quantity or 1
        
        if not user_id:
            return InventoryActionResponse(
                success=False,
                error="user_id is required"
            )
        
        ctx.logger.info(f"📦 Inventory {action} for user {user_id}: {product_ids}")
        
        if action == "check_availability":
            availability_result = await check_product_availability(ctx, product_ids)
            return InventoryActionResponse(
                success=True,
                availability=availability_result
            )
            
        elif action == "reserve_products":
            reservation_result = await reserve_products(ctx, product_ids, quantity, user_id)
            return InventoryActionResponse(
                success=True,
                reservation=reservation_result
            )
            
        elif action == "release_reservation":
            release_result = await release_product_reservation(ctx, product_ids, user_id)
            return InventoryActionResponse(
                success=True,
                release=release_result
            )
        
        else:
            return InventoryActionResponse(
                success=False,
                error=f"Unknown action: {action}"
            )
            
    except Exception as e:
        ctx.logger.error(f"❌ Inventory action error: {e}")
        return InventoryActionResponse(
            success=False,
            error="Internal server error"
        )

@inventory_agent.on_rest_get("/inventory/seller/{seller_id}", SellerInventoryResponse)
async def get_seller_inventory_endpoint(ctx: Context, req) -> SellerInventoryResponse:
    """Get inventory for a specific seller"""
    try:
        seller_id = req.path_params.get("seller_id")
        
        # Filter products by seller
        seller_products = [
            product for product in inventory_database.values()
            if product.get("seller_id") == seller_id
        ]
        
        # Generate alerts and recommendations
        low_stock_alerts = generate_stock_alerts(seller_products)
        recommendations = generate_inventory_recommendations(seller_products)
        
        return SellerInventoryResponse(
            success=True,
            data={
                "products": seller_products,
                "total_count": len(seller_products),
                "low_stock_alerts": low_stock_alerts,
                "recommendations": recommendations
            }
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Seller inventory error: {e}")
        return SellerInventoryResponse(
            success=False,
            error="Internal server error"
        )

@inventory_agent.on_rest_get("/inventory/alerts", InventoryAlertsResponse)
async def get_inventory_alerts_endpoint(ctx: Context, req) -> InventoryAlertsResponse:
    """Get all inventory alerts"""
    try:
        all_products = list(inventory_database.values())
        alerts = generate_stock_alerts(all_products)
        
        # Get critical alerts (out of stock or very low)
        critical_alerts = []
        warning_alerts = []
        
        for product in all_products:
            if product["stock_quantity"] == 0:
                critical_alerts.append({
                    "product_id": product["product_id"],
                    "name": product["name"],
                    "level": "critical",
                    "message": f"OUT OF STOCK: {product['name']}"
                })
            elif product["stock_quantity"] <= product["min_stock_threshold"]:
                warning_alerts.append({
                    "product_id": product["product_id"],
                    "name": product["name"],
                    "level": "warning",
                    "current_stock": product["stock_quantity"],
                    "threshold": product["min_stock_threshold"],
                    "message": f"LOW STOCK: {product['name']} - {product['stock_quantity']} remaining"
                })
        
        return InventoryAlertsResponse(
            success=True,
            alerts={
                "critical": critical_alerts,
                "warning": warning_alerts,
                "summary": alerts
            }
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Inventory alerts error: {e}")
        return InventoryAlertsResponse(
            success=False,
            error="Internal server error"
        )

@inventory_agent.on_rest_get("/inventory/recommendations", InventoryRecommendationsResponse)
async def get_inventory_recommendations_endpoint(ctx: Context, req) -> InventoryRecommendationsResponse:
    """Get inventory management recommendations"""
    try:
        all_products = list(inventory_database.values())
        recommendations = generate_inventory_recommendations(all_products)
        
        # Enhanced recommendations with actionable insights
        enhanced_recommendations = []
        
        for rec in recommendations:
            enhanced_recommendations.append({
                "recommendation": rec,
                "priority": determine_recommendation_priority(rec),
                "category": categorize_recommendation(rec)
            })
        
        return InventoryRecommendationsResponse(
            success=True,
            recommendations=enhanced_recommendations
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Inventory recommendations error: {e}")
        return InventoryRecommendationsResponse(
            success=False,
            error="Internal server error"
        )

@inventory_agent.on_rest_get("/health", HealthCheckResponse)
async def health_check_endpoint(ctx: Context, req) -> HealthCheckResponse:
    """Health check endpoint"""
    try:
        total_products = len(inventory_database)
        low_stock_count = sum(1 for p in inventory_database.values() if p["stock_quantity"] <= p["min_stock_threshold"])
        icp_connected = await test_icp_connection(ctx)
        
        return HealthCheckResponse(
            status="healthy",
            total_products=total_products,
            low_stock_products=low_stock_count,
            icp_connected=icp_connected,
            timestamp=datetime.now().timestamp()
        )
    except Exception as e:
        ctx.logger.error(f"❌ Health check error: {e}")
        return HealthCheckResponse(
            status="error",
            total_products=0,
            low_stock_products=0,
            icp_connected=False,
            timestamp=datetime.now().timestamp()
        )

# Agent Message Handling
@inventory_agent.on_message(model=InventoryUpdate)
async def handle_inventory_update(ctx: Context, sender: str, msg: InventoryUpdate):
    ctx.logger.info(f"📦 Inventory {msg.action} for product {msg.product_id}")
    
    if msg.action == "add":
        inventory_database[msg.product_id] = msg.data
        ctx.logger.info(f"✅ Product {msg.product_id} added to inventory")
        
    elif msg.action == "update":
        if msg.product_id in inventory_database:
            inventory_database[msg.product_id].update(msg.data)
            ctx.logger.info(f"✅ Product {msg.product_id} updated")
        
    elif msg.action == "remove":
        if msg.product_id in inventory_database:
            del inventory_database[msg.product_id]
            ctx.logger.info(f"✅ Product {msg.product_id} removed")
    
    elif msg.action == "restock":
        if msg.product_id in inventory_database:
            new_quantity = msg.data.get("quantity", 0)
            inventory_database[msg.product_id]["stock_quantity"] += new_quantity
            inventory_database[msg.product_id]["last_restocked"] = int(datetime.now().timestamp())
            ctx.logger.info(f"✅ Product {msg.product_id} restocked with {new_quantity} units")
    
    # Generate stock alerts if needed
    await check_stock_levels(ctx, msg.product_id)
    
    # Sync to ICP
    await sync_inventory_to_icp(ctx, msg.product_id, msg.action, msg.data)

@inventory_agent.on_message(model=InventoryQuery)
async def handle_inventory_query(ctx: Context, sender: str, msg: InventoryQuery):
    ctx.logger.info(f"📋 Inventory query from seller {msg.seller_id}")
    
    # Filter products by seller
    seller_products = [
        product for product in inventory_database.values()
        if product.get("seller_id") == msg.seller_id
    ]
    
    # Apply additional filters if provided
    if msg.filters:
        seller_products = apply_inventory_filters(seller_products, msg.filters)
    
    # Generate alerts and recommendations
    low_stock_alerts = generate_stock_alerts(seller_products)
    recommendations = generate_inventory_recommendations(seller_products)
    
    response = InventoryResponse(
        products=seller_products,
        total_count=len(seller_products),
        low_stock_alerts=low_stock_alerts,
        recommendations=recommendations
    )
    
    await ctx.send(sender, response)

# Core Inventory Functions
async def check_product_availability(ctx: Context, product_ids: List[str]) -> Dict[str, Any]:
    """Check availability of specific products"""
    
    availability = {}
    
    for product_id in product_ids:
        if product_id in inventory_database:
            product = inventory_database[product_id]
            available_qty = product["available_quantity"]
            
            availability[product_id] = {
                "available": available_qty > 0,
                "quantity_available": available_qty,
                "stock_level": determine_stock_level(product),
                "estimated_restock": estimate_restock_date(product) if available_qty == 0 else None
            }
        else:
            availability[product_id] = {
                "available": False,
                "quantity_available": 0,
                "stock_level": "not_found",
                "estimated_restock": None
            }
    
    return availability

async def reserve_products(ctx: Context, product_ids: List[str], quantity: int, user_id: str) -> Dict[str, Any]:
    """Reserve products for a user"""
    
    reservations = {}
    
    for product_id in product_ids:
        if product_id in inventory_database:
            product = inventory_database[product_id]
            
            if product["available_quantity"] >= quantity:
                # Make reservation
                product["reserved_quantity"] += quantity
                product["available_quantity"] -= quantity
                
                reservations[product_id] = {
                    "reserved": True,
                    "quantity": quantity,
                    "reservation_id": f"res_{user_id}_{product_id}_{int(datetime.now().timestamp())}",
                    "expires_at": int(datetime.now().timestamp()) + 3600  # 1 hour
                }
                
                ctx.logger.info(f"✅ Reserved {quantity} units of {product_id} for user {user_id}")
            else:
                reservations[product_id] = {
                    "reserved": False,
                    "reason": "insufficient_stock",
                    "available_quantity": product["available_quantity"]
                }
        else:
            reservations[product_id] = {
                "reserved": False,
                "reason": "product_not_found"
            }
    
    return reservations

async def release_product_reservation(ctx: Context, product_ids: List[str], user_id: str) -> Dict[str, Any]:
    """Release product reservations"""
    
    releases = {}
    
    for product_id in product_ids:
        if product_id in inventory_database:
            # This is simplified - in real system, you'd track reservations by user
            releases[product_id] = {
                "released": True,
                "message": f"Reservation released for {product_id}"
            }
            ctx.logger.info(f"✅ Released reservation for {product_id} by user {user_id}")
        else:
            releases[product_id] = {
                "released": False,
                "reason": "product_not_found"
            }
    
    return releases

def determine_stock_level(product: Dict) -> str:
    """Determine stock level category"""
    
    stock_qty = product["stock_quantity"]
    threshold = product["min_stock_threshold"]
    
    if stock_qty == 0:
        return "out_of_stock"
    elif stock_qty <= threshold:
        return "low_stock"
    elif stock_qty <= threshold * 2:
        return "moderate_stock"
    else:
        return "good_stock"

def estimate_restock_date(product: Dict) -> str:
    """Estimate when product will be restocked"""
    
    lead_time = product["supplier_info"]["lead_time_days"]
    estimated_date = datetime.now() + datetime.timedelta(days=lead_time)
    
    return estimated_date.strftime("%Y-%m-%d")

async def check_stock_levels(ctx: Context, product_id: str):
    """Check and alert for low stock levels"""
    
    if product_id not in inventory_database:
        return
    
    product = inventory_database[product_id]
    current_stock = product["stock_quantity"]
    min_threshold = product["min_stock_threshold"]
    
    if current_stock <= min_threshold:
        alert = StockAlert(
            product_id=product_id,
            current_stock=current_stock,
            recommended_restock=min_threshold * 3,
            urgency_level="high" if current_stock == 0 else "medium"
        )
        
        ctx.logger.warning(f"⚠️ Low stock alert: {product['name']} - {current_stock} remaining")
        
        # Update product status
        if current_stock == 0:
            product["status"] = "out_of_stock"
        else:
            product["status"] = "low_stock"

def apply_inventory_filters(products: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Apply filters to inventory query"""
    
    filtered = products
    
    if "fragrance_family" in filters:
        family = filters["fragrance_family"]
        filtered = [p for p in filtered if p.get("fragrance_family") == family]
    
    if "low_stock_only" in filters and filters["low_stock_only"]:
        filtered = [p for p in filtered if p.get("stock_quantity", 0) <= p.get("min_stock_threshold", 5)]
    
    if "price_range" in filters:
        min_price, max_price = filters["price_range"]
        filtered = [p for p in filtered if min_price <= p.get("price_idr", 0) <= max_price]
    
    if "status" in filters:
        status = filters["status"]
        filtered = [p for p in filtered if p.get("status") == status]
    
    if "location" in filters:
        location = filters["location"]
        filtered = [p for p in filtered if location.lower() in p.get("location", "").lower()]
    
    return filtered

def generate_stock_alerts(products: List[Dict]) -> List[str]:
    """Generate stock alert messages"""
    
    alerts = []
    
    for product in products:
        stock = product.get("stock_quantity", 0)
        threshold = product.get("min_stock_threshold", 5)
        name = product.get("name", "Unknown Product")
        
        if stock == 0:
            alerts.append(f"🚨 OUT OF STOCK: {name} - Immediate restock required!")
        elif stock <= threshold:
            alerts.append(f"⚠️ LOW STOCK: {name} - Only {stock} units remaining")
        elif stock <= threshold * 1.5:
            alerts.append(f"📊 MODERATE STOCK: {name} - {stock} units (consider restocking soon)")
    
    return alerts

def generate_inventory_recommendations(products: List[Dict]) -> List[str]:
    """Generate AI-powered inventory recommendations"""
    
    recommendations = []
    
    # Analyze product performance
    total_products = len(products)
    low_stock_count = sum(1 for p in products if p.get("stock_quantity", 0) <= p.get("min_stock_threshold", 5))
    out_of_stock_count = sum(1 for p in products if p.get("stock_quantity", 0) == 0)
    
    if out_of_stock_count > 0:
        recommendations.append(f"🚨 URGENT: {out_of_stock_count} products are out of stock - prioritize immediate restocking")
    
    if low_stock_count > total_products * 0.3:
        recommendations.append(f"📈 Consider increasing overall inventory levels - {low_stock_count}/{total_products} products running low")
    
    # Seasonal recommendations
    current_month = datetime.now().month
    month_name = datetime.now().strftime("%B").lower()
    
    if 6 <= current_month <= 8:  # Dry season in Indonesia
        recommendations.append("🌞 Dry season strategy: Increase fresh & citrus fragrance inventory - high demand period")
        recommendations.append("🌡️ Hot weather boost: Stock up on light, refreshing scents and aquatic fragrances")
    else:  # Rainy season
        recommendations.append("🌧️ Rainy season preparation: Boost woody & oriental inventory for cozy weather preferences")
        recommendations.append("☔ Comfort scents: Increase gourmand and warm fragrance families")
    
    # Category-specific recommendations
    family_counts = {}
    for product in products:
        family = product.get("fragrance_family", "unknown")
        family_counts[family] = family_counts.get(family, 0) + 1
    
    if family_counts.get("fresh", 0) < 3:
        recommendations.append("🌿 Fresh category opportunity: Add more fresh fragrances - consistently high demand in tropical climate")
    
    if family_counts.get("floral", 0) < 2:
        recommendations.append("🌸 Floral expansion: Consider adding more floral options - popular for Indonesian market")
    
    # Check for halal-certified products
    halal_count = sum(1 for p in products if p.get("halal_certified", False))
    if halal_count < total_products * 0.6:
        recommendations.append("☪️ Halal certification priority: Increase halal-certified options - important for Indonesian Muslim market (85%+ population)")
    
    # Indonesian heritage recommendations
    indonesian_count = sum(1 for p in products if p.get("indonesian_heritage", False))
    if indonesian_count < total_products * 0.5:
        recommendations.append("🇮🇩 Local brand focus: Add more Indonesian heritage brands - supports local economy and cultural connection")
    
    # Supplier and logistics recommendations
    overdue_restocks = []
    for product in products:
        days_since_restock = (datetime.now().timestamp() - product.get("last_restocked", 0)) / 86400
        if days_since_restock > 30:  # 30 days
            overdue_restocks.append(product["name"])
    
    if overdue_restocks:
        recommendations.append(f"📅 Restock schedule review: {len(overdue_restocks)} products haven't been restocked in 30+ days")
    
    # Price optimization recommendations
    high_price_low_stock = [p for p in products if p.get("price_idr", 0) > 200000 and p.get("stock_quantity", 0) < 10]
    if high_price_low_stock:
        recommendations.append(f"💰 Premium inventory risk: {len(high_price_low_stock)} high-value products have low stock - prioritize for cash flow")
    
    # Warehouse optimization
    locations = set(p.get("location", "") for p in products)
    if len(locations) > 1:
        recommendations.append(f"🏭 Multi-warehouse optimization: Review stock distribution across {len(locations)} locations")
    
    return recommendations

def determine_recommendation_priority(recommendation: str) -> str:
    """Determine priority level of recommendation"""
    
    if "URGENT" in recommendation or "🚨" in recommendation:
        return "critical"
    elif "⚠️" in recommendation or "priority" in recommendation.lower():
        return "high"
    elif "Consider" in recommendation or "opportunity" in recommendation.lower():
        return "medium"
    else:
        return "low"

def categorize_recommendation(recommendation: str) -> str:
    """Categorize recommendation type"""
    
    if "stock" in recommendation.lower():
        return "stock_management"
    elif "seasonal" in recommendation.lower() or "🌞" in recommendation or "🌧️" in recommendation:
        return "seasonal_planning"
    elif "halal" in recommendation.lower() or "indonesian" in recommendation.lower():
        return "market_localization"
    elif "price" in recommendation.lower() or "💰" in recommendation:
        return "pricing_strategy"
    elif "warehouse" in recommendation.lower() or "location" in recommendation.lower():
        return "logistics"
    else:
        return "general"

async def perform_stock_health_check(ctx: Context):
    """Perform comprehensive stock health check on startup"""
    
    ctx.logger.info("🏥 Performing inventory health check...")
    
    total_products = len(inventory_database)
    healthy_products = 0
    warning_products = 0
    critical_products = 0
    
    for product_id, product in inventory_database.items():
        stock_level = determine_stock_level(product)
        
        if stock_level == "good_stock":
            healthy_products += 1
        elif stock_level in ["moderate_stock", "low_stock"]:
            warning_products += 1
        elif stock_level == "out_of_stock":
            critical_products += 1
            ctx.logger.warning(f"🚨 Critical: {product['name']} is out of stock")
    
    health_percentage = (healthy_products / total_products) * 100 if total_products > 0 else 0
    
    ctx.logger.info(f"📊 Inventory Health Summary:")
    ctx.logger.info(f"   Total Products: {total_products}")
    ctx.logger.info(f"   Healthy Stock: {healthy_products} ({health_percentage:.1f}%)")
    ctx.logger.info(f"   Warning Level: {warning_products}")
    ctx.logger.info(f"   Critical Level: {critical_products}")
    
    if critical_products > 0:
        ctx.logger.warning(f"⚠️ {critical_products} products need immediate attention")

# ICP Integration Functions
async def sync_inventory_to_icp(ctx: Context, product_id: str, action: str, data: Dict[str, Any]) -> bool:
    """Sync inventory changes to ICP canister"""
    
    try:
        # Prepare data for ICP canister
        icp_data = {
            "product_id": product_id,
            "action": action,
            "inventory_data": data,
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Determine which ICP method to call based on action
        if action == "add":
            method = "add_product"
            # Convert inventory data to product format
            product_data = inventory_database.get(product_id, {})
            icp_data = {
                "id": product_id,
                "seller_id": product_data.get("seller_id", "unknown"),
                "name": product_data.get("name", "Unknown Product"),
                "brand": product_data.get("brand", "Unknown Brand"),
                "price_idr": product_data.get("price_idr", 0),
                "fragrance_family": product_data.get("fragrance_family", "unknown"),
                "stock": product_data.get("stock_quantity", 0),
                "verified": True,
                "created_at": int(datetime.now().timestamp()),
                "updated_at": int(datetime.now().timestamp())
            }
        elif action == "update":
            method = "update_product_stock"
            icp_data = {
                "product_id": product_id,
                "new_stock": data.get("stock_quantity", 0)
            }
        else:
            method = "update_product_stock"
        
        result = await call_icp_canister(ctx, method, icp_data)
        
        if result.get("success"):
            ctx.logger.info(f"✅ Inventory synced to ICP: {action} for {product_id}")
            return True
        else:
            ctx.logger.error(f"❌ ICP inventory sync failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        ctx.logger.error(f"❌ ICP inventory sync error: {e}")
        return False

async def get_inventory_from_icp(ctx: Context, seller_id: str) -> Optional[List[Dict]]:
    """Get inventory data from ICP canister"""
    
    try:
        result = await call_icp_canister(
            ctx,
            "get_products",
            {}
        )
        
        if result.get("success") and result.get("result"):
            # Filter by seller if specified
            products = result["result"]
            if seller_id:
                products = [p for p in products if p.get("seller_id") == seller_id]
            return products
        else:
            return None
            
    except Exception as e:
        ctx.logger.error(f"❌ ICP inventory retrieval error: {e}")
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
        result = await call_icp_canister(ctx, "greet", {"name": "Inventory Agent Test"})
        return result.get("success", False)
    except:
        return False

if __name__ == "__main__":
    inventory_agent.run()
