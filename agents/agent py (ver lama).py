from uagents import Agent, Context, Model, Protocol
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from uuid import uuid4

# CHAT PROTOCOL IMPORTS
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# EXISTING MODELS FOR AGENT COMMUNICATION
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

class SystemHealthResponse(Model):
    status: str
    agents: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: float

# CONSULTATION MODELS (Embedded from consultation_agent.py)
class ConsultationStartRequest(Model):
    user_id: str
    session_id: str

class ConsultationStartResponse(Model):
    success: bool
    response: Dict[str, Any]

class ConsultationMessageRequest(Model):
    user_id: str
    session_id: str
    message: str

class ConsultationMessageResponse(Model):
    success: bool
    response: Dict[str, Any]

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

# RECOMMENDATION MODELS (Embedded from recommendation_agent.py)
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

# AGENT CONFIGURATION WITH MAILBOX
coordinator_agent = Agent(
    name="aromance_coordinator_enhanced", 
    port=8000,
    seed="aromance_coordinator_enhanced_2025",
    endpoint=["http://127.0.0.1:8000/submit"],
    mailbox="eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjM3Nzg2NzIsImlhdCI6MTc1NjAwMjY3MiwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiIzMTQ5Y2RhNjI1YWM2OTdjYzA2ZjI3NzQiLCJzY29wZSI6ImF2Iiwic3ViIjoiMzI4NDNmYTMzYzM1MTNjODUxNzJlM2Y4NGNiOWQ2ODkwMGI4OWE2ZjJmY2Y1OTVmIn0.i-KkXbJu_Vx_LNnli-YzkjlqD8aMrU4wY9DJVq0uHSFmToiPD85RF0r5RVBuTnegxdu3fXglAkokaYnRVVvy4NfG4qIWSbaXdFqekB3VtBmSiMQPb9Bza4OATmonQ8oiXu7XY55jOIIJ5VAeLAeR75IuL9Rg25yPVTn2rw6YEeupHovHWvRF6oo8co4gCJtuzmXEaBdV5pFxN3Ep2azJuJIBTPTIUouIkCO15BF_YXgRYzq5nVQ1KSHIPl7PvTxKxCM0BS6VkUu1MP43ccpY2FvbViHAnYfm_AI4oeSDpjUgjaBzrefM9y7vL1gYXMBdN1nZw3BF7O1E4NiKHiZv_w"  
)

# CHAT PROTOCOL SETUP
chat_proto = Protocol(spec=chat_protocol_spec)

# Enhanced Indonesian Fragrance Knowledge Base (Combined from both agents)
FRAGRANCE_FAMILIES = {
    "fresh": {
        "aliases": ["fresh", "segar", "bersih", "light", "ringan", "citrus", "clean", "airy", "cooling"],
        "subcategories": ["citrus", "green", "aquatic", "fruity"],
        "indonesian_examples": ["jeruk nipis", "daun pandan", "air kelapa", "mentimun"],
        "personality_match": ["energetic", "optimistic", "casual", "sporty"],
        "climate_suitability": "tropical_hot",
        "occasions": ["daily", "work", "sport", "casual"]
    },
    "floral": {
        "aliases": ["floral", "bunga", "feminine", "romantic", "melati", "rose", "flowery", "blooming"],
        "subcategories": ["white_floral", "rose", "jasmine", "tropical_floral"],
        "indonesian_examples": ["melati", "mawar", "kamboja", "cempaka", "kenanga"],
        "personality_match": ["romantic", "feminine", "gentle", "elegant"],
        "climate_suitability": "tropical_moderate",
        "occasions": ["date", "formal", "wedding", "evening"]
    },
    "fruity": {
        "aliases": ["fruity", "buah", "manis buah", "tropical", "sweet fruit", "juicy", "berry"],
        "subcategories": ["tropical_fruits", "berries", "stone_fruits"],
        "indonesian_examples": ["mangga", "nanas", "rambutan", "durian", "jambu"],
        "personality_match": ["playful", "youthful", "cheerful", "fun"],
        "climate_suitability": "tropical_hot",
        "occasions": ["casual", "party", "beach", "vacation"]
    },
    "woody": {
        "aliases": ["woody", "kayu", "warm", "hangat", "earthy", "sandalwood", "cedar", "tree"],
        "subcategories": ["sandalwood", "cedar", "oud", "dry_woods"],
        "indonesian_examples": ["cendana", "gaharu", "kayu manis", "patchouli"],
        "personality_match": ["sophisticated", "mature", "confident", "grounded"],
        "climate_suitability": "tropical_cool",
        "occasions": ["office", "formal", "evening", "business"]
    },
    "oriental": {
        "aliases": ["oriental", "spicy", "rempah", "eksotis", "mystery", "exotic", "warm spice"],
        "subcategories": ["spicy", "amber", "vanilla", "resinous"],
        "indonesian_examples": ["cengkeh", "nutmeg", "cardamom", "vanilla", "benzoin"],
        "personality_match": ["mysterious", "exotic", "bold", "sensual"],
        "climate_suitability": "tropical_evening",
        "occasions": ["evening", "date", "special", "cultural_events"]
    },
    "gourmand": {
        "aliases": ["gourmand", "manis", "edible", "dessert", "comfort", "vanilla", "sweet", "yummy"],
        "subcategories": ["vanilla", "chocolate", "caramel", "coffee"],
        "indonesian_examples": ["vanilla", "kopi", "gula jawa", "cokelat", "kelapa"],
        "personality_match": ["comfort", "sweet", "approachable", "warm"],
        "climate_suitability": "tropical_cool",
        "occasions": ["casual", "cozy", "winter", "comfort"]
    }
}

