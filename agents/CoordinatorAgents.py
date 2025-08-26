from uagents import Agent, Context, Model
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from uuid import uuid4
import hashlib
import re

# CHAT PROTOCOL IMPORTS - using only available modules
try:
    from uagents.protocols.chat import (
        ChatMessage,
        ChatAcknowledgement,
        TextContent,
        EndSessionContent,
        StartSessionContent,
        chat_protocol_spec,
    )
except ImportError:
    from uagents_core.contrib.protocols.chat import (
        ChatMessage,
        ChatAcknowledgement,
        TextContent,
        EndSessionContent,
        StartSessionContent,
        chat_protocol_spec,
    )

# BASIC MODELS FOR CHAT
class FragranceProfile(Model):
    user_id: str
    personality_type: str
    lifestyle: str
    preferred_families: List[str]
    occasion_preferences: List[str]
    season_preferences: List[str]
    sensitivity_level: str
    budget_range: str
    consultation_progress: float

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

# AGENT CONFIGURATION WITH MAILBOX
coordinator_agent = Agent(
    name="aromance_chat_coordinator", 
    port=8000,
    seed="aromance_chat_coordinator_2025",
    endpoint=["http://127.0.0.1:8000/submit"],
    mailbox="eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjM3Nzg2NzIsImlhdCI6MTc1NjAwMjY3MiwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiIzMTQ5Y2RhNjI1YWM2OTdjYzA2ZjI3NzQiLCJzY29wZSI6ImF2Iiwic3ViIjoiMzI4NDNmYTMzYzM1MTNjODUxNzJlM2Y4NGNiOWQ2ODkwMGI4OWE2ZjJmY2Y1OTVmIn0.i-KkXbJu_Vx_LNnli-YzkjlqD8aMrU4wY9DJVq0uHSFmToiPD85RF0r5RVBuTnegxdu3fXglAkokaYnRVVvy4NfG4qIWSbaXdFqekB3VtBmSiMQPb9Bza4OATmonQ8oiXu7XY55jOIIJ5VAeLAeR75IuL9Rg25yPVTn2rw6YEeupHovHWvRF6oo8co4gCJtuzmXEaBdV5pFxN3Ep2azJuJIBTPTIUouIkCO15BF_YXgRYzq5nVQ1KSHIPl7PvTxKxCM0BS6VkUu1MP43ccpY2FvbViHAnYfm_AI4oeSDpjUgjaBzrefM9y7vL1gYXMBdN1nZw3BF7O1E4NiKHiZv_w"  
)

# CHAT PROTOCOL SETUP
chat_proto = Protocol(spec=chat_protocol_spec)

# Enhanced Indonesian Fragrance Knowledge Base
FRAGRANCE_FAMILIES = {
    "fresh": {
        "keywords": ["fresh", "segar", "bersih", "light", "ringan", "citrus", "clean", "airy", "cooling", "lemon", "lime", "mint", "cucumber", "energizing", "refreshing", "bright", "crisp", "zingy", "aromatic", "herby", "citrusy", "oceanic", "aquatic", "laut", "samudra", "harum segar", "wangi bersih"],
        "variations": ["i like fresh", "love fresh scents", "want something light", "prefer clean", "something refreshing", "citrus scents", "bright fragrance", "i love citrusy smells", "oceanic scents", "aquatic fragrances", "saya suka segar", "cinta wangi ringan", "ingin harum bersih", "parfum citrus", "bau laut"],
        "indonesian_examples": ["jeruk nipis", "daun pandan", "air kelapa", "mentimun", "teh hijau", "daun mint", "air laut"],
        "personality_match": ["energetic", "optimistic", "casual", "sporty"],
        "description": "Fresh and invigorating scents perfect for daily wear in tropical climate"
    },
    "floral": {
        "keywords": ["floral", "bunga", "feminine", "romantic", "melati", "rose", "flowery", "blooming", "jasmine", "flower", "petals", "garden", "bouquet", "elegant", "powdery", "fresh cut flowers", "mekar", "bunga-bungaan", "wangi bunga", "harum mawar"],
        "variations": ["i love flowers", "floral scents", "something feminine", "romantic fragrance", "flower perfume", "jasmine scent", "rose perfume", "elegant floral", "powdery floral", "blooming scents", "saya cinta bunga", "parfum floral", "wangi romantis", "bau melati"],
        "indonesian_examples": ["melati", "mawar", "kamboja", "cempaka", "kenanga", "anggrek", "bunga matahari"],
        "personality_match": ["romantic", "feminine", "gentle", "elegant"],
        "description": "Beautiful flower scents that capture femininity and romance"
    },
    "fruity": {
        "keywords": ["fruity", "buah", "manis buah", "tropical", "sweet fruit", "juicy", "berry", "mango", "pineapple", "apple", "peach", "berry", "tropical fruit", "buah-buahan", "manis segar", "wangi buah", "harum tropis", "berry manis"],
        "variations": ["fruit scents", "sweet fruit", "tropical fragrance", "something fruity", "mango scent", "berry perfume", "tropical fruit", "juicy smells", "sweet berry", "saya suka buah", "parfum fruity", "wangi manis buah", "bau mangga"],
        "indonesian_examples": ["mangga", "nanas", "rambutan", "durian", "jambu", "pisang", "stroberi"],
        "personality_match": ["playful", "youthful", "cheerful", "fun"],
        "description": "Sweet tropical fruit scents that are playful and joyful"
    },
    "woody": {
        "keywords": ["woody", "kayu", "warm", "hangat", "earthy", "sandalwood", "cedar", "tree", "wood", "sophisticated", "mature", "grounding", "deep", "opulent", "resinous", "kayu-kayuan", "wangi tanah", "harum kayu", "cendana"],
        "variations": ["woody scents", "warm fragrance", "sandalwood perfume", "earthy scent", "sophisticated fragrance", "mature scent", "wood notes", "resinous smells", "opulent woody", "saya cinta kayu", "parfum woody", "wangi hangat", "bau cendana"],
        "indonesian_examples": ["cendana", "gaharu", "kayu manis", "patchouli", "kayu jati", "pinus", "akar wangi"],
        "personality_match": ["sophisticated", "mature", "confident", "grounded"],
        "description": "Warm woody scents perfect for sophisticated personalities"
    },
    "oriental": {
        "keywords": ["oriental", "spicy", "rempah", "eksotis", "mystery", "exotic", "warm spice", "cinnamon", "clove", "mysterious", "bold", "intense", "amber", "resin", "dry resin", "timur", "wangi rempah", "harum eksotis", "kayu manis"],
        "variations": ["spicy scents", "exotic fragrance", "oriental perfume", "mysterious scent", "spice fragrance", "bold perfume", "intense fragrance", "amber smells", "resin notes", "saya suka rempah", "parfum oriental", "wangi misterius", "bau cengkeh"],
        "indonesian_examples": ["cengkeh", "nutmeg", "cardamom", "vanilla", "benzoin", "jahe", "kunyit"],
        "personality_match": ["mysterious", "exotic", "bold", "sensual"],
        "description": "Exotic spicy scents with Indonesian heritage spices"
    },
    "gourmand": {
        "keywords": ["gourmand", "manis", "edible", "dessert", "comfort", "vanilla", "sweet", "yummy", "chocolate", "caramel", "cozy", "warm", "comforting", "dessert-like", "manis makanan", "wangi manis", "harum vanila", "cokelat"],
        "variations": ["sweet scents", "vanilla perfume", "dessert fragrance", "chocolate scent", "comforting fragrance", "cozy perfume", "sweet vanilla", "edible smells", "yummy gourmand", "saya cinta manis", "parfum gourmand", "wangi dessert", "bau cokelat"],
        "indonesian_examples": ["vanilla", "kopi", "gula jawa", "cokelat", "kelapa", "kue", "madu"],
        "personality_match": ["comfort", "sweet", "approachable", "warm"],
        "description": "Sweet edible scents that bring comfort and warmth"
    }
}

