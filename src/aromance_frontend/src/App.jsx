import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import './App.css';

// ICP Backend Integration
const CANISTER_ID = process.env.CANISTER_ID_AROMANCE_BACKEND || 'uxrrr-q7777-77774-qaaaq-cai';
const HOST = process.env.DFX_NETWORK === 'ic' ? 'https://icp-api.io' : 'http://localhost:4943';

// Main Wallet Address for all transactions
const MAIN_WALLET_ADDRESS = "afa05153e88aa30ec9af2ff13617ea9e57f47083ee67bfb62b6ad17b6097f390";

// AI Agent Endpoints (Fixed paths without /api prefix)
const AGENT_ENDPOINTS = {
  coordinator: 'http://127.0.0.1:8000',
  consultation: 'http://127.0.0.1:8001',
  recommendation: 'http://127.0.0.1:8002',
  analytics: 'http://127.0.0.1:8004',
  inventory: 'http://127.0.0.1:8005'
};

// Fixed IDL Factory matching backend exactly
const idlFactory = ({ IDL }) => {
  // Enums and Variants
  const VerificationStatus = IDL.Variant({
    'Unverified': IDL.Null,
    'Basic': IDL.Null,
    'Premium': IDL.Null,
    'Elite': IDL.Null,
  });

  const VerificationTier = IDL.Variant({
    'BasicReviewer': IDL.Null,
    'PremiumReviewer': IDL.Null,
    'EliteReviewer': IDL.Null,
    'BasicSeller': IDL.Null,
    'PremiumSeller': IDL.Null,
    'EliteSeller': IDL.Null,
  });

  const BudgetRange = IDL.Variant({
    'Budget': IDL.Null,
    'Moderate': IDL.Null,
    'Premium': IDL.Null,
    'Luxury': IDL.Null,
  });

  const TransactionTier = IDL.Variant({
    'Budget': IDL.Null,
    'Standard': IDL.Null,
    'Premium': IDL.Null,
    'Luxury': IDL.Null,
  });

  const TransactionStatus = IDL.Variant({
    'Pending': IDL.Null,
    'Processing': IDL.Null,
    'Confirmed': IDL.Null,
    'Completed': IDL.Null,
    'Failed': IDL.Null,
    'Cancelled': IDL.Null,
  });

  const LongevityRating = IDL.Variant({
    'VeryWeak': IDL.Null,
    'Weak': IDL.Null,
    'Moderate': IDL.Null,
    'Good': IDL.Null,
    'VeryGood': IDL.Null,
    'Excellent': IDL.Null,
  });

  const SillageRating = IDL.Variant({
    'Intimate': IDL.Null,
    'Moderate': IDL.Null,
    'Heavy': IDL.Null,
    'Enormous': IDL.Null,
  });

  const ProjectionRating = IDL.Variant({
    'Skin': IDL.Null,
    'Light': IDL.Null,
    'Moderate': IDL.Null,
    'Strong': IDL.Null,
  });

  // Complex Types
  const StakeInfo = IDL.Record({
    'amount': IDL.Nat64,
    'tier': VerificationTier,
    'staked_at': IDL.Nat64,
    'last_reward': IDL.Nat64,
    'total_rewards': IDL.Nat64,
  });

  const ScentEvolution = IDL.Record({
    'stage': IDL.Text,
    'notes': IDL.Vec(IDL.Text),
    'duration_hours': IDL.Nat32,
  });

  const FragranceIdentity = IDL.Record({
    'personality_type': IDL.Text,
    'lifestyle': IDL.Text,
    'preferred_families': IDL.Vec(IDL.Text),
    'occasion_preferences': IDL.Vec(IDL.Text),
    'season_preferences': IDL.Vec(IDL.Text),
    'sensitivity_level': IDL.Text,
    'budget_range': BudgetRange,
    'scent_journey': IDL.Vec(ScentEvolution),
  });

  // Main Data Types
  const UserProfile = IDL.Record({
    'user_id': IDL.Text,
    'wallet_address': IDL.Opt(IDL.Text),
    'did': IDL.Opt(IDL.Text),
    'verification_status': VerificationStatus,
    'stake_info': IDL.Opt(StakeInfo),
    'preferences': IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text)),
    'consultation_completed': IDL.Bool,
    'ai_consent': IDL.Bool,
    'data_monetization_consent': IDL.Bool, // REQUIRED FIELD
    'reputation_score': IDL.Float64,
    'total_transactions': IDL.Nat32,
    'created_at': IDL.Nat64,
    'last_active': IDL.Nat64,
  });

  const DecentralizedIdentity = IDL.Record({
    'user_id': IDL.Text,
    'identity_hash': IDL.Text,
    'personality_data': FragranceIdentity,
    'created_at': IDL.Nat64,
    'permissions': IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text)),
  });

  const Product = IDL.Record({
    'id': IDL.Text,
    'seller_id': IDL.Text,
    'seller_verification': VerificationStatus,
    'name': IDL.Text,
    'brand': IDL.Text,
    'price_idr': IDL.Nat64,
    'fragrance_family': IDL.Text,
    'top_notes': IDL.Vec(IDL.Text),
    'middle_notes': IDL.Vec(IDL.Text),
    'base_notes': IDL.Vec(IDL.Text),
    'occasion': IDL.Vec(IDL.Text),
    'season': IDL.Vec(IDL.Text),
    'longevity': LongevityRating,
    'sillage': SillageRating,
    'projection': ProjectionRating,
    'versatility_score': IDL.Float64,
    'description': IDL.Text,
    'ingredients': IDL.Vec(IDL.Text),
    'halal_certified': IDL.Bool,
    'image_urls': IDL.Vec(IDL.Text),
    'stock': IDL.Nat32,
    'verified': IDL.Bool,
    'ai_analyzed': IDL.Bool,
    'personality_matches': IDL.Vec(IDL.Text),
    'created_at': IDL.Nat64,
    'updated_at': IDL.Nat64,
  });

  const AIRecommendation = IDL.Record({
    'recommendation_id': IDL.Text,
    'user_id': IDL.Text,
    'product_id': IDL.Text,
    'match_score': IDL.Float64,
    'personality_alignment': IDL.Float64,
    'lifestyle_fit': IDL.Float64,
    'occasion_match': IDL.Float64,
    'budget_compatibility': IDL.Float64,
    'reasoning': IDL.Text,
    'confidence_level': IDL.Float64,
    'seasonal_relevance': IDL.Float64,
    'trend_factor': IDL.Float64,
    'generated_at': IDL.Nat64,
    'user_feedback': IDL.Opt(IDL.Float64),
  });

  const Transaction = IDL.Record({
    'transaction_id': IDL.Text,
    'buyer_id': IDL.Text,
    'seller_id': IDL.Text,
    'product_id': IDL.Text,
    'quantity': IDL.Nat32,
    'unit_price_idr': IDL.Nat64,
    'total_amount_idr': IDL.Nat64,
    'commission_rate': IDL.Float64,
    'commission_amount': IDL.Nat64,
    'transaction_tier': TransactionTier,
    'status': TransactionStatus,
    'escrow_locked': IDL.Bool,
    'payment_method': IDL.Text,
    'shipping_address': IDL.Text,
    'created_at': IDL.Nat64,
    'completed_at': IDL.Opt(IDL.Nat64),
  });

  const VerifiedReview = IDL.Record({
    'review_id': IDL.Text,
    'reviewer_id': IDL.Text,
    'reviewer_stake': IDL.Nat64,
    'reviewer_tier': VerificationTier,
    'product_id': IDL.Text,
    'overall_rating': IDL.Nat8,
    'longevity_rating': IDL.Nat8,
    'sillage_rating': IDL.Nat8,
    'projection_rating': IDL.Nat8,
    'versatility_rating': IDL.Nat8,
    'value_rating': IDL.Nat8,
    'detailed_review': IDL.Text,
    'verified_purchase': IDL.Bool,
    'skin_type': IDL.Text,
    'age_group': IDL.Text,
    'wear_occasion': IDL.Text,
    'season_tested': IDL.Text,
    'helpful_votes': IDL.Nat32,
    'reported_count': IDL.Nat32,
    'ai_validated': IDL.Bool,
    'review_date': IDL.Nat64,
    'last_updated': IDL.Nat64,
  });

  return IDL.Service({
    // User Management
    'create_user_profile': IDL.Func([UserProfile], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'get_user_profile': IDL.Func([IDL.Text], [IDL.Opt(UserProfile)], ['query']),
    'create_decentralized_identity': IDL.Func([IDL.Text, FragranceIdentity], [IDL.Variant({ 'Ok': DecentralizedIdentity, 'Err': IDL.Text })], []),
    'update_user_data_permissions': IDL.Func([IDL.Text, IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text))], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    
    // Staking & Verification
    'stake_for_verification': IDL.Func([IDL.Text, IDL.Nat64, VerificationTier], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'process_stake_rewards': IDL.Func([], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'penalize_malicious_behavior': IDL.Func([IDL.Text, IDL.Text], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    
    // Product Management
    'add_product': IDL.Func([Product], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'get_products': IDL.Func([], [IDL.Vec(Product)], ['query']),
    'search_products_advanced': IDL.Func([
      IDL.Opt(IDL.Text), // fragrance_family
      IDL.Opt(IDL.Nat64), // budget_min
      IDL.Opt(IDL.Nat64), // budget_max
      IDL.Opt(IDL.Text), // occasion
      IDL.Opt(IDL.Text), // season
      IDL.Opt(LongevityRating), // longevity
      IDL.Opt(IDL.Bool) // verified_only
    ], [IDL.Vec(Product)], ['query']),
    'search_products_by_personality': IDL.Func([IDL.Text], [IDL.Vec(Product)], ['query']),
    'get_halal_products': IDL.Func([], [IDL.Vec(Product)], ['query']),
    'update_product_ai_analysis': IDL.Func([IDL.Text, IDL.Vec(IDL.Text)], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'validate_halal_certification': IDL.Func([IDL.Text, IDL.Bool], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    
    // AI Recommendations
    'generate_ai_recommendations': IDL.Func([IDL.Text], [IDL.Variant({ 'Ok': IDL.Vec(AIRecommendation), 'Err': IDL.Text })], []),
    'get_recommendations_for_user': IDL.Func([IDL.Text], [IDL.Vec(AIRecommendation)], ['query']),
    
    // Reviews
    'create_verified_review': IDL.Func([VerifiedReview], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'get_product_reviews': IDL.Func([IDL.Text], [IDL.Vec(VerifiedReview)], ['query']),
    
    // Transactions
    'create_transaction': IDL.Func([Transaction], [IDL.Variant({ 'Ok': IDL.Text, 'Err': IDL.Text })], []),
    'get_user_transactions': IDL.Func([IDL.Text], [IDL.Vec(Transaction)], ['query']),
    
    // Platform Stats
    'get_platform_statistics': IDL.Func([], [IDL.Record({
      'total_users': IDL.Nat64,
      'verified_users': IDL.Nat64,
      'total_products': IDL.Nat64,
      'verified_products': IDL.Nat64,
      'total_transactions': IDL.Nat64,
      'total_gmv_idr': IDL.Nat64,
      'total_reviews': IDL.Nat64,
      'total_staked_idr': IDL.Nat64,
    })], ['query']),
    'get_trending_fragrances': IDL.Func([], [IDL.Vec(IDL.Text)], ['query']),
    
    // Utility Functions
    'greet': IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_aromance_info': IDL.Func([], [IDL.Text], ['query']),
  });
};

// Plug Wallet Integration with real payment handling
const connectWallet = async () => {
  try {
    if (!window.ic?.plug) {
      window.open('https://plugwallet.ooo/', '_blank');
      return null;
    }

    const connected = await window.ic.plug.requestConnect({
      whitelist: [CANISTER_ID],
      host: HOST,
    });

    if (connected) {
      const principal = await window.ic.plug.agent.getPrincipal();
      return principal.toString();
    }
    return null;
  } catch (error) {
    console.error('Wallet connection failed:', error);
    return null;
  }
};

// Payment function for staking
const processPayment = async (amount, recipient = MAIN_WALLET_ADDRESS) => {
  try {
    if (!window.ic?.plug) {
      throw new Error('Plug wallet not available');
    }

    const params = {
      to: recipient,
      amount: amount,
    };

    const result = await window.ic.plug.requestTransfer(params);
    return result;
  } catch (error) {
    console.error('Payment failed:', error);
    throw error;
  }
};

// Image URL resolver
const resolveImageUrl = (imageUrl) => {
  if (!imageUrl) return '/images/default-product.png';
  if (imageUrl.startsWith('/')) return `https://aromance-e56c8.web.app${imageUrl}`;
  return imageUrl;
};

// Custom SVG Icons
const CustomIcons = {
  Cart: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7ZM9 3V4H15V3H9ZM7 6V19H17V6H7Z" fill="currentColor"/>
      <path d="M9 8V17H11V8H9ZM13 8V17H15V8H13Z" fill="currentColor"/>
    </svg>
  ),
  User: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 6.5C14.65 6.5 14.3 6.3 14.1 6L11.5 2H9.5L12.1 6C12.3 6.3 12.65 6.5 13 6.5L19 7V9H21ZM16 12C16 13.1 15.1 14 14 14S12 13.1 12 12 12.9 10 14 10 16 10.9 16 12Z" fill="currentColor"/>
    </svg>
  ),
  Robot: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H14A7,7 0 0,1 21,14H22A1,1 0 0,1 23,15V18A1,1 0 0,1 22,19H21A7,7 0 0,1 14,26H10A7,7 0 0,1 3,19H2A1,1 0 0,1 1,18V15A1,1 0 0,1 2,14H3A7,7 0 0,1 10,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M12,4A0.5,0.5 0 0,0 11.5,4.5A0.5,0.5 0 0,0 12,5A0.5,0.5 0 0,0 12.5,4.5A0.5,0.5 0 0,0 12,4M10,9A5,5 0 0,0 5,14V17A5,5 0 0,0 10,22H14A5,5 0 0,0 19,17V14A5,5 0 0,0 14,9H10M8.5,11A1.5,1.5 0 0,1 10,12.5A1.5,1.5 0 0,1 8.5,14A1.5,1.5 0 0,1 7,12.5A1.5,1.5 0 0,1 8.5,11M15.5,11A1.5,1.5 0 0,1 17,12.5A1.5,1.5 0 0,1 15.5,14A1.5,1.5 0 0,1 14,12.5A1.5,1.5 0 0,1 15.5,11M12,16.5C13.25,16.5 14.29,17.17 14.71,18.1C14.21,18.5 13.64,18.75 13,18.75H11C10.36,18.75 9.79,18.5 9.29,18.1C9.71,17.17 10.75,16.5 12,16.5Z" fill="currentColor"/>
    </svg>
  ),
  Flower: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,2A3,3 0 0,1 15,5C15,5.8 14.7,6.5 14.2,7C15.3,7.3 16,8.3 16,9.5A3.5,3.5 0 0,1 12.5,13H12.35C12.75,13.6 13,14.3 13,15A3,3 0 0,1 10,18C9.2,18 8.5,17.7 8,17.2C7.7,18.3 6.7,19 5.5,19A3.5,3.5 0 0,1 2,15.5C2,14.4 2.7,13.4 3.8,13.1C3.3,12.4 3,11.7 3,11A3,3 0 0,1 6,8C6.8,8 7.5,8.3 8,8.8C8.3,7.7 9.3,7 10.5,7A3.5,3.5 0 0,1 14,10.5C14,11.6 13.3,12.6 12.2,12.9C12.7,13.6 13,14.3 13,15A3,3 0 0,1 10,18L12,2Z" fill="currentColor"/>
    </svg>
  ),
  Star: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" fill="currentColor"/>
    </svg>
  ),
  Close: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" fill="currentColor"/>
    </svg>
  ),
  Plus: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill="currentColor"/>
    </svg>
  ),
  Minus: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M19,13H5V11H19V13Z" fill="currentColor"/>
    </svg>
  ),
  Delete: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z" fill="currentColor"/>
    </svg>
  ),
  Wallet: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M21,18V19A2,2 0 0,1 19,21H5C3.89,21 3,20.1 3,19V5A2,2 0 0,1 5,3H19A2,2 0 0,1 21,5V6H12A2,2 0 0,0 10,8V16A2,2 0 0,0 12,18M12,16H22V8H12M16,13.5A1.5,1.5 0 0,1 14.5,12A1.5,1.5 0 0,1 16,10.5A1.5,1.5 0 0,1 17.5,12A1.5,1.5 0 0,1 16,13.5Z" fill="currentColor"/>
    </svg>
  ),
  Settings: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M19.14,12.94a7.997,7.997,0,0,0,0-1.88l2.03-1.58a.5.5,0,0,0,.12-.66l-1.92-3.32a.5.5,0,0,0-.61-.22l-2.39.96a7.936,7.936,0,0,0-1.62-.94l-.36-2.54A.5.5,0,0,0,14,2h-4a.5.5,0,0,0-.5.42l-.36,2.54a7.936,7.936,0,0,0-1.62.94l-2.39-.96a.5.5,0,0,0-.61.22L2.98,8.82a.5.5,0,0,0,.12.66l2.03,1.58a7.997,7.997,0,0,0,0,1.88l-2.03,1.58a.5.5,0,0,0-.12.66l1.92,3.32c.14.24.42.34.68.24l2.39-.96c.5.39,1.05.71,1.62.94l.36,2.54c.04.26.26.46.52.46h4c.26,0,.48-.2.52-.46l.36-2.54c.57-.23,1.12-.55,1.62-.94l2.39.96c.26.1.54,0,.68-.24l1.92-3.32a.5.5,0,0,0-.12-.66L19.14,12.94ZM12,15.5A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" fill="currentColor"/>
    </svg>
  ),
  Refresh: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" fill="currentColor"/>
    </svg>
  ),
  Orders: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" fill="currentColor"/>
    </svg>
  ),
  Crown: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M5 16L3 5L8.5 12L12 4L15.5 12L21 5L19 16H5Z" fill="currentColor"/>
    </svg>
  ),
  Search: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M15.5,14H14.71L14.43,13.73C15.41,12.59 16,11.11 16,9.5A6.5,6.5 0 0,0 9.5,3A6.5,6.5 0 0,0 3,9.5A6.5,6.5 0 0,0 9.5,16C11.11,16 12.59,15.41 13.73,14.43L14,14.71V15.5L21,22.49L22.49,21L15.5,14M9.5,14C7,14 5,12 5,9.5C5,7 7,5 9.5,5C12,5 14,7 14,9.5C14,12 12,14 9.5,14Z" fill="currentColor"/>
    </svg>
  ),
  Heart: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,21.35L10.55,20.03C5.4,15.36 2,12.27 2,8.5C2,5.41 4.42,3 7.5,3C9.24,3 10.91,3.81 12,5.08C13.09,3.81 14.76,3 16.5,3C19.58,3 22,5.41 22,8.5C22,12.27 18.6,15.36 13.45,20.03L12,21.35Z" fill="currentColor"/>
    </svg>
  )
};

