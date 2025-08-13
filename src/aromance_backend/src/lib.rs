use ic_cdk_macros::*;
use std::collections::HashMap;
use candid::{CandidType, Deserialize};
use ic_cdk::api::time;

#[derive(CandidType, Deserialize, Clone)]
pub struct DecentralizedIdentity {
    pub did: String,
    pub public_key: String,
    pub private_key_hash: String,
    pub verified_claims: Vec<VerifiedClaim>,
    pub data_permissions: HashMap<String, PermissionLevel>,
    pub fragrance_identity: FragranceIdentity,
    pub created_at: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct VerifiedClaim {
    pub claim_type: String,
    pub issuer: String,
    pub claim_data: String,
    pub verified_at: u64,
    pub expiry: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum PermissionLevel {
    None,
    ReadOnly,
    Limited,
    Full,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct FragranceIdentity {
    pub personality_type: String,
    pub lifestyle: String,
    pub preferred_families: Vec<String>,
    pub occasion_preferences: Vec<String>,
    pub season_preferences: Vec<String>,
    pub sensitivity_level: String,
    pub budget_range: BudgetRange,
    pub scent_journey: Vec<ScentEvolution>,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum BudgetRange {
    Budget,      // <50k IDR
    Moderate,    // 50k-200k IDR
    Premium,     // 200k-500k IDR
    Luxury,      // >500k IDR
}

#[derive(CandidType, Deserialize, Clone)]
pub struct ScentEvolution {
    pub date: u64,
    pub preference_change: String,
    pub trigger_event: String,
    pub confidence_score: f64,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct UserProfile {
    pub user_id: String,
    pub wallet_address: Option<String>,
    pub did: Option<String>,
    pub verification_status: VerificationStatus,
    pub stake_info: Option<StakeInfo>,
    pub preferences: HashMap<String, String>,
    pub consultation_completed: bool,
    pub ai_consent: bool,
    pub data_monetization_consent: bool,
    pub reputation_score: f64,
    pub total_transactions: u32,
    pub created_at: u64,
    pub last_active: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum VerificationStatus {
    Unverified,
    Basic,
    Premium,
    Elite,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct StakeInfo {
    pub amount_idr: u64,
    pub tier: VerificationTier,
    pub locked_until: u64,
    pub penalty_count: u32,
    pub reward_earned: u64,
    pub annual_return_rate: f64,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub enum VerificationTier {
    BasicReviewer { stake: u64 },    // 300k IDR
    PremiumReviewer { stake: u64 },  // 950k IDR  
    EliteReviewer { stake: u64 },    // 1.9M IDR
    BasicSeller { stake: u64 },      // 500k IDR
    PremiumSeller { stake: u64 },    // 1.5M IDR
    EliteSeller { stake: u64 },      // 3M IDR
}

#[derive(CandidType, Deserialize, Clone)]
pub struct Product {
    pub id: String,
    pub seller_id: String,
    pub seller_verification: VerificationStatus,
    pub name: String,
    pub brand: String,
    pub price_idr: u64,
    pub fragrance_family: String,
    pub top_notes: Vec<String>,
    pub middle_notes: Vec<String>,
    pub base_notes: Vec<String>,
    pub occasion: Vec<String>,
    pub season: Vec<String>,
    pub longevity: LongevityRating,
    pub sillage: SillageRating,
    pub projection: ProjectionRating,
    pub versatility_score: f64,
    pub description: String,
    pub ingredients: Vec<String>,
    pub halal_certified: bool,
    pub image_urls: Vec<String>,
    pub stock: u32,
    pub verified: bool,
    pub ai_analyzed: bool,
    pub personality_matches: Vec<String>,
    pub created_at: u64,
    pub updated_at: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum LongevityRating {
    VeryWeak,    // 0-2 hours
    Weak,        // 2-4 hours
    Moderate,    // 4-6 hours
    Good,        // 6-8 hours
    VeryGood,    // 8-12 hours
    Excellent,   // 12+ hours
}

#[derive(CandidType, Deserialize, Clone)]
pub enum SillageRating {
    Intimate,    // Very close to skin
    Moderate,    // Arms length
    Heavy,       // Room filling
    Enormous,    // Multiple rooms
}

#[derive(CandidType, Deserialize, Clone)]
pub enum ProjectionRating {
    Skin,        // Projects close to skin
    Light,       // 1-2 feet
    Moderate,    // 3-5 feet
    Strong,      // 6+ feet
}

#[derive(CandidType, Deserialize, Clone)]
pub struct VerifiedReview {
    pub review_id: String,
    pub reviewer_id: String,
    pub reviewer_stake: u64,
    pub reviewer_tier: VerificationTier,
    pub product_id: String,
    pub overall_rating: u8,
    pub longevity_rating: u8,
    pub sillage_rating: u8,
    pub projection_rating: u8,
    pub versatility_rating: u8,
    pub value_rating: u8,
    pub detailed_review: String,
    pub verified_purchase: bool,
    pub skin_type: String,
    pub age_group: String,
    pub wear_occasion: String,
    pub season_tested: String,
    pub helpful_votes: u32,
    pub reported_count: u32,
    pub ai_validated: bool,
    pub review_date: u64,
    pub last_updated: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct AIRecommendation {
    pub recommendation_id: String,
    pub user_id: String,
    pub product_id: String,
    pub match_score: f64,
    pub personality_alignment: f64,
    pub lifestyle_fit: f64,
    pub occasion_match: f64,
    pub budget_compatibility: f64,
    pub reasoning: String,
    pub confidence_level: f64,
    pub seasonal_relevance: f64,
    pub trend_factor: f64,
    pub generated_at: u64,
    pub user_feedback: Option<f64>,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct Transaction {
    pub transaction_id: String,
    pub buyer_id: String,
    pub seller_id: String,
    pub product_id: String,
    pub quantity: u32,
    pub unit_price_idr: u64,
    pub total_amount_idr: u64,
    pub commission_rate: f64,
    pub commission_amount: u64,
    pub transaction_tier: TransactionTier,
    pub status: TransactionStatus,
    pub escrow_locked: bool,
    pub payment_method: String,
    pub shipping_address: String,
    pub created_at: u64,
    pub completed_at: Option<u64>,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum TransactionTier {
    Budget,      // <100k IDR - 1.5% fee
    Standard,    // 100k-500k IDR - 2% fee
    Premium,     // 500k-1M IDR - 2.5% fee
    Luxury,      // >1M IDR - 3% fee
}

#[derive(CandidType, Deserialize, Clone)]
pub enum TransactionStatus {
    Pending,
    Processing,
    Confirmed,
    Shipped,
    Delivered,
    Completed,
    Disputed,
    Cancelled,
    Refunded,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct AnalyticsSubscription {
    pub subscription_id: String,
    pub seller_id: String,
    pub tier: AnalyticsTier,
    pub monthly_fee: u64,
    pub features_included: Vec<String>,
    pub data_retention_days: u32,
    pub api_calls_limit: u32,
    pub started_at: u64,
    pub expires_at: u64,
    pub auto_renew: bool,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum AnalyticsTier {
    Basic,       // 1.2M IDR/month
    Premium,     // 2.8M IDR/month
    Enterprise,  // 4.5M IDR/month
}

#[derive(CandidType, Deserialize, Clone)]
pub struct AnalyticsData {
    pub analytics_id: String,
    pub seller_id: String,
    pub period_start: u64,
    pub period_end: u64,
    pub total_views: u32,
    pub unique_visitors: u32,
    pub conversion_rate: f64,
    pub top_performing_products: Vec<String>,
    pub customer_demographics: HashMap<String, u32>,
    pub sales_trends: Vec<SalesTrend>,
    pub competitor_analysis: Option<CompetitorData>,
    pub predictive_insights: Option<PredictiveInsight>,
    pub generated_at: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct SalesTrend {
    pub date: u64,
    pub sales_volume: u32,
    pub revenue_idr: u64,
    pub avg_order_value: u64,
    pub top_category: String,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct CompetitorData {
    pub competitor_prices: HashMap<String, u64>,
    pub market_position: String,
    pub competitive_advantage: Vec<String>,
    pub threat_level: String,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct PredictiveInsight {
    pub predicted_demand: HashMap<String, f64>,
    pub optimal_pricing: HashMap<String, u64>,
    pub inventory_recommendations: Vec<String>,
    pub seasonal_adjustments: Vec<String>,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct Advertisement {
    pub ad_id: String,
    pub advertiser_id: String,
    pub product_id: String,
    pub ad_type: AdType,
    pub placement: AdPlacement,
    pub annual_fee: u64,
    pub impressions: u32,
    pub clicks: u32,
    pub conversions: u32,
    pub ctr: f64,
    pub conversion_rate: f64,
    pub active: bool,
    pub started_at: u64,
    pub expires_at: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum AdType {
    Banner,
    Featured,
    Sponsored,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum AdPlacement {
    Homepage,
    CategoryPage,
    SearchResults,
    ProductPage,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct TreasuryInvestment {
    pub investment_id: String,
    pub principal_amount: u64,
    pub investment_type: InvestmentType,
    pub annual_return_rate: f64,
    pub maturity_date: u64,
    pub current_value: u64,
    pub created_at: u64,
}

#[derive(CandidType, Deserialize, Clone)]
pub enum InvestmentType {
    FixedIncome,     // 60% allocation
    MoneyMarket,     // 30% allocation
    EmergencyFund,   // 10% allocation
}

static mut USER_PROFILES: Option<HashMap<String, UserProfile>> = None;
static mut DECENTRALIZED_IDENTITIES: Option<HashMap<String, DecentralizedIdentity>> = None;
static mut PRODUCTS: Option<HashMap<String, Product>> = None;
static mut VERIFIED_REVIEWS: Option<HashMap<String, VerifiedReview>> = None;
static mut AI_RECOMMENDATIONS: Option<HashMap<String, Vec<AIRecommendation>>> = None;
static mut TRANSACTIONS: Option<HashMap<String, Transaction>> = None;
static mut ANALYTICS_SUBSCRIPTIONS: Option<HashMap<String, AnalyticsSubscription>> = None;
static mut ANALYTICS_DATA: Option<HashMap<String, Vec<AnalyticsData>>> = None;
static mut ADVERTISEMENTS: Option<HashMap<String, Advertisement>> = None;
static mut TREASURY_INVESTMENTS: Option<HashMap<String, TreasuryInvestment>> = None;
static mut STAKE_POOL: Option<u64> = None;

#[init]
fn init() {
    unsafe {
        USER_PROFILES = Some(HashMap::new());
        DECENTRALIZED_IDENTITIES = Some(HashMap::new());
        PRODUCTS = Some(HashMap::new());
        VERIFIED_REVIEWS = Some(HashMap::new());
        AI_RECOMMENDATIONS = Some(HashMap::new());
        TRANSACTIONS = Some(HashMap::new());
        ANALYTICS_SUBSCRIPTIONS = Some(HashMap::new());
        ANALYTICS_DATA = Some(HashMap::new());
        ADVERTISEMENTS = Some(HashMap::new());
        TREASURY_INVESTMENTS = Some(HashMap::new());
        STAKE_POOL = Some(0);
    }
}

#[update]
fn create_decentralized_identity(user_id: String, personality_data: FragranceIdentity) -> Result<DecentralizedIdentity, String> {
    let current_time = time();
    let did = format!("did:icp:aromance:{}", user_id);
    let public_key = format!("pub_key_{}", current_time);
    let private_key_hash = format!("priv_hash_{}", current_time);
    
    let identity = DecentralizedIdentity {
        did: did.clone(),
        public_key,
        private_key_hash,
        verified_claims: Vec::new(),
        data_permissions: HashMap::new(),
        fragrance_identity: personality_data,
        created_at: current_time,
    };
    
    unsafe {
        if let Some(identities) = &mut DECENTRALIZED_IDENTITIES {
            identities.insert(did.clone(), identity.clone());
            
            if let Some(profiles) = &mut USER_PROFILES {
                if let Some(profile) = profiles.get_mut(&user_id) {
                    profile.did = Some(did);
                }
            }
            
            Ok(identity)
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[update]
fn stake_for_verification(user_id: String, amount: u64, tier: VerificationTier) -> Result<String, String> {
    let current_time = time();
    let lock_duration = 365 * 24 * 60 * 60 * 1_000_000_000u64;
    
    let (required_amount, annual_return) = match &tier {
        VerificationTier::BasicReviewer { .. } => (300_000u64, 6.0),
        VerificationTier::PremiumReviewer { .. } => (950_000u64, 7.5),
        VerificationTier::EliteReviewer { .. } => (1_900_000u64, 9.0),
        VerificationTier::BasicSeller { .. } => (500_000u64, 6.0),
        VerificationTier::PremiumSeller { .. } => (1_500_000u64, 7.5),
        VerificationTier::EliteSeller { .. } => (3_000_000u64, 9.0),
    };
    
    if amount < required_amount {
        return Err(format!("Insufficient stake amount. Required: {} IDR", required_amount));
    }
    
    unsafe {
        if let Some(profiles) = &mut USER_PROFILES {
            if let Some(profile) = profiles.get_mut(&user_id) {
                profile.stake_info = Some(StakeInfo {
                    amount_idr: amount,
                    tier: tier.clone(),
                    locked_until: current_time + lock_duration,
                    penalty_count: 0,
                    reward_earned: 0,
                    annual_return_rate: annual_return,
                });
                
                profile.verification_status = match tier {
                    VerificationTier::BasicReviewer { .. } | VerificationTier::BasicSeller { .. } => VerificationStatus::Basic,
                    VerificationTier::PremiumReviewer { .. } | VerificationTier::PremiumSeller { .. } => VerificationStatus::Premium,
                    VerificationTier::EliteReviewer { .. } | VerificationTier::EliteSeller { .. } => VerificationStatus::Elite,
                };
                
                if let Some(stake_pool) = &mut STAKE_POOL {
                    *stake_pool += amount;
                }
                
                Ok(format!("Staked {} IDR for verification tier", amount))
            } else {
                Err("User not found".to_string())
            }
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[update]
fn create_user_profile(profile: UserProfile) -> Result<String, String> {
    unsafe {
        if let Some(profiles) = &mut USER_PROFILES {
            profiles.insert(profile.user_id.clone(), profile.clone());
            Ok(format!("Profile created for user: {}", profile.user_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_user_profile(user_id: String) -> Option<UserProfile> {
    unsafe {
        USER_PROFILES.as_ref()?.get(&user_id).cloned()
    }
}

#[update]
fn add_product(product: Product) -> Result<String, String> {
    unsafe {
        if let Some(products) = &mut PRODUCTS {
            products.insert(product.id.clone(), product.clone());
            Ok(format!("Product added: {}", product.name))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_products() -> Vec<Product> {
    unsafe {
        PRODUCTS.as_ref()
            .map(|products| products.values().cloned().collect())
            .unwrap_or_default()
    }
}

#[query]
fn search_products_advanced(
    fragrance_family: Option<String>,
    budget_min: Option<u64>,
    budget_max: Option<u64>,
    occasion: Option<String>,
    season: Option<String>,
    _longevity: Option<LongevityRating>,
    verified_only: Option<bool>
) -> Vec<Product> {
    unsafe {
        PRODUCTS.as_ref()
            .map(|products| {
                products.values()
                    .filter(|p| {
                        if let Some(ref family) = fragrance_family {
                            if !p.fragrance_family.to_lowercase().contains(&family.to_lowercase()) {
                                return false;
                            }
                        }
                        
                        if let Some(min) = budget_min {
                            if p.price_idr < min {
                                return false;
                            }
                        }
                        
                        if let Some(max) = budget_max {
                            if p.price_idr > max {
                                return false;
                            }
                        }
                        
                        if let Some(ref occ) = occasion {
                            if !p.occasion.iter().any(|o| o.to_lowercase().contains(&occ.to_lowercase())) {
                                return false;
                            }
                        }
                        
                        if let Some(ref seas) = season {
                            if !p.season.iter().any(|s| s.to_lowercase().contains(&seas.to_lowercase())) {
                                return false;
                            }
                        }
                        
                        if let Some(verified) = verified_only {
                            if verified && !p.verified {
                                return false;
                            }
                        }
                        
                        true
                    })
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
fn create_verified_review(review: VerifiedReview) -> Result<String, String> {
    let reviewer_verification = unsafe {
        USER_PROFILES.as_ref()
            .and_then(|profiles| profiles.get(&review.reviewer_id))
            .map(|profile| &profile.verification_status)
    };
    
    match reviewer_verification {
        Some(VerificationStatus::Unverified) => {
            return Err("User must be verified to create reviews".to_string());
        },
        None => {
            return Err("User not found".to_string());
        },
        _ => {}
    }
    
    unsafe {
        if let Some(reviews) = &mut VERIFIED_REVIEWS {
            reviews.insert(review.review_id.clone(), review.clone());
            Ok(format!("Verified review created: {}", review.review_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_product_reviews(product_id: String) -> Vec<VerifiedReview> {
    unsafe {
        VERIFIED_REVIEWS.as_ref()
            .map(|reviews| {
                reviews.values()
                    .filter(|r| r.product_id == product_id)
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
async fn generate_ai_recommendations(user_id: String) -> Result<Vec<AIRecommendation>, String> {
    let user_profile = unsafe {
        USER_PROFILES.as_ref()
            .and_then(|profiles| profiles.get(&user_id))
    };
    
    let user_did = unsafe {
        DECENTRALIZED_IDENTITIES.as_ref()
            .and_then(|identities| {
                user_profile?.did.as_ref()
                    .and_then(|did| identities.get(did))
            })
    };
    
    if user_profile.is_none() || user_did.is_none() {
        return Err("User profile or DID not found".to_string());
    }
    
    let _profile = user_profile.unwrap();
    let did = user_did.unwrap();
    let current_time = time();
    
    let products = unsafe {
        PRODUCTS.as_ref()
            .map(|products| products.values().collect::<Vec<_>>())
            .unwrap_or_default()
    };
    
    let mut recommendations = Vec::new();
    
    for product in products {
        let personality_score = calculate_personality_match(&did.fragrance_identity, product);
        let budget_score = calculate_budget_compatibility(&did.fragrance_identity.budget_range, product.price_idr);
        let occasion_score = calculate_occasion_match(&did.fragrance_identity.occasion_preferences, &product.occasion);
        let seasonal_score = calculate_seasonal_relevance(&did.fragrance_identity.season_preferences, &product.season);
        
        let overall_score = (personality_score + budget_score + occasion_score + seasonal_score) / 4.0;
        
        if overall_score > 0.6 {
            let recommendation = AIRecommendation {
                recommendation_id: format!("rec_{}_{}", user_id, product.id),
                user_id: user_id.clone(),
                product_id: product.id.clone(),
                match_score: overall_score,
                personality_alignment: personality_score,
                lifestyle_fit: calculate_lifestyle_fit(&did.fragrance_identity.lifestyle, product),
                occasion_match: occasion_score,
                budget_compatibility: budget_score,
                reasoning: format!("Based on your {} personality and {} lifestyle", 
                    did.fragrance_identity.personality_type, 
                    did.fragrance_identity.lifestyle),
                confidence_level: overall_score * 0.9,
                seasonal_relevance: seasonal_score,
                trend_factor: 0.8,
                generated_at: current_time,
                user_feedback: None,
            };
            
            recommendations.push(recommendation);
        }
    }
    
    recommendations.sort_by(|a, b| b.match_score.partial_cmp(&a.match_score).unwrap());
    recommendations.truncate(10);
    
    unsafe {
        if let Some(ai_recs) = &mut AI_RECOMMENDATIONS {
            ai_recs.insert(user_id, recommendations.clone());
        }
    }
    
    Ok(recommendations)
}

fn calculate_personality_match(fragrance_identity: &FragranceIdentity, product: &Product) -> f64 {
    let mut score = 0.0;
    let mut factors = 0;
    
    for preferred_family in &fragrance_identity.preferred_families {
        if product.fragrance_family.to_lowercase().contains(&preferred_family.to_lowercase()) {
            score += 1.0;
        }
        factors += 1;
    }
    
    if product.personality_matches.contains(&fragrance_identity.personality_type) {
        score += 1.0;
        factors += 1;
    }
    
    if factors > 0 {
        score / factors as f64
    } else {
        0.5
    }
}

fn calculate_budget_compatibility(budget_range: &BudgetRange, price: u64) -> f64 {
    match budget_range {
        BudgetRange::Budget => {
            if price < 50_000 { 1.0 }
            else if price < 100_000 { 0.7 }
            else { 0.3 }
        },
        BudgetRange::Moderate => {
            if price >= 50_000 && price < 200_000 { 1.0 }
            else if price < 50_000 || (price >= 200_000 && price < 300_000) { 0.7 }
            else { 0.3 }
        },
        BudgetRange::Premium => {
            if price >= 200_000 && price < 500_000 { 1.0 }
            else if price >= 100_000 && price < 200_000 { 0.7 }
            else if price >= 500_000 && price < 700_000 { 0.7 }
            else { 0.3 }
        },
        BudgetRange::Luxury => {
            if price >= 500_000 { 1.0 }
            else if price >= 300_000 { 0.7 }
            else { 0.3 }
        }
    }
}

fn calculate_occasion_match(user_occasions: &Vec<String>, product_occasions: &Vec<String>) -> f64 {
    if user_occasions.is_empty() || product_occasions.is_empty() {
        return 0.5;
    }
    
    let matches = user_occasions.iter()
        .filter(|uo| product_occasions.iter().any(|po| 
            po.to_lowercase().contains(&uo.to_lowercase()) ||
            uo.to_lowercase().contains(&po.to_lowercase())
        ))
        .count();
    
    matches as f64 / user_occasions.len() as f64
}

fn calculate_seasonal_relevance(user_seasons: &Vec<String>, product_seasons: &Vec<String>) -> f64 {
    if user_seasons.is_empty() || product_seasons.is_empty() {
        return 0.5;
    }
    
    let matches = user_seasons.iter()
        .filter(|us| product_seasons.iter().any(|ps| 
            ps.to_lowercase().contains(&us.to_lowercase())
        ))
        .count();
    
    matches as f64 / user_seasons.len() as f64
}

fn calculate_lifestyle_fit(lifestyle: &String, product: &Product) -> f64 {
    match lifestyle.to_lowercase().as_str() {
        "professional" => {
            if product.occasion.iter().any(|o| o.contains("office") || o.contains("formal")) {
                0.9
            } else if product.versatility_score > 0.7 {
                0.8
            } else {
                0.5
            }
        },
        "casual" => {
            if product.occasion.iter().any(|o| o.contains("daily") || o.contains("casual")) {
                0.9
            } else {
                0.6
            }
        },
        "evening" => {
            if product.occasion.iter().any(|o| o.contains("night") || o.contains("date")) {
                0.9
            } else {
                0.5
            }
        },
        _ => 0.7
    }
}

#[update]
fn create_transaction(transaction: Transaction) -> Result<String, String> {
    let commission = calculate_commission_by_tier(&transaction.transaction_tier, transaction.total_amount_idr);
    
    let mut updated_transaction = transaction;
    updated_transaction.commission_amount = commission;
    
    unsafe {
        if let Some(transactions) = &mut TRANSACTIONS {
            transactions.insert(updated_transaction.transaction_id.clone(), updated_transaction.clone());
            Ok(format!("Transaction created: {}", updated_transaction.transaction_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

fn calculate_commission_by_tier(tier: &TransactionTier, amount: u64) -> u64 {
    let rate = match tier {
        TransactionTier::Budget => 0.015,
        TransactionTier::Standard => 0.02,
        TransactionTier::Premium => 0.025,
        TransactionTier::Luxury => 0.03,
    };
    
    (amount as f64 * rate) as u64
}

#[query]
fn get_user_transactions(user_id: String) -> Vec<Transaction> {
    unsafe {
        TRANSACTIONS.as_ref()
            .map(|transactions| {
                transactions.values()
                    .filter(|t| t.buyer_id == user_id || t.seller_id == user_id)
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
fn subscribe_analytics(subscription: AnalyticsSubscription) -> Result<String, String> {
    let monthly_fee = match subscription.tier {
        AnalyticsTier::Basic => 1_200_000u64,
        AnalyticsTier::Premium => 2_800_000u64,
        AnalyticsTier::Enterprise => 4_500_000u64,
    };
    
    let features = match subscription.tier {
        AnalyticsTier::Basic => vec![
            "Basic Demographics".to_string(),
            "Sales Overview".to_string(),
            "Product Performance".to_string()
        ],
        AnalyticsTier::Premium => vec![
            "Advanced Demographics".to_string(),
            "Predictive Analytics".to_string(),
            "Competitor Analysis".to_string(),
            "Custom Reports".to_string(),
            "API Access".to_string()
        ],
        AnalyticsTier::Enterprise => vec![
            "Full Analytics Suite".to_string(),
            "Real-time Insights".to_string(),
            "Advanced ML Models".to_string(),
            "Dedicated Support".to_string(),
            "Custom Integrations".to_string(),
            "White-label Reports".to_string()
        ],
    };
    
    let updated_subscription = AnalyticsSubscription {
        monthly_fee,
        features_included: features,
        ..subscription
    };
    
    unsafe {
        if let Some(subscriptions) = &mut ANALYTICS_SUBSCRIPTIONS {
            subscriptions.insert(updated_subscription.subscription_id.clone(), updated_subscription.clone());
            Ok(format!("Analytics subscription created: {}", updated_subscription.subscription_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[update]
fn generate_analytics_data(seller_id: String, period_start: u64, period_end: u64) -> Result<AnalyticsData, String> {
    let subscription = unsafe {
        ANALYTICS_SUBSCRIPTIONS.as_ref()
            .and_then(|subs| subs.values().find(|s| s.seller_id == seller_id && s.expires_at > time()))
    };
    
    if subscription.is_none() {
        return Err("Valid analytics subscription required".to_string());
    }
    
    let sub = subscription.unwrap();
    let current_time = time();
    
    let seller_transactions = unsafe {
        TRANSACTIONS.as_ref()
            .map(|transactions| {
                transactions.values()
                    .filter(|t| t.seller_id == seller_id && 
                               t.created_at >= period_start && 
                               t.created_at <= period_end)
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default()
    };
    
    let total_revenue: u64 = seller_transactions.iter().map(|t| t.total_amount_idr).sum();
    let total_orders = seller_transactions.len() as u32;
    let _avg_order_value = if total_orders > 0 { total_revenue / total_orders as u64 } else { 0 };
    
    let mut sales_trends = Vec::new();
    let mut customer_demographics = HashMap::new();
    
    for transaction in &seller_transactions {
        let trend = SalesTrend {
            date: transaction.created_at,
            sales_volume: 1,
            revenue_idr: transaction.total_amount_idr,
            avg_order_value: transaction.total_amount_idr,
            top_category: "Fragrance".to_string(),
        };
        sales_trends.push(trend);
        
        let buyer_profile = unsafe {
            USER_PROFILES.as_ref()
                .and_then(|profiles| profiles.get(&transaction.buyer_id))
        };
        
        if let Some(_profile) = buyer_profile {
            *customer_demographics.entry("active_users".to_string()).or_insert(0) += 1;
        }
    }
    
    let competitor_analysis = match sub.tier {
        AnalyticsTier::Premium | AnalyticsTier::Enterprise => {
            Some(CompetitorData {
                competitor_prices: HashMap::new(),
                market_position: "Competitive".to_string(),
                competitive_advantage: vec!["AI Recommendations".to_string(), "Verified Reviews".to_string()],
                threat_level: "Medium".to_string(),
            })
        },
        _ => None,
    };
    
    let predictive_insights = match sub.tier {
        AnalyticsTier::Enterprise => {
            Some(PredictiveInsight {
                predicted_demand: HashMap::new(),
                optimal_pricing: HashMap::new(),
                inventory_recommendations: vec!["Increase floral fragrances".to_string()],
                seasonal_adjustments: vec!["Summer collection launch".to_string()],
            })
        },
        _ => None,
    };
    
    let analytics = AnalyticsData {
        analytics_id: format!("analytics_{}_{}", seller_id.clone(), current_time),
        seller_id: seller_id.clone(),
        period_start,
        period_end,
        total_views: total_orders * 3,
        unique_visitors: total_orders * 2,
        conversion_rate: if total_orders > 0 { 15.5 } else { 0.0 },
        top_performing_products: vec!["Product1".to_string(), "Product2".to_string()],
        customer_demographics,
        sales_trends,
        competitor_analysis,
        predictive_insights,
        generated_at: current_time,
    };
    
    unsafe {
        if let Some(analytics_data) = &mut ANALYTICS_DATA {
            analytics_data.entry(seller_id).or_insert_with(Vec::new).push(analytics.clone());
        }
    }
    
    Ok(analytics)
}

#[query]
fn get_seller_analytics(seller_id: String) -> Vec<AnalyticsData> {
    unsafe {
        ANALYTICS_DATA.as_ref()
            .and_then(|data| data.get(&seller_id))
            .cloned()
            .unwrap_or_default()
    }
}

#[update]
fn create_advertisement(ad: Advertisement) -> Result<String, String> {
    let annual_fee = 1_500_000u64;
    
    let updated_ad = Advertisement {
        annual_fee,
        impressions: 0,
        clicks: 0,
        conversions: 0,
        ctr: 0.0,
        conversion_rate: 0.0,
        active: true,
        ..ad
    };
    
    unsafe {
        if let Some(ads) = &mut ADVERTISEMENTS {
            ads.insert(updated_ad.ad_id.clone(), updated_ad.clone());
            Ok(format!("Advertisement created: {}", updated_ad.ad_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_active_advertisements(placement: AdPlacement) -> Vec<Advertisement> {
    unsafe {
        ADVERTISEMENTS.as_ref()
            .map(|ads| {
                ads.values()
                    .filter(|ad| ad.active && 
                                ad.expires_at > time() &&
                                std::mem::discriminant(&ad.placement) == std::mem::discriminant(&placement))
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
fn invest_treasury_funds(amount: u64, investment_type: InvestmentType) -> Result<String, String> {
    let current_time = time();
    let maturity_duration = 365 * 24 * 60 * 60 * 1_000_000_000u64;
    
    let annual_return_rate = match investment_type {
        InvestmentType::FixedIncome => 0.07,
        InvestmentType::MoneyMarket => 0.06,
        InvestmentType::EmergencyFund => 0.04,
    };
    
    let investment = TreasuryInvestment {
        investment_id: format!("inv_{}_{}", current_time, amount),
        principal_amount: amount,
        investment_type,
        annual_return_rate,
        maturity_date: current_time + maturity_duration,
        current_value: amount,
        created_at: current_time,
    };
    
    unsafe {
        if let Some(investments) = &mut TREASURY_INVESTMENTS {
            investments.insert(investment.investment_id.clone(), investment.clone());
            Ok(format!("Treasury investment created: {}", investment.investment_id))
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn calculate_treasury_returns() -> u64 {
    let current_time = time();
    
    unsafe {
        TREASURY_INVESTMENTS.as_ref()
            .map(|investments| {
                investments.values()
                    .map(|inv| {
                        let time_elapsed = (current_time - inv.created_at) as f64 / (365.0 * 24.0 * 60.0 * 60.0 * 1_000_000_000.0);
                        let returns = inv.principal_amount as f64 * inv.annual_return_rate * time_elapsed;
                        returns as u64
                    })
                    .sum()
            })
            .unwrap_or(0)
    }
}

#[update]
fn process_stake_rewards() -> Result<String, String> {
    let current_time = time();
    let mut total_rewards = 0u64;
    
    unsafe {
        if let Some(profiles) = &mut USER_PROFILES {
            for (_user_id, profile) in profiles.iter_mut() {
                if let Some(stake_info) = &mut profile.stake_info {
                    let time_elapsed = (current_time - profile.created_at) as f64 / (365.0 * 24.0 * 60.0 * 60.0 * 1_000_000_000.0);
                    let annual_reward = stake_info.amount_idr as f64 * stake_info.annual_return_rate / 100.0;
                    let current_reward = (annual_reward * time_elapsed) as u64;
                    
                    if current_reward > stake_info.reward_earned {
                        let new_reward = current_reward - stake_info.reward_earned;
                        stake_info.reward_earned = current_reward;
                        total_rewards += new_reward;
                    }
                }
            }
        }
    }
    
    Ok(format!("Processed stake rewards: {} IDR total", total_rewards))
}

#[update]
fn penalize_malicious_behavior(user_id: String, violation_type: String) -> Result<String, String> {
    unsafe {
        if let Some(profiles) = &mut USER_PROFILES {
            if let Some(profile) = profiles.get_mut(&user_id) {
                if let Some(stake_info) = &mut profile.stake_info {
                    stake_info.penalty_count += 1;
                    
                    let penalty_amount = match violation_type.as_str() {
                        "fake_review" => stake_info.amount_idr / 10,
                        "misleading_product" => stake_info.amount_idr / 5,
                        "spam_behavior" => stake_info.amount_idr / 20,
                        _ => stake_info.amount_idr / 50,
                    };
                    
                    if stake_info.penalty_count >= 3 {
                        profile.verification_status = VerificationStatus::Unverified;
                        stake_info.amount_idr = 0;
                        return Ok(format!("User {} verification revoked due to repeated violations", user_id));
                    }
                    
                    stake_info.amount_idr = stake_info.amount_idr.saturating_sub(penalty_amount);
                    profile.reputation_score = (profile.reputation_score - 0.1).max(0.0);
                    
                    Ok(format!("Penalty applied to {}: {} IDR deducted", user_id, penalty_amount))
                } else {
                    Err("User has no stake to penalize".to_string())
                }
            } else {
                Err("User not found".to_string())
            }
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_platform_statistics() -> HashMap<String, u64> {
    let mut stats = HashMap::new();
    
    unsafe {
        if let Some(profiles) = &USER_PROFILES {
            stats.insert("total_users".to_string(), profiles.len() as u64);
            stats.insert("verified_users".to_string(), 
                profiles.values().filter(|p| !matches!(p.verification_status, VerificationStatus::Unverified)).count() as u64);
        }
        
        if let Some(products) = &PRODUCTS {
            stats.insert("total_products".to_string(), products.len() as u64);
            stats.insert("verified_products".to_string(), 
                products.values().filter(|p| p.verified).count() as u64);
        }
        
        if let Some(transactions) = &TRANSACTIONS {
            stats.insert("total_transactions".to_string(), transactions.len() as u64);
            let total_gmv: u64 = transactions.values().map(|t| t.total_amount_idr).sum();
            stats.insert("total_gmv_idr".to_string(), total_gmv);
        }
        
        if let Some(reviews) = &VERIFIED_REVIEWS {
            stats.insert("total_reviews".to_string(), reviews.len() as u64);
        }
        
        if let Some(stake_pool) = &STAKE_POOL {
            stats.insert("total_staked_idr".to_string(), *stake_pool);
        }
    }
    
    stats
}

#[update]
fn update_product_ai_analysis(product_id: String, personality_matches: Vec<String>) -> Result<String, String> {
    unsafe {
        if let Some(products) = &mut PRODUCTS {
            if let Some(product) = products.get_mut(&product_id) {
                product.personality_matches = personality_matches;
                product.ai_analyzed = true;
                product.updated_at = time();
                Ok(format!("AI analysis updated for product: {}", product_id))
            } else {
                Err("Product not found".to_string())
            }
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_recommendations_for_user(user_id: String) -> Vec<AIRecommendation> {
    unsafe {
        AI_RECOMMENDATIONS.as_ref()
            .and_then(|recs| recs.get(&user_id))
            .cloned()
            .unwrap_or_default()
    }
}

#[update]
fn update_user_data_permissions(user_id: String, permissions: HashMap<String, PermissionLevel>) -> Result<String, String> {
    unsafe {
        if let Some(identities) = &mut DECENTRALIZED_IDENTITIES {
            if let Some(profiles) = &USER_PROFILES {
                if let Some(profile) = profiles.get(&user_id) {
                    if let Some(did_id) = &profile.did {
                        if let Some(identity) = identities.get_mut(did_id) {
                            identity.data_permissions = permissions;
                            return Ok(format!("Data permissions updated for user: {}", user_id));
                        }
                    }
                }
            }
        }
        Err("User DID not found".to_string())
    }
}

#[query]
fn search_products_by_personality(personality_type: String) -> Vec<Product> {
    unsafe {
        PRODUCTS.as_ref()
            .map(|products| {
                products.values()
                    .filter(|p| p.personality_matches.contains(&personality_type))
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
fn validate_halal_certification(product_id: String, certified: bool) -> Result<String, String> {
    unsafe {
        if let Some(products) = &mut PRODUCTS {
            if let Some(product) = products.get_mut(&product_id) {
                product.halal_certified = certified;
                product.updated_at = time();
                Ok(format!("Halal certification updated for product: {}", product_id))
            } else {
                Err("Product not found".to_string())
            }
        } else {
            Err("Storage not initialized".to_string())
        }
    }
}

#[query]
fn get_halal_products() -> Vec<Product> {
    unsafe {
        PRODUCTS.as_ref()
            .map(|products| {
                products.values()
                    .filter(|p| p.halal_certified)
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }
}

#[update]
fn create_fragrance_family_trend(family: String, trend_score: f64) -> Result<String, String> {
    Ok(format!("Trend analysis created for {} family with score: {}", family, trend_score))
}

#[query]
fn get_trending_fragrances() -> Vec<String> {
    vec![
        "Fresh Citrus".to_string(),
        "Woody Oriental".to_string(),
        "Floral Fruity".to_string(),
        "Gourmand".to_string(),
    ]
}

#[update]
fn process_monthly_treasury_allocation() -> Result<String, String> {
    let _current_time = time();
    let treasury_revenue = calculate_treasury_returns();
    
    let fixed_income_allocation = (treasury_revenue as f64 * 0.6) as u64;
    let money_market_allocation = (treasury_revenue as f64 * 0.3) as u64;
    let emergency_fund_allocation = (treasury_revenue as f64 * 0.1) as u64;
    
    invest_treasury_funds(fixed_income_allocation, InvestmentType::FixedIncome)?;
    invest_treasury_funds(money_market_allocation, InvestmentType::MoneyMarket)?;
    invest_treasury_funds(emergency_fund_allocation, InvestmentType::EmergencyFund)?;
    
    Ok(format!("Monthly treasury allocation completed: {} IDR total", treasury_revenue))
}

#[query]
fn greet(name: String) -> String {
    format!("Hello, {}! Welcome to Aromance - Your Decentralized Fragrance Identity Platform! 🌸", name)
}

#[query]
fn get_aromance_info() -> String {
    "Aromance: AI-Powered Decentralized Perfume Marketplace with Web3 Identity & Verified Reviews - Built for NextGen Agents Hackathon 🌸🇮🇩".to_string()
}