# Enhanced navigation keywords
NAVIGATION_KEYWORDS = {
    "main_menu": ["main menu", "menu", "home", "back", "return", "start over", "go back", "main", "homepage", "kembali", "utama", "menu utama", "pulang"],
    "consultation": ["consultation", "consult", "help me find", "personality", "start consultation", "begin consultation", "discover", "find my scent", "saya mau konsultasi", "mau konsultasi", "konsultasi", "ingin konsultasi", "bantu cari parfum", "bantu pilih parfum", "temukan parfum", "berkonsultasi", "panduan pilih", "sarankan wangi", "bimbingan parfum", "i want to consult", "want to consult", "help me choose", "find a fragrance", "pick a perfume", "guide me", "start choosing", "discover my scent"],
    "recommendations": ["recommendation", "recommend", "show products", "what products", "my matches", "show my recommendations", "view recommendations", "rekomendasi", "sarankan", "tunjukkan produk", "lihat rekomendasi", "cocok untuk saya"],
    "search": ["search", "find product", "do you have", "is there", "look for", "show me", "find", "browse", "cari", "temukan", "lihat parfum", "jelajahi wangi", "ada parfum", "cari wangi", "browse scents"],
    "yes": ["yes", "ya", "yeah", "sure", "okay", "ok", "yep", "iya", "baik", "of course", "tentu", "setuju"],
    "no": ["no", "nope", "tidak", "nah", "skip", "maybe later", "not now", "bukan", "lewatkan"]
}

# Enhanced choice keywords
CHOICE_PATTERNS = {
    "numbers": r'\b([1-6])\b',
    "choice_words": {
        "1": ["first", "one", "option 1", "choice 1", "number one"],
        "2": ["second", "two", "option 2", "choice 2", "number two"], 
        "3": ["third", "three", "option 3", "choice 3", "number three"],
        "4": ["fourth", "four", "option 4", "choice 4", "number four"],
        "5": ["fifth", "five", "option 5", "choice 5", "number five"],
        "6": ["sixth", "six", "option 6", "choice 6", "number six"]
    }
}

# Sample Indonesian Fragrance Database
FRAGRANCE_DATABASE = [
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

# FIXED SESSION MANAGEMENT - Using sender address as session ID
chat_sessions = {}
user_profiles = {}

def get_user_session_id(sender: str) -> str:
    """Generate consistent session ID based on sender address only"""
    return hashlib.md5(sender.encode()).hexdigest()[:16]

def get_or_create_session(sender: str) -> Dict:
    """Get existing session or create new one"""
    session_id = get_user_session_id(sender)
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "user_address": sender,
            "stage": "main_menu",
            "collected_data": {},
            "consultation_progress": 0.0,
            "started_at": datetime.now().timestamp(),
            "conversation_history": [],
            "has_completed_consultation": False,
            "session_started": False
        }
    
    return chat_sessions[session_id]

# ENHANCED NATURAL LANGUAGE PROCESSING
def extract_number_choice(message: str) -> Optional[str]:
    """Extract number choice from message with multiple methods"""
    message_lower = message.lower().strip()
    
    # Direct number match
    number_match = re.search(CHOICE_PATTERNS["numbers"], message)
    if number_match:
        return number_match.group(1)
    
    # Word-based choices
    for number, words in CHOICE_PATTERNS["choice_words"].items():
        if any(word in message_lower for word in words):
            return number
    
    # Handle phrases like "I choose 2" or "maybe option 3"
    choice_patterns = [
        r"(?:choose|pick|select|want|prefer|go with|take)\s*(?:option|choice|number)?\s*([1-6])",
        r"(?:i'll|i will|i'd|i would)?\s*(?:take|choose|pick|go with|select)\s*(?:option|choice|number)?\s*([1-6])",
        r"([1-6])\s*(?:please|sounds good|looks good|that one)"
    ]
    
    for pattern in choice_patterns:
        match = re.search(pattern, message_lower)
        if match:
            return match.group(1)
    
    return None

def detect_navigation_intent(message: str) -> Optional[str]:
    """Detect navigation intents with scoring-based partial matching"""
    message_lower = message.lower().strip()
    
    # Define intent keywords with broader synonyms
    intent_keywords = {
        "main_menu": ["main menu", "menu", "home", "back", "return", "start over", "go back", "main", "homepage", "kembali", "utama", "menu utama", "pulang", "kembali ke awal"],
        "consultation": [
            "consultation", "consult", "help me find", "personality", "start consultation", "begin consultation", "discover", "find my scent",
            "konsultasi", "saya mau konsultasi", "ingin konsultasi", "bantu cari", "bantu pilih", "temukan parfum", "pilih parfum",
            "i want to consult", "help me choose", "find a fragrance", "pick a perfume", "guide me", "start choosing",
            "berkonsultasi", "panduan pilih", "sarankan wangi", "bimbingan parfum", "discover my scent", "temukan harum saya", "pilih wangi"
        ],
        "recommendations": ["recommendation", "recommend", "show products", "what products", "my matches", "show my recommendations", "view recommendations", "rekomendasi", "tunjukkan produk", "sarankan", "lihat rekomendasi", "cocok untuk saya", "apa yang direkomendasikan"],
        "search": ["search", "find product", "do you have", "is there", "look for", "show me", "find", "browse", "cari", "tunjukkan", "temukan", "lihat parfum", "jelajahi wangi", "ada parfum", "cari wangi", "browse scents", "temukan aroma"],
        "yes": ["yes", "ya", "yeah", "sure", "okay", "ok", "yep", "iya", "baik", "of course", "tentu", "setuju", "benar"],
        "no": ["no", "nope", "tidak", "nah", "skip", "maybe later", "not now", "bukan", "lewatkan", "tidak mau"]
    }
    
    best_intent = None
    best_score = 0.0
    
    for intent, keywords in intent_keywords.items():
        score = 0.0
        for keyword in keywords:
            # Exact match
            if keyword in message_lower:
                return intent
            # Partial match for single words or phrases
            keyword_words = keyword.split()
            if len(keyword_words) == 1:
                # Single word: check if it's a substring or close match
                if keyword in message_lower or any(word.startswith(keyword[:3]) for word in message_lower.split()):
                    score = max(score, 0.8)
            else:
                # Multi-word phrase: count matching words
                match_count = sum(1 for word in keyword_words if word in message_lower)
                phrase_score = match_count / len(keyword_words)
                score = max(score, phrase_score * 0.9)  # Weight multi-word matches slightly lower
        
        # Update best intent if score is high enough
        if score > best_score and score >= 0.5:  # Threshold for considering a match
            best_intent = intent
            best_score = score
    
    # Fallback for consultation-related terms
    if not best_intent and any(term in message_lower for term in ["konsultasi", "consult", "bantu", "pilih", "cari parfum", "choose", "pick", "find fragrance"]):
        return "consultation"
    
    return best_intent

def enhanced_fragrance_family_detection(message: str) -> List[str]:
    """Enhanced fragrance family detection with natural language"""
    detected_families = []
    message_lower = message.lower()
    
    for family, data in FRAGRANCE_FAMILIES.items():
        # Check main keywords
        if any(keyword in message_lower for keyword in data["keywords"]):
            detected_families.append(family)
            continue
        
        # Check natural variations
        if any(variation in message_lower for variation in data.get("variations", [])):
            detected_families.append(family)
            continue
    
    return detected_families