const App = () => {
  // UI States
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showAIConsultation, setShowAIConsultation] = useState(false);
  const [showProductDetail, setShowProductDetail] = useState(false);
  const [showOrderHistory, setShowOrderHistory] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // User States
  const [userProfile, setUserProfile] = useState(null);
  const [tempUsername, setTempUsername] = useState('');
  const [walletConnected, setWalletConnected] = useState(false);
  const [userWallet, setUserWallet] = useState(null);
  const [userDID, setUserDID] = useState(null);
  const [consultationCompleted, setConsultationCompleted] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [consultationData, setConsultationData] = useState(null);
  
  // Data States
  const [products, setProducts] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [topRecommendations, setTopRecommendations] = useState([]);
  const [personalizedProducts, setPersonalizedProducts] = useState([]);
  const [otherProducts, setOtherProducts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [productReviews, setProductReviews] = useState({});
  const [platformStats, setPlatformStats] = useState(null);
  const [agentHealth, setAgentHealth] = useState({});
  const [otherPage, setOtherPage] = useState(0);
  
  // Loading States
  const [loading, setLoading] = useState(true);
  const [profileLoading, setProfileLoading] = useState(false);
  const [productsLoading, setProductsLoading] = useState(false);
  const [consultationLoading, setConsultationLoading] = useState(false);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [subscriptionLoading, setSubscriptionLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  
  // Backend States
  const [actor, setActor] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const BRIDGE_ENDPOINT = 'http://127.0.0.1:8080';
  
  // Error States
  const [error, setError] = useState(null);

  // Initialize ICP agent
  useEffect(() => {
    const initBackend = async () => {
      try {
        setLoading(true);
        
        // Check bridge health
        const bridgeHealthResponse = await fetch(`${BRIDGE_ENDPOINT}/api/health`);
        if (!bridgeHealthResponse.ok) {
          throw new Error('Bridge not available');
        }
        const bridgeHealth = await bridgeHealthResponse.json();
        setBackendConnected(bridgeHealth.ic_backend_connected);

        // Initialize ICP agent only for direct canister calls
        const agent = new HttpAgent({ host: HOST });
        if (process.env.DFX_NETWORK !== 'ic') {
          await agent.fetchRootKey();
        }
        const backendActor = Actor.createActor(idlFactory, {
          agent,
          canisterId: CANISTER_ID,
        });
        setActor(backendActor);

        // Load initial data through bridge
        await loadInitialData();
        await checkAgentHealth();
        
      } catch (error) {
        console.error('Failed to initialize backend:', error);
        setError('Failed to connect to backend. Some features may not work.');
        setBackendConnected(false);
      } finally {
        setLoading(false);
      }
    };

    initBackend();
  }, []);

  // Load user data when wallet connected
  useEffect(() => {
    if (walletConnected && userWallet && actor) {
      loadUserData();
    }
  }, [walletConnected, userWallet, actor]);

  // Search effect with debouncing
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch(searchQuery);
      } else {
        setShowSearchResults(false);
      }
    }, 500);

    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);

  const checkAgentHealth = async () => {
    const healthChecks = {};
    
    for (const [name, url] of Object.entries(AGENT_ENDPOINTS)) {
      try {
        const response = await fetch(`${url}/health`, { timeout: 5000 });
        if (response.ok) {
          const health = await response.json();
          healthChecks[name] = { status: 'connected', ...health };
        } else {
          healthChecks[name] = { status: 'error' };
        }
      } catch (error) {
        healthChecks[name] = { status: 'disconnected' };
      }
    }
    
    setAgentHealth(healthChecks);
  };

  const loadInitialData = async (backendActor) => {
    try {
      setProductsLoading(true);
      
      // Load products through bridge
      const productsResponse = await fetch(`${BRIDGE_ENDPOINT}/api/ic/products`, { method: 'GET' });
      if (productsResponse.ok) {
        const { products } = await productsResponse.json();
        setProducts(products);
        setOtherProducts(products.slice(0, 8));
      }

      // Load platform stats through bridge
      const statsResponse = await fetch(`${BRIDGE_ENDPOINT}/api/ic/platform_stats`, { method: 'GET' });
      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setPlatformStats(stats);
      }
      
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setProductsLoading(false);
    }
  };

  const loadUserData = async () => {
    if (!userWallet) return;

    try {
      setProfileLoading(true);
      
      // Load user profile through bridge
      const profileResponse = await fetch(`${BRIDGE_ENDPOINT}/api/ic/user/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_data: { user_id: userWallet } })
      });
      if (profileResponse.ok) {
        const { user_id, success } = await profileResponse.json();
        if (success) {
          const userProfile = await (await fetch(`${BRIDGE_ENDPOINT}/api/ic/user/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userWallet })
          })).json();
          setUserProfile(userProfile);
          setTempUsername(userProfile.user_id);
          setConsultationCompleted(userProfile.consultation_completed);
          if (userProfile.did) {
            setUserDID(userProfile.did);
          }
        }
      }

      // Load user-specific data
      await Promise.all([
        loadUserRecommendations(),
        loadUserOrders(),
        sendAnalyticsEvent('user_profile_loaded', {})
      ]);
    } catch (error) {
      console.error('Error loading user data:', error);
      setError('Failed to load user data');
    } finally {
      setProfileLoading(false);
    }
  };

  const createNewUserProfile = async () => {
    if (!actor || !userWallet) return;

    try {
      const now = BigInt(Date.now() * 1000000);
      
      // Complete UserProfile with all required fields
      const newProfile = {
        user_id: userWallet,
        wallet_address: [userWallet], // Optional field as array
        did: [], // Optional field as array
        verification_status: { Unverified: null },
        stake_info: [], // Optional as array
        preferences: [], // Vec<(Text, Text)> for HashMap representation
        consultation_completed: false,
        ai_consent: true,
        data_monetization_consent: true, // REQUIRED FIELD - CRITICAL FIX
        reputation_score: 0.0,
        total_transactions: 0,
        created_at: now,
        last_active: now,
      };

      const result = await actor.create_user_profile(updatedProfile);
      
      if (result.Ok) {
        setUserProfile(updatedProfile);
        setTempUsername(updatedProfile.user_id);
        alert('Profile updated successfully!');
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      setError('Failed to save profile. Please try again.');
    } finally {
      setProfileLoading(false);
    }
  };

  const loadProductReviews = async (productId) => {
    if (!actor) return;
    
    try {
      const reviews = await actor.get_product_reviews(productId);
      setProductReviews(prev => ({
        ...prev,
        [productId]: reviews
      }));
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
  };

  const submitReview = async (productId, reviewData) => {
    if (!actor || !userWallet) return;
    
    try {
      // Get user's verification tier for review
      const userStake = userProfile?.stake_info?.[0]?.amount || 0n;
      const userTier = userProfile?.stake_info?.[0]?.tier || { BasicReviewer: null };
      
      const review = {
        review_id: `review_${Date.now()}_${productId}`,
        reviewer_id: userWallet,
        reviewer_stake: userStake,
        reviewer_tier: userTier,
        product_id: productId,
        overall_rating: reviewData.overall_rating,
        longevity_rating: reviewData.longevity_rating || reviewData.overall_rating,
        sillage_rating: reviewData.sillage_rating || reviewData.overall_rating,
        projection_rating: reviewData.projection_rating || reviewData.overall_rating,
        versatility_rating: reviewData.versatility_rating || reviewData.overall_rating,
        value_rating: reviewData.value_rating || reviewData.overall_rating,
        detailed_review: reviewData.detailed_review,
        verified_purchase: true,
        skin_type: reviewData.skin_type || 'normal',
        age_group: reviewData.age_group || '25-35',
        wear_occasion: reviewData.wear_occasion || 'daily',
        season_tested: reviewData.season_tested || 'spring',
        helpful_votes: 0,
        reported_count: 0,
        ai_validated: false,
        review_date: BigInt(Date.now() * 1000000),
        last_updated: BigInt(Date.now() * 1000000),
      };
      
      const result = await actor.create_verified_review(review);
      
      if (result.Ok) {
        await loadProductReviews(productId);
        alert('Review submitted successfully!');
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      setError('Failed to submit review. Please try again.');
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (Number(item.price_idr) * item.quantity), 0);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(price);
  };

  const openProductDetail = async (product) => {
    setSelectedProduct(product);
    await loadProductReviews(product.id);
    setShowProductDetail(true);
  };

  const getVerificationBadgeText = (status) => {
    if (!status) return null;
    if (status.Basic) return 'Basic';
    if (status.Premium) return 'Premium';
    if (status.Elite) return 'Elite';
    return null;
  };

  const getStakeRewards = (stakeInfo) => {
    if (!stakeInfo || stakeInfo.length === 0) return null;
    
    const stake = stakeInfo[0];
    const tierRates = {
      BasicReviewer: 0.06,
      PremiumReviewer: 0.075,
      EliteReviewer: 0.09,
      BasicSeller: 0.06,
      PremiumSeller: 0.075,
      EliteSeller: 0.09,
    };
    
    const tierName = Object.keys(stake.tier)[0];
    const rate = tierRates[tierName] || 0.06;
    const annualReward = Number(stake.amount) * rate;
    
    return {
      amount: Number(stake.amount),
      annualReward: annualReward,
      totalRewards: Number(stake.total_rewards),
      rate: rate * 100,
    };
  };

  const saveUserProfile = async () => {
    if (!actor || !userProfile || !tempUsername.trim()) return;
    
    try {
      setProfileLoading(true);
      
      // Update complete profile (not just username)
      const updatedProfile = {
        ...userProfile,
        user_id: tempUsername.trim(),
        last_active: BigInt(Date.now() * 1000000),
      };
      
      const result = await actor.create_
      user_profile(newProfile);
      
      if (result.Ok) {
        setUserProfile(newProfile);
        setTempUsername(newProfile.user_id);
        console.log('User profile created successfully');
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error('Error creating user profile:', error);
      setError(`Failed to create user profile: ${error.message}`);
    }
  };

  const loadUserRecommendations = async () => {
    if (!userWallet) return;

    try {
      setRecommendationsLoading(true);
      const response = await fetch(`${BRIDGE_ENDPOINT}/api/ic/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userWallet })
      });
      if (response.ok) {
        const { recommendations } = await response.json();
        setAiRecommendations(recommendations);
        setTopRecommendations(recommendations);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const loadUserOrders = async () => {
    if (!userWallet) return;

    try {
      setOrdersLoading(true);
      const response = await fetch(`${BRIDGE_ENDPOINT}/api/ic/transactions/get`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userWallet })
      });
      if (response.ok) {
        const { transactions } = await response.json();
        setOrders(transactions);
      }
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setOrdersLoading(false);
    }
  };

  const sendAnalyticsEvent = async (eventType, data) => {
    try {
      await fetch(`${AGENT_ENDPOINTS.analytics}/analytics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userWallet,
          event_type: eventType,
          ...data
        })
      });
    } catch (error) {
      console.log('Analytics event failed:', error);
    }
  };

  const performSearch = async (query) => {
    try {
      setSearchLoading(true);
      const searchParams = {
        fragrance_family: query.includes('fresh') ? 'Fresh' : query.includes('floral') ? 'Floral' : null,
        budget_min: query.includes('budget') ? 0 : query.includes('premium') ? 200000 : null,
        budget_max: query.includes('budget') ? 50000 : query.includes('premium') ? 500000 : null,
        occasion: query.includes('daily') ? 'Daily Work' : query.includes('evening') ? 'Evening Date' : null,
        season: query.includes('spring') ? 'Spring' : query.includes('summer') ? 'Summer' : null,
        longevity: query.includes('long lasting') ? { Good: null } : null,
        verified_only: query.includes('verified') ? true : null
      };
      
      const response = await fetch(`${BRIDGE_ENDPOINT}/api/ic/products/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ search_params: searchParams, user_id: userWallet || 'anonymous' })
      });
      
      if (response.ok) {
        const { product } = await response.json();
        setSearchResults(product);
        setShowSearchResults(true);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError('Search failed. Please try again.');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleWalletConnect = async () => {
    const principal = await connectWallet();
    if (principal) {
      setWalletConnected(true);
      setUserWallet(principal);
      console.log('Connected to wallet:', principal);
    }
  };

  const startAIConsultation = async () => {
    if (!walletConnected) {
      setError('Please connect your wallet first');
      return;
    }
    
    try {
      setConsultationLoading(true);
      const userId = userWallet;
      
      // Start consultation with Coordinator Agent (fixed path)
      const coordinatorResponse = await fetch(`${AGENT_ENDPOINTS.coordinator}/consultation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      
      if (coordinatorResponse.ok) {
        const result = await coordinatorResponse.json();
        setSessionId(result.session_id);
        
        // Start consultation with Consultation Agent
        const consultationResponse = await fetch(`${AGENT_ENDPOINTS.consultation}/consultation/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            session_id: result.session_id
          })
        });
        
        if (consultationResponse.ok) {
          setShowAIConsultation(true);
        } else {
          throw new Error('Failed to start consultation');
        }
      } else {
        throw new Error('Failed to initialize consultation');
      }
    } catch (error) {
      console.error('Error starting consultation:', error);
      setError('Failed to start AI consultation. Please try again.');
    } finally {
      setConsultationLoading(false);
    }
  };

  const completeConsultation = async (consultationData) => {
    if (!actor || !userWallet) return;

    try {
      setConsultationLoading(true);
      
      // Send consultation data through bridge
      const response = await fetch(`${BRIDGE_ENDPOINT}/api/ic/identity/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userWallet,
          fragrance_identity: {
            personality_type: consultationData.personality_type,
            lifestyle: consultationData.lifestyle,
            preferred_families: consultationData.fragrance_families,
            occasion_preferences: consultationData.occasions,
            season_preferences: consultationData.seasons,
            sensitivity_level: consultationData.sensitivity,
            budget_range: { [consultationData.budget_range]: null },
            scent_journey: consultationData.scent_journey
          }
        })
      });

      if (response.ok) {
        const { success, identity } = await response.json();
        if (success) {
          setUserDID(identity.identity_hash);
          setConsultationCompleted(true);
          setConsultationData(consultationData);
          await loadUserRecommendations();
          await sendAnalyticsEvent('consultation_completed', consultationData);
        }
      }
    } catch (error) {
      console.error('Error completing consultation:', error);
      setError('Failed to complete AI consultation');
    } finally {
      setConsultationLoading(false);
      setShowAIConsultation(false);
    }
  };

  const generateAIRecommendations = async () => {
    if (!actor || !userWallet) return;
    
    try {
      setRecommendationsLoading(true);
      
      // Generate recommendations via backend
      const result = await actor.generate_ai_recommendations(userWallet);
      
      if (result.Ok) {
        const recommendations = result.Ok;
        
        // Sort by match_score descending and organize into sections
        const sortedRecs = recommendations.sort((a, b) => b.match_score - a.match_score);
        setAiRecommendations(sortedRecs);
        setTopRecommendations(sortedRecs.slice(0, 6));
        
        // Get product details for recommendations
        const recProductIds = sortedRecs.map(r => r.product_id);
        const recProducts = products.filter(p => recProductIds.includes(p.id));
        setPersonalizedProducts(recProducts.slice(6, 18));
        
        // Load personality-based products
        if (consultationData?.personality_type) {
          const personalityProds = await actor.search_products_by_personality(consultationData.personality_type);
          // Mix with recommendations
          setPersonalizedProducts(prev => [...prev, ...personalityProds.slice(0, 6)]);
        }
        
      } else {
        throw new Error(result.Err);
      }
      
    } catch (error) {
      console.error('Error generating recommendations:', error);
      setError('Failed to generate recommendations. Please try again.');
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const refreshOtherProducts = async () => {
    if (!actor) return;
    
    try {
      setRefreshing(true);
      const pageSize = 8;
      const start = otherPage * pageSize;
      const end = start + pageSize;
      
      // Use pagination instead of shuffle
      if (aiRecommendations.length > 18) {
        // Use remaining recommendations
        const remaining = aiRecommendations.slice(18 + start, 18 + end);
        const remainingProducts = products.filter(p => 
          remaining.some(r => r.product_id === p.id)
        );
        setOtherProducts(remainingProducts);
      } else {
        // Fallback to all products with pagination
        const allProducts = await actor.get_products();
        setOtherProducts(allProducts.slice(start, end));
      }
      
      setOtherPage(prev => prev + 1);
      
    } catch (error) {
      console.error('Error refreshing products:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    
    // Send analytics event
    sendAnalyticsEvent('product_added_to_cart', { product_id: product.id });
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateCartQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(cart.map(item => 
      item.id === productId 
        ? { ...item, quantity }
        : item
    ));
  };

  const calculateTransactionTier = (amount) => {
    if (amount < 100000) return { Budget: null };
    if (amount < 500000) return { Standard: null };
    if (amount < 1000000) return { Premium: null };
    return { Luxury: null };
  };

  const calculateCommissionRate = (amount) => {
    if (amount < 100000) return 0.015; // 1.5%
    if (amount < 500000) return 0.02; // 2%
    if (amount < 1000000) return 0.025; // 2.5%
    return 0.03; // 3%
  };

  const purchaseProduct = async (product, quantity = 1) => {
    if (!actor || !userWallet) {
      setError('Please connect your wallet first');
      return;
    }
    
    try {
      setCheckoutLoading(true);
      
      // Check inventory via agent
      const inventoryCheck = await fetch(`${AGENT_ENDPOINTS.inventory}/inventory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userWallet,
          product_ids: [product.id],
          action: 'check_availability'
        })
      });
      
      if (!inventoryCheck.ok) {
        throw new Error('Product not available');
      }
      
      const totalAmount = Number(product.price_idr) * quantity;
      const commissionRate = calculateCommissionRate(totalAmount);
      const commissionAmount = Math.floor(totalAmount * commissionRate);
      
      // Create complete transaction matching backend structure
      const transaction = {
        transaction_id: `tx_${Date.now()}_${product.id}`,
        buyer_id: userWallet,
        seller_id: product.seller_id,
        product_id: product.id,
        quantity: quantity,
        unit_price_idr: BigInt(product.price_idr),
        total_amount_idr: BigInt(totalAmount),
        commission_rate: commissionRate,
        commission_amount: BigInt(commissionAmount),
        transaction_tier: calculateTransactionTier(totalAmount),
        status: { Completed: null },
        escrow_locked: false,
        payment_method: 'Plug Wallet',
        shipping_address: 'To be provided by user',
        created_at: BigInt(Date.now() * 1000000),
        completed_at: [BigInt(Date.now() * 1000000)],
      };
      
      const result = await actor.create_transaction(transaction);
      
      if (result.Ok) {
        // Remove from cart if exists
        removeFromCart(product.id);
        
        // Reload orders and update profile transaction count
        await loadUserOrders();
        
        // Send analytics
        await sendAnalyticsEvent('checkout_success', {
          product_id: product.id,
          amount: totalAmount
        });
        
        alert('Purchase successful! Check your order history.');
      } else {
        throw new Error(result.Err);
      }
      
    } catch (error) {
      console.error('Error purchasing product:', error);
      setError('Failed to complete purchase. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const checkout = async () => {
    if (!actor || !userWallet || cart.length === 0) return;

    try {
      setCheckoutLoading(true);
      
      const now = BigInt(Date.now() * 1000000);
      for (const item of cart) {
        const transaction = {
          transaction_id: `tx_${Date.now()}_${Math.random().toString(36).slice(2)}`,
          buyer_id: userWallet,
          seller_id: item.seller_id,
          product_id: item.id,
          quantity: item.quantity,
          unit_price_idr: item.price_idr,
          total_amount_idr: item.price_idr * item.quantity,
          commission_rate: 0.05,
          commission_amount: Math.floor(item.price_idr * item.quantity * 0.05),
          transaction_tier: { Standard: null },
          status: { Pending: null },
          escrow_locked: true,
          payment_method: 'ICP',
          shipping_address: 'TBD',
          created_at: now,
          completed_at: [],
        };

        const response = await fetch(`${BRIDGE_ENDPOINT}/api/ic/transactions/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ transaction })
        });

        if (response.ok) {
          const { transaction_id } = await response.json();
          await processPayment(BigInt(transaction.total_amount_idr + transaction.commission_amount));
          setOrders(prev => [...prev, transaction]);
        }
      }

      setCart([]);
      setShowCart(false);
      await sendAnalyticsEvent('checkout_completed', { cart });
    } catch (error) {
      console.error('Checkout failed:', error);
      setError('Checkout failed. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const subscribeToTier = async (tier) => {
    if (!actor || !userWallet) {
      setError('Please connect your wallet first');
      return;
    }
    
    try {
      setSubscriptionLoading(true);
      setPaymentLoading(true);
      
      // Define tier amounts and types matching backend exactly
      const tierMap = {
        'Basic Reviewer': { amount: 300000n, type: { BasicReviewer: null } },
        'Premium Reviewer': { amount: 950000n, type: { PremiumReviewer: null } },
        'Elite Reviewer': { amount: 1900000n, type: { EliteReviewer: null } },
        'Basic Seller': { amount: 500000n, type: { BasicSeller: null } },
        'Premium Seller': { amount: 1500000n, type: { PremiumSeller: null } },
        'Elite Seller': { amount: 3000000n, type: { EliteSeller: null } }
      };
      
      const tierInfo = tierMap[tier];
      if (!tierInfo) {
        throw new Error('Invalid tier selected');
      }
      
      // Process real payment via Plug Wallet
      try {
        const paymentResult = await processPayment(Number(tierInfo.amount), MAIN_WALLET_ADDRESS);
        console.log('Payment successful:', paymentResult);
      } catch (paymentError) {
        throw new Error(`Payment failed: ${paymentError.message}`);
      }
      
      // Stake for verification in backend
      const result = await actor.stake_for_verification(userWallet, tierInfo.amount, tierInfo.type);
      
      if (result.Ok) {
        // Reload user profile to get updated verification status
        const updatedProfile = await actor.get_user_profile(userWallet);
        if (updatedProfile.length > 0) {
          setUserProfile(updatedProfile[0]);
        }
        
        setShowSubscriptionModal(false);
        alert(`Successfully subscribed to ${tier} tier! Payment processed.`);
        
        // Send analytics
        await sendAnalyticsEvent('tier_subscription', {
          tier: tier,
          amount: Number(tierInfo.amount)
        });
      } else {
        throw new Error(result.Err);
      }
      
    } catch (error) {
      console.error('Error subscribing to tier:', error);
      setError(`Failed to subscribe to tier: ${error.message}`);
    } finally {
      setSubscriptionLoading(false);
      setPaymentLoading(false);
    }
  };

  const claimStakeRewards = async () => {
    if (!actor || !userWallet) return;
    
    try {
      setPaymentLoading(true);
      const result = await actor.process_stake_rewards();
      
      if (result.Ok) {
        // Reload user profile to see updated stake info
        const updatedProfile = await actor.get_user_profile(userWallet);
        if (updatedProfile.length > 0) {
          setUserProfile(updatedProfile[0]);
        }
        
        alert('Stake rewards processed successfully!');
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error('Error claiming rewards:', error);
      setError('Failed to claim rewards. Please try again.');
    } finally {
      setPaymentLoading(false);
    }
  };
  
  // Component helper functions
  const ErrorToast = () => error && (
    <div className="error-toast">
      <span>{error}</span>
      <button onClick={() => setError(null)}>
        <CustomIcons.Close />
      </button>
    </div>
  );

  const LoadingSpinner = () => (
    <div className="loading-spinner">
      <div className="spinner"></div>
    </div>
  );

  const ProductCard = ({ product, isRecommended = false, showAIBadge = false, matchScore = null }) => (
    <div className={`product-card ${isRecommended ? 'recommended' : ''}`}>
      <div className="product-image" onClick={() => openProductDetail(product)}>
        <img src={resolveImageUrl(product.image_urls?.[0])} alt={product.name} />
        
        {/* Badges */}
        {showAIBadge && (
          <div className="ai-badge">
            <CustomIcons.Robot />
            <span>AI Pick</span>
            {matchScore && <span className="match-score">{Math.round(matchScore * 100)}%</span>}
          </div>
        )}
        {product.verified && (
          <div className="verified-badge">
            <CustomIcons.Star />
            <span>Verified</span>
          </div>
        )}
        {product.halal_certified && (
          <div className="halal-badge">
            <span>Halal</span>
          </div>
        )}
      </div>
      
      <div className="product-info">
        <div className="product-brand">{product.brand}</div>
        <h3 className="product-name" onClick={() => openProductDetail(product)}>{product.name}</h3>
        <div className="product-family">{product.fragrance_family}</div>
        <div className="product-notes">
          <div className="notes-section">
            <span className="notes-label">Top:</span>
            <span className="notes-list">{product.top_notes?.slice(0, 2).join(', ') || 'N/A'}</span>
          </div>
        </div>
        <div className="product-price">{formatPrice(Number(product.price_idr))}</div>
        <div className="product-stock">Stock: {Number(product.stock)}</div>
        
        <div className="product-actions">
          <button 
            className="add-to-cart-btn"
            onClick={() => addToCart(product)}
            disabled={Number(product.stock) === 0}
          >
            <CustomIcons.Plus />
            <span>Add to Cart</span>
          </button>
          <button 
            className="buy-now-btn"
            onClick={() => purchaseProduct(product)}
            disabled={checkoutLoading || Number(product.stock) === 0}
          >
            {checkoutLoading ? <LoadingSpinner /> : 'Buy Now'}
          </button>
        </div>
      </div>
    </div>
  );

  const ProductSection = ({ 
    title, 
    products, 
    isRecommended = false, 
    showAIBadge = false, 
    icon: Icon, 
    showRefresh = false, 
    isLoading = false,
    recommendations = []
  }) => (
    <div className="product-section">
      <div className="section-header">
        <h2 className="section-title">
          {Icon && <Icon />}
          {title}
          {isLoading && <LoadingSpinner />}
        </h2>
        {showRefresh && (
          <button 
            className="refresh-btn" 
            onClick={refreshOtherProducts}
            disabled={refreshing}
          >
            <CustomIcons.Refresh />
            <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        )}
      </div>
      
      <div className="products-container">
        <div className="products-scroll">
          {isLoading ? (
            <div className="loading-products">
              <LoadingSpinner />
              <p>Loading products...</p>
            </div>
          ) : products.length > 0 ? products.map((product, index) => {
            const recommendation = recommendations.find(r => r.product_id === product.id);
            return (
              <ProductCard 
                key={product.id} 
                product={product} 
                isRecommended={isRecommended}
                showAIBadge={showAIBadge}
                matchScore={recommendation?.match_score}
              />
            );
          }) : (
            <div className="empty-products">
              <p>No products available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Search Bar Component
  const SearchBar = () => (
    <div className="search-container">
      <div className="search-bar">
        <CustomIcons.Search />
        <input
          type="text"
          placeholder="Search fragrances, brands, or families..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        {searchLoading && <LoadingSpinner />}
      </div>
    </div>
  );

  // Product Detail Modal
  const ProductDetailModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showProductDetail ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>{selectedProduct?.name}</h2>
          <button className="close-btn" onClick={() => setShowProductDetail(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {selectedProduct && (
            <div className="product-detail-content">
              <div className="product-detail-image">
                <img src={resolveImageUrl(selectedProduct.image_urls?.[0])} alt={selectedProduct.name} />
              </div>
              <div className="product-detail-info">
                <h3>{selectedProduct.brand}</h3>
                <h2>{selectedProduct.name}</h2>
                <div className="product-price-large">{formatPrice(Number(selectedProduct.price_idr))}</div>
                <div className="product-details">
                  <p><strong>Fragrance Family:</strong> {selectedProduct.fragrance_family}</p>
                  <p><strong>Top Notes:</strong> {selectedProduct.top_notes?.join(', ')}</p>
                  <p><strong>Middle Notes:</strong> {selectedProduct.middle_notes?.join(', ')}</p>
                  <p><strong>Base Notes:</strong> {selectedProduct.base_notes?.join(', ')}</p>
                  <p><strong>Occasions:</strong> {selectedProduct.occasion?.join(', ')}</p>
                  <p><strong>Description:</strong> {selectedProduct.description}</p>
                  <p><strong>Stock:</strong> {Number(selectedProduct.stock)}</p>
                </div>
                <div className="product-actions-large">
                  <button 
                    className="add-to-cart-btn-large"
                    onClick={() => addToCart(selectedProduct)}
                    disabled={Number(selectedProduct.stock) === 0}
                  >
                    <CustomIcons.Plus />
                    Add to Cart
                  </button>
                  <button 
                    className="buy-now-btn-large"
                    onClick={() => purchaseProduct(selectedProduct)}
                    disabled={checkoutLoading || Number(selectedProduct.stock) === 0}
                  >
                    {checkoutLoading ? <LoadingSpinner /> : 'Buy Now'}
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Reviews Section */}
          <div className="reviews-section">
            <h3>Reviews</h3>
            {orders.some(order => order.product?.id === selectedProduct?.id && order.canReview) ? (
              <div className="review-form">
                <textarea 
                  placeholder="Write your detailed review here..." 
                  rows="4"
                  id="review-text"
                ></textarea>
                <div className="rating-inputs">
                  <div className="rating-input">
                    <span>Overall Rating: </span>
                    <div className="stars-input" id="overall-rating">
                      {[1,2,3,4,5].map(star => (
                        <CustomIcons.Star key={star} className="star-input" data-rating={star} />
                      ))}
                    </div>
                  </div>
                </div>
                <button 
                  className="submit-review-btn"
                  onClick={() => {
                    const reviewText = document.getElementById('review-text').value;
                    const rating = 5; // Default for demo - would implement star click handling
                    
                    if (reviewText.trim()) {
                      submitReview(selectedProduct.id, {
                        overall_rating: rating,
                        detailed_review: reviewText,
                        skin_type: 'normal',
                        age_group: '25-35',
                        wear_occasion: 'daily',
                        season_tested: 'spring'
                      });
                    } else {
                      alert('Please write a review first');
                    }
                  }}
                >
                  Submit Review
                </button>
              </div>
            ) : (
              <p>You can only review products you've purchased.</p>
            )}
            
            <div className="existing-reviews">
              {productReviews[selectedProduct?.id]?.map(review => (
                <div key={review.review_id} className="review-item">
                  <div className="reviewer-info">
                    <strong>{review.reviewer_id.slice(0, 8)}...</strong>
                    <div className="rating">
                      {[1,2,3,4,5].map(star => (
                        <CustomIcons.Star 
                          key={star} 
                          className={`star ${star <= review.overall_rating ? 'filled' : ''}`} 
                        />
                      ))}
                    </div>
                    {review.verified_purchase && <span className="verified-purchase">✓ Verified Purchase</span>}
                  </div>
                  <p>{review.detailed_review}</p>
                  <div className="review-metadata">
                    <span>Skin: {review.skin_type}</span>
                    <span>Season: {review.season_tested}</span>
                    <span>Occasion: {review.wear_occasion}</span>
                  </div>
                  <div className="review-date">
                    {new Date(Number(review.review_date) / 1000000).toLocaleDateString()}
                  </div>
                </div>
              )) || (
                <div className="no-reviews">
                  <p>No reviews yet. Be the first to review this product!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Order History Modal
  const OrderHistoryModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showOrderHistory ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>
            <CustomIcons.Orders />
            Order History
          </h2>
          <button className="close-btn" onClick={() => setShowOrderHistory(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {ordersLoading ? (
            <div className="loading-section">
              <LoadingSpinner />
              <p>Loading your orders...</p>
            </div>
          ) : orders.length === 0 ? (
            <div className="empty-orders">
              <CustomIcons.Orders />
              <p>No orders yet</p>
              <p>Start shopping to see your orders here</p>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map(order => (
                <div key={order.id} className="order-item">
                  <img 
                    src={resolveImageUrl(order.product?.image_urls?.[0])} 
                    alt={order.product?.name} 
                  />
                  <div className="order-info">
                    <h4>{order.product?.name}</h4>
                    <p>{order.product?.brand}</p>
                    <p>Quantity: {order.quantity}</p>
                    <p className="order-total">{formatPrice(order.total)}</p>
                    <p className="order-date">{new Date(order.date).toLocaleDateString()}</p>
                  </div>
                  <div className="order-status">
                    <span className={`status-badge ${order.status}`}>{order.status}</span>
                    {order.canReview && (
                      <button 
                        className="review-btn"
                        onClick={() => {
                          setSelectedProduct(order.product);
                          setShowOrderHistory(false);
                          setShowProductDetail(true);
                        }}
                      >
                        Write Review
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Subscription Modal
  const SubscriptionModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showSubscriptionModal ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>
            <CustomIcons.Crown />
            Proof of Stake Verification
          </h2>
          <button className="close-btn" onClick={() => setShowSubscriptionModal(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          <div className="subscription-intro">
            <p>Join our Proof of Stake verification system to gain trust and unlock premium features.</p>
            <p>All payments are processed through your Plug Wallet and flow to our main treasury.</p>
          </div>
          
          <div className="payment-info-header">
            <div className="treasury-address">
              <strong>Treasury Address:</strong>
              <code>{MAIN_WALLET_ADDRESS}</code>
            </div>
          </div>
          
          <div className="subscription-tiers">
            <div className="tier-section">
              <h3>Reviewer Tiers</h3>
              <div className="tier-cards">
                {[
                  { name: 'Basic Reviewer', price: 300000, rate: 6, features: ['Write verified reviews', 'Basic trust badge', 'Community access'] },
                  { name: 'Premium Reviewer', price: 950000, rate: 7.5, features: ['All Basic features', 'Premium trust badge', 'Higher review priority', 'Early access to products'] },
                  { name: 'Elite Reviewer', price: 1900000, rate: 9, features: ['All Premium features', 'Elite trust badge', 'Influence on platform', 'Exclusive events'] }
                ].map((tier, index) => (
                  <div key={tier.name} className={`tier-card ${index === 1 ? 'premium' : index === 2 ? 'elite' : ''}`}>
                    <h4>{tier.name}</h4>
                    <div className="tier-price">{formatPrice(tier.price)}</div>
                    <div className="tier-return">{tier.rate}% Annual Return</div>
                    <ul>
                      {tier.features.map((feature, i) => (
                        <li key={i}>{feature}</li>
                      ))}
                    </ul>
                    <button 
                      className="tier-btn"
                      onClick={() => subscribeToTier(tier.name)}
                      disabled={subscriptionLoading || paymentLoading}
                    >
                      {(subscriptionLoading || paymentLoading) ? <LoadingSpinner /> : 'Subscribe & Pay'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="tier-section">
              <h3>Seller Tiers</h3>
              <div className="tier-cards">
                {[
                  { name: 'Basic Seller', price: 500000, rate: 6, features: ['Sell products', 'Basic analytics', 'Standard commission'] },
                  { name: 'Premium Seller', price: 1500000, rate: 7.5, features: ['All Basic features', 'Advanced analytics', 'Reduced commission', 'Priority support'] },
                  { name: 'Elite Seller', price: 3000000, rate: 9, features: ['All Premium features', 'Lowest commission', 'Featured placement', 'White-label options'] }
                ].map((tier, index) => (
                  <div key={tier.name} className={`tier-card ${index === 1 ? 'premium' : index === 2 ? 'elite' : ''}`}>
                    <h4>{tier.name}</h4>
                    <div className="tier-price">{formatPrice(tier.price)}</div>
                    <div className="tier-return">{tier.rate}% Annual Return</div>
                    <ul>
                      {tier.features.map((feature, i) => (
                        <li key={i}>{feature}</li>
                      ))}
                    </ul>
                    <button 
                      className="tier-btn"
                      onClick={() => subscribeToTier(tier.name)}
                      disabled={subscriptionLoading || paymentLoading}
                    >
                      {(subscriptionLoading || paymentLoading) ? <LoadingSpinner /> : 'Subscribe & Pay'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="payment-disclaimer">
            <p><strong>Important:</strong> All stake amounts are processed as real payments through Plug Wallet.</p>
            <p>Your stake will be locked in the smart contract and earn the specified annual returns.</p>
            <p>Rewards can be claimed periodically through the platform.</p>
          </div>
        </div>
      </div>
    </div>
  );

  // User Settings Modal
  const UserSettingsModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showUserSettings ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2><CustomIcons.Settings /> User Settings</h2>
          <button className="close-btn" onClick={() => setShowUserSettings(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {/* Profile Section */}
          {walletConnected && userProfile && (
            <div className="settings-section">
              <h3>Profile</h3>
              <div className="profile-edit">
                <div className="profile-image-edit">
                  <img 
                    src={'./src/log1_.png'} 
                    alt="Profile" 
                    className="profile-image"
                  />
                  <button className="edit-image-btn">
                    <CustomIcons.Settings />
                  </button>
                </div>
                <div className="profile-info-edit">
                  <label>User ID:</label>
                  <input 
                    type="text"
                    value={tempUsername}
                    onChange={(e) => setTempUsername(e.target.value)}
                    placeholder="Enter user ID"
                  />
                  <button 
                    className="save-profile-btn" 
                    onClick={saveUserProfile}
                    disabled={profileLoading}
                  >
                    {profileLoading ? <LoadingSpinner /> : 'Save Profile'}
                  </button>
                  
                  {/* Verification Status */}
                  {getVerificationBadgeText(userProfile.verification_status) && (
                    <div className="verification-badge">
                      <CustomIcons.Crown />
                      <span>{getVerificationBadgeText(userProfile.verification_status)} Verified</span>
                    </div>
                  )}
                  
                  {/* Stake Information */}
                  {userProfile.stake_info && userProfile.stake_info.length > 0 && (
                    <div className="stake-info">
                      <h4>Stake Information</h4>
                      {(() => {
                        const stakeRewards = getStakeRewards(userProfile.stake_info);
                        return stakeRewards && (
                          <div className="stake-details">
                            <p>Staked: {formatPrice(stakeRewards.amount)}</p>
                            <p>Annual Rate: {stakeRewards.rate}%</p>
                            <p>Total Rewards: {formatPrice(stakeRewards.totalRewards)}</p>
                            <button 
                              className="claim-rewards-btn"
                              onClick={claimStakeRewards}
                              disabled={paymentLoading}
                            >
                              {paymentLoading ? <LoadingSpinner /> : 'Claim Rewards'}
                            </button>
                          </div>
                        );
                      })()}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Connection Status */}
          <div className="settings-section">
            <h3>Connection Status</h3>
            <div className={`connection-status ${backendConnected ? 'connected' : 'disconnected'}`}>
              <div className="status-indicator"></div>
              <span>{backendConnected ? 'Connected to ICP Backend' : 'Backend Disconnected'}</span>
            </div>
            <div className={`connection-status ${walletConnected ? 'connected' : 'disconnected'}`}>
              <div className="status-indicator"></div>
              <span>{walletConnected ? `Wallet Connected: ${userWallet?.slice(0, 10)}...` : 'Wallet Disconnected'}</span>
            </div>
            
            {/* Agent Health Status */}
            <div className="agent-health">
              <h4>AI Agents Status</h4>
              {Object.entries(agentHealth).map(([name, health]) => (
                <div key={name} className={`connection-status ${health.status === 'connected' ? 'connected' : 'disconnected'}`}>
                  <div className="status-indicator"></div>
                  <span>{name}: {health.status}</span>
                </div>
              ))}
              <button className="refresh-health-btn" onClick={checkAgentHealth}>
                <CustomIcons.Refresh /> Check Agent Health
              </button>
            </div>
          </div>
          
          {/* Wallet Connection */}
          <div className="settings-section">
            <h3>Wallet</h3>
            {!walletConnected ? (
              <button className="setting-btn" onClick={handleWalletConnect}>
                <CustomIcons.Wallet /> Connect Plug Wallet
              </button>
            ) : (
              <div className="setting-item">
                <div className="user-avatar">
                  <CustomIcons.Wallet />
                </div>
                <div className="user-info">
                  <div className="user-name">Plug Wallet Connected</div>
                  <div className="user-status">{userWallet?.slice(0, 20)}...</div>
                  {userDID && <div className="user-did">DID: {userDID}</div>}
                </div>
              </div>
            )}
          </div>

          {/* AI Consultation */}
          <div className="settings-section">
            <h3>AI Consultation</h3>
            {!consultationCompleted ? (
              <button 
                className="setting-btn" 
                onClick={startAIConsultation}
                disabled={!walletConnected || consultationLoading}
              >
                <CustomIcons.Robot /> 
                {consultationLoading ? <LoadingSpinner /> : 'Start AI Consultation & Create Identity'}
              </button>
            ) : (
              <div className="setting-item">
                <div className="user-avatar">
                  <CustomIcons.Robot />
                </div>
                <div className="user-info">
                  <div className="user-name">Consultation Completed</div>
                  <div className="user-status">Identity Created: {userDID}</div>
                  <button 
                    className="regenerate-btn"
                    onClick={generateAIRecommendations}
                    disabled={recommendationsLoading}
                  >
                    {recommendationsLoading ? <LoadingSpinner /> : 'Regenerate Recommendations'}
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Verification & Staking */}
          <div className="settings-section">
            <h3>Verification & Staking</h3>
            <button 
              className="setting-btn" 
              onClick={() => setShowSubscriptionModal(true)}
              disabled={!walletConnected}
            >
              <CustomIcons.Crown /> Subscribe to Verification Tier
            </button>
          </div>
          
          {/* Order History */}
          <div className="settings-section">
            <h3>Orders</h3>
            <button 
              className="setting-btn" 
              onClick={() => setShowOrderHistory(true)}
            >
              <CustomIcons.Orders /> View Order History ({orders.length})
            </button>
          </div>
          
          {/* Preferences */}
          <div className="settings-section">
            <h3>Preferences</h3>
            <div className="setting-toggle">
              <span>Dark Mode</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={isDarkMode}
                  onChange={(e) => setIsDarkMode(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          {/* Platform Statistics */}
          {platformStats && (
            <div className="settings-section">
              <h3>Platform Statistics</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.total_users)}</span>
                  <span className="stat-label">Total Users</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.total_products)}</span>
                  <span className="stat-label">Products</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.total_transactions)}</span>
                  <span className="stat-label">Transactions</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{formatPrice(Number(platformStats.total_gmv_idr))}</span>
                  <span className="stat-label">Total GMV</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const AIConsultationModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showAIConsultation ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2><CustomIcons.Robot /> AI Fragrance Consultation</h2>
          <button className="close-btn" onClick={() => setShowAIConsultation(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          <div className="consultation-content">
            <div className="consultation-step">
              <h3>Welcome to Aromance AI Consultation! 🌸</h3>
              <p>Our AI will analyze your personality and preferences to create your unique fragrance identity.</p>
              
              <div className="consultation-info">
                <div className="info-card">
                  <CustomIcons.Robot />
                  <h4>Personalized Analysis</h4>
                  <p>AI-powered personality matching with fragrance families</p>
                </div>
                <div className="info-card">
                  <CustomIcons.Wallet />
                  <h4>Decentralized Identity</h4>
                  <p>Your data is secured with blockchain technology</p>
                </div>
                <div className="info-card">
                  <CustomIcons.Star />
                  <h4>Verified Results</h4>
                  <p>Get recommendations from verified sellers only</p>
                </div>
              </div>

              <div className="consultation-form">
                <h4>Quick Personality Assessment</h4>
                <div className="form-group">
                  <label>What's your lifestyle?</label>
                  <select id="lifestyle-select">
                    <option value="professional">Professional & Business</option>
                    <option value="casual">Casual & Relaxed</option>
                    <option value="creative">Creative & Artistic</option>
                    <option value="active">Active & Sporty</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Preferred fragrance families (select multiple):</label>
                  <div className="checkbox-group">
                    {['Fresh', 'Floral', 'Woody', 'Oriental', 'Citrus', 'Fruity'].map(family => (
                      <label key={family} className="checkbox-label">
                        <input type="checkbox" value={family.toLowerCase()} />
                        <span>{family}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Budget range:</label>
                  <select id="budget-select">
                    <option value="budget">Budget (Under 50k IDR)</option>
                    <option value="moderate">Moderate (50k - 200k IDR)</option>
                    <option value="premium">Premium (200k - 500k IDR)</option>
                    <option value="luxury">Luxury (Above 500k IDR)</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Main occasions for wearing fragrance:</label>
                  <div className="checkbox-group">
                    {['Daily Work', 'Evening Date', 'Special Events', 'Casual Outings', 'Travel'].map(occasion => (
                      <label key={occasion} className="checkbox-label">
                        <input type="checkbox" value={occasion.toLowerCase().replace(' ', '_')} />
                        <span>{occasion}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="consultation-status">
                {consultationLoading ? (
                  <>
                    <p>🤖 Processing your personality profile...</p>
                    <p>🔍 Analyzing fragrance preferences...</p>
                    <p>✨ Creating your decentralized identity...</p>
                    <div className="loading-bar">
                      <div className="loading-progress"></div>
                    </div>
                  </>
                ) : (
                  <p>Ready to create your personalized fragrance profile!</p>
                )}
              </div>

              <button 
                className="consultation-btn"
                onClick={() => {
                  const lifestyle = document.getElementById('lifestyle-select').value;
                  const budget = document.getElementById('budget-select').value;
                  
                  const selectedFamilies = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                    .filter(cb => ['fresh', 'floral', 'woody', 'oriental', 'citrus', 'fruity'].includes(cb.value))
                    .map(cb => cb.value);
                  
                  const selectedOccasions = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                    .filter(cb => ['daily_work', 'evening_date', 'special_events', 'casual_outings', 'travel'].includes(cb.value))
                    .map(cb => cb.value);
                  
                  completeConsultation({
                    personality_type: 'confident_modern',
                    lifestyle: lifestyle,
                    fragrance_families: selectedFamilies.length > 0 ? selectedFamilies : ['fresh', 'floral'],
                    budget_range: budget,
                    personality_traits: ['confident', 'elegant'],
                    occasions: selectedOccasions.length > 0 ? selectedOccasions : ['daily_work'],
                    seasons: ['spring', 'summer'],
                    sensitivity: 'medium',
                    scent_journey: [
                      {
                        stage: 'morning',
                        notes: ['citrus', 'fresh'],
                        duration_hours: 4
                      }
                    ]
                  });
                }}
                disabled={consultationLoading}
              >
                {consultationLoading ? <LoadingSpinner /> : 'Complete AI Consultation'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const CartModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showCart ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>
            <CustomIcons.Cart />
            Shopping Cart
          </h2>
          <button className="close-btn" onClick={() => setShowCart(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {cart.length === 0 ? (
            <div className="empty-cart">
              <CustomIcons.Cart />
              <p>Your cart is empty</p>
              <p>Add some fragrances to get started</p>
              <button className="browse-btn" onClick={() => setShowCart(false)}>
                Continue Shopping
              </button>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <img 
                      src={resolveImageUrl(item.image_urls?.[0])} 
                      alt={item.name} 
                      className="cart-item-image" 
                    />
                    <div className="cart-item-info">
                      <h4>{item.name}</h4>
                      <p>{item.brand}</p>
                      <p className="cart-item-price">{formatPrice(Number(item.price_idr))}</p>
                    </div>
                    <div className="cart-item-controls">
                      <button onClick={() => updateCartQuantity(item.id, item.quantity - 1)}>
                        <CustomIcons.Minus />
                      </button>
                      <span className="quantity">{item.quantity}</span>
                      <button onClick={() => updateCartQuantity(item.id, item.quantity + 1)}>
                        <CustomIcons.Plus />
                      </button>
                    </div>
                    <button 
                      className="remove-btn"
                      onClick={() => removeFromCart(item.id)}
                    >
                      <CustomIcons.Delete />
                    </button>
                  </div>
                ))}
              </div>
              <div className="cart-total">
                <h3>Total: {formatPrice(getTotalPrice())}</h3>
                <p>Payment to: {MAIN_WALLET_ADDRESS.slice(0, 20)}...</p>
                <button 
                  className="checkout-btn" 
                  onClick={checkout}
                  disabled={checkoutLoading}
                >
                  <CustomIcons.Wallet />
                  {checkoutLoading ? <LoadingSpinner /> : 'Checkout with Plug Wallet'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  // Search Results Modal
  const SearchResultsModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showSearchResults ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>
            <CustomIcons.Search />
            Search Results for "{searchQuery}"
          </h2>
          <button className="close-btn" onClick={() => setShowSearchResults(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {searchLoading ? (
            <div className="loading-section">
              <LoadingSpinner />
              <p>Searching products...</p>
            </div>
          ) : (
            <div className="search-results-grid">
              {searchResults.length > 0 ? searchResults.map(product => (
                <ProductCard key={product.id} product={product} />
              )) : (
                <div className="no-search-results">
                  <CustomIcons.Search />
                  <p>No products found for "{searchQuery}"</p>
                  <p>Try searching for different keywords or browse our categories</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-logo">
            <img src="./src/log1_.png" alt="Aromance" style={{ width: "67px", height: "67px" }} />
          </div>
          <div className="loading-text">Loading Aromance...</div>
          <div className="loading-bar">
            <div className="loading-progress"></div>
          </div>
          <div className="loading-status">
            <p>Connecting to ICP network...</p>
            <p>Initializing AI agents...</p>
            <p>Loading product catalog...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
      <ErrorToast />
      
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-content">
          <div className="logo-section">
            <div className="logo-link">
              <img src="./src/log1_.png" alt="Aromance" className="logo-image" />
              <span className="brand-name">Aromance</span>
            </div>
          </div>
          
          {/* Search Bar */}
          {walletConnected && (
            <div className="navbar-search">
              <SearchBar />
            </div>
          )}
          
          <div className="nav-actions">
            {!walletConnected && (
              <button 
                className="nav-action-btn wallet-btn"
                onClick={handleWalletConnect}
                title="Connect Plug Wallet"
              >
                <CustomIcons.Wallet />
              </button>
            )}
            <button 
              className="nav-action-btn cart-btn"
              onClick={() => setShowCart(true)}
            >
              <CustomIcons.Cart />
              {cart.length > 0 && <span className="cart-count">{cart.length}</span>}
            </button>
            <button 
              className="nav-action-btn user-btn"
              onClick={() => setShowUserSettings(true)}
            >
              <CustomIcons.User />
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Welcome Section */}
        {!walletConnected && (
          <div className="welcome-section">
            <h1>Welcome to Aromance 🌸</h1>
            <p>Decentralized fragrance marketplace powered by AI consultation</p>
            <div className="welcome-features">
              <div className="feature-card">
                <CustomIcons.Robot />
                <h3>AI-Powered Recommendations</h3>
                <p>Get personalized fragrance suggestions based on your personality</p>
              </div>
              <div className="feature-card">
                <CustomIcons.Crown />
                <h3>Proof of Stake Verification</h3>
                <p>Earn rewards while building trust in the community</p>
              </div>
              <div className="feature-card">
                <CustomIcons.Wallet />
                <h3>Decentralized Identity</h3>
                <p>Your data is secured with blockchain technology</p>
              </div>
            </div>
            <button className="cta-button" onClick={handleWalletConnect}>
              <CustomIcons.Wallet /> Connect Wallet to Start
            </button>
          </div>
        )}

        {walletConnected && !consultationCompleted && (
          <div className="welcome-section">
            <h1>Get Started with AI Consultation</h1>
            <p>Let our AI analyze your personality and find the perfect fragrance for you</p>
            <div className="consultation-benefits">
              <div className="benefit-item">
                <CustomIcons.Star />
                <span>Personalized recommendations</span>
              </div>
              <div className="benefit-item">
                <CustomIcons.Robot />
                <span>AI-powered matching</span>
              </div>
              <div className="benefit-item">
                <CustomIcons.Wallet />
                <span>Decentralized identity creation</span>
              </div>
            </div>
            <button 
              className="cta-button" 
              onClick={startAIConsultation}
              disabled={consultationLoading}
            >
              <CustomIcons.Robot /> 
              {consultationLoading ? <LoadingSpinner /> : 'Start AI Consultation'}
            </button>
          </div>
        )}

        {/* AI Recommendations Section - Top picks */}
        {consultationCompleted && topRecommendations.length > 0 && (
          <ProductSection 
            title="AI Recommendations for You"
            products={topRecommendations.map(rec => products.find(p => p.id === rec.product_id)).filter(Boolean)}
            recommendations={topRecommendations}
            isRecommended={true}
            showAIBadge={true}
            icon={CustomIcons.Robot}
            isLoading={recommendationsLoading}
          />
        )}

        {/* Personalized Products - You might like */}
        {consultationCompleted && personalizedProducts.length > 0 && (
          <ProductSection 
            title="You Might Like"
            products={personalizedProducts}
            icon={CustomIcons.Heart}
            isLoading={recommendationsLoading}
          />
        )}

        {/* Other Products - Paginated, not random */}
        <ProductSection 
          title="Other Products"
          products={otherProducts}
          icon={CustomIcons.Flower}
          showRefresh={true}
          isLoading={productsLoading}
        />

        {/* Platform Status */}
        <div className="platform-status">
          <h3>Platform Status</h3>
          <div className="status-grid">
            <div className="status-card">
              <CustomIcons.Robot />
              <h4>AI Agents</h4>
              <p>{Object.values(agentHealth).filter(h => h.status === 'connected').length}/{Object.keys(agentHealth).length} Online</p>
            </div>
            <div className="status-card">
              <CustomIcons.Wallet />
              <h4>Wallet</h4>
              <p>{walletConnected ? 'Connected' : 'Not Connected'}</p>
            </div>
            <div className="status-card">
              <CustomIcons.Star />
              <h4>DID System</h4>
              <p>{userDID ? 'Active' : 'Pending'}</p>
            </div>
            <div className="status-card">
              <CustomIcons.Crown />
              <h4>Verification</h4>
              <p>{getVerificationBadgeText(userProfile?.verification_status) || 'Unverified'}</p>
            </div>
          </div>
          
          {/* Platform Statistics */}
          {platformStats && (
            <div className="platform-stats">
              <h4>Platform Statistics</h4>
              <div className="stats-row">
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.total_users)}</span>
                  <span className="stat-label">Users</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.total_products)}</span>
                  <span className="stat-label">Products</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{Number(platformStats.verified_products)}</span>
                  <span className="stat-label">Verified</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{formatPrice(Number(platformStats.total_gmv_idr))}</span>
                  <span className="stat-label">Total GMV</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* All Modals */}
      <UserSettingsModal />
      <CartModal />
      <AIConsultationModal />
      <ProductDetailModal />
      <OrderHistoryModal />
      <SubscriptionModal />
      <SearchResultsModal />

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-brand">
              <img src="./src/log1_.png" alt="Aromance" className="footer-logo" />
              <span className="footer-brand-text">Aromance</span>
            </div>
            <div className="footer-copyright">
              © Aromance 2025 - Decentralized Fragrance Marketplace
            </div>
          </div>
          
          <div className="footer-center">
            <div className="footer-links">
              <a href="#" className="footer-link">Terms of Use</a>
              <a href="#" className="footer-link">Privacy Policy</a>
              <a href="#" className="footer-link">Proof of Stake</a>
              <a href="#" className="footer-link">AI Technology</a>
            </div>
          </div>
          
          <div className="footer-right">
            <div className="footer-treasury">
              <p>Treasury: {MAIN_WALLET_ADDRESS.slice(0, 16)}...</p>
            </div>
            <a href="https://www.instagram.com/75s.comm?igsh=MXJ6cTV3dm5rZXlvZg==" className="footer-social">
              <img src="./src/insta.png" alt="Instagram" style={{ width: "24px", height: "24px" }} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;

  
    