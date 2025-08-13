from uagents import Agent, Context, Model
from typing import List, Dict, Any, Optional
import json
import aiohttp
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Enhanced Models
class ChatMessage(Model):
    user_id: str
    session_id: str
    message: str
    timestamp: int

class ChatResponse(Model):
    user_id: str
    session_id: str
    response: str
    follow_up_questions: List[str]
    data_collected: Dict[str, Any]
    consultation_progress: float
    next_step: str

class FragranceProfile(Model):
    user_id: str
    personality_type: str
    lifestyle: str
    preferred_families: List[str]
    occasion_preferences: List[str]
    season_preferences: List[str]
    sensitivity_level: str
    budget_range: str
    scent_journey: List[Dict[str, Any]]

class ConsultationStartRequest(BaseModel):
    user_id: str
    session_id: str

class ConsultationMessageRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

consultation_agent = Agent(
    name="aromance_consultation_ai",
    port=8001,
    seed="aromance_consultation_enhanced_2025",
    endpoint=["http://127.0.0.1:8001/submit"],
    mailbox=True,
)

# Enhanced Indonesian Fragrance Knowledge Base
FRAGRANCE_FAMILIES = {
    "fresh": {
        "aliases": ["fresh", "segar", "bersih", "light", "ringan", "citrus"],
        "subcategories": ["citrus", "green", "aquatic", "fruity"],
        "indonesian_examples": ["jeruk nipis", "daun pandan", "air kelapa", "mentimun"],
        "personality_match": ["energetic", "optimistic", "casual", "sporty"],
        "climate_suitability": "tropical_hot",
        "occasions": ["daily", "work", "sport", "casual"]
    },
    "floral": {
        "aliases": ["floral", "bunga", "feminine", "romantic", "melati", "rose"],
        "subcategories": ["white_floral", "rose", "jasmine", "tropical_floral"],
        "indonesian_examples": ["melati", "mawar", "kamboja", "cempaka", "kenanga"],
        "personality_match": ["romantic", "feminine", "gentle", "elegant"],
        "climate_suitability": "tropical_moderate",
        "occasions": ["date", "formal", "wedding", "evening"]
    },
    "fruity": {
        "aliases": ["fruity", "buah", "manis buah", "tropical", "sweet fruit"],
        "subcategories": ["tropical_fruits", "berries", "stone_fruits"],
        "indonesian_examples": ["mangga", "nanas", "rambutan", "durian", "jambu"],
        "personality_match": ["playful", "youthful", "cheerful", "fun"],
        "climate_suitability": "tropical_hot",
        "occasions": ["casual", "party", "beach", "vacation"]
    },
    "woody": {
        "aliases": ["woody", "kayu", "warm", "hangat", "earthy", "sandalwood"],
        "subcategories": ["sandalwood", "cedar", "oud", "dry_woods"],
        "indonesian_examples": ["cendana", "gaharu", "kayu manis", "patchouli"],
        "personality_match": ["sophisticated", "mature", "confident", "grounded"],
        "climate_suitability": "tropical_cool",
        "occasions": ["office", "formal", "evening", "business"]
    },
    "oriental": {
        "aliases": ["oriental", "spicy", "rempah", "eksotis", "mystery", "exotic"],
        "subcategories": ["spicy", "amber", "vanilla", "resinous"],
        "indonesian_examples": ["cengkeh", "nutmeg", "cardamom", "vanilla", "benzoin"],
        "personality_match": ["mysterious", "exotic", "bold", "sensual"],
        "climate_suitability": "tropical_evening",
        "occasions": ["evening", "date", "special", "cultural_events"]
    },
    "gourmand": {
        "aliases": ["gourmand", "manis", "edible", "dessert", "comfort", "vanilla"],
        "subcategories": ["vanilla", "chocolate", "caramel", "coffee"],
        "indonesian_examples": ["vanilla", "kopi", "gula jawa", "cokelat", "kelapa"],
        "personality_match": ["comfort", "sweet", "approachable", "warm"],
        "climate_suitability": "tropical_cool",
        "occasions": ["casual", "cozy", "winter", "comfort"]
    }
}