def smart_intent_analysis(message: str, current_stage: str) -> Dict[str, Any]:
    """Enhanced intent analysis with broader natural language support"""
    message_lower = message.lower().strip()
    
    # Check for navigation intents with improved detection
    nav_intent = detect_navigation_intent(message)
    if nav_intent:
        return {"intent": f"navigate_{nav_intent}", "confidence": 0.9}
    
    # Extract number choices
    number_choice = extract_number_choice(message)
    if number_choice:
        return {"intent": "menu_choice", "choice": number_choice, "confidence": 1.0}
    
    # Context-aware intent detection based on current stage
    if current_stage == "main_menu":
        # Enhanced consultation intent detection
        consultation_indicators = [
            "konsultasi", "consult", "bantu", "pilih", "cari parfum", "temukan", "ingin parfum",
            "choose", "pick", "find fragrance", "help me", "guide", "discover scent",
            "berkonsultasi", "panduan pilih", "sarankan wangi", "bimbingan parfum", "temukan harum", "pilih aroma", "sarankan parfum", "ingin konsultasi parfum"
        ]
        if any(indicator in message_lower for indicator in consultation_indicators):
            return {"intent": "start_consultation", "confidence": 0.95}
        elif any(word in message_lower for word in ["recommendation", "recommend", "show products", "my matches", "rekomendasi", "tunjukkan produk", "sarankan", "cocok untuk saya"]):
            return {"intent": "show_recommendations", "confidence": 0.9}
        elif any(word in message_lower for word in ["search", "find", "do you have", "look for", "browse", "cari", "tunjukkan", "temukan", "jelajahi wangi"]):
            return {"intent": "search_product", "confidence": 0.9}
        
        # Fallback for unclear consultation-related inputs
        if any(word in message_lower for word in ["parfum", "perfume", "scent", "aroma", "fragrance", "wangi", "harum", "bau"]):
            return {"intent": "start_consultation", "confidence": 0.7}  # Assume consultation intent
    
    # Fragrance family detection for consultation stages
    if "consultation_" in current_stage:
        fragrance_families = enhanced_fragrance_family_detection(message)
        if fragrance_families:
            return {"intent": "fragrance_preference", "families": fragrance_families, "confidence": 0.8}
        
        # Detect preference expressions
        if current_stage == "consultation_fragrance":
            preference_indicators = ["like", "love", "prefer", "want", "enjoy", "drawn to", "attracted to", "suka", "cinta", "ingin", "favorit", "pilih", "gemar"]
            if any(indicator in message_lower for indicator in preference_indicators):
                return {"intent": "preference_expression", "confidence": 0.7}
    
    # Default to consultation response with lower confidence
    return {"intent": "consultation_response", "confidence": 0.5}

# CHAT UTILITY FUNCTIONS
def create_chat_message(text: str, end_session: bool = False) -> ChatMessage:
    """Create a properly formatted ChatMessage"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=str(uuid4()),
        content=content,
    )

def is_greeting_message(message: str) -> bool:
    """Check if message is a true greeting"""
    message_lower = message.lower()
    greeting_words = ["hello", "hi", "halo", "hey", "good morning", "good afternoon", "selamat pagi", "selamat siang"]
    return any(word in message_lower for word in greeting_words) and not any(word in message_lower for word in ["consult", "konsultasi", "start consultation", "begin consultation"])

# MAIN HANDLERS WITH ENHANCED NLP
async def handle_greeting(ctx: Context, sender: str, session: Dict) -> str:
    """Handle initial greeting and show main menu"""
    
    session["session_started"] = True
    session["stage"] = "main_menu"
    
    greeting_response = """🌸 **Welcome to Aromance!** 🌸

Hello! I'm your personal Indonesian fragrance consultant! ✨

I can help you discover the perfect scent that matches your unique personality and lifestyle.

🎯 **What would you like to do today?**

**1. Start Consultation** 🗣️
   Discover your fragrance personality through guided questions

**2. View Recommendations** 🎁  
   See products (requires completed consultation first)

**3. Search Products** 🔍
   Search specific fragrances in our Indonesian collection

**You can:**
• Type the number (1, 2, or 3)
• Say things like "I want to start consultation" or "help me find a perfume"
• Ask questions like "do you have vanilla perfumes?"

What interests you? 😊"""

    return greeting_response

async def handle_main_menu(ctx: Context, sender: str, session: Dict, message: str) -> str:
    """Enhanced main menu handler with better NLP"""
    
    intent_analysis = smart_intent_analysis(message, "main_menu")
    intent = intent_analysis.get("intent")
    choice = intent_analysis.get("choice")
    
    ctx.logger.info(f"🎯 Enhanced main menu intent: {intent}, choice: {choice}")
    
    has_consultation = session.get("has_completed_consultation", False)
    
    # Handle navigation
    if intent == "navigate_main_menu":
        return await show_main_menu_again()
    
    # Handle numbered choices
    if intent == "menu_choice":
        if choice == "1":
            return await start_consultation(ctx, session)
        elif choice == "2":
            return await handle_recommendations_request(ctx, session, has_consultation)
        elif choice == "3":
            return await start_product_search(ctx, session)
        else:
            return await show_choice_help()
    
    # Handle text-based choices
    elif intent == "start_consultation":
        return await start_consultation(ctx, session)
    elif intent == "show_recommendations":
        return await handle_recommendations_request(ctx, session, has_consultation)
    elif intent == "search_product":
        return await start_product_search(ctx, session)
    else:
        return await handle_unclear_main_menu_response(message)

async def show_choice_help() -> str:
    """Help for invalid choices"""
    return """🤔 **Please choose a valid option!**

**Available choices:**
**1** - Start Consultation (discover your fragrance personality)
**2** - View Recommendations (see matching products)  
**3** - Search Products (find specific fragrances)

You can type:
• Just the number: "1", "2", or "3"
• Natural language: "I want to start consultation"
• Questions: "Do you have floral perfumes?"

What would you like to do? 😊"""

async def handle_unclear_main_menu_response(message: str) -> str:
    """Handle unclear responses with context-aware suggestions"""
    
    message_lower = message.lower()
    suggestions = []
    
    # Infer possible intents from the message
    if any(word in message_lower for word in ["konsultasi", "consult", "bantu", "pilih", "cari parfum", "choose", "pick", "find fragrance"]):
        suggestions.append("🗣️ Try saying **'saya mau konsultasi'** or **'I want to consult'** to start a personalized fragrance consultation")
    
    if any(word in message_lower for word in ["parfum", "perfume", "scent", "aroma", "fragrance"]):
        suggestions.append("🗣️ Say **'konsultasi'** or **'help me find a perfume'** to discover your perfect scent")
    
    if any(word in message_lower for word in ["find", "have", "show", "cari", "tunjukkan"]):
        suggestions.append("🔍 Say **'cari parfum'** or **'search'** to find specific fragrances")
    
    if any(word in message_lower for word in ["help", "confused", "don't know", "bantu", "bingung"]):
        suggestions.append("🎯 Say **'saya mau konsultasi'** or **'start consultation'** for guided help")
    
    base_response = f"""💭 **I didn't quite catch that. You said: "{message[:50]}..."**

Let me help you find the right option! """

    if suggestions:
        base_response += "\n\n**Suggestions based on your message:**\n" + "\n".join(suggestions)
    
    base_response += """\n
**🎯 Main Options:**
**1** - Start Consultation (discover your style) 🗣️
**2** - View Recommendations (see matches) 🎁
**3** - Search Products (find specific items) 🔍

**💡 You can say:**
• Numbers: "1", "2", "3"
• Natural: "saya mau konsultasi", "I want to consult", "cari parfum bunga"
• Questions: "do you have vanilla scents?" or "bantu pilih parfum"

What would you like to do? 😊"""

    return base_response

async def show_main_menu_again() -> str:
    """Show main menu again with encouraging message"""
    return """🏠 **Back to Main Menu!**

**What would you like to do?**

**1. Start Consultation** - Discover your fragrance personality 🗣️
**2. View Recommendations** - See matching products 🎁
**3. Search Products** - Find specific fragrances 🔍

**💡 Pro tip:** You can type naturally! 
• "I want to find my perfect scent" (consultation)
• "Do you have vanilla perfumes?" (search)
• "Show me my matches" (recommendations)

What sounds interesting? 😊"""

# ENHANCED CONSULTATION HANDLERS
async def start_consultation(ctx: Context, session: Dict) -> str:
    """Start the consultation process with enhanced options"""
    
    session["stage"] = "consultation_fragrance"
    session["consultation_progress"] = 0.1
    
    return """🌿 **Starting Your Fragrance Consultation!** 🌿