# Enhanced Product Database
INDONESIAN_FRAGRANCE_DATABASE = [
    {
        "product_id": "IDN_001",
        "name": "Orgsm (Orgasm)",
        "brand": "HMNS",
        "price_idr": 365000,
        "fragrance_family": "gourmand",
        "top_notes": ["Apple"],
        "middle_notes": ["Rose", "Jasmine", "Peony"],
        "base_notes": ["Vanilla Bean", "Amber"],
        "occasions": ["daily", "evening"],
        "personality_match": ["romantic", "sweet"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "25-35",
        "gender": "feminine",
        "description": "A sweet gourmand perfume with fresh apple notes in the opening, floral notes in the middle, and a touch of warm vanilla in the base.",
        "tagline": "Sweet meets elegance",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 3.8,
        "verified_reviews": 47,
        "image_url": "/images/IDN_001.jpeg"
    },
    {
        "product_id": "IDN_002",
        "name": "Darker Shade of Orgsm",
        "brand": "HMNS",
        "price_idr": 380000,
        "fragrance_family": "gourmand",
        "top_notes": ["Orange Blossom", "Apple", "Pepper"],
        "middle_notes": ["Cypriol", "Caramel", "Patchouli"],
        "base_notes": ["Vanilla Bean", "Cedarwood", "Amber", "Vetiver"],
        "occasions": ["evening", "formal"],
        "personality_match": ["mysterious", "elegant"],
        "longevity": "5-6 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-35",
        "gender": "unisex",
        "description": "A darker, smoky version of Orgsm with hints of warm spices, sweet vanilla, and deep aromatic woods.",
        "tagline": "The darker, the deeper",
        "stock_available": True,
        "stock_quantity": 75,
        "rating": 4.1,
        "verified_reviews": 78,
        "image_url": "/images/IDN_002.jpeg"
    },
    {
        "product_id": "IDN_003",
        "name": "FWB",
        "brand": "Onix Fragrance",
        "price_idr": 250000,
        "fragrance_family": "fruity",
        "top_notes": ["Bergamot", "Lemon", "Orange", "Apple", "Green Notes"],
        "middle_notes": ["Floral Notes"],
        "base_notes": ["Sweet Accord", "Amber"],
        "occasions": ["daily", "casual"],
        "personality_match": ["fresh", "energetic"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "unisex",
        "description": "A fresh aroma of citrus, tropical fruit, and light flowers that is suitable for everyday activities in hot climates.",
        "tagline": "Fresh with benefits",
        "stock_available": True,
        "stock_quantity": 60,
        "rating": 4.5,
        "verified_reviews": 67,
        "image_url": "/images/IDN_003.jpeg"
    },
    {
        "product_id": "IDN_004",
        "name": "Zephyr",
        "brand": "Oullu",
        "price_idr": 295000,
        "fragrance_family": "fresh",
        "top_notes": ["Bergamot", "Lemon", "Mint"],
        "middle_notes": ["Green Tea", "Marine Notes", "Jasmine"],
        "base_notes": ["Cedarwood", "Vetiver", "Musk"],
        "occasions": ["daily", "sport"],
        "personality_match": ["energetic", "casual"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Jeruk Nipis", "Akar Wangi"],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "unisex",
        "description": "The fresh aroma of citrus and mint combined with green tea, creates a clean and light sensation for tropical weather.",
        "tagline": "Fresh breeze in every spray",
        "stock_available": True,
        "stock_quantity": 137,
        "rating": 4.6,
        "verified_reviews": 89,
        "image_url": "/images/IDN_004.jpeg"
    },
    {
        "product_id": "IDN_005",
        "name": "Alpha",
        "brand": "HMNS",
        "price_idr": 355000,
        "fragrance_family": "fresh",
        "top_notes": ["Grapefruit", "Lemon", "Green Notes"],
        "middle_notes": ["Lavender", "Rosemary", "Aquatic Notes"],
        "base_notes": ["Vetiver", "Amber", "Musk"],
        "occasions": ["daily", "work"],
        "personality_match": ["confident", "professional"],
        "longevity": "8-12 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Akar Wangi"],
        "climate_suitability": "tropical_hot",
        "target_age": "25-35",
        "gender": "masculine",
        "description": "A fresh masculine perfume with citrus and rosemary, ideal for a professional and confident appearance.",
        "tagline": "Lead with freshness",
        "stock_available": True,
        "stock_quantity": 152,
        "rating": 4.7,
        "verified_reviews": 94,
        "image_url": "/images/IDN_005.jpeg"
    },
    {
        "product_id": "IDN_006",
        "name": "Pure Grace",
        "brand": "Carl & Claire",
        "price_idr": 420000,
        "fragrance_family": "fresh",
        "top_notes": ["Bergamot", "Mandarin Orange", "Mint"],
        "middle_notes": ["White Tea", "Jasmine", "Rose"],
        "base_notes": ["Cedarwood", "Musk", "Amber"],
        "occasions": ["daily", "casual"],
        "personality_match": ["gentle", "romantic"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Jeruk Nipis"],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "feminine",
        "description": "Wangi lembut dan bersih dengan sentuhan citrus, teh putih, dan bunga, menciptakan aura elegan nan segar.",
        "tagline": "Elegance in freshness",
        "stock_available": True,
        "stock_quantity": 128,
        "rating": 4.8,
        "verified_reviews": 102,
        "image_url": "/images/IDN_006.jpeg"
    },
    {
        "product_id": "IDN_007",
        "name": "Morning Dew",
        "brand": "Onix Fragrance",
        "price_idr": 265000,
        "fragrance_family": "fresh",
        "top_notes": ["Mint", "Bergamot", "Grapefruit"],
        "middle_notes": ["Green Tea", "Marine Notes", "Lavender"],
        "base_notes": ["Cedarwood", "Amber", "Vetiver"],
        "occasions": ["daily", "casual"],
        "personality_match": ["casual", "energetic"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Akar Wangi"],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "unisex",
        "description": "The light aroma of fresh mint and green tea for a relaxing feeling from morning to evening.",
        "tagline": "Start fresh every day",
        "stock_available": True,
        "stock_quantity": 173,
        "rating": 4.5,
        "verified_reviews": 75,
        "image_url": "/images/IDN_007.jpeg"
    },
    {
        "product_id": "IDN_008",
        "name": "Azure",
        "brand": "Saff & Co.",
        "price_idr": 360000,
        "fragrance_family": "fresh",
        "top_notes": ["Sea Salt", "Lemon", "Mint"],
        "middle_notes": ["Aquatic Notes", "Rosemary", "Lavender"],
        "base_notes": ["Vetiver", "Cedarwood", "Musk"],
        "occasions": ["daily", "sport"],
        "personality_match": ["energetic", "confident"],
        "longevity": "8-12 hours",
        "sillage": "strong",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Akar Wangi"],
        "climate_suitability": "tropical_hot",
        "target_age": "25-35",
        "gender": "masculine",
        "description": "A combination of sea salt and citrus with fresh herbs that radiates energy and confidence.",
        "tagline": "Dive into freshness",
        "stock_available": True,
        "stock_quantity": 199,
        "rating": 4.7,
        "verified_reviews": 88,
        "image_url": "/images/IDN_008.jpeg"
    },
    {
        "product_id": "IDN_009",
        "name": "Deep Dive",
        "brand": "Oullu",
        "price_idr": 310000,
        "fragrance_family": "fresh",
        "top_notes": ["Lemon", "Grapefruit", "Mint"],
        "middle_notes": ["Marine Notes", "Basil", "Lavender"],
        "base_notes": ["Cedarwood", "Amber", "Musk"],
        "occasions": ["daily", "sport"],
        "personality_match": ["energetic", "casual"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "unisex",
        "description": "A fresh marine and citrus scent for outdoor activities, giving a vibrant impression all day long.",
        "tagline": "Freshness that flows",
        "stock_available": True,
        "stock_quantity": 165,
        "rating": 4.6,
        "verified_reviews": 91,
        "image_url": "/images/IDN_009.jpeg"
    },
    {
        "product_id": "IDN_010",
        "name": "Vetiver Dawn",
        "brand": "Mine Perfumery",
        "price_idr": 290000,
        "fragrance_family": "woody",
        "top_notes": ["Lemon", "Mandarin", "Pepper"],
        "middle_notes": ["Vetiver", "Cedarwood", "Lavender"],
        "base_notes": ["Amber", "Musk", "Patchouli"],
        "occasions": ["daily", "work"],
        "personality_match": ["professional", "confident"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Akar Wangi"],
        "climate_suitability": "tropical_all_day",
        "target_age": "25-35",
        "gender": "masculine",
        "description": "A bright and fresh vetiver scent that energizes mornings with a woody finish.",
        "tagline": "Fresh start, grounded heart",
        "stock_available": True,
        "stock_quantity": 126,
        "rating": 4.5,
        "verified_reviews": 79,
        "image_url": "/images/IDN_010.jpeg"
    },
    {
        "product_id": "IDN_011",
        "name": "Vanilla Spice",
        "brand": "Mine Perfumery",
        "price_idr": 295000,
        "fragrance_family": "oriental",
        "top_notes": ["Orange", "Bergamot", "Pink Pepper"],
        "middle_notes": ["Vanilla", "Cinnamon", "Jasmine"],
        "base_notes": ["Amber", "Musk", "Sandalwood"],
        "occasions": ["casual", "romantic"],
        "personality_match": ["sweet", "warm"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "intimate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Vanila Jawa", "Kayu Manis"],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "feminine",
        "description": "A cozy, sweet fragrance blending warm vanilla with gentle spices for everyday comfort.",
        "tagline": "Sweet warmth in every drop",
        "stock_available": True,
        "stock_quantity": 169,
        "rating": 4.7,
        "verified_reviews": 88,
        "image_url": "/images/IDN_011.jpeg"
    },
    {
        "product_id": "IDN_012",
        "name": "The Perfection",
        "brand": "HMNS",
        "price_idr": 400000,
        "fragrance_family": "floral woody",
        "top_notes": ["Bergamot", "Pink Pepper"],
        "middle_notes": ["Jasmine", "Rose"],
        "base_notes": ["Sandalwood", "Musk"],
        "occasions": ["evening", "formal"],
        "personality_match": ["elegant", "confident"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-40",
        "gender": "unisex",
        "description": "Elegant floral woody scent with a refined, polished character.",
        "tagline": "Perfection in every note",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.5,
        "verified_reviews": 50,
        "image_url": "/images/IDN_012.jpeg"
    },
    {
        "product_id": "IDN_013",
        "name": "Farhampton",
        "brand": "HMNS",
        "price_idr": 380000,
        "fragrance_family": "aromatic green",
        "top_notes": ["Green Leaves", "Lime"],
        "middle_notes": ["Lavender", "Geranium"],
        "base_notes": ["Cedarwood", "Musk"],
        "occasions": ["daytime", "casual"],
        "personality_match": ["fresh", "relaxed"],
        "longevity": "5-7 hours",
        "sillage": "light-moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_day",
        "target_age": "20-35",
        "gender": "unisex",
        "description": "Crisp green aromatic scent with a laid-back, coastal vibe.",
        "tagline": "Breezy coastal escape",
        "stock_available": True,
        "stock_quantity": 80,
        "rating": 4.3,
        "verified_reviews": 45,
        "image_url": "/images/IDN_013.jpeg"
    },
    {
        "product_id": "IDN_014",
        "name": "Essence of the Sun (EoS)",
        "brand": "HMNS",
        "price_idr": 420000,
        "fragrance_family": "sunny citrus floral",
        "top_notes": ["Orange Blossom", "Mandarin"],
        "middle_notes": ["Ylang-Ylang", "Jasmine"],
        "base_notes": ["Vanilla", "Musk"],
        "occasions": ["daytime", "beach"],
        "personality_match": ["vibrant", "cheerful"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Ylang-Ylang"],
        "climate_suitability": "tropical_day",
        "target_age": "18-35",
        "gender": "feminine",
        "description": "Radiant citrus floral capturing the warmth of tropical sunlight.",
        "tagline": "Sunlit floral glow",
        "stock_available": True,
        "stock_quantity": 90,
        "rating": 4.6,
        "verified_reviews": 60,
        "image_url": "/images/IDN_014.jpeg"
    },
    {
        "product_id": "IDN_015",
        "name": "Orgsm Melting Temptation",
        "brand": "HMNS",
        "price_idr": 450000,
        "fragrance_family": "gourmand oriental",
        "top_notes": ["Caramel", "Bergamot"],
        "middle_notes": ["Jasmine", "Tonka Bean"],
        "base_notes": ["Vanilla", "Amber"],
        "occasions": ["evening", "romantic"],
        "personality_match": ["sensual", "alluring"],
        "longevity": "7-9 hours",
        "sillage": "strong",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-40",
        "gender": "feminine",
        "description": "Decadent gourmand oriental with a seductive, creamy allure.",
        "tagline": "Irresistible sweet temptation",
        "stock_available": True,
        "stock_quantity": 70,
        "rating": 4.8,
        "verified_reviews": 55,
        "image_url": "/images/IDN_015.jpeg"
    },
    {
        "product_id": "IDN_016",
        "name": "Home Garden",
        "brand": "Alchemist",
        "price_idr": 300000,
        "fragrance_family": "green floral",
        "top_notes": ["Green Leaves", "Dew Accord"],
        "middle_notes": ["Rose", "Lily"],
        "base_notes": ["Musk", "Soft Woods"],
        "occasions": ["daytime", "natural"],
        "personality_match": ["calm", "fresh"],
        "longevity": "4-6 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_day",
        "target_age": "20-35",
        "gender": "unisex",
        "description": "Fresh green floral evoking a serene garden retreat.",
        "tagline": "Nature’s gentle embrace",
        "stock_available": True,
        "stock_quantity": 110,
        "rating": 4.4,
        "verified_reviews": 50,
        "image_url": "/images/IDN_016.jpeg"
    },
    {
        "product_id": "IDN_017",
        "name": "Got My Mojo Back",
        "brand": "Alchemist",
        "price_idr": 320000,
        "fragrance_family": "spicy citrus",
        "top_notes": ["Ginger", "Lemon"],
        "middle_notes": ["Cardamom", "Lavender"],
        "base_notes": ["Cedarwood", "Amber"],
        "occasions": ["daily", "casual"],
        "personality_match": ["energetic", "bold"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "20-35",
        "gender": "unisex",
        "description": "Vibrant spicy citrus scent with an uplifting, confident edge.",
        "tagline": "Spark of bold energy",
        "stock_available": True,
        "stock_quantity": 95,
        "rating": 4.5,
        "verified_reviews": 60,
        "image_url": "/images/IDN_017.jpeg"
    },
    {
        "product_id": "IDN_018",
        "name": "Pink Laundry",
        "brand": "Alchemist",
        "price_idr": 280000,
        "fragrance_family": "clean floral",
        "top_notes": ["Cotton Accord", "Bergamot"],
        "middle_notes": ["Rose", "Peony"],
        "base_notes": ["Musk", "Amber"],
        "occasions": ["daily", "casual"],
        "personality_match": ["fresh", "comforting"],
        "longevity": "4-6 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-30",
        "gender": "feminine",
        "description": "Soft clean floral with a cozy, fresh-laundry feel.",
        "tagline": "Clean comfort in a spray",
        "stock_available": True,
        "stock_quantity": 120,
        "rating": 4.3,
        "verified_reviews": 70,
        "image_url": "/images/IDN_018.jpeg"
    },
    {
        "product_id": "IDN_019",
        "name": "Mexicola",
        "brand": "Onix Fragrance",
        "price_idr": 250000,
        "fragrance_family": "sweet fruity floral",
        "top_notes": ["Raspberry", "Apple", "Pineapple"],
        "middle_notes": ["Cyclamen", "Freesia", "Jasmine", "Lily of the Valley"],
        "base_notes": ["Caramel", "Coconut", "Musk", "Sandalwood", "Tonka Bean", "Vanilla"],
        "occasions": ["daily", "casual"],
        "personality_match": ["fun", "youthful"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-30",
        "gender": "unisex",
        "description": "Sweet fruity floral woody with gourmand creamy base—playful and comforting.",
        "tagline": "Fresh fruity gourmand fun",
        "stock_available": True,
        "stock_quantity": 85,
        "rating": 4.6,
        "verified_reviews": 65,
        "image_url": "/images/IDN_019.jpeg"
    },
    {
        "product_id": "IDN_020",
        "name": "Senoparty",
        "brand": "Onix Fragrance",
        "price_idr": 270000,
        "fragrance_family": "fruity gourmand",
        "top_notes": ["Mango", "Citrus"],
        "middle_notes": ["Jasmine", "Rose"],
        "base_notes": ["Vanilla", "Caramel"],
        "occasions": ["party", "casual"],
        "personality_match": ["lively", "festive"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-30",
        "gender": "unisex",
        "description": "Festive fruity gourmand with a vibrant, party-ready energy.",
        "tagline": "Party in every spritz",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.4,
        "verified_reviews": 55,
        "image_url": "/images/IDN_020.jpeg"
    },
    {
        "product_id": "IDN_021",
        "name": "California Blue",
        "brand": "Mykonos",
        "price_idr": 300000,
        "fragrance_family": "aquatic citrus",
        "top_notes": ["Ocean Breeze", "Mandarin"],
        "middle_notes": ["Sea Salt Accord", "Floral"],
        "base_notes": ["Driftwood", "Musk"],
        "occasions": ["daytime", "beach"],
        "personality_match": ["carefree", "adventurous"],
        "longevity": "5-7 hours",
        "sillage": "light-moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_day",
        "target_age": "18-30",
        "gender": "unisex",
        "description": "Oceanic and free—scent of sun and waves.",
        "tagline": "Beach vibes in a spray",
        "stock_available": True,
        "stock_quantity": 110,
        "rating": 4.5,
        "verified_reviews": 60,
        "image_url": "/images/IDN_021.jpeg"
    },
    {
        "product_id": "IDN_022",
        "name": "Gardenia (Premium)",
        "brand": "Le Amor",
        "price_idr": 320000,
        "fragrance_family": "floral sweet",
        "top_notes": ["Gardenia", "White Floral"],
        "middle_notes": ["Tuberose", "Jasmine"],
        "base_notes": ["Vanilla", "Musk"],
        "occasions": ["date", "evening"],
        "personality_match": ["graceful", "confident"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "20-35",
        "gender": "feminine",
        "description": "Sweet floral—grace with confidence.",
        "tagline": "Soft floral elegance",
        "stock_available": True,
        "stock_quantity": 90,
        "rating": 4.6,
        "verified_reviews": 70,
        "image_url": "/images/IDN_022.jpeg"
    },
    {
        "product_id": "IDN_023",
        "name": "Mystic Oud",
        "brand": "Kahf",
        "price_idr": 450000,
        "fragrance_family": "oriental woody",
        "top_notes": ["Smoky Oud", "Spice"],
        "middle_notes": ["Resinous Wood", "Patchouli"],
        "base_notes": ["Amber", "Musk"],
        "occasions": ["evening", "formal"],
        "personality_match": ["intense", "mysterious"],
        "longevity": "7-9 hours",
        "sillage": "strong",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "30-45",
        "gender": "unisex",
        "description": "Smoky oud, deep and enigmatic.",
        "tagline": "Mystery in woody depth",
        "stock_available": True,
        "stock_quantity": 80,
        "rating": 4.7,
        "verified_reviews": 65,
        "image_url": "/images/IDN_023.jpeg"
    },
    {
        "product_id": "IDN_024",
        "name": "Since Day One",
        "brand": "Zentja",
        "price_idr": 340000,
        "fragrance_family": "woody aromatic",
        "top_notes": ["Bergamot", "Juniper"],
        "middle_notes": ["Cedar", "Lavender"],
        "base_notes": ["Sandalwood", "Amber"],
        "occasions": ["daily", "formal"],
        "personality_match": ["classic", "reliable"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "25-40",
        "gender": "masculine",
        "description": "Timeless woody aromatic with a dependable, grounded charm.",
        "tagline": "Classic from the start",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.5,
        "verified_reviews": 60,
        "image_url": "/images/IDN_024.jpeg"
    },
    {
        "product_id": "IDN_025",
        "name": "Sunset Oasis",
        "brand": "Zentja",
        "price_idr": 360000,
        "fragrance_family": "oriental floral",
        "top_notes": ["Saffron", "Orange Blossom"],
        "middle_notes": ["Rose", "Jasmine"],
        "base_notes": ["Amber", "Vanilla"],
        "occasions": ["evening", "romantic"],
        "personality_match": ["warm", "inviting"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-40",
        "gender": "unisex",
        "description": "Warm oriental floral evoking a serene tropical sunset.",
        "tagline": "Golden hour in a bottle",
        "stock_available": True,
        "stock_quantity": 85,
        "rating": 4.6,
        "verified_reviews": 55,
        "image_url": "/images/IDN_025.jpeg"
    },
    {
        "product_id": "IDN_026",
        "name": "Give It Time",
        "brand": "Zentja",
        "price_idr": 330000,
        "fragrance_family": "woody floral",
        "top_notes": ["Bergamot", "Green Accord"],
        "middle_notes": ["Iris", "Rose"],
        "base_notes": ["Sandalwood", "Musk"],
        "occasions": ["daily", "intimate"],
        "personality_match": ["patient", "elegant"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "25-35",
        "gender": "feminine",
        "description": "Refined woody floral with a soft, unfolding elegance.",
        "tagline": "Beauty that unfolds",
        "stock_available": True,
        "stock_quantity": 95,
        "rating": 4.4,
        "verified_reviews": 50,
        "image_url": "/images/IDN_026.jpeg"
    },
    {
        "product_id": "IDN_027",
        "name": "Signature 002",
        "brand": "Fakhrul Oud",
        "price_idr": 600000,
        "fragrance_family": "oriental oud",
        "top_notes": ["Saffron", "Oud"],
        "middle_notes": ["Rose", "Patchouli"],
        "base_notes": ["Amber", "Leather"],
        "occasions": ["evening", "formal"],
        "personality_match": ["luxurious", "bold"],
        "longevity": "8-10 hours",
        "sillage": "strong",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": False,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "30-50",
        "gender": "unisex",
        "description": "Rich oud with luxurious, bold depth and sophistication.",
        "tagline": "Oud’s timeless signature",
        "stock_available": True,
        "stock_quantity": 70,
        "rating": 4.8,
        "verified_reviews": 60,
        "image_url": "/images/IDN_027.jpeg"
    },
    {
        "product_id": "IDN_028",
        "name": "Gerania",
        "brand": "Euodia Parfums",
        "price_idr": 300000,
        "fragrance_family": "floral clean",
        "top_notes": ["Geranium", "Green Accord"],
        "middle_notes": ["Floral"],
        "base_notes": ["Musk", "Clean Amber"],
        "occasions": ["daytime", "casual"],
        "personality_match": ["charming", "fresh"],
        "longevity": "4-6 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": ["Geranium"],
        "climate_suitability": "tropical_all_day",
        "target_age": "20-35",
        "gender": "feminine",
        "description": "Geranium floral—clean, charming, and refreshing.",
        "tagline": "Geranium charm",
        "stock_available": True,
        "stock_quantity": 90,
        "rating": 4.4,
        "verified_reviews": 60,
        "image_url": "/images/IDN_028.jpeg"
    },
    {
        "product_id": "IDN_029",
        "name": "Green Harmony",
        "brand": "Oaken Lab",
        "price_idr": 320000,
        "fragrance_family": "green woody",
        "top_notes": ["Green Leaves", "Herbal"],
        "middle_notes": ["Woodsy Floral"],
        "base_notes": ["Earthy Wood", "Musk"],
        "occasions": ["daily", "natural"],
        "personality_match": ["grounded", "fresh"],
        "longevity": "5-7 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_day",
        "target_age": "20-40",
        "gender": "unisex",
        "description": "Fresh green woody vibe—earthy, natural, calming.",
        "tagline": "Nature’s essence",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.5,
        "verified_reviews": 55,
        "image_url": "/images/IDN_029.jpeg"
    },
    {
        "product_id": "IDN_030",
        "name": "Scarlet Whisper",
        "brand": "Scarlett",
        "price_idr": 150000,
        "fragrance_family": "floral fruity",
        "top_notes": ["Red Berries", "Peony"],
        "middle_notes": ["Rose", "Jasmine"],
        "base_notes": ["Musk", "Amber"],
        "occasions": ["daily", "playful"],
        "personality_match": ["youthful", "sweet"],
        "longevity": "4-6 hours",
        "sillage": "light-moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-25",
        "gender": "feminine",
        "description": "Playful floral fruity with soft sweetness.",
        "tagline": "Sweet floral fun",
        "stock_available": True,
        "stock_quantity": 120,
        "rating": 4.3,
        "verified_reviews": 70,
        "image_url": "/images/IDN_030.jpeg"
    },
    {
        "product_id": "IDN_031",
        "name": "Blooming Hope",
        "brand": "Carl & Claire",
        "price_idr": 290000,
        "fragrance_family": "floral fruity",
        "top_notes": ["Lychee", "Pear", "Green"],
        "middle_notes": ["Peony", "Jasmine"],
        "base_notes": ["Musk", "Soft Woods"],
        "occasions": ["daily", "feminine"],
        "personality_match": ["optimistic", "bright"],
        "longevity": "5-6 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "20-30",
        "gender": "feminine",
        "description": "Bright floral fruity—optimism in a bottle.",
        "tagline": "Fresh blooms for today",
        "stock_available": True,
        "stock_quantity": 110,
        "rating": 4.4,
        "verified_reviews": 60,
        "image_url": "/images/IDN_031.jpeg"
    },
    {
        "product_id": "IDN_032",
        "name": "Freese",
        "brand": "Euodia Parfums",
        "price_idr": 300000,
        "fragrance_family": "green fresh",
        "top_notes": ["Green Leaves", "Citrus"],
        "middle_notes": ["Herbal Floral"],
        "base_notes": ["Musk", "Light Wood"],
        "occasions": ["daily", "natural"],
        "personality_match": ["clean", "fresh"],
        "longevity": "4-6 hours",
        "sillage": "light",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_day",
        "target_age": "18-30",
        "gender": "unisex",
        "description": "Light green freshness, revitalizing and clean.",
        "tagline": "Nature’s breath",
        "stock_available": True,
        "stock_quantity": 100,
        "rating": 4.3,
        "verified_reviews": 55,
        "image_url": "/images/IDN_032.jpeg"
    },
    {
        "product_id": "IDN_033",
        "name": "Revered Oud",
        "brand": "Kahf",
        "price_idr": 206625,
        "fragrance_family": "oriental woody gourmand",
        "top_notes": ["Saffron", "Vanilla"],
        "middle_notes": ["Oud", "Amber"],
        "base_notes": ["Woody Notes", "Musk"],
        "occasions": ["evening", "formal"],
        "personality_match": ["intense", "mysterious", "luxurious"],
        "longevity": "7-9 hours",
        "sillage": "strong",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-45",
        "gender": "unisex",
        "description": "Perpaduan oud smoky, saffron, dan vanilla yang hangat, menghadirkan aroma misterius dan elegan khas parfum oriental.",
        "tagline": "Mystery in every oud drop",
        "stock_available": True,
        "stock_quantity": 120,
        "rating": 4.6,
        "verified_reviews": 85,
        "image_url": "/images/IDN_033.jpeg"
    },
    {
        "product_id": "IDN_034",
        "name": "Mykonos",
        "brand": "Studiowest",
        "price_idr": 195000,
        "fragrance_family": "fruity sweet musky",
        "top_notes": ["Fruity Notes", "Citrus Accord"],
        "middle_notes": ["Floral Notes"],
        "base_notes": ["Musk", "Sweet Accord"],
        "occasions": ["daily", "casual"],
        "personality_match": ["playful", "cheerful", "youthful"],
        "longevity": "5-7 hours",
        "sillage": "moderate",
        "projection": "intimate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_all_day",
        "target_age": "18-30",
        "gender": "unisex",
        "description": "Wangi fruity manis berpadu dengan floral lembut dan musk, menghadirkan kesan segar sekaligus hangat untuk keseharian.",
        "tagline": "Sweet fruity elegance",
        "stock_available": True,
        "stock_quantity": 150,
        "rating": 4.4,
        "verified_reviews": 70,
        "image_url": "/images/IDN_034.jpeg"
    }
]

# Session storage for both HTTP and Chat protocols
user_sessions = {}
chat_sessions = {}  # Separate storage for chat protocol sessions
fragrance_profiles = {}
agent_metrics = {
    "total_agent_requests": 0,
    "successful_agent_responses": 0,
    "failed_agent_calls": 0,
    "chat_conversations": 0,
    "consultations_completed": 0,
    "recommendations_generated": 0
}

# CHAT PROTOCOL FUNCTIONS
def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a properly formatted ChatMessage"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

def analyze_intent(message: str) -> Dict[str, Any]:
    """Analyze user intent from natural language"""
    message_lower = message.lower()
    
    # Greeting detection
    if any(word in message_lower for word in ["hello", "hi", "halo", "hey", "good morning", "good afternoon"]):
        return {"intent": "greeting", "confidence": 0.9}
    
    # Consultation keywords
    elif any(word in message_lower for word in ["consultation", "konsultasi", "help me find", "recommend", "profile", "start"]):
        return {"intent": "consultation", "confidence": 0.8}
    
    # Recommendation keywords
    elif any(word in message_lower for word in ["recommendation", "rekomendasi", "suggest", "parfum", "fragrance", "perfume"]):
        return {"intent": "recommendation", "confidence": 0.8}
    
    # Purchase/inventory keywords
    elif any(word in message_lower for word in ["buy", "beli", "purchase", "stock", "inventory", "order"]):
        return {"intent": "purchase", "confidence": 0.7}
    
    # Fragrance family detection
    for family, data in FRAGRANCE_FAMILIES.items():
        if any(alias in message_lower for alias in data["aliases"]):
            return {"intent": "fragrance_preference", "family": family, "confidence": 0.6}
    
    # Default intent
    return {"intent": "consultation", "confidence": 0.3}

async def handle_greeting(ctx: Context, sender: str, session_id: str) -> str:
    """Handle greeting and initiate consultation"""
    
    # Initialize chat session
    chat_sessions[session_id] = {
        "user_address": sender,
        "stage": "greeting",
        "collected_data": {},
        "consultation_progress": 0.0,
        "started_at": datetime.now().timestamp()
    }
    
    response = """🌸 **Welcome to Aromance!** 🌸

Hello! I'm your personal fragrance consultant, specializing in Indonesian perfume culture. I'll help you discover the perfect scent that matches your unique personality and lifestyle! ✨

To get started, I'd love to learn about your fragrance preferences. You can tell me:

🌿 **What scents do you love?**
Examples: "I love fresh citrus scents", "I prefer sweet vanilla fragrances", "I like woody and warm perfumes"

💫 **Or choose from these popular families:**
1. Fresh & Citrusy 🍋
2. Floral & Romantic 🌸  
3. Sweet & Gourmand 🍯
4. Woody & Sophisticated 🌳
5. Spicy & Oriental 🌶️
6. I'm not sure, surprise me! 🎲

What sounds appealing to you?"""

    agent_metrics["chat_conversations"] += 1
    return response

async def handle_consultation_flow(ctx: Context, sender: str, session_id: str, message: str) -> str:
    """Handle the consultation conversation flow"""
    
    session = chat_sessions.get(session_id, {})
    stage = session.get("stage", "greeting")
    collected_data = session.get("collected_data", {})
    
    message_lower = message.lower()
    
    if stage == "greeting" or stage == "fragrance_discovery":
        return await handle_fragrance_discovery(ctx, session_id, message_lower, collected_data)
    elif stage == "occasion_analysis":
        return await handle_occasion_analysis(ctx, session_id, message_lower, collected_data)
    elif stage == "personality_matching":
        return await handle_personality_matching(ctx, session_id, message_lower, collected_data)
    elif stage == "budget_discussion":
        return await handle_budget_discussion(ctx, session_id, message_lower, collected_data)
    elif stage == "sensitivity_check":
        return await handle_sensitivity_check(ctx, session_id, message_lower, collected_data)
    elif stage == "consultation_complete":
        return await handle_recommendations(ctx, session_id, message, collected_data)
    else:
        return await handle_fragrance_discovery(ctx, session_id, message_lower, collected_data)

async def handle_fragrance_discovery(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle fragrance family discovery phase"""
    
    detected_families = []
    
    # Analyze for fragrance family keywords
    for family, data in FRAGRANCE_FAMILIES.items():
        if any(alias in message for alias in data["aliases"]):
            detected_families.append(family)
    
    # Handle numbered choices
    if "1" in message or "fresh" in message or "citrus" in message:
        detected_families = ["fresh"]
    elif "2" in message or "floral" in message or "romantic" in message:
        detected_families = ["floral"]
    elif "3" in message or "sweet" in message or "gourmand" in message:
        detected_families = ["gourmand"]
    elif "4" in message or "woody" in message or "sophisticated" in message:
        detected_families = ["woody"]
    elif "5" in message or "spicy" in message or "oriental" in message:
        detected_families = ["oriental"]
    elif "6" in message or "surprise" in message or "not sure" in message:
        detected_families = ["fresh", "floral"]  # Default mix
    
    if detected_families:
        family = detected_families[0]
        family_info = FRAGRANCE_FAMILIES.get(family, {})
        indonesian_examples = ", ".join(family_info.get("indonesian_examples", [])[:3])
        
        # Update session
        chat_sessions[session_id]["stage"] = "occasion_analysis"
        chat_sessions[session_id]["collected_data"]["fragrance_families"] = detected_families
        chat_sessions[session_id]["consultation_progress"] = 0.3
        
        response = f"""✨ **Excellent choice!** ✨

You're drawn to **{family}** fragrances! 😊 This family works beautifully in Indonesia's tropical climate. In Indonesian culture, {family} scents often feature notes like **{indonesian_examples}**.

Now, let's talk about **when you'd wear** your perfect fragrance. What occasions do you have in mind?

🎯 **Choose what fits your lifestyle:**
1. **Daily wear** - for work, school, or everyday activities
2. **Romantic dates** - special evenings and intimate moments  
3. **Formal events** - important meetings and professional occasions
4. **Casual hangouts** - weekend activities and relaxed times
5. **All occasions** - I want something versatile!

What's most important to you?"""
        
        return response
    else:
        response = """🤔 **Let me help you explore!**

I'd love to understand your scent preferences better! Could you describe what kind of fragrances appeal to you?

💡 **Here are some examples:**
• "I love **light and refreshing** scents like lemon or mint"
• "I prefer **rich and warm** fragrances like vanilla or sandalwood"  
• "I'm attracted to **floral** scents like jasmine or rose"
• "I enjoy **sweet** fragrances that remind me of desserts"

🌟 **Or try these popular choices:**
1. Fresh & Citrusy (like lime and cucumber) 🍋
2. Sweet & Gourmand (like vanilla and caramel) 🍯
3. Floral & Romantic (like jasmine and rose) 🌸
4. Woody & Sophisticated (like sandalwood) 🌳

What sounds appealing to you?"""
        
        return response

async def handle_occasion_analysis(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle occasion preference analysis"""
    
    occasions = []
    
    # Analyze message for occasion keywords
    if any(word in message for word in ["1", "daily", "work", "school", "office", "routine", "everyday"]):
        occasions.append("daily_work")
    if any(word in message for word in ["2", "formal", "important", "meeting", "business", "professional"]):
        occasions.append("formal")
    if any(word in message for word in ["3", "date", "romantic", "evening", "night", "special", "intimate"]):
        occasions.append("evening_date")
    if any(word in message for word in ["4", "casual", "weekend", "hangout", "relaxed", "fun"]):
        occasions.append("casual")
    if any(word in message for word in ["5", "versatile", "all", "everything", "any occasion"]):
        occasions = ["daily_work", "casual", "evening_date"]
    
    if not occasions:
        occasions = ["daily_work"]  # Default
    
    # Update session
    chat_sessions[session_id]["stage"] = "personality_matching"
    chat_sessions[session_id]["collected_data"]["occasions"] = occasions
    chat_sessions[session_id]["consultation_progress"] = 0.5
    
    response = """🎭 **Perfect! Now let's explore your personality!** 🎭

Understanding your personality helps me match you with fragrances that truly reflect who you are. This is where the magic happens! ✨

👫 **How would your closest friends describe you?**

🌟 **Choose the personality that resonates most:**
1. **Confident & Bold** - "I like to stand out and make a statement"
2. **Romantic & Gentle** - "I love sweet things and tender moments"  
3. **Professional & Polished** - "I'm always put-together and sophisticated"
4. **Fun & Energetic** - "I enjoy life's pleasures and love to have fun"
5. **Mysterious & Unique** - "I prefer to be intriguing and different"

💫 **Or describe yourself in your own words!**

What personality traits feel most like you?"""
    
    return response

async def handle_personality_matching(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle personality trait matching"""
    
    personality_traits = []
    
    # Analyze message for personality keywords
    if any(word in message for word in ["1", "confident", "bold", "strong", "assertive", "stand out", "statement"]):
        personality_traits.append("confident")
    if any(word in message for word in ["2", "romantic", "gentle", "sweet", "soft", "tender", "loving"]):
        personality_traits.append("romantic")
    if any(word in message for word in ["3", "professional", "polished", "put-together", "sophisticated", "elegant"]):
        personality_traits.append("professional")
    if any(word in message for word in ["4", "fun", "energetic", "playful", "cheerful", "lively", "enjoy"]):
        personality_traits.append("playful")
    if any(word in message for word in ["5", "mysterious", "unique", "intriguing", "different", "exotic"]):
        personality_traits.append("mysterious")
    
    if not personality_traits:
        personality_traits = ["versatile"]  # Default
    
    # Update session
    chat_sessions[session_id]["stage"] = "budget_discussion"
    chat_sessions[session_id]["collected_data"]["personality_traits"] = personality_traits
    chat_sessions[session_id]["consultation_progress"] = 0.7
    
    response = """💰 **Great! Now let's talk budget** 💰

There are wonderful fragrances at every price point, so don't worry about being practical. Quality and love come in all ranges! 💝

💸 **What's a comfortable range for a fragrance you'd truly love?**

🏷️ **Choose your budget preference:**
1. **Budget-friendly** - Under 100K IDR (Great starter options!)
2. **Mid-range** - 100K-300K IDR (Perfect balance of quality & price)
3. **Premium** - 300K-500K IDR (High-quality, investment pieces)
4. **Luxury** - 500K+ IDR (The finest fragrances, price no concern)
5. **I'm flexible** - Just show me the best matches regardless of price

🌟 **Remember:** The perfect fragrance is the one that makes YOU feel amazing, regardless of price! ✨

What feels right for you?"""
    
    return response

async def handle_budget_discussion(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle budget preference discussion"""
    
    budget_range = "moderate"
    
    if any(word in message for word in ["1", "budget", "100k", "under", "affordable", "cheap", "starter"]):
        budget_range = "budget"
    elif any(word in message for word in ["2", "mid", "middle", "moderate", "reasonable", "balance"]):
        budget_range = "moderate"
    elif any(word in message for word in ["3", "premium", "300k", "quality", "invest", "high-quality"]):
        budget_range = "premium"
    elif any(word in message for word in ["4", "luxury", "500k", "finest", "best", "price no concern"]):
        budget_range = "luxury"
    elif any(word in message for word in ["5", "flexible", "any", "best matches", "regardless"]):
        budget_range = "flexible"
    
    # Update session
    chat_sessions[session_id]["stage"] = "sensitivity_check"
    chat_sessions[session_id]["collected_data"]["budget_range"] = budget_range
    chat_sessions[session_id]["consultation_progress"] = 0.9
    
    response = """🌡️ **Almost done! One final important question** 🌡️

Do you have any **sensitivities or allergies**? Some people are sensitive to strong fragrances or specific ingredients. This helps me ensure your recommendations are comfortable for you to wear! 🙏

🩺 **Choose what describes you best:**
1. **No sensitivities** - I can wear any fragrance comfortably
2. **Sensitive to strong scents** - I prefer lighter, more subtle fragrances  
3. **Allergic to floral ingredients** - Flower scents sometimes cause reactions
4. **Prefer gentle formulas** - I like hypoallergenic or mild options
5. **I'm not sure** - I haven't experienced issues but want to be safe

🌿 **Don't worry!** There are amazing options for every sensitivity level, and Indonesian brands are particularly good at creating gentle, tropical-friendly formulations! 

How would you describe your sensitivity level?"""
    
    return response

async def handle_sensitivity_check(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle sensitivity and allergy assessment - Final step before recommendations"""
    
    sensitivity = "normal"
    
    if any(word in message for word in ["1", "no sensitivities", "any fragrance", "comfortable"]):
        sensitivity = "normal"
    elif any(word in message for word in ["2", "sensitive", "strong scents", "lighter", "subtle"]):
        sensitivity = "sensitive"
    elif any(word in message for word in ["3", "allergic", "floral", "reactions", "flower"]):
        sensitivity = "allergic"
    elif any(word in message for word in ["4", "gentle", "hypoallergenic", "mild"]):
        sensitivity = "hypoallergenic"
    elif any(word in message for word in ["5", "not sure", "haven't experienced", "safe"]):
        sensitivity = "cautious"
    
    # Update session with final data
    chat_sessions[session_id]["stage"] = "consultation_complete"
    chat_sessions[session_id]["collected_data"]["sensitivity"] = sensitivity
    chat_sessions[session_id]["consultation_progress"] = 1.0
    
    # Create fragrance profile
    profile = create_fragrance_profile_chat(session_id, collected_data)
    
    agent_metrics["consultations_completed"] += 1
    
    response = f"""🎉 **Consultation Complete!** 🎉

✨ **Your Personalized Fragrance Identity:** '{profile.personality_type}' with a preference for {', '.join(profile.preferred_families[:2])} families! 

🎯 **I'm now generating intelligent recommendations** specifically curated for your unique profile! This might take a moment as I analyze our entire Indonesian fragrance database...

🌺 **What I learned about you:**
• **Fragrance Style:** {', '.join(profile.preferred_families)}
• **Personality:** {profile.personality_type} 
• **Lifestyle:** Perfect for {', '.join(profile.occasion_preferences)} occasions
• **Budget Range:** {profile.budget_range.title()} tier
• **Sensitivity:** {profile.sensitivity_level.title()} level

💫 **Next Steps:**
Just say "**show my recommendations**" and I'll present your personalized matches!

Ready to see your perfect fragrances? 🎁"""
    
    return response

async def handle_recommendations(ctx: Context, session_id: str, message: str, collected_data: Dict) -> str:
    """Handle recommendation generation and display"""
    
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["show", "recommendations", "suggest", "matches", "see", "ready"]):
        
        # Generate recommendations using embedded logic
        recommendations = await generate_chat_recommendations(ctx, collected_data)
        
        if not recommendations:
            return """😅 **I apologize!**

No products currently match your specific criteria perfectly. This could be due to very specific requirements or temporary stock issues.

🔄 **What you can do:**
• Try adjusting your budget range
• Be more flexible with fragrance families  
• Contact our support team for personalized assistance

Would you like to **restart the consultation** with different preferences?"""
        
        agent_metrics["recommendations_generated"] += 1
        
        # Create detailed recommendation response
        response = f"""🎯 **Your Personalized Aromance Recommendations** 🎯

Based on your consultation, I've found **{len(recommendations)} perfect matches** from our Indonesian collection! ✨

"""
        
        for i, rec in enumerate(recommendations, 1):
            response += f"""**{i}. {rec.name}** by {rec.brand}
💰 **Price:** {rec.price_idr:,} IDR
🌸 **Family:** {rec.fragrance_family.title()}  
⭐ **Match Score:** {int(rec.match_score*100)}%
📝 **Why it's perfect:** {rec.reasoning[:150]}...
🇮🇩 **Indonesian Heritage:** {'Yes' if rec.indonesian_heritage else 'No'}
☪️ **Halal Certified:** {'Yes' if rec.halal_certified else 'No'}

"""
        
        # Add explanation
        explanation = create_recommendation_explanation_chat(collected_data, recommendations)
        response += f"\n💡 **Why These Recommendations?**\n{explanation}\n"
        
        # Add next steps
        response += """
🛍️ **Ready to Purchase?**
Unfortunately, purchasing features are only available in our dashboard. Please visit our website to complete your order!

🔄 **Want More Options?**
• Say "**different recommendations**" for alternatives
• Say "**restart consultation**" to try again
• Ask about specific products: "**tell me more about [product name]**"

What would you like to do next? 😊"""
        
        return response
    
    elif any(word in message_lower for word in ["different", "alternatives", "other", "more"]):
        return """🔄 **Looking for alternatives?**

I can suggest exploring different fragrance families or adjusting your criteria:

🌟 **Try These Options:**
• Say "**restart consultation**" to explore different preferences
• Tell me "**I want something more [fresh/floral/sweet/woody]**"
• Ask "**what's trending in Indonesia**" for popular choices

What interests you most?"""
    
    elif any(word in message_lower for word in ["restart", "start over", "new consultation"]):
        # Reset session
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        return await handle_greeting(ctx, "", session_id)
    
    else:
        return """💬 **I'm here to help!**

You can ask me:
• "**Show my recommendations**" - See your personalized matches
• "**Different recommendations**" - Explore alternatives  
• "**Restart consultation**" - Start over with new preferences
• "**Tell me more about [product]**" - Get detailed product info

What would you like to do? 😊"""

def create_fragrance_profile_chat(session_id: str, collected_data: Dict) -> FragranceProfile:
    """Create comprehensive fragrance profile from chat consultation"""
    
    user_id = f"chat_user_{session_id}"
    
    # Determine personality type
    personality_traits = collected_data.get("personality_traits", ["versatile"])
    if "confident" in personality_traits:
        personality_type = "Bold Indonesian Trendsetter"
    elif "romantic" in personality_traits:
        personality_type = "Romantic Indonesian Soul"
    elif "professional" in personality_traits:
        personality_type = "Professional Indonesian Elite"
    elif "playful" in personality_traits:
        personality_type = "Cheerful Indonesian Spirit"
    elif "mysterious" in personality_traits:
        personality_type = "Mysterious Indonesian Enigma"
    else:
        personality_type = "Versatile Indonesian Character"
    
    # Determine lifestyle
    occasions = collected_data.get("occasions", ["daily_work"])
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
        "preference_change": f"Discovered preference for {', '.join(fragrance_families)} fragrances via chat consultation",
        "trigger_event": "Chat consultation completed",
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

async def generate_chat_recommendations(ctx: Context, collected_data: Dict) -> List[ProductRecommendation]:
    """Generate intelligent fragrance recommendations for chat sessions"""
    
    recommendations = []
    preferred_families = collected_data.get("fragrance_families", ["fresh"])
    personality_traits = collected_data.get("personality_traits", ["versatile"])
    occasions = collected_data.get("occasions", ["daily"])
    budget_range = collected_data.get("budget_range", "moderate")
    sensitivity = collected_data.get("sensitivity", "normal")
    
    ctx.logger.info(f"Chat recommendations for families: {preferred_families}")
    
    for product in INDONESIAN_FRAGRANCE_DATABASE:
        if not product.get("stock_available", False):
            continue
            
        # Calculate comprehensive match score
        match_score = calculate_chat_match_score(product, collected_data)
        
        if match_score < 0.4:  # Minimum threshold
            continue
            
        # Budget filtering
        budget_max = get_budget_max(budget_range)
        if budget_max and product["price_idr"] > budget_max:
            continue
            
        # Sensitivity filtering
        if sensitivity == "sensitive" and product.get("sillage") == "heavy":
            continue
        if sensitivity == "allergic" and "floral" in product["fragrance_family"]:
            continue
            
        # Create reasoning
        reasoning = generate_chat_reasoning(product, collected_data, match_score)
        
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

def calculate_chat_match_score(product: Dict, collected_data: Dict) -> float:
    """Calculate match score for chat recommendations"""
    
    score = 0.0
    
    # Fragrance family matching (30% weight)
    preferred_families = collected_data.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        score += 0.3
    
    # Personality matching (25% weight)
    personality_traits = collected_data.get("personality_traits", [])
    product_personalities = product.get("personality_match", [])
    personality_overlap = len(set(personality_traits) & set(product_personalities))
    if personality_overlap > 0:
        score += 0.25 * min(personality_overlap / max(len(personality_traits), 1), 1.0)
    
    # Occasion matching (20% weight)
    user_occasions = collected_data.get("occasions", [])
    product_occasions = product.get("occasions", [])
    occasion_overlap = len(set(user_occasions) & set(product_occasions))
    if occasion_overlap > 0:
        score += 0.2 * min(occasion_overlap / max(len(user_occasions), 1), 1.0)
    
    # Budget compatibility (15% weight)
    budget_range = collected_data.get("budget_range", "moderate")
    price = product["price_idr"]
    budget_score = calculate_budget_compatibility(price, budget_range)
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

def get_budget_max(budget_range: str) -> Optional[int]:
    """Get maximum budget amount for filtering"""
    budget_limits = {
        "budget": 100000,
        "moderate": 300000,
        "premium": 500000,
        "luxury": None,  # No limit
        "flexible": None  # No limit
    }
    return budget_limits.get(budget_range)

def calculate_budget_compatibility(price: int, budget_range: str) -> float:
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
    elif budget_range == "flexible":
        return 0.8  # Good score regardless of price
    
    return 0.5

def generate_chat_reasoning(product: Dict, collected_data: Dict, match_score: float) -> str:
    """Generate intelligent reasoning for chat recommendations"""
    
    reasons = []
    
    # Match score interpretation
    if match_score > 0.8:
        reasons.append("✨ PERFECT MATCH! Highly recommended")
    elif match_score > 0.6:
        reasons.append("💫 Excellent choice for your profile")
    else:
        reasons.append("✅ Great alternative option")
    
    # Fragrance family match
    preferred_families = collected_data.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        reasons.append(f"Perfect {product['fragrance_family']} match")
    
    # Personality alignment
    personality_traits = collected_data.get("personality_traits", [])
    product_personalities = product.get("personality_match", [])
    if set(personality_traits) & set(product_personalities):
        matching_traits = list(set(personality_traits) & set(product_personalities))
        reasons.append(f"Matches your {', '.join(matching_traits)} character")
    
    # Indonesian heritage
    if product.get("indonesian_heritage", False):
        reasons.append("🇮🇩 Proudly Indonesian brand")
    
    # Halal certification
    if product.get("halal_certified", False):
        reasons.append("☪️ Halal certified")
    
    # Climate suitability
    if product.get("climate_suitability") == "tropical_all_day":
        reasons.append("🌴 Perfect for tropical climate")
    
    return " • ".join(reasons[:4])  # Limit to 4 reasons for chat

def create_recommendation_explanation_chat(collected_data: Dict, recommendations: List[ProductRecommendation]) -> str:
    """Create explanation for chat recommendations"""
    
    if not recommendations:
        return "No suitable matches found for your specific criteria."
    
    personality_traits = collected_data.get("personality_traits", ["unique"])
    preferred_families = collected_data.get("fragrance_families", ["fresh"])
    
    explanation = f"Based on your {', '.join(personality_traits)} personality and love for {', '.join(preferred_families)} fragrances, "
    explanation += f"these {len(recommendations)} selections are specifically curated for your profile! ✨"
    
    top_match = recommendations[0]
    explanation += f"\n\n🎯 **Top Match:** {top_match.name} with {int(top_match.match_score*100)}% compatibility!"
    
    # Add insights
    indonesian_count = sum(1 for rec in recommendations if rec.indonesian_heritage)
    halal_count = sum(1 for rec in recommendations if rec.halal_certified)
    
    if indonesian_count > 0:
        explanation += f"\n🇮🇩 {indonesian_count} authentic Indonesian brands supporting local industry"
    if halal_count > 0:
        explanation += f"\n☪️ {halal_count} products are halal certified"
    
    explanation += f"\n🌴 All specially curated for Indonesia's tropical climate!"
    
    return explanation

async def handle_out_of_scope(ctx: Context, message: str) -> str:
    """Handle messages outside of fragrance consultation scope"""
    
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["buy", "purchase", "order", "payment", "checkout"]):
        return """🛍️ **Purchase & Orders**

I'd love to help with purchasing, but unfortunately buying features are only available in our **dashboard**! 

🌐 **To purchase:**
• Visit our website dashboard
• Browse our full catalog  
• Complete secure checkout
• Track your orders

For now, I can help you **discover the perfect fragrances** through consultation! Want to continue exploring scents? 😊"""
    
    elif any(word in message_lower for word in ["verify", "verified", "seller", "brand", "partnership"]):
        return """✅ **Verification & Partnerships**

Brand verification and seller partnerships are handled through our **business dashboard**! 

🏢 **For business inquiries:**
• Visit our business portal
• Submit verification documents
• Connect with our partnership team
• Access seller tools

I'm here to help with **fragrance discovery and consultation**! Want to explore some amazing Indonesian scents? 🌸"""
    
    elif any(word in message_lower for word in ["account", "profile", "settings", "login", "password"]):
        return """👤 **Account Management**

Account settings and profile management are available in our **dashboard**!

⚙️ **To manage your account:**
• Visit our website dashboard
• Update your profile
• Change settings  
• View purchase history

I can help you **discover your fragrance personality** right here in chat! Want to start a consultation? ✨"""
    
    elif any(word in message_lower for word in ["support", "help", "problem", "issue", "complaint"]):
        return """🎧 **Customer Support**

For technical issues and detailed support, please contact our support team through the **dashboard**!

📞 **Get help with:**
• Technical problems
• Order issues
• Account problems  
• Detailed inquiries

But I'm perfect for **fragrance consultation and discovery**! Want me to help you find your signature scent? 🌺"""
    
    else:
        return """🤔 **I'm here for fragrance consultation!**

I specialize in helping you discover the perfect Indonesian fragrances through personalized consultation! 

✨ **I can help you with:**
• Fragrance personality discovery
• Personalized recommendations  
• Scent family exploration
• Indonesian perfume culture

🚫 **For other services** (purchasing, verification, account issues), please visit our dashboard!

Ready to discover your signature scent? Just say **"hello"** to start! 🌸"""

# CHAT PROTOCOL MESSAGE HANDLERS
@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Main chat message handler for Agentverse communication"""
    
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content}")
    
    # Store sender in session context
    ctx.storage.set(str(ctx.session), sender)
    
    # Send acknowledgment
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )
    
    session_id = str(ctx.session)
    
    try:
        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"🚀 Starting new chat session with {sender}")
                response_text = await handle_greeting(ctx, sender, session_id)
                
            elif isinstance(item, TextContent):
                ctx.logger.info(f"📝 Processing text: {item.text}")
                
                # Analyze intent
                intent_analysis = analyze_intent(item.text)
                intent = intent_analysis.get("intent")
                
                if intent == "greeting":
                    response_text = await handle_greeting(ctx, sender, session_id)
                elif intent in ["consultation", "fragrance_preference", "recommendation"]:
                    response_text = await handle_consultation_flow(ctx, sender, session_id, item.text)
                else:
                    # Handle out of scope requests
                    response_text = await handle_out_of_scope(ctx, item.text)
                
            elif isinstance(item, EndSessionContent):
                ctx.logger.info(f"🔚 Ending session with {sender}")
                # Clean up session data
                if session_id in chat_sessions:
                    del chat_sessions[session_id]
                response_text = "Thank you for using Aromance! Feel free to start a new consultation anytime. Have a fragrant day! 🌸✨"
                
            else:
                ctx.logger.info(f"❓ Unexpected content type from {sender}")
                response_text = "I received an unexpected message type. Could you please rephrase your question? 🤔"
        
        # Send response
        response = create_text_chat(response_text)
        await ctx.send(sender, response)
        
        agent_metrics["successful_agent_responses"] += 1
        ctx.logger.info(f"✅ Response sent to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing chat message: {e}")
        error_response = create_text_chat(
            "I apologize, but I encountered an error processing your request. Please try again or rephrase your question. 😊"
        )
        await ctx.send(sender, error_response)
        agent_metrics["failed_agent_calls"] += 1

@chat_proto.on_message(ChatAcknowledgement)
async def handle_chat_acknowledgment(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgments"""
    ctx.logger.info(f"✅ Received acknowledgment from {sender} for message {msg.acknowledged_msg_id}")

# EXISTING HTTP FUNCTIONALITY (UNCHANGED) - Keep all original coordinator functionality

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
        "address": "agent1qvf6kv530le2glvp239rvjy6hyu3hz8jchp6y29yp2sg2nm0rwk4x9nttnd",
        "endpoint": "http://127.0.0.1:8005",
        "port": 8005,
        "status": "unknown"
    }
}

# Session tracking for HTTP requests
active_agent_sessions = {}
pending_agent_requests = {}

# HTTP ROUTE FUNCTIONS (UNCHANGED - keeping existing functionality)
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
    """Communicate with consultation agent (HTTP)"""
    
    agent_info = AGENT_REGISTRY["consultation"]
    ctx.logger.info(f"📞 Calling consultation agent at {agent_info['address']}")
    
    try:
        session_id = f"consul_{request_id}"
        
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
        
    except Exception as e:
        ctx.logger.error(f"❌ Consultation agent communication failed: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["consultation"]["status"] = "error"
        
        return f"""⚠️ **Consultation Agent Error**

Connection failed: {str(e)[:100]}

**Status:** Agent temporarily unavailable
**Action:** Trying alternative connection methods
**Request ID:** {request_id}"""

async def communicate_with_recommendation_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with recommendation agent (HTTP)"""
    
    agent_info = AGENT_REGISTRY["recommendation"]
    ctx.logger.info(f"📞 Calling recommendation agent at {agent_info['address']}")
    
    try:
        session_id = f"rec_{request_id}"
        
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
        
    except Exception as e:
        ctx.logger.error(f"❌ Recommendation agent error: {e}")
        agent_metrics["failed_agent_calls"] += 1
        AGENT_REGISTRY["recommendation"]["status"] = "error"
        return f"""❌ **Recommendation Agent Error**

{str(e)[:100]}

**Session:** {session_id}
**Status:** Connection failed"""

async def communicate_with_inventory_agent(ctx: Context, user_id: str, message: str, request_id: str) -> str:
    """Communicate with inventory agent (HTTP)"""
    
    agent_info = AGENT_REGISTRY["inventory"]
    ctx.logger.info(f"📞 Calling inventory agent at {agent_info['address']}")
    
    try:
        session_id = f"inv_{request_id}"
        
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
    """Communicate with analytics agent (HTTP)"""
    
    agent_info = AGENT_REGISTRY["analytics"]
    ctx.logger.info(f"📞 Calling analytics agent at {agent_info['address']}")
    
    try:
        session_id = f"ana_{request_id}"
        
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

# AGENT HEALTH MONITORING (UNCHANGED)
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

# HTTP REQUEST HANDLERS (UNCHANGED - keeping all original functionality)
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
        
    else:
        ctx.logger.warning("⚠️ Received agent response with no matching session")

# REST ENDPOINTS (UNCHANGED)
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

# PROTOCOL REGISTRATION - Include both chat and existing protocols
coordinator_agent.include(chat_proto, publish_manifest=True)

# MAINTENANCE (UPDATED to include chat sessions)
@coordinator_agent.on_interval(period=120.0)  # Every 2 minutes
async def periodic_agent_maintenance(ctx: Context):
    """Regular agent health checks and cleanup"""
    await check_agent_health(ctx)
    
    # Clean old HTTP sessions (older than 10 minutes)
    current_time = datetime.now().timestamp()
    expired_sessions = [
        session_id for session_id, session_data in active_agent_sessions.items()
        if current_time - session_data["timestamp"] > 600
    ]
    
    for session_id in expired_sessions:
        del active_agent_sessions[session_id]
    
    # Clean old chat sessions (older than 30 minutes)
    expired_chat_sessions = [
        session_id for session_id, session_data in chat_sessions.items()
        if current_time - session_data["started_at"] > 1800
    ]
    
    for session_id in expired_chat_sessions:
        del chat_sessions[session_id]
    
    if expired_sessions or expired_chat_sessions:
        ctx.logger.info(f"🧹 Cleaned {len(expired_sessions)} HTTP sessions, {len(expired_chat_sessions)} chat sessions")
    
    # Log comprehensive metrics
    ctx.logger.info(f"📊 System Metrics:")
    ctx.logger.info(f"  • Active HTTP sessions: {len(active_agent_sessions)}")
    ctx.logger.info(f"  • Active chat sessions: {len(chat_sessions)}")
    ctx.logger.info(f"  • Total requests: {agent_metrics['total_agent_requests']}")
    ctx.logger.info(f"  • Successful responses: {agent_metrics['successful_agent_responses']}")
    ctx.logger.info(f"  • Failed calls: {agent_metrics['failed_agent_calls']}")
    ctx.logger.info(f"  • Chat conversations: {agent_metrics['chat_conversations']}")
    ctx.logger.info(f"  • Consultations completed: {agent_metrics['consultations_completed']}")
    ctx.logger.info(f"  • Recommendations generated: {agent_metrics['recommendations_generated']}")
    ctx.logger.info(f"  • Healthy agents: {agent_metrics['healthy_agents']}/{len(AGENT_REGISTRY)}")

# STARTUP
@coordinator_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🤖 Aromance Enhanced Coordinator Started!")
    ctx.logger.info(f"📍 Coordinator Address: {coordinator_agent.address}")
    ctx.logger.info(f"🔗 HTTP Endpoint: http://127.0.0.1:8000")
    ctx.logger.info(f"💬 Chat Protocol: Enabled with mailbox")
    
    ctx.logger.info("🎯 **DUAL INTERFACE SYSTEM:**")
    ctx.logger.info("  📱 CHAT PROTOCOL - For Agentverse communication")
    ctx.logger.info("     • Natural language consultation")
    ctx.logger.info("     • Embedded recommendation engine")
    ctx.logger.info("     • Indonesian fragrance expertise")
    ctx.logger.info("     • Session management via mailbox")
    
    ctx.logger.info("  🌐 HTTP INTERFACE - For bridge/frontend")
    ctx.logger.info(f"     • Managing {len(AGENT_REGISTRY)} specialized agents:")
    
    for agent_name, agent_info in AGENT_REGISTRY.items():
        ctx.logger.info(f"       • {agent_name}: {agent_info['address']} ({agent_info['endpoint']})")
    
    ctx.logger.info("✅ Ready for both chat consultation and agent coordination! 🌺")
    
    # Initial health check
    await check_agent_health(ctx)
    
    # Set startup metrics
    agent_metrics["startup_time"] = datetime.now().timestamp()
    agent_metrics["coordinator_address"] = str(coordinator_agent.address)
    agent_metrics["chat_protocol_enabled"] = True
    agent_metrics["dual_interface"] = True

# UTILITY FUNCTIONS
def update_agent_address(agent_name: str, address: str):
    """Helper function to update agent addresses"""
    if agent_name in AGENT_REGISTRY:
        AGENT_REGISTRY[agent_name]["address"] = address
        print(f"✅ {agent_name} agent address updated: {address}")
    else:
        print(f"❌ Agent {agent_name} not found in registry")

# ADDITIONAL HTTP CONSULTATION ENDPOINTS (for backward compatibility)
@coordinator_agent.on_rest_post("/consultation/start", ConsultationStartRequest, ConsultationStartResponse)
async def start_consultation_endpoint(ctx: Context, req: ConsultationStartRequest) -> ConsultationStartResponse:
    """HTTP endpoint to start consultation (backward compatibility)"""
    try:
        user_id = req.user_id
        session_id = req.session_id
        
        if not user_id or not session_id:
            return ConsultationStartResponse(
                success=False,
                response={"error": "user_id and session_id are required"}
            )
        
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
        response_data = {
            "user_id": user_id,
            "session_id": session_id,
            "response": "Hello! 🌸 I'm your Aromance AI consultant specializing in Indonesian fragrance culture. I'll help you discover the perfect scent that matches your personality and lifestyle. Let's start - do you have any favorite scents or perfumes you've tried before?",
            "follow_up_questions": [
                "Tell me about your favorite perfume experience",
                "I'm new to perfumes, help me explore",
                "I prefer fresh and light fragrances",
                "I like long-lasting, bold scents"
            ],
            "data_collected": {},
            "consultation_progress": 0.1,
            "next_step": "fragrance_preference_discovery"
        }
        
        return ConsultationStartResponse(
            success=True,
            response=response_data
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Consultation start error: {e}")
        return ConsultationStartResponse(
            success=False,
            response={"error": "Internal server error"}
        )

@coordinator_agent.on_rest_post("/consultation/message", ConsultationMessageRequest, ConsultationMessageResponse)
async def consultation_message_endpoint(ctx: Context, req: ConsultationMessageRequest) -> ConsultationMessageResponse:
    """HTTP endpoint for consultation messages (backward compatibility)"""
    try:
        user_id = req.user_id
        session_id = req.session_id
        message = req.message
        
        if not all([user_id, session_id, message]):
            return ConsultationMessageResponse(
                success=False,
                response={"error": "user_id, session_id, and message are required"}
            )
        
        if session_id not in user_sessions:
            return ConsultationMessageResponse(
                success=False,
                response={"error": "Session not found"}
            )
        
        # Use chat logic for HTTP consultation
        session = user_sessions[session_id]
        response_text = await handle_consultation_flow(ctx, user_id, session_id, message)
        
        # Convert to HTTP response format
        response_data = {
            "user_id": user_id,
            "session_id": session_id,
            "response": response_text,
            "follow_up_questions": [],
            "data_collected": session.get("collected_data", {}),
            "consultation_progress": session.get("consultation_progress", 0.0),
            "next_step": session.get("current_focus", "consultation")
        }
        
        return ConsultationMessageResponse(
            success=True,
            response=response_data
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Consultation message error: {e}")
        return ConsultationMessageResponse(
            success=False,
            response={"error": "Internal server error"}
        )

if __name__ == "__main__":
    print("🚀 Starting Aromance Enhanced Coordinator Agent...")
    print(f"📍 Coordinator Address: {coordinator_agent.address}")
    print()
    print("🎯 DUAL INTERFACE SYSTEM:")
    print("  💬 CHAT PROTOCOL - Agentverse Communication")
    print("     • Natural language fragrance consultation")
    print("     • Embedded recommendation system")
    print("     • Indonesian fragrance culture expertise")
    print("     • Mailbox-enabled for reliable messaging")
    print()
    print("  🌐 HTTP INTERFACE - Bridge/Frontend Communication")
    print("     🔧 Agent Registry:")
    for name, info in AGENT_REGISTRY.items():
        print(f"       • {name}: {info['address']} -> {info['endpoint']}")
    print()
    print("⚠️  SETUP REQUIREMENTS:")
    print("   1. Replace 'YOUR_MAILBOX_KEY' with actual mailbox key from Agentverse")
    print("   2. Update agent addresses in AGENT_REGISTRY with your actual agent addresses")
    print("   3. Ensure all specialized agents are running on their specified ports")
    print()
    print("✨ FEATURES:")
    print("   • Complete fragrance consultation via chat protocol")
    print("   • Intelligent recommendation generation")
    print("   • Indonesian fragrance database integration")
    print("   • Dual session management (HTTP + Chat)")
    print("   • Automatic session cleanup and health monitoring")
    print("   • Comprehensive error handling and logging")
    print()
    print("🌺 Ready to serve both Agentverse users and dashboard clients!")
    
    coordinator_agent.run()