# Session storage
user_sessions = {}
fragrance_profiles = {}

# FastAPI integration for HTTP endpoints
app = FastAPI()

@consultation_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🌸 Aromance Enhanced Consultation Agent Started")
    ctx.logger.info(f"Agent Address: {consultation_agent.address}")
    ctx.logger.info("Ready for intelligent fragrance consultation with full integration! 🇮🇩")

# HTTP Endpoints
@consultation_agent.on_rest_post("/consultation/start")
async def start_consultation_endpoint(ctx: Context, req):
    """HTTP endpoint to start consultation"""
    try:
        data = await req.json()
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        
        if not user_id or not session_id:
            return {"error": "user_id and session_id are required"}, 400
        
        # Initialize session
        user_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "conversation_history": [],
            "collected_data": {},
            "current_focus": "greeting",
            "consultation_progress": 0.0,
            "started_at": datetime.now().timestamp()
        }
        
        # Generate welcome response
        response = ChatResponse(
            user_id=user_id,
            session_id=session_id,
            response="Hello! 🌸 I'm your Aromance AI consultant specializing in Indonesian fragrance culture. I'll help you discover the perfect scent that matches your personality and lifestyle. Let's start - do you have any favorite scents or perfumes you've tried before?",
            follow_up_questions=[
                "Tell me about your favorite perfume experience",
                "I'm new to perfumes, help me explore",
                "I prefer fresh and light fragrances",
                "I like long-lasting, bold scents"
            ],
            data_collected={},
            consultation_progress=0.1,
            next_step="fragrance_preference_discovery"
        )
        
        return {
            "success": True,
            "response": response.dict()
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Consultation start error: {e}")
        return {"error": "Internal server error"}, 500

@consultation_agent.on_rest_post("/consultation/message")
async def consultation_message_endpoint(ctx: Context, req):
    """HTTP endpoint for consultation messages"""
    try:
        data = await req.json()
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        message = data.get("message")
        
        if not all([user_id, session_id, message]):
            return {"error": "user_id, session_id, and message are required"}, 400
        
        if session_id not in user_sessions:
            return {"error": "Session not found"}, 404
        
        # Process message
        chat_message = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            message=message,
            timestamp=int(datetime.now().timestamp())
        )
        
        response = await process_consultation_message(ctx, user_sessions[session_id], message)
        
        # Update session
        session = user_sessions[session_id]
        session["consultation_progress"] = response.consultation_progress
        session["current_focus"] = response.next_step
        session["collected_data"].update(response.data_collected)
        session["conversation_history"].append({
            "timestamp": chat_message.timestamp,
            "user_message": message,
            "ai_response": response.response,
            "focus": session["current_focus"]
        })
        
        return {
            "success": True,
            "response": response.dict()
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Consultation message error: {e}")
        return {"error": "Internal server error"}, 500

@consultation_agent.on_rest_get("/consultation/profile/{user_id}")
async def get_consultation_profile_endpoint(ctx: Context, req):
    """HTTP endpoint to get user's fragrance profile"""
    try:
        user_id = req.path_params.get("user_id")
        
        if user_id in fragrance_profiles:
            profile = fragrance_profiles[user_id]
            return {
                "success": True,
                "profile": profile.dict()
            }
        else:
            return {"error": "Profile not found"}, 404
            
    except Exception as e:
        ctx.logger.error(f"❌ Profile retrieval error: {e}")
        return {"error": "Internal server error"}, 500

@consultation_agent.on_rest_get("/health")
async def health_check_endpoint(ctx: Context, req):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(user_sessions),
        "created_profiles": len(fragrance_profiles),
        "timestamp": datetime.now().timestamp()
    }