Let's discover your perfect scent! I'll ask you a few questions to understand your preferences.

**First, what fragrance families appeal to you?**

**🎨 Choose your preferred style:**
**1. Fresh & Citrusy** 🍋 - Light, clean, energizing (lime, mint, cucumber)
**2. Floral & Romantic** 🌸 - Feminine, elegant (jasmine, rose, frangipani)  
**3. Sweet & Gourmand** 🍯 - Comforting, dessert-like (vanilla, chocolate)
**4. Woody & Sophisticated** 🌳 - Warm, mature (sandalwood, cedar)
**5. Spicy & Oriental** 🌶️ - Exotic, mysterious (clove, nutmeg, cardamom)
**6. Fruity & Tropical** 🥭 - Playful, joyful (mango, pineapple)

**💬 You can respond by:**
• Typing a number (1-6)
• Describing what you like: "I love fresh and clean scents"
• Being specific: "vanilla perfumes" or "floral fragrances"
• Saying "back" to return to main menu

What appeals to you? 😊"""

async def handle_consultation_fragrance(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced fragrance family selection handler"""
    
    # Check for navigation first
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    preferences = []
    choice = extract_number_choice(message)
    
    # Handle numbered choices
    if choice:
        family_map = {
            "1": "fresh", "2": "floral", "3": "gourmand",
            "4": "woody", "5": "oriental", "6": "fruity"
        }
        if choice in family_map:
            preferences = [family_map[choice]]
    
    # Handle natural language preferences
    if not preferences:
        preferences = enhanced_fragrance_family_detection(message)
    
    if preferences:
        family = preferences[0]
        family_info = FRAGRANCE_FAMILIES.get(family, {})
        examples = ", ".join(family_info.get("indonesian_examples", [])[:3])
        
        # Update session
        session["stage"] = "consultation_occasion"
        session["collected_data"]["fragrance_families"] = preferences
        session["consultation_progress"] = 0.3
        
        response = f"""✨ **Excellent choice!** ✨

You're drawn to **{family}** fragrances! 😊 {family_info.get('description', '')}

In Indonesian culture, {family} scents often feature beautiful notes like **{examples}**.

🎯 **Next: When would you wear your perfect fragrance?**

**Choose what fits your lifestyle:**
**1. Daily wear** - Work, school, everyday activities ☀️
**2. Evening events** - Dates, dinners, special nights 🌙  
**3. Formal occasions** - Business meetings, important events 💼
**4. Casual hangouts** - Weekend fun, relaxed times 🎉
**5. All occasions** - I want something versatile! ✨

**💬 You can say:**
• A number (1-5)
• "daily use" or "for work"
• "evening wear" or "for dates"
• "back" to return to previous question

What's most important to you?"""
        
        return response
    
    else:
        return await handle_unclear_fragrance_response(message)

async def handle_unclear_fragrance_response(message: str) -> str:
    """Handle unclear fragrance preference responses"""
    
    message_lower = message.lower()
    suggestions = []
    
    # Analyze their message for clues
    if any(word in message_lower for word in ["don't know", "not sure", "confused", "help"]):
        suggestions.append("💡 **Try describing what you like:** \"I prefer light scents\" or \"I love sweet fragrances\"")
    
    if any(word in message_lower for word in ["all", "everything", "any", "versatile"]):
        suggestions.append("🎯 **Say '5' or 'all occasions'** for versatile options")
    
    response = f"""🤔 **Let me help you explore fragrance families!**

You said: "{message[:50]}..." """

    if suggestions:
        response += "\n\n" + "\n".join(suggestions)

    response += """

**🎨 Here are some examples to help you choose:**

**Fresh** 🍋 - "I like clean, light scents" 
**Floral** 🌸 - "I love flower scents like roses or jasmine"
**Sweet** 🍯 - "I prefer vanilla or chocolate notes"
**Woody** 🌳 - "I like warm, sophisticated scents"
**Spicy** 🌶️ - "I enjoy exotic, mysterious fragrances"
**Fruity** 🥭 - "I love tropical, playful scents"

**💬 Try saying:**
• A number: "1" for Fresh
• Description: "I love sweet vanilla scents"
• Simple: "floral" or "woody"
• "back" to return to main menu

What kind of scents do you enjoy? 😊"""

    return response

