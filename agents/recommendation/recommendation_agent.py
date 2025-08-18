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
        "image_url": "/images/IDN_001.jpg"
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
        "image_url": "/images/IDN_002.jpg"
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
        "image_url": "/images/IDN_003.jpg"
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
        "image_url": "/images/IDN_004.jpg"
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
        "image_url": "/images/IDN_005.jpg"
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
        "image_url": "/images/IDN_006.jpg"
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
        "image_url": "/images/IDN_007.jpg"
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
        "image_url": "/images/IDN_008.jpg"
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
        "image_url": "/images/IDN_009.jpg"
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
        "image_url": "/images/IDN_010.jpg"
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
        "image_url": "/images/IDN_011.jpg"
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
        "image_url": "/images/IDN_012.jpg"
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
        "image_url": "/images/IDN_013.jpg"
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
        "image_url": "/images/IDN_014.jpg"
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
        "image_url": "/images/IDN_015.jpg"
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
        "image_url": "/images/IDN_016.jpg"
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
        "image_url": "/images/IDN_017.jpg"
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
        "image_url": "/images/IDN_018.jpg"
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
        "image_url": "/images/IDN_019.jpg"
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
        "image_url": "/images/IDN_020.jpg"
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
        "image_url": "/images/IDN_021.jpg"
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
        "image_url": "/images/IDN_022.jpg"
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
        "image_url": "/images/IDN_023.jpg"
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
        "image_url": "/images/IDN_024.jpg"
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
        "image_url": "/images/IDN_025.jpg"
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
        "image_url": "/images/IDN_026.jpg"
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
        "image_url": "/images/IDN_027.jpg"
    },
    {
        "product_id": "IDN_028",
        "name": "Heirloom Tuberose",
        "brand": "Mother of Pearl",
        "price_idr": 550000,
        "fragrance_family": "white floral",
        "top_notes": ["Green Leaf", "Tuberose"],
        "middle_notes": ["Jasmine", "Gardenia"],
        "base_notes": ["Soft Musk", "Cream"],
        "occasions": ["evening", "romantic"],
        "personality_match": ["elegant", "sensual"],
        "longevity": "6-8 hours",
        "sillage": "moderate",
        "projection": "moderate",
        "indonesian_heritage": True,
        "halal_certified": True,
        "local_ingredients": [],
        "climate_suitability": "tropical_evening",
        "target_age": "25-40",
        "gender": "feminine",
        "description": "Rich white floral color like jewelry—soft, elegant, and alluring.",
        "tagline": "Floral heirloom luxury",
        "stock_available": True,
        "stock_quantity": 80,
        "rating": 4.7,
        "verified_reviews": 65,
        "image_url": "/images/IDN_028.jpg"
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
        "image_url": "/images/IDN_029.jpg"
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
        "image_url": "/images/IDN_030.jpg"
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
        "image_url": "/images/IDN_031.jpg"
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
        "image_url": "/images/IDN_032.jpg"
    },
    {
        "product_id": "IDN_033",
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
        "image_url": "/images/IDN_033.jpg"
    },
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