# Agent Message Handling
@consultation_agent.on_message(model=ChatMessage)
async def handle_chat_consultation(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"💬 Chat from user {msg.user_id}: {msg.message}")
    
    if msg.session_id not in user_sessions:
        # Initialize session if not exists
        user_sessions[msg.session_id] = {
            "session_id": msg.session_id,
            "user_id": msg.user_id,
            "conversation_history": [],
            "collected_data": {},
            "current_focus": "greeting",
            "consultation_progress": 0.0,
            "started_at": datetime.now().timestamp()
        }
    
    session = user_sessions[msg.session_id]
    response = await process_consultation_message(ctx, session, msg.message)
    
    # Update session
    session["consultation_progress"] = response.consultation_progress
    session["current_focus"] = response.next_step
    session["collected_data"].update(response.data_collected)
    
    await ctx.send(sender, response)

async def process_consultation_message(ctx: Context, session: Dict, user_message: str) -> ChatResponse:
    """Enhanced message processing with intelligent analysis"""
    
    user_message_lower = user_message.lower()
    collected_data = session["collected_data"]
    current_focus = session["current_focus"]
    
    # Analyze message for fragrance keywords
    detected_families = analyze_fragrance_preferences(user_message_lower)
    detected_occasions = analyze_occasion_preferences(user_message_lower)
    detected_personality = analyze_personality_traits(user_message_lower)
    detected_budget = analyze_budget_mentions(user_message_lower)
    
    # Update collected data with new insights
    if detected_families:
        collected_data["fragrance_families"] = list(set(collected_data.get("fragrance_families", []) + detected_families))
    if detected_occasions:
        collected_data["occasions"] = list(set(collected_data.get("occasions", []) + detected_occasions))
    if detected_personality:
        collected_data["personality_traits"] = list(set(collected_data.get("personality_traits", []) + detected_personality))
    if detected_budget:
        collected_data["budget_mentions"] = detected_budget
    
    # Route to appropriate conversation handler
    if current_focus == "greeting" or current_focus == "fragrance_preference_discovery":
        return await handle_fragrance_discovery(session, user_message_lower, collected_data)
    elif current_focus == "occasion_analysis":
        return await handle_occasion_analysis(session, user_message_lower, collected_data)
    elif current_focus == "personality_matching":
        return await handle_personality_matching(session, user_message_lower, collected_data)
    elif current_focus == "budget_discussion":
        return await handle_budget_discussion(session, user_message_lower, collected_data)
    elif current_focus == "sensitivity_check":
        return await handle_sensitivity_check(session, user_message_lower, collected_data)
    else:
        return await finalize_consultation(session, collected_data)

async def handle_fragrance_discovery(session: Dict, message: str, collected_data: Dict) -> ChatResponse:
    """Handle fragrance family discovery phase"""
    
    detected_families = collected_data.get("fragrance_families", [])
    
    if not detected_families:
        # Enhanced keyword detection
        for family, data in FRAGRANCE_FAMILIES.items():
            if any(alias in message for alias in data["aliases"]):
                detected_families.append(family)
                break
    
    if detected_families:
        family = detected_families[0]
        family_info = FRAGRANCE_FAMILIES.get(family, {})
        indonesian_examples = ", ".join(family_info.get("indonesian_examples", [])[:3])
        
        response_text = f"Excellent choice! You're drawn to {family} fragrances 😊 This family works beautifully in Indonesia's tropical climate. "
        response_text += f"In Indonesian culture, {family} scents often feature notes like {indonesian_examples}. "
        response_text += f"Now, let's talk about when you'd wear your perfect fragrance. What occasions do you have in mind?"
        
        return ChatResponse(
            user_id=session["user_id"],
            session_id=session["session_id"],
            response=response_text,
            follow_up_questions=[
                "Daily wear for work or school",
                "Romantic dates and special evenings",
                "Formal events and important meetings",
                "Casual hangouts and weekend activities"
            ],
            data_collected={"fragrance_families": detected_families},
            consultation_progress=0.3,
            next_step="occasion_analysis"
        )
    else:
        return ChatResponse(
            user_id=session["user_id"],
            session_id=session["session_id"],
            response="I'd love to understand your scent preferences better! Could you describe what kind of fragrances appeal to you? For example, do you prefer something light and refreshing, or rich and warm?",
            follow_up_questions=[
                "I love fresh, citrusy scents",
                "I prefer sweet, vanilla-like fragrances",
                "I'm attracted to woody, sophisticated scents",
                "I'm not sure, surprise me!"
            ],
            data_collected={},
            consultation_progress=0.1,
            next_step="fragrance_preference_discovery"
        )