async def handle_consultation_occasion(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced occasion preference handler"""
    
    # Check for navigation
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    occasions = []
    choice = extract_number_choice(message)
    
    # Handle numbered choices
    if choice:
        occasion_map = {
            "1": ["daily"],
            "2": ["evening"], 
            "3": ["formal"],
            "4": ["casual"],
            "5": ["daily", "evening", "formal"]
        }
        if choice in occasion_map:
            occasions = occasion_map[choice]
    
    # Handle natural language
    if not occasions:
        occasions = extract_occasion_preferences_enhanced(message)
    
    if occasions:
        # Update session
        session["stage"] = "consultation_personality"
        session["collected_data"]["occasions"] = occasions
        session["consultation_progress"] = 0.5
        
        occasion_desc = ", ".join(occasions).title()
        
        response = f"""🎭 **Perfect! You chose {occasion_desc} occasions** 🎭

Now let's discover your personality! Understanding who you are helps me match you with fragrances that truly reflect your essence! ✨

💫 **How would your closest friends describe you?**

**Choose the personality that resonates most:**
**1. Confident & Bold** - "I like to make a statement and stand out" 💪
**2. Romantic & Gentle** - "I love beauty and tender moments" 💕  
**3. Professional & Polished** - "I'm sophisticated and put-together" 👑
**4. Playful & Energetic** - "I'm fun-loving and enjoy life" 🎊
**5. Mysterious & Unique** - "I prefer to be intriguing and different" 🔮

**💬 You can respond with:**
• A number (1-5)
• Descriptions: "I'm confident" or "romantic personality"
• Multiple traits: "confident and playful"
• "back" to return to previous question

What personality traits feel most like you?"""
        
        return response
    else:
        return await handle_unclear_occasion_response(message)

async def handle_unclear_occasion_response(message: str) -> str:
    """Handle unclear occasion responses"""
    
    return f"""🤔 **Let me help you think about occasions!**

You said: "{message[:50]}..."

**🎯 Think about when you'd wear your perfect fragrance:**

**Daily** ☀️ - Work, school, everyday life
**Evening** 🌙 - Dates, dinners, going out  
**Formal** 💼 - Business, important meetings
**Casual** 🎉 - Weekends, hanging with friends
**All occasions** ✨ - Something versatile!

**💬 You can say:**
• Numbers: "1" for daily, "2" for evening
• Natural: "for work" or "evening wear"
• Specific: "dates and dinners"
• "back" to return to fragrance preferences

When do you most want to smell amazing? 😊"""

async def handle_consultation_personality(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced personality discovery handler"""
    
    # Check for navigation
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    traits = []
    choice = extract_number_choice(message)
    
    # Handle numbered choices
    if choice:
        trait_map = {
            "1": ["confident"],
            "2": ["romantic"],
            "3": ["professional"],
            "4": ["playful"],
            "5": ["mysterious"]
        }
        if choice in trait_map:
            traits = trait_map[choice]
    
    # Handle natural language
    if not traits:
        traits = extract_personality_traits_enhanced(message)
    
    if traits:
        # Update session
        session["stage"] = "consultation_budget"
        session["collected_data"]["personality_traits"] = traits
        session["consultation_progress"] = 0.7
        
        trait_desc = ", ".join(traits).title()
        
        response = f"""💖 **{trait_desc} - I love that about you!** 💖

Now let's talk about investment! There are wonderful fragrances at every price point - quality and love come in all ranges 💝

💰 **What's a comfortable investment for a fragrance you'd truly love?**

🏷️ **Choose your budget preference:**
**1. Budget-friendly** - Under 200K IDR 💚 (Great starter options)
**2. Mid-range** - 200K-400K IDR 💛 (Quality everyday scents)
**3. Premium** - 400K-600K IDR 🧡 (Luxurious experiences)
**4. Luxury** - 600K+ IDR ❤️ (Exclusive collections)
**5. I'm flexible** - Show me the best matches regardless of price! 💜

**💬 You can say:**
• Numbers: "2" for mid-range
• Natural: "budget friendly" or "something premium"
• Specific: "under 300k" or "around 400k"
• "back" to return to personality question

🌟 **Remember:** The perfect fragrance is the one that makes YOU feel amazing! ✨

What feels right for your budget?"""
        
        return response
    else:
        return await handle_unclear_personality_response(message)

async def handle_unclear_personality_response(message: str) -> str:
    """Handle unclear personality responses"""
    
    return f"""💭 **Let's explore your personality together!**

You said: "{message[:50]}..."

**🎭 Think about how others see you:**

**Confident** 💪 - Bold, assertive, like to stand out
**Romantic** 💕 - Gentle, loving, appreciate beauty
**Professional** 👑 - Sophisticated, polished, elegant  
**Playful** 🎊 - Fun, energetic, youthful spirit
**Mysterious** 🔮 - Unique, intriguing, different

**💬 You can describe yourself as:**
• "I'm confident and outgoing"
• "romantic and gentle"
• "professional but fun"
• Or just pick a number (1-5)
• "back" to return to occasion preferences

How do your friends describe you? 😊"""

async def handle_consultation_budget(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced budget preference handler"""
    
    # Check for navigation
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    budget = extract_budget_preference_enhanced(message)
    choice = extract_number_choice(message)
    
    # Handle numbered choices
    if choice:
        budget_map = {
            "1": "budget",
            "2": "moderate", 
            "3": "premium",
            "4": "luxury",
            "5": "flexible"
        }
        if choice in budget_map:
            budget = budget_map[choice]
    
    if budget:
        # Update session
        session["stage"] = "consultation_sensitivity"
        session["collected_data"]["budget_range"] = budget
        session["consultation_progress"] = 0.9
        
        budget_desc = {
            "budget": "Budget-friendly (Under 200K)",
            "moderate": "Mid-range (200K-400K)", 
            "premium": "Premium (400K-600K)",
            "luxury": "Luxury (600K+)",
            "flexible": "Flexible budget"
        }.get(budget, budget.title())
        
        response = f"""🌡️ **Almost done! You chose: {budget_desc}** 🌡️

Final important question! Do you have any **sensitivities or allergies** to fragrances? This helps me ensure your recommendations are comfortable and enjoyable! 🙏

🩺 **Choose what describes you best:**
**1. No sensitivities** - I can wear any fragrance comfortably ✅
**2. Sensitive to strong scents** - I prefer lighter, subtle fragrances 🌿  
**3. Prefer gentle formulas** - I like mild, hypoallergenic options 🕊️
**4. I'm not sure** - I want to be safe with my choices 🤔

**💬 You can say:**
• Numbers: "1" for no sensitivities
• Natural: "I'm sensitive" or "prefer gentle"
• Specific: "allergic to strong perfumes"
• "back" to return to budget question

🌿 **Don't worry!** Indonesian brands are particularly good at creating gentle, tropical-friendly formulations! 

How would you describe your sensitivity level?"""
        
        return response
    else:
        return await handle_unclear_budget_response(message)

async def handle_unclear_budget_response(message: str) -> str:
    """Handle unclear budget responses"""
    
    return f"""💰 **Let's find the right budget for you!**

You said: "{message[:50]}..."

**🎯 Think about what you're comfortable investing:**

**Budget-friendly** 💚 - Under 200K (great starter options)
**Mid-range** 💛 - 200K-400K (quality everyday scents)  
**Premium** 🧡 - 400K-600K (luxurious experiences)
**Luxury** ❤️ - 600K+ (exclusive collections)
**Flexible** 💜 - Show me the best regardless of price

**💬 You can say:**
• "budget friendly" or "under 200k"
• "mid range" or "around 300k"
• "premium quality" 
• "I'm flexible with budget"
• Numbers 1-5, or "back"

What investment level feels comfortable? 😊"""

async def handle_consultation_sensitivity(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced sensitivity assessment and complete consultation"""
    
    # Check for navigation
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    sensitivity = extract_sensitivity_level(message)
    choice = extract_number_choice(message)
    
    # Handle numbered choices
    if choice:
        sensitivity_map = {
            "1": "normal",
            "2": "sensitive", 
            "3": "gentle",
            "4": "cautious"
        }
        if choice in sensitivity_map:
            sensitivity = sensitivity_map[choice]
    
    if sensitivity:
        # Complete consultation and create profile
        collected_data = session.get("collected_data", {})
        collected_data["sensitivity"] = sensitivity
        
        # Create fragrance profile
        profile = create_fragrance_profile(session, collected_data)
        
        # Update session - MARK CONSULTATION AS COMPLETED
        session["stage"] = "consultation_complete"
        session["collected_data"] = collected_data
        session["consultation_progress"] = 1.0
        session["has_completed_consultation"] = True
        
        # Generate recommendations immediately
        recommendations = generate_recommendations(collected_data)
        
        sensitivity_desc = {
            "normal": "No sensitivities",
            "sensitive": "Sensitive to strong scents",
            "gentle": "Prefer gentle formulas", 
            "cautious": "Cautious approach"
        }.get(sensitivity, sensitivity.title())
        
        response = f"""🎉 **Consultation Complete!** 🎉

✨ **Your Personalized Fragrance Profile:** 
**'{profile.personality_type}'** with a preference for **{', '.join(profile.preferred_families)}** families! 

🌺 **Your Profile Summary:**
• **Fragrance Style:** {', '.join(profile.preferred_families).title()}
• **Personality:** {profile.personality_type} 
• **Perfect For:** {', '.join(profile.occasion_preferences).title()} occasions
• **Budget Range:** {profile.budget_range.title()} tier
• **Sensitivity:** {sensitivity_desc}

🎯 **Here are your personalized recommendations:**

"""
        
        # Add recommendations to response
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                heritage = "🇮🇩" if rec.indonesian_heritage else ""
                halal = "☪️" if rec.halal_certified else ""
                
                response += f"""**{i}. {rec.name}** by {rec.brand} {heritage} {halal}
💰 **Price:** {rec.price_idr:,} IDR
🌸 **Family:** {rec.fragrance_family.title()}  
⭐ **Match:** {int(rec.match_score*100)}%
🎯 **Why perfect:** {rec.reasoning}

"""
            
            # Add explanation
            explanation = create_recommendation_explanation(collected_data, recommendations)
            response += f"💡 **Why These Recommendations?**\n{explanation}\n"
        else:
            response += "😅 No perfect matches found with current criteria. Let's try adjusting preferences!\n"
        
        response += """
🏠 **What's next?**
• **"main menu"** - Return to main options
• **"new consultation"** - Start fresh consultation  
• **"search [product name]"** - Find specific products
• Just chat naturally - I understand you better now!

What would you like to do? 😊"""
        
        return response
    else:
        return await handle_unclear_sensitivity_response(message)

async def handle_unclear_sensitivity_response(message: str) -> str:
    """Handle unclear sensitivity responses"""
    
    return f"""🤔 **Let me help you determine your sensitivity level!**

You said: "{message[:50]}..."

**🌡️ Think about your experience with fragrances:**

**No sensitivities** ✅ - You can wear any perfume comfortably
**Sensitive** 🌿 - Strong scents give you headaches/irritation
**Gentle preference** 🕊️ - You like mild, soft fragrances
**Not sure** 🤔 - Better to be cautious and safe

**💬 You can say:**
• "no allergies" or "I'm fine with strong scents"
• "sensitive to perfumes" or "prefer light scents"  
• "gentle formulas please"
• Numbers 1-4, or "back"

How do you typically react to fragrances? 😊"""

# ENHANCED UTILITY FUNCTIONS
def extract_occasion_preferences_enhanced(message: str) -> List[str]:
    """Enhanced occasion preference extraction"""
    occasions = []
    message_lower = message.lower()
    
    occasion_mapping = {
        "daily": ["daily", "everyday", "work", "office", "routine", "regular", "normal day", "day to day"],
        "evening": ["evening", "night", "date", "romantic", "dinner", "going out", "nighttime", "special nights"],
        "formal": ["formal", "business", "meeting", "professional", "important", "work meetings", "corporate", "official"],
        "casual": ["casual", "weekend", "relaxed", "hangout", "fun", "friends", "chill", "informal"]
    }
    
    for occasion, keywords in occasion_mapping.items():
        if any(keyword in message_lower for keyword in keywords):
            occasions.append(occasion)
    
    # Handle "all" or "versatile" requests
    if any(word in message_lower for word in ["all", "everything", "versatile", "any occasion", "various"]):
        occasions = ["daily", "evening", "formal"]
    
    return occasions if occasions else []

def extract_personality_traits_enhanced(message: str) -> List[str]:
    """Enhanced personality trait extraction"""
    traits = []
    message_lower = message.lower()
    
    trait_mapping = {
        "confident": ["confident", "bold", "strong", "assertive", "leader", "outgoing", "dominant", "powerful"],
        "romantic": ["romantic", "gentle", "sweet", "loving", "tender", "soft", "feminine", "delicate"],
        "professional": ["professional", "sophisticated", "elegant", "formal", "business", "polished", "mature", "refined"],
        "playful": ["playful", "fun", "energetic", "cheerful", "young", "lively", "vibrant", "bubbly", "spirited"],
        "mysterious": ["mysterious", "unique", "different", "exotic", "intriguing", "enigmatic", "complex", "deep"]
    }
    
    for trait, keywords in trait_mapping.items():
        if any(keyword in message_lower for keyword in keywords):
            traits.append(trait)
    
    return traits if traits else []

def extract_budget_preference_enhanced(message: str) -> str:
    """Enhanced budget preference extraction"""
    message_lower = message.lower()
    
    # Check for specific price mentions
    price_patterns = [
        (r'under (\d+)', 'budget'),
        (r'below (\d+)', 'budget'), 
        (r'less than (\d+)', 'budget'),
        (r'around (\d+)', 'moderate'),
        (r'about (\d+)', 'moderate'),
        (r'(\d+)k', 'moderate')
    ]
    
    for pattern, category in price_patterns:
        match = re.search(pattern, message_lower)
        if match:
            price = int(match.group(1))
            if price < 200:
                return 'budget'
            elif price < 400:
                return 'moderate'
            elif price < 600:
                return 'premium'
            else:
                return 'luxury'
    
    # Check for keyword-based budget
    if any(word in message_lower for word in ["budget", "cheap", "affordable", "inexpensive", "low cost"]):
        return "budget"
    elif any(word in message_lower for word in ["premium", "high quality", "expensive", "luxury", "high end"]):
        return "premium"
    elif any(word in message_lower for word in ["mid", "moderate", "reasonable", "balance", "medium"]):
        return "moderate"
    elif any(word in message_lower for word in ["flexible", "any", "doesn't matter", "open", "whatever"]):
        return "flexible"
    else:
        return ""

def extract_sensitivity_level(message: str) -> str:
    """Extract sensitivity level from message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["no sensitivities", "no allergies", "fine", "comfortable", "any fragrance"]):
        return "normal"
    elif any(word in message_lower for word in ["sensitive", "allergic", "headaches", "strong scents", "irritation"]):
        return "sensitive"
    elif any(word in message_lower for word in ["gentle", "mild", "soft", "hypoallergenic", "light"]):
        return "gentle"
    elif any(word in message_lower for word in ["not sure", "don't know", "careful", "cautious", "safe"]):
        return "cautious"
    else:
        return ""

# Continue with the rest of the handlers and utility functions...

async def start_product_search(ctx: Context, session: Dict) -> str:
    """Enhanced product search mode"""
    
    session["stage"] = "product_search"
    
    return """🔍 **Product Search**

I can help you find specific fragrances in our Indonesian collection!

**🎯 Search examples:**
• "Do you have vanilla perfumes?"
• "Show me HMNS products"  
• "Find something under 300k"
• "What floral perfumes do you have?"
• "Indonesian heritage fragrances"

**💬 You can also:**
• Ask naturally: "I'm looking for sweet scents"
• Be specific: "Bali Essence brand products"
• Set budgets: "premium fragrances under 500k"
• Say "main menu" to go back

**What are you looking for?** 🤔"""

async def handle_product_search(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced product search with better NLP"""
    
    # Check for navigation
    nav_intent = detect_navigation_intent(message)
    if nav_intent == "main_menu":
        session["stage"] = "main_menu" 
        return await show_main_menu_again()
    
    message_lower = message.lower()
    results = []
    
    # Enhanced search logic
    for product in FRAGRANCE_DATABASE:
        product_match = False
        
        # Brand search (case insensitive)
        if product["brand"].lower() in message_lower:
            product_match = True
        
        # Product name search  
        if any(word in product["name"].lower() for word in message_lower.split()):
            product_match = True
        
        # Fragrance family search
        if product["fragrance_family"] in message_lower:
            product_match = True
            
        # Enhanced fragrance family detection
        detected_families = enhanced_fragrance_family_detection(message)
        if product["fragrance_family"] in detected_families:
            product_match = True
        
        # Price search with better parsing
        budget = extract_budget_preference_enhanced(message)
        if budget and passes_budget_filter(product["price_idr"], budget):
            product_match = True
        
        # Notes search (top, middle, base)
        all_notes = product["top_notes"] + product["middle_notes"] + product["base_notes"]
        if any(note.lower() in message_lower for note in all_notes):
            product_match = True
        
        # Heritage search
        if any(word in message_lower for word in ["indonesian", "heritage", "local", "traditional"]):
            if product.get("indonesian_heritage"):
                product_match = True
        
        # Halal search  
        if any(word in message_lower for word in ["halal", "certified", "islamic"]):
            if product.get("halal_certified"):
                product_match = True
        
        if product_match:
            results.append(product)
    
    if not results:
        return await handle_no_search_results(message)
    
    # Format enhanced search results
    response = f"""🎯 **Found {len(results)} products for "{message}":**

"""
    
    for i, product in enumerate(results, 1):
        heritage = "🇮🇩 Indonesian Heritage" if product.get("indonesian_heritage") else ""
        halal = "☪️ Halal Certified" if product.get("halal_certified") else ""
        
        response += f"""**{i}. {product["name"]}** by {product["brand"]}
💰 **Price:** {product["price_idr"]:,} IDR
🌸 **Family:** {product["fragrance_family"].title()}
📝 **Description:** {product["description"]}
{heritage} {halal}

"""
    
    response += """💡 **Want to refine your search?**
• Try: "show me cheaper options" or "premium fragrances only"
• Ask: "which one is best for daily wear?"
• Say: "main menu" to see all options
• Continue: "tell me more about product 1"

What else can I help you find? 🔍"""
    
    return response

async def handle_no_search_results(message: str) -> str:
    """Handle when no search results are found"""
    
    return f"""😔 **No products found for "{message[:50]}..."**

**🎯 Try searching for:**
• **Brands:** "HMNS", "Bali Essence", "Nusantara Scents"
• **Fragrance types:** "floral", "fresh", "woody", "sweet"
• **Price ranges:** "under 300k", "budget friendly", "premium"
• **Specific notes:** "vanilla", "jasmine", "sandalwood"
• **Features:** "Indonesian heritage", "halal certified"

**💡 Search suggestions:**
• "Do you have sweet vanilla perfumes?"
• "Show me floral fragrances under 350k"
• "Indonesian heritage brands"

**🏠 Or say "main menu"** to explore other options!

What would you like to search for? 🤔"""

# POST-CONSULTATION HANDLERS
async def handle_post_consultation(ctx: Context, session: Dict, message: str) -> str:
    """Enhanced post-consultation message handler"""
    
    nav_intent = detect_navigation_intent(message)
    message_lower = message.lower()
    
    if nav_intent == "main_menu":
        session["stage"] = "main_menu"
        return await show_main_menu_again()
    
    elif nav_intent == "consultation":
        # Reset consultation data but keep completion status
        session["stage"] = "consultation_fragrance" 
        session["collected_data"] = {}
        session["consultation_progress"] = 0.1
        return await start_consultation(ctx, session)
    
    elif nav_intent == "search" or any(word in message_lower for word in ["search", "find", "look for"]):
        session["stage"] = "product_search"
        return await start_product_search(ctx, session)
    
    elif any(word in message_lower for word in ["recommendations", "show recommendations", "my matches"]):
        collected_data = session.get("collected_data", {})
        return await generate_and_show_recommendations(ctx, session, collected_data)
    
    else:
        return """🤔 **I can help you with:**

• **"main menu"** - Return to main options  
• **"new consultation"** - Start fresh consultation with different preferences
• **"search [product]"** - Find specific fragrances
• **"show recommendations"** - See your matches again
• Natural questions like: "do you have woody perfumes?"

What would you like to do? 😊"""

# MAIN CONSULTATION FLOW ROUTER - ENHANCED
async def handle_consultation_flow(ctx: Context, sender: str, session: Dict, message: str) -> str:
    """Enhanced consultation flow router with better error handling"""
    
    stage = session.get("stage", "main_menu")
    
    ctx.logger.info(f"📋 Enhanced consultation flow - Stage: {stage}, Message: {message[:50]}...")
    
    try:
        # Handle different stages
        if stage == "main_menu":
            return await handle_main_menu(ctx, sender, session, message)
        elif stage == "consultation_fragrance":
            return await handle_consultation_fragrance(ctx, session, message)
        elif stage == "consultation_occasion":
            return await handle_consultation_occasion(ctx, session, message)
        elif stage == "consultation_personality":
            return await handle_consultation_personality(ctx, session, message)
        elif stage == "consultation_budget":
            return await handle_consultation_budget(ctx, session, message)
        elif stage == "consultation_sensitivity":
            return await handle_consultation_sensitivity(ctx, session, message)
        elif stage == "consultation_complete":
            return await handle_post_consultation(ctx, session, message)
        elif stage == "product_search":
            return await handle_product_search(ctx, session, message)
        else:
            # Default back to main menu with helpful message
            session["stage"] = "main_menu"
            return await show_main_menu_again()
            
    except Exception as e:
        ctx.logger.error(f"❌ Error in consultation flow: {str(e)}")
        # Graceful error recovery
        return """😅 **Oops! Something went wrong.**

Let me help you get back on track! 

🏠 **Say "main menu"** to return to the main options
🔄 **Or just tell me what you're looking for** and I'll understand!

What can I help you with? 😊"""

# Keep all the existing utility functions (create_fragrance_profile, generate_recommendations, etc.)
def create_fragrance_profile(session: Dict, collected_data: Dict) -> FragranceProfile:
    """Create comprehensive fragrance profile from consultation"""
    
    user_id = session["user_address"]
    
    # Determine personality type
    traits = collected_data.get("personality_traits", ["versatile"])
    if "confident" in traits:
        personality_type = "Bold Indonesian Trendsetter"
    elif "romantic" in traits:
        personality_type = "Romantic Indonesian Soul"
    elif "professional" in traits:
        personality_type = "Professional Indonesian Elite"
    elif "playful" in traits:
        personality_type = "Cheerful Indonesian Spirit"
    elif "mysterious" in traits:
        personality_type = "Mysterious Indonesian Enigma"
    else:
        personality_type = "Versatile Indonesian Character"
    
    # Determine lifestyle
    occasions = collected_data.get("occasions", ["daily"])
    if any(occ in occasions for occ in ["formal", "daily"]):
        lifestyle = "professional"
    elif "evening" in occasions:
        lifestyle = "social"
    elif "casual" in occasions:
        lifestyle = "relaxed"
    else:
        lifestyle = "balanced"
    
    profile = FragranceProfile(
        user_id=user_id,
        personality_type=personality_type,
        lifestyle=lifestyle,
        preferred_families=collected_data.get("fragrance_families", ["fresh"]),
        occasion_preferences=occasions,
        season_preferences=["tropical_year_round"],
        sensitivity_level=collected_data.get("sensitivity", "normal"),
        budget_range=collected_data.get("budget_range", "moderate"),
        consultation_progress=1.0
    )
    
    user_profiles[user_id] = profile
    return profile

def generate_recommendations(collected_data: Dict) -> List[ProductRecommendation]:
    """Generate personalized fragrance recommendations"""
    
    recommendations = []
    preferred_families = collected_data.get("fragrance_families", ["fresh"])
    personality_traits = collected_data.get("personality_traits", ["versatile"])
    occasions = collected_data.get("occasions", ["daily"])
    budget_range = collected_data.get("budget_range", "moderate")
    sensitivity = collected_data.get("sensitivity", "normal")
    
    for product in FRAGRANCE_DATABASE:
        # Calculate match score
        match_score = calculate_match_score(product, collected_data)
        
        if match_score < 0.3:  # Lower threshold for better results
            continue
            
        # Budget filtering
        if not passes_budget_filter(product["price_idr"], budget_range):
            continue
            
        # Sensitivity filtering
        if sensitivity == "sensitive" and product["fragrance_family"] in ["oriental"]:
            match_score *= 0.8  # Reduce score for potentially strong scents
        
        # Create reasoning
        reasoning = generate_reasoning(product, collected_data, match_score)
        
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
            occasions=product["occasions"]
        )
        
        recommendations.append(recommendation)
    
    # Sort by match score and return top matches
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:3]  # Return top 3 matches

def calculate_match_score(product: Dict, collected_data: Dict) -> float:
    """Calculate comprehensive match score"""
    
    score = 0.0
    
    # Fragrance family matching (40% weight)
    preferred_families = collected_data.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        score += 0.4
    
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
    
    # Indonesian heritage bonus (10% weight)
    if product.get("indonesian_heritage", False):
        score += 0.1
    
    # Halal certification bonus (5% weight)
    if product.get("halal_certified", False):
        score += 0.05
    
    return min(score, 1.0)

def passes_budget_filter(price: int, budget_range: str) -> bool:
    """Check if product price fits user budget"""
    
    budget_limits = {
        "budget": 200000,
        "moderate": 400000,
        "premium": 600000,
        "luxury": float('inf'),
        "flexible": float('inf')
    }
    
    return price <= budget_limits.get(budget_range, float('inf'))

def generate_reasoning(product: Dict, collected_data: Dict, match_score: float) -> str:
    """Generate intelligent reasoning for recommendations"""
    
    reasons = []
    
    # Match score interpretation
    if match_score > 0.8:
        reasons.append("✨ PERFECT MATCH!")
    elif match_score > 0.6:
        reasons.append("💫 Excellent choice")
    else:
        reasons.append("✅ Great alternative")
    
    # Fragrance family match
    preferred_families = collected_data.get("fragrance_families", [])
    if any(family in product["fragrance_family"] for family in preferred_families):
        reasons.append(f"Perfect {product['fragrance_family']} match")
    
    # Personality alignment
    personality_traits = collected_data.get("personality_traits", [])
    product_personalities = product.get("personality_match", [])
    if set(personality_traits) & set(product_personalities):
        matching_traits = list(set(personality_traits) & set(product_personalities))
        reasons.append(f"Matches your {', '.join(matching_traits)} nature")
    
    # Indonesian heritage
    if product.get("indonesian_heritage", False):
        reasons.append("🇮🇩 Proudly Indonesian")
    
    # Halal certification
    if product.get("halal_certified", False):
        reasons.append("☪️ Halal certified")
    
    return " • ".join(reasons[:3])  # Limit to 3 key reasons