async def handle_occasion_analysis(session: Dict, message: str, collected_data: Dict) -> ChatResponse:
    """Handle occasion preference analysis"""
    
    occasions = []
    if any(word in message for word in ["daily", "work", "school", "office", "routine"]):
        occasions.append("daily_work")
    if any(word in message for word in ["formal", "important", "meeting", "business", "professional"]):
        occasions.append("formal")
    if any(word in message for word in ["date", "romantic", "evening", "night", "special"]):
        occasions.append("evening_date")
    if any(word in message for word in ["casual", "weekend", "hangout", "relaxed", "versatile"]):
        occasions.append("casual")
    
    collected_data["occasions"] = occasions
    
    response_text = "Perfect! Understanding your lifestyle helps me recommend the right fragrance intensity and character. "
    response_text += "Now, let's explore your personality. How would your closest friends describe you? "
    response_text += "This helps me match you with fragrances that truly reflect who you are."
    
    return ChatResponse(
        user_id=session["user_id"],
        session_id=session["session_id"],
        response=response_text,
        follow_up_questions=[
            "Confident and bold, I like to stand out",
            "Romantic and gentle, I love sweet things",
            "Professional and polished, always put-together",
            "Fun and energetic, I enjoy life's pleasures"
        ],
        data_collected={"occasions": occasions},
        consultation_progress=0.5,
        next_step="personality_matching"
    )

async def handle_personality_matching(session: Dict, message: str, collected_data: Dict) -> ChatResponse:
    """Handle personality trait matching"""
    
    personality_traits = []
    if any(word in message for word in ["confident", "bold", "strong", "assertive", "stand out"]):
        personality_traits.append("confident")
    if any(word in message for word in ["romantic", "gentle", "sweet", "soft", "tender"]):
        personality_traits.append("romantic")
    if any(word in message for word in ["professional", "polished", "put-together", "sophisticated", "elegant"]):
        personality_traits.append("professional")
    if any(word in message for word in ["fun", "energetic", "playful", "cheerful", "lively"]):
        personality_traits.append("playful")
    
    collected_data["personality_traits"] = personality_traits
    
    response_text = "Great! Your personality insights are really helpful. Now let's talk about budget - "
    response_text += "there are wonderful fragrances at every price point, so don't worry about being practical. "
    response_text += "What's a comfortable range for a fragrance you'd truly love?"
    
    return ChatResponse(
        user_id=session["user_id"],
        session_id=session["session_id"],
        response=response_text,
        follow_up_questions=[
            "Under 100K - I prefer budget-friendly options",
            "100K-300K - Mid-range is perfect for me",
            "300K-500K - I don't mind investing in quality",
            "500K+ - I want the best, price isn't a concern"
        ],
        data_collected={"personality_traits": personality_traits},
        consultation_progress=0.7,
        next_step="budget_discussion"
    )

async def handle_budget_discussion(session: Dict, message: str, collected_data: Dict) -> ChatResponse:
    """Handle budget preference discussion"""
    
    budget_range = "moderate"
    if any(word in message for word in ["100k", "under", "budget", "affordable", "cheap"]):
        budget_range = "budget"
    elif any(word in message for word in ["300k", "mid", "middle", "moderate", "reasonable"]):
        budget_range = "moderate"
    elif any(word in message for word in ["500k", "quality", "invest", "premium"]):
        budget_range = "premium"
    elif any(word in message for word in ["best", "luxury", "price isn't", "expensive", "high-end"]):
        budget_range = "luxury"
    
    collected_data["budget_range"] = budget_range
    
    response_text = "Excellent! One last important question - do you have any sensitivities or allergies? "
    response_text += "Some people are sensitive to strong fragrances or specific ingredients. "
    response_text += "This helps me ensure your recommendations are comfortable for you to wear."
    
    return ChatResponse(
        user_id=session["user_id"],
        session_id=session["session_id"],
        response=response_text,
        follow_up_questions=[
            "No sensitivities, I can wear any fragrance",
            "I'm sensitive to very strong scents",
            "I'm allergic to certain floral ingredients",
            "I prefer hypoallergenic or gentle formulas"
        ],
        data_collected={"budget_range": budget_range},
        consultation_progress=0.9,
        next_step="sensitivity_check"
    )

async def handle_sensitivity_check(session: Dict, message: str, collected_data: Dict) -> ChatResponse:
    """Handle sensitivity and allergy assessment"""
    
    sensitivity = "normal"
    if any(word in message for word in ["sensitive", "strong scents", "overpowering"]):
        sensitivity = "sensitive"
    elif any(word in message for word in ["allergic", "allergy", "floral", "reaction"]):
        sensitivity = "allergic"
    elif any(word in message for word in ["hypoallergenic", "gentle", "mild", "safe"]):
        sensitivity = "hypoallergenic"
    
    collected_data["sensitivity"] = sensitivity
    
    # Create comprehensive fragrance profile
    profile = create_fragrance_profile(session["user_id"], collected_data)
    
    # Notify coordinator about completion
    await notify_coordinator_consultation_complete(session, collected_data)
    
    response_text = f"✨ Perfect! Your consultation is complete. I've created your personalized fragrance identity: "
    response_text += f"'{profile.personality_type}' with a preference for {', '.join(profile.preferred_families[:2])} families. "
    response_text += f"I'm now generating intelligent recommendations specifically curated for your unique profile! 🎯"
    
    return ChatResponse(
        user_id=session["user_id"],
        session_id=session["session_id"],
        response=response_text,
        follow_up_questions=[
            "Show me my personalized recommendations!",
            "Explain my fragrance profile in detail",
            "I'd like to modify some preferences"
        ],
        data_collected={"sensitivity": sensitivity, "profile_created": True},
        consultation_progress=1.0,
        next_step="consultation_complete"
    )

async def finalize_consultation(session: Dict, collected_data: Dict) -> ChatResponse:
    """Handle post-consultation interactions"""
    
    response_text = "Your fragrance consultation is complete! Your personalized profile is ready and recommendations are being generated. "
    response_text += "Would you like to see your recommendations or learn more about your fragrance personality?"
    
    return ChatResponse(
        user_id=session["user_id"],
        session_id=session["session_id"],
        response=response_text,
        follow_up_questions=[
            "Show my recommendations now",
            "Explain my fragrance personality",
            "Start a new consultation"
        ],
        data_collected={},
        consultation_progress=1.0,
        next_step="consultation_complete"
    )

async def notify_coordinator_consultation_complete(session: Dict, collected_data: Dict):
    """Notify coordinator that consultation is complete"""
    try:
        coordinator_endpoint = "http://127.0.0.1:8000"
        
        journey_data = {
            "user_id": session["user_id"],
            "session_id": session["session_id"],
            "current_stage": "consultation_complete",
            "data": collected_data,
            "next_action": "generate_recommendations",
            "timestamp": int(datetime.now().timestamp())
        }
        
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f"{coordinator_endpoint}/user_journey",
                json=journey_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    print(f"✅ Coordinator notified for user {session['user_id']}")
                else:
                    print(f"❌ Failed to notify coordinator: {response.status}")
                    
    except Exception as e:
        print(f"❌ Coordinator notification error: {e}")

def analyze_fragrance_preferences(message: str) -> List[str]:
    """Analyze message for fragrance family keywords"""
    detected = []
    for family, data in FRAGRANCE_FAMILIES.items():
        if any(alias in message for alias in data["aliases"]):
            detected.append(family)
    return detected