def create_recommendation_explanation(collected_data: Dict, recommendations: List[ProductRecommendation]) -> str:
    """Create personalized explanation for recommendations"""
    
    if not recommendations:
        return "No suitable matches found for your criteria."
    
    personality_traits = collected_data.get("personality_traits", ["unique"])
    preferred_families = collected_data.get("fragrance_families", ["fresh"])
    
    explanation = f"Based on your **{', '.join(personality_traits)}** personality and love for **{', '.join(preferred_families)}** fragrances, "
    explanation += f"these {len(recommendations)} selections perfectly capture your essence! ✨"
    
    top_match = recommendations[0]
    explanation += f"\n\n🎯 **Top Pick:** {top_match.name} with {int(top_match.match_score*100)}% compatibility!"
    
    # Add cultural insights
    indonesian_count = sum(1 for rec in recommendations if rec.indonesian_heritage)
    halal_count = sum(1 for rec in recommendations if rec.halal_certified)
    
    if indonesian_count > 0:
        explanation += f"\n🇮🇩 {indonesian_count} authentic Indonesian brands supporting local artistry"
    if halal_count > 0:
        explanation += f"\n☪️ {halal_count} products are halal certified for your peace of mind"
    
    explanation += f"\n🌴 All specially curated for Indonesia's beautiful tropical climate!"
    
    return explanation

async def generate_and_show_recommendations(ctx: Context, session: Dict, collected_data: Dict) -> str:
    """Generate and display recommendations for completed consultation"""
    
    recommendations = generate_recommendations(collected_data)
    
    if not recommendations:
        return """😅 **No current matches found!**

This could be due to very specific requirements or limited database.

🔄 **What you can do:**
• Say **"new consultation"** to explore different preferences
• Say **"search products"** to browse our collection
• Say **"main menu"** to see all options

What would you like to try? 😊"""
    
    # Create recommendation response
    response = f"""🎯 **Your Personalized Aromance Recommendations** 🎯

Based on your completed consultation, here are **{len(recommendations)}** perfect matches! ✨

"""
    
    for i, rec in enumerate(recommendations, 1):
        heritage = "🇮🇩 Indonesian Heritage" if rec.indonesian_heritage else ""
        halal = "☪️ Halal Certified" if rec.halal_certified else ""
        
        response += f"""**{i}. {rec.name}** by {rec.brand}
💰 **Price:** {rec.price_idr:,} IDR
🌸 **Family:** {rec.fragrance_family.title()}  
⭐ **Match:** {int(rec.match_score*100)}%
🎯 **Why perfect:** {rec.reasoning}
{heritage} {halal}

"""
    
    # Add explanation
    explanation = create_recommendation_explanation(collected_data, recommendations)
    response += f"\n💡 **Why These Recommendations?**\n{explanation}\n"
    
    # Add next steps
    response += """
🛍️ **Want to purchase?**
Visit our website dashboard for secure purchasing!

🔄 **Want to explore more?**
• Say **"new consultation"** for fresh recommendations
• Say **"search products"** to browse collection
• Say **"main menu"** to return to main options
• Ask naturally: "tell me more about option 1"

What would you like to do next? 😊"""
    
    return response

# MAIN CHAT MESSAGE HANDLER - ENHANCED
@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Enhanced main chat message handler with smarter intent handling"""
    
    ctx.logger.info(f"💬 Received chat message from {sender}")
    
    # Get or create consistent session based on sender address
    session = get_or_create_session(sender)
    
    # Send acknowledgment immediately
    ack = ChatAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=msg.msg_id
    )
    await ctx.send(sender, ack)
    
    response_text = ""
    
    try:
        # Process each content item in the message
        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"🚀 Starting new chat session with {sender}")
                session["session_started"] = True
                response_text = await handle_greeting(ctx, sender, session)
                
            elif isinstance(item, TextContent):
                ctx.logger.info(f"📝 Processing text: {item.text}")
                
                # Check for consultation intent first
                intent_analysis = smart_intent_analysis(item.text, session.get("stage", "main_menu"))
                if intent_analysis["intent"] == "start_consultation":
                    response_text = await handle_consultation_flow(ctx, sender, session, item.text)
                # Only trigger greeting for true greeting messages
                elif is_greeting_message(item.text) and not session.get("session_started", False):
                    response_text = await handle_greeting(ctx, sender, session)
                else:
                    # Process message with enhanced consultation flow
                    response_text = await handle_consultation_flow(ctx, sender, session, item.text)
                
            elif isinstance(item, EndSessionContent):
                ctx.logger.info(f"🔚 Ending session with {sender}")
                # Clean up session
                session_id = get_user_session_id(sender)
                if session_id in chat_sessions:
                    del chat_sessions[session_id]
                response_text = "Thank you for using Aromance! Feel free to start a new consultation anytime. Have a wonderfully fragrant day! 🌸✨"
                
            else:
                ctx.logger.warning(f"⚠️ Unexpected content type: {type(item)}")
                response_text = "I received an unexpected message type. Could you please rephrase your question? 🤔"
        
        # Send response ONLY ONCE
        if response_text:
            response_msg = create_chat_message(response_text)
            await ctx.send(sender, response_msg)
            ctx.logger.info(f"✅ Enhanced response sent to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing chat message: {str(e)}")
        import traceback
        ctx.logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
        # Send error response with helpful recovery
        error_msg = create_chat_message(
            "😅 I encountered an error. Please try saying 'saya mau konsultasi' or 'main menu' to continue! I'm here to help you find your perfect fragrance! 🌸"
        )
        await ctx.send(sender, error_msg)

@chat_proto.on_message(ChatAcknowledgement)
async def handle_chat_acknowledgment(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgments"""
    ctx.logger.info(f"✅ Received acknowledgment from {sender} for message {msg.acknowledged_msg_id}")

# SESSION CLEANUP
@coordinator_agent.on_interval(period=300.0)  # Every 5 minutes
async def cleanup_old_sessions(ctx: Context):
    """Clean up old chat sessions"""
    current_time = datetime.now().timestamp()
    
    # Remove sessions older than 30 minutes
    expired_sessions = [
        session_id for session_id, session_data in chat_sessions.items()
        if current_time - session_data.get("started_at", 0) > 1800
    ]
    
    for session_id in expired_sessions:
        del chat_sessions[session_id]
    
    if expired_sessions:
        ctx.logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired chat sessions")
    
    # Log current status
    active_sessions = len(chat_sessions)
    total_profiles = len(user_profiles)
    
    ctx.logger.info(f"📊 Chat Status: {active_sessions} active sessions, {total_profiles} user profiles")

# PROTOCOL REGISTRATION
coordinator_agent.include(chat_proto, publish_manifest=True)

# STARTUP EVENT
@coordinator_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🌸 Enhanced Aromance Chat Coordinator Started! 🌸")
    ctx.logger.info(f"🆔 Agent Address: {coordinator_agent.address}")
    ctx.logger.info(f"💬 Chat Protocol: Enabled with enhanced NLP")
    ctx.logger.info(f"🌐 Endpoint: http://127.0.0.1:8000")
    
    ctx.logger.info("✨ ENHANCED FEATURES:")
    ctx.logger.info("  • Advanced natural language understanding")
    ctx.logger.info("  • Smart intent analysis with context awareness")
    ctx.logger.info("  • Flexible conversation flow with navigation")
    ctx.logger.info("  • Enhanced keyword detection and matching")
    ctx.logger.info("  • Graceful error handling and recovery")
    ctx.logger.info("  • Improved search functionality")
    
    ctx.logger.info(f"🗂️ KNOWLEDGE BASE:")
    ctx.logger.info(f"  • {len(FRAGRANCE_FAMILIES)} fragrance families with enhanced keywords")
    ctx.logger.info(f"  • {len(FRAGRANCE_DATABASE)} Indonesian products")
    ctx.logger.info(f"  • Smart conversation flow management")
    ctx.logger.info(f"  • Cultural insights and local fragrance expertise")
    
    ctx.logger.info("🚀 Ready to provide intelligent fragrance consultation!")

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