def analyze_occasion_preferences(message: str) -> List[str]:
    """Analyze message for occasion keywords"""
    occasions = []
    occasion_keywords = {
        "daily": ["daily", "everyday", "work", "school", "office", "routine"],
        "formal": ["formal", "important", "meeting", "business", "professional"],
        "evening": ["evening", "night", "date", "romantic", "special"],
        "casual": ["casual", "weekend", "hangout", "relaxed", "fun"],
        "special": ["special", "party", "celebration", "event"]
    }
    
    for occasion, keywords in occasion_keywords.items():
        if any(keyword in message for keyword in keywords):
            occasions.append(occasion)
    
    return occasions

def analyze_personality_traits(message: str) -> List[str]:
    """Analyze message for personality indicators"""
    traits = []
    personality_keywords = {
        "confident": ["confident", "bold", "strong", "assertive", "stand out"],
        "romantic": ["romantic", "gentle", "sweet", "soft", "tender"],
        "professional": ["professional", "polished", "sophisticated", "elegant", "put-together"],
        "playful": ["playful", "fun", "energetic", "cheerful", "lively"],
        "sophisticated": ["mature", "classy", "refined", "cultured"]
    }
    
    for trait, keywords in personality_keywords.items():
        if any(keyword in message for keyword in keywords):
            traits.append(trait)
    
    return traits

def analyze_budget_mentions(message: str) -> str:
    """Analyze message for budget indicators"""
    if any(word in message for word in ["100k", "under", "budget", "affordable", "cheap"]):
        return "budget"
    elif any(word in message for word in ["300k", "mid", "middle", "moderate"]):
        return "moderate"
    elif any(word in message for word in ["500k", "quality", "premium", "invest"]):
        return "premium"
    elif any(word in message for word in ["luxury", "best", "expensive", "high-end", "price isn't"]):
        return "luxury"
    return "moderate"

def create_fragrance_profile(user_id: str, collected_data: Dict) -> FragranceProfile:
    """Create comprehensive fragrance profile from collected data"""
    
    # Determine personality type based on traits
    personality_traits = collected_data.get("personality_traits", [])
    if "confident" in personality_traits:
        personality_type = "Bold Indonesian Trendsetter"
    elif "romantic" in personality_traits:
        personality_type = "Romantic Indonesian Soul"
    elif "professional" in personality_traits:
        personality_type = "Professional Indonesian Elite"
    elif "playful" in personality_traits:
        personality_type = "Cheerful Indonesian Spirit"
    else:
        personality_type = "Versatile Indonesian Character"
    
    # Determine lifestyle
    occasions = collected_data.get("occasions", [])
    if "daily_work" in occasions or "formal" in occasions:
        lifestyle = "professional"
    elif "evening_date" in occasions:
        lifestyle = "social"
    elif "casual" in occasions:
        lifestyle = "relaxed"
    else:
        lifestyle = "balanced"
    
    # Get fragrance families
    fragrance_families = collected_data.get("fragrance_families", ["fresh"])
    
    # Create scent journey entry
    scent_journey = [{
        "date": datetime.now().timestamp(),
        "preference_change": f"Discovered preference for {', '.join(fragrance_families)} fragrances",
        "trigger_event": "AI consultation completed",
        "confidence_score": 0.85
    }]
    
    profile = FragranceProfile(
        user_id=user_id,
        personality_type=personality_type,
        lifestyle=lifestyle,
        preferred_families=fragrance_families,
        occasion_preferences=occasions,
        season_preferences=["tropical_year_round"],  # Default for Indonesia
        sensitivity_level=collected_data.get("sensitivity", "normal"),
        budget_range=collected_data.get("budget_range", "moderate"),
        scent_journey=scent_journey
    )
    
    fragrance_profiles[user_id] = profile
    return profile

if __name__ == "__main__":
    consultation_agent.run()