import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import './App.css';

// ICP Backend Integration
const CANISTER_ID = process.env.CANISTER_ID_AROMANCE_BACKEND || 'bkyz2-fmaaa-aaaaa-qaaaq-cai';
const HOST = process.env.DFX_NETWORK === 'ic' ? 'https://icp-api.io' : 'http://localhost:4943';

// Main Wallet Address for all transactions (Principal for ICP transfers)
const MAIN_WALLET_PRINCIPAL = Principal.fromText("afa05153e88aa30ec9af2ff13617ea9e57f47083ee67bfb62b6ad17b6097f390");

// AI Agent Endpoints (corrected paths without /api prefix)
const AGENT_ENDPOINTS = {
  coordinator: 'http://127.0.0.1:8000',
  consultation: 'http://127.0.0.1:8001',
  recommendation: 'http://127.0.0.1:8002',
  analytics: 'http://127.0.0.1:8004',
  inventory: 'http://127.0.0.1:8005'
};

// IDL Factory (fully synced with backend lib.rs structures)
const idlFactory = ({ IDL }) => {
  const UserProfile = IDL.Record({
    'user_id': IDL.Text,
    'wallet_address': IDL.Opt(IDL.Text),
    'did': IDL.Opt(IDL.Text),
    'verification_status': IDL.Variant({
      'Unverified': IDL.Null,
      'Basic': IDL.Null,
      'Premium': IDL.Null,
      'Elite': IDL.Null
    }),
    'stake_info': IDL.Opt(IDL.Record({
      'amount_idr': IDL.Nat64,
      'tier': IDL.Variant({
        'BasicReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
        'PremiumReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
        'EliteReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
        'BasicSeller': IDL.Record({ 'stake': IDL.Nat64 }),
        'PremiumSeller': IDL.Record({ 'stake': IDL.Nat64 }),
        'EliteSeller': IDL.Record({ 'stake': IDL.Nat64 })
      }),
      'locked_until': IDL.Nat64,
      'penalty_count': IDL.Nat32,
      'reward_earned': IDL.Nat64,
      'annual_return_rate': IDL.Float64
    })),
    'preferences': IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text)), // HashMap as Vec<Tuple>
    'consultation_completed': IDL.Bool,
    'ai_consent': IDL.Bool,
    'data_monetization_consent': IDL.Bool,
    'reputation_score': IDL.Float64,
    'total_transactions': IDL.Nat32,
    'created_at': IDL.Nat64,
    'last_active': IDL.Nat64
  });

  const FragranceIdentity = IDL.Record({
    'personality_type': IDL.Text,
    'lifestyle': IDL.Text,
    'preferred_families': IDL.Vec(IDL.Text),
    'occasion_preferences': IDL.Vec(IDL.Text),
    'season_preferences': IDL.Vec(IDL.Text),
    'sensitivity_level': IDL.Text,
    'budget_range': IDL.Variant({
      'Budget': IDL.Null,
      'Moderate': IDL.Null,
      'Premium': IDL.Null,
      'Luxury': IDL.Null
    }),
    'scent_journey': IDL.Vec(IDL.Record({
      'date': IDL.Nat64,
      'preference_change': IDL.Text,
      'trigger_event': IDL.Text,
      'confidence_score': IDL.Float64
    }))
  });

  const DecentralizedIdentity = IDL.Record({
    'did': IDL.Text,
    'public_key': IDL.Text,
    'private_key_hash': IDL.Text,
    'verified_claims': IDL.Vec(IDL.Record({
      'claim_type': IDL.Text,
      'issuer': IDL.Text,
      'claim_data': IDL.Text,
      'verified_at': IDL.Nat64,
      'expiry': IDL.Nat64
    })),
    'data_permissions': IDL.Vec(IDL.Tuple(IDL.Text, IDL.Variant({
      'None': IDL.Null,
      'ReadOnly': IDL.Null,
      'Limited': IDL.Null,
      'Full': IDL.Null
    }))),
    'fragrance_identity': FragranceIdentity,
    'created_at': IDL.Nat64
  });

  const Product = IDL.Record({
    'id': IDL.Text,
    'seller_id': IDL.Text,
    'seller_verification': IDL.Variant({
      'Unverified': IDL.Null,
      'Basic': IDL.Null,
      'Premium': IDL.Null,
      'Elite': IDL.Null
    }),
    'name': IDL.Text,
    'brand': IDL.Text,
    'price_idr': IDL.Nat64,
    'fragrance_family': IDL.Text,
    'top_notes': IDL.Vec(IDL.Text),
    'middle_notes': IDL.Vec(IDL.Text),
    'base_notes': IDL.Vec(IDL.Text),
    'occasion': IDL.Vec(IDL.Text),
    'season': IDL.Vec(IDL.Text),
    'longevity': IDL.Variant({
      'VeryWeak': IDL.Null,
      'Weak': IDL.Null,
      'Moderate': IDL.Null,
      'Good': IDL.Null,
      'VeryGood': IDL.Null,
      'Excellent': IDL.Null
    }),
    'sillage': IDL.Variant({
      'Intimate': IDL.Null,
      'Moderate': IDL.Null,
      'Heavy': IDL.Null,
      'Enormous': IDL.Null
    }),
    'projection': IDL.Variant({
      'Skin': IDL.Null,
      'Light': IDL.Null,
      'Moderate': IDL.Null,
      'Strong': IDL.Null
    }),
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
    'updated_at': IDL.Nat64
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
    'user_feedback': IDL.Opt(IDL.Float64)
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
    'transaction_tier': IDL.Variant({
      'Budget': IDL.Null,
      'Standard': IDL.Null,
      'Premium': IDL.Null,
      'Luxury': IDL.Null
    }),
    'status': IDL.Variant({
      'Pending': IDL.Null,
      'Processing': IDL.Null,
      'Confirmed': IDL.Null,
      'Shipped': IDL.Null,
      'Delivered': IDL.Null,
      'Completed': IDL.Null,
      'Disputed': IDL.Null,
      'Cancelled': IDL.Null,
      'Refunded': IDL.Null
    }),
    'escrow_locked': IDL.Bool,
    'payment_method': IDL.Text,
    'shipping_address': IDL.Text,
    'created_at': IDL.Nat64,
    'completed_at': IDL.Opt(IDL.Nat64)
  });

  const VerifiedReview = IDL.Record({
    'review_id': IDL.Text,
    'reviewer_id': IDL.Text,
    'reviewer_stake': IDL.Nat64,
    'reviewer_tier': IDL.Variant({
      'BasicReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'PremiumReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'EliteReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'BasicSeller': IDL.Record({ 'stake': IDL.Nat64 }),
      'PremiumSeller': IDL.Record({ 'stake': IDL.Nat64 }),
      'EliteSeller': IDL.Record({ 'stake': IDL.Nat64 })
    }),
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
    'last_updated': IDL.Nat64
  });

  return IDL.Service({
    // User Management
    'create_user_profile': IDL.Func([UserProfile], [IDL.Text], []),
    'get_user_profile': IDL.Func([IDL.Text], [IDL.Opt(UserProfile)], ['query']),
    'create_decentralized_identity': IDL.Func([IDL.Text, FragranceIdentity], [DecentralizedIdentity], []),

    // Staking & Verification
    'stake_for_verification': IDL.Func([IDL.Text, IDL.Nat64, IDL.Variant({
      'BasicReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'PremiumReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'EliteReviewer': IDL.Record({ 'stake': IDL.Nat64 }),
      'BasicSeller': IDL.Record({ 'stake': IDL.Nat64 }),
      'PremiumSeller': IDL.Record({ 'stake': IDL.Nat64 }),
      'EliteSeller': IDL.Record({ 'stake': IDL.Nat64 })
    })], [IDL.Text], []),
    'process_stake_rewards': IDL.Func([IDL.Text], [IDL.Text], []),

    // Product Management
    'get_products': IDL.Func([], [IDL.Vec(Product)], ['query']),
    'search_products_by_personality': IDL.Func([IDL.Text], [IDL.Vec(Product)], ['query']),
    'get_halal_products': IDL.Func([], [IDL.Vec(Product)], ['query']),

    // AI Recommendations
    'generate_ai_recommendations': IDL.Func([IDL.Text], [IDL.Vec(AIRecommendation)], []),
    'get_recommendations_for_user': IDL.Func([IDL.Text], [IDL.Vec(AIRecommendation)], ['query']),

    // Reviews
    'create_verified_review': IDL.Func([VerifiedReview], [IDL.Text], []),
    'get_product_reviews': IDL.Func([IDL.Text], [IDL.Vec(VerifiedReview)], ['query']),

    // Transactions
    'create_transaction': IDL.Func([Transaction], [IDL.Text], []),
    'get_user_transactions': IDL.Func([IDL.Text], [IDL.Vec(Transaction)], ['query']),

    // Platform Stats
    'get_platform_statistics': IDL.Func([], [IDL.Record({
      'total_users': IDL.Nat64,
      'verified_users': IDL.Nat64,
      'total_products': IDL.Nat64,
      'verified_products': IDL.Nat64,
      'total_transactions': IDL.Nat64,
      'total_gmv_idr': IDL.Nat64,
      'total_staked_idr': IDL.Nat64
    })], ['query']),
    'get_trending_fragrances': IDL.Func([], [IDL.Vec(IDL.Text)], ['query'])
  });
};

// Plug Wallet Integration (for connections and transfers)
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

// Helper to perform ICP transfers via Plug (for staking, payments - assuming tokenized IDR on ICP)
const performICPTransfer = async (amountICP) => {
  try {
    const params = {
      to: MAIN_WALLET_PRINCIPAL.toText(),
      amount: BigInt(amountICP * 1e8), // Convert to e8s (ICP subunits)
    };
    const result = await window.ic.plug.requestTransfer(params);
    return result;
  } catch (error) {
    console.error('ICP Transfer failed:', error);
    throw error;
  }
};

// Custom SVG Icons (existing, no change)
const CustomIcons = {
  Cart: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7ZM9 3V4H15V3H9ZM7 6V19H17V6H7Z" fill="currentColor"/>
      <path d="M9 8V17H11V8H9ZM13 8V17H15V8H13Z" fill="currentColor"/>
    </svg>
  ),
  User: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9H15V22H13V16H11V22H9V9H3V7H21V9Z" fill="currentColor"/>
    </svg>
  ),
  Robot: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M13 1H11V3H13V1ZM12 5C9.24 5 7 7.24 7 10V13H5V15H3V17H5V19C5 20.1 5.9 21 7 21H17C18.1 21 19 20.1 19 19V17H21V15H19V13H17V10C17 7.24 14.76 5 12 5ZM9 10C9 8.9 9.9 8 11 8H13C14.1 8 15 8.9 15 10V12H9V10ZM17 19H7V17H17V19ZM15 15H9V14H15V15ZM19 9H21V11H19V9ZM3 9H5V11H3V9ZM19 5H21V7H19V5ZM3 5H5V7H3V5ZM19 1H21V3H19V1ZM3 1H5V3H3V1ZM19 13H21V15H19V13ZM3 13H5V15H3V13ZM19 17H21V19H19V17ZM3 17H5V19H3V17ZM19 21H21V23H19V21ZM3 21H5V23H3V21Z" fill="currentColor"/>
    </svg>
  ),
  Flower: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12 2C12 2 17 4 17 7C17 4 22 2 22 2C22 2 17 4 17 7C17 4 12 2 12 2ZM2 2C2 2 7 4 7 7C7 4 12 2 12 2C12 2 7 4 7 7C7 4 2 2 2 2ZM12 22C12 22 7 20 7 17C7 20 2 22 2 22C2 22 7 20 7 17C7 20 12 22 12 22ZM22 22C22 22 17 20 17 17C17 20 12 22 12 22C12 22 17 20 17 17C17 20 22 22 22 22ZM5 12C5 12 3 7 6 7C3 7 1 2 1 2C1 2 3 7 6 7C3 7 5 12 5 12ZM19 12C19 12 21 7 18 7C21 7 23 2 23 2C23 2 21 7 18 7C21 7 19 12 19 12ZM12 5C12 5 7 3 7 6C7 3 2 1 2 1C2 1 7 3 7 6C7 3 12 5 12 5ZM12 19C12 19 7 21 7 18C7 21 2 23 2 23C2 23 7 21 7 18C7 21 12 19 12 19Z" fill="currentColor"/>
    </svg>
  ),
  Star: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="currentColor"/>
    </svg>
  ),
  Wallet: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M21 18V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5V6H12C10.9 6 10 6.9 10 8V14C10 15.1 10.9 16 12 16H21V18ZM18 14V11C18 10.45 17.55 10 17 10H14V12H17C17.55 12 18 12.45 18 13V14H18Z" fill="currentColor"/>
    </svg>
  )
};

// Loading Spinner Component
const LoadingSpinner = () => (
  <div className="spinner">
    <div className="double-bounce1"></div>
    <div className="double-bounce2"></div>
  </div>
);

// Error Toast Component
const ErrorToast = ({ message }) => (
  message && (
    <div className="error-toast">
      {message}
    </div>
  )
);

// Product Card Component (with fixed image resolver and badges)
const ProductCard = ({ product, isRecommended, showAIBadge }) => {
  const resolveImageUrl = (url) => {
    if (url?.startsWith('/')) {
      return 'https://aromance-e56c8.web.app' + url;
    }
    return url || '/images/default-product.png';
  };

  return (
    <div className="product-card">
      <div className="product-image-container">
        <img src={resolveImageUrl(product.image_urls?.[0])} alt={product.name} className="product-image" />
        {product.verified && <span className="badge verified">Verified</span>}
        {product.halal_certified && <span className="badge halal">Halal</span>}
        {showAIBadge && <span className="badge ai">AI Match</span>}
      </div>
      <h3 className="product-name">{product.name}</h3>
      <p className="product-brand">{product.brand}</p>
      <p className="product-price">Rp {product.price_idr.toLocaleString('id-ID')}</p>
      <p className="product-family">{product.fragrance_family}</p>
      {isRecommended && <p className="match-score">Match: {(product.match_score * 100).toFixed(0)}%</p>}
      <button className="add-to-cart-btn">Add to Cart</button>
    </div>
  );
};

// Product Section Component (per-section loading)
const ProductSection = ({ title, products, isRecommended, showAIBadge, icon: Icon, isLoading, showRefresh, onRefresh }) => (
  <section className="product-section">
    <h2 className="section-title">
      {Icon && <Icon />}
      {title}
    </h2>
    {isLoading ? (
      <LoadingSpinner />
    ) : (
      <div className="product-grid">
        {products.map(product => (
          <ProductCard 
            key={product.id} 
            product={product} 
            isRecommended={isRecommended} 
            showAIBadge={showAIBadge} 
          />
        ))}
      </div>
    )}
    {showRefresh && <button className="refresh-btn" onClick={onRefresh}>Refresh</button>}
  </section>
);

const App = () => {
  const [loading, setLoading] = useState(true);
  const [walletConnected, setWalletConnected] = useState(false);
  const [userPrincipal, setUserPrincipal] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [actor, setActor] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [showAIConsultation, setShowAIConsultation] = useState(false);
  const [consultationSessionId, setConsultationSessionId] = useState(null);
  const [consultationMessages, setConsultationMessages] = useState([]);
  const [consultationLoading, setConsultationLoading] = useState(false);
  const [fragranceProfile, setFragranceProfile] = useState(null);
  const [consultationCompleted, setConsultationCompleted] = useState(false);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [personalizedProducts, setPersonalizedProducts] = useState([]);
  const [otherProducts, setOtherProducts] = useState([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [productsLoading, setProductsLoading] = useState(false);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [showProductDetail, setShowProductDetail] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showOrderHistory, setShowOrderHistory] = useState(false);
  const [orders, setOrders] = useState([]);
  const [showSubscription, setShowSubscription] = useState(false);
  const [verificationTier, setVerificationTier] = useState(null);
  const [userDID, setUserDID] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [otherPage, setOtherPage] = useState(0);
  const PAGE_SIZE = 8;

  useEffect(() => {
    const init = async () => {
      const agent = new HttpAgent({ host: HOST });
      if (process.env.DFX_NETWORK !== 'ic') {
        agent.fetchRootKey();
      }
      const newActor = Actor.createActor(idlFactory, { agent, canisterId: CANISTER_ID });
      setActor(newActor);
      setBackendConnected(true);
      setLoading(false);
    };
    init();
  }, []);

  const handleWalletConnect = async () => {
    const principal = await connectWallet();
    if (principal) {
      setUserPrincipal(principal);
      setWalletConnected(true);
      await loadUserData(principal);
    }
  };

  const loadUserData = async (principal) => {
    setProfileLoading(true);
    try {
      const profile = await actor.get_user_profile(principal);
      if (profile[0]) {
        setUserProfile(profile[0]);
        setConsultationCompleted(profile[0].consultation_completed);
        setUserDID(profile[0].did[0] || null);
        await loadRecommendations(principal);
        await loadOrders(principal);
      } else {
        await createNewUserProfile(principal);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      setErrorMessage('Failed to load user data');
    }
    setProfileLoading(false);
  };

  const createNewUserProfile = async (principal) => {
    setProfileLoading(true);
    try {
      const newProfile = {
        user_id: principal,
        wallet_address: [principal],
        did: [],
        verification_status: { Unverified: null },
        stake_info: [],
        preferences: [],
        consultation_completed: false,
        ai_consent: true,
        data_monetization_consent: true, // Required field to fix subtyping error
        reputation_score: 0.0,
        total_transactions: 0,
        created_at: BigInt(Date.now()),
        last_active: BigInt(Date.now())
      };
      await actor.create_user_profile(newProfile);
      setUserProfile(newProfile);
    } catch (error) {
      console.error('Error creating user profile:', error);
      setErrorMessage('Failed to create user profile');
    }
    setProfileLoading(false);
  };

  const updateUserProfile = async (updatedProfile) => {
    setProfileLoading(true);
    try {
      // Ensure full profile with all required fields
      const fullUpdatedProfile = {
        ...userProfile,
        ...updatedProfile,
        data_monetization_consent: userProfile.data_monetization_consent || true, // Preserve required
        last_active: BigInt(Date.now())
      };
      await actor.create_user_profile(fullUpdatedProfile); // Using create as upsert
      setUserProfile(fullUpdatedProfile);
    } catch (error) {
      console.error('Error updating user profile:', error);
      setErrorMessage('Failed to update user profile');
    }
    setProfileLoading(false);
  };

  const startAIConsultation = async () => {
    setConsultationLoading(true);
    try {
      const response = await fetch(`${AGENT_ENDPOINTS.consultation}/consultation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userPrincipal, session_id: `session_${Date.now()}` })
      });
      const data = await response.json();
      setConsultationSessionId(data.session_id);
      setConsultationMessages([{ role: 'ai', content: data.response }]);
      setShowAIConsultation(true);
    } catch (error) {
      console.error('Error starting consultation:', error);
      setErrorMessage('Failed to start AI consultation');
    }
    setConsultationLoading(false);
  };

  const sendConsultationMessage = async (message) => {
    setConsultationLoading(true);
    try {
      const response = await fetch(`${AGENT_ENDPOINTS.consultation}/consultation/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userPrincipal, session_id: consultationSessionId, message })
      });
      const data = await response.json();
      setConsultationMessages(prev => [...prev, { role: 'user', content: message }, { role: 'ai', content: data.response }]);
      if (data.consultation_progress === 1.0) {
        setFragranceProfile(data.data_collected);
        await createDecentralizedIdentity(data.data_collected);
        setConsultationCompleted(true);
        await loadRecommendations(userPrincipal);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setErrorMessage('Failed to send message');
    }
    setConsultationLoading(false);
  };

  const createDecentralizedIdentity = async (fragranceProfile) => {
    try {
      const did = await actor.create_decentralized_identity(userPrincipal, fragranceProfile);
      setUserDID(did.did);
      // Update profile with DID
      await updateUserProfile({ did: [did.did] });
    } catch (error) {
      console.error('Error creating DID:', error);
      setErrorMessage('Failed to create Decentralized Identity');
    }
  };

  const loadRecommendations = async (userId) => {
    setRecommendationsLoading(true);
    try {
      const recs = await actor.get_recommendations_for_user(userId);
      const sortedRecs = recs.sort((a, b) => b.match_score - a.match_score);
      setAiRecommendations(sortedRecs.slice(0, 6)); // Top 6 for AI Recommended
      setPersonalizedProducts(sortedRecs.slice(6, 18)); // Next 12 for Might Like
      const otherStart = otherPage * PAGE_SIZE + 18;
      setOtherProducts(sortedRecs.slice(otherStart, otherStart + PAGE_SIZE)); // Paged others
      // Send analytics event
      await fetch(`${AGENT_ENDPOINTS.analytics}/analytics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          event_type: 'recs_loaded',
          recommendations_count: sortedRecs.length,
          personality_type: fragranceProfile?.personality_type || 'unknown'
        })
      });
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setErrorMessage('Failed to load recommendations');
    }
    setRecommendationsLoading(false);
  };

  const handleRefreshOther = () => {
    setOtherPage(prev => prev + 1);
    // Reload otherProducts based on new page (from sorted recs)
    loadRecommendations(userPrincipal); // Re-slice
  };

  const loadOrders = async (userId) => {
    setOrdersLoading(true);
    try {
      const transactions = await actor.get_user_transactions(userId);
      setOrders(transactions);
    } catch (error) {
      console.error('Error loading orders:', error);
      setErrorMessage('Failed to load orders');
    }
    setOrdersLoading(false);
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query) {
      try {
        // Use search_products_by_personality as advanced search proxy (or extend backend if needed)
        const results = await actor.search_products_by_personality(query); // Assuming personality-like search
        setOtherProducts(results);
      } catch (error) {
        console.error('Search error:', error);
        setErrorMessage('Search failed');
      }
    } else {
      loadRecommendations(userPrincipal); // Reset to recs
    }
  };

  const subscribeToTier = async (tier) => {
    try {
      let amount;
      let backendTier;
      switch (tier) {
        case 'Basic Reviewer':
          amount = 300000;
          backendTier = { BasicReviewer: { stake: BigInt(300000) } };
          break;
        case 'Premium Reviewer':
          amount = 950000;
          backendTier = { PremiumReviewer: { stake: BigInt(950000) } };
          break;
        case 'Elite Reviewer':
          amount = 1900000;
          backendTier = { EliteReviewer: { stake: BigInt(1900000) } };
          break;
        case 'Basic Seller':
          amount = 500000;
          backendTier = { BasicSeller: { stake: BigInt(500000) } };
          break;
        case 'Premium Seller':
          amount = 1500000;
          backendTier = { PremiumSeller: { stake: BigInt(1500000) } };
          break;
        case 'Elite Seller':
          amount = 3000000;
          backendTier = { EliteSeller: { stake: BigInt(3000000) } };
          break;
        default:
          return;
      }
      // Perform real ICP transfer (assuming 1 ICP = 100000 IDR for simulation; adjust rate)
      const icpAmount = amount / 100000; // Example conversion
      await performICPTransfer(icpAmount);
      await actor.stake_for_verification(userPrincipal, BigInt(amount), backendTier);
      await loadUserData(userPrincipal); // Reload profile for updated status
      setVerificationTier(tier);
    } catch (error) {
      console.error('Subscription error:', error);
      setErrorMessage('Failed to subscribe');
    }
  };

  const claimRewards = async () => {
    try {
      await actor.process_stake_rewards(userPrincipal);
      await loadUserData(userPrincipal); // Reload for updated stake_info
    } catch (error) {
      console.error('Claim rewards error:', error);
      setErrorMessage('Failed to claim rewards');
    }
  };

  const createReview = async (review) => {
    try {
      // Ensure verified_purchase based on orders
      const hasPurchase = orders.some(o => o.product_id === review.product_id && o.status === { Completed: null });
      const fullReview = {
        ...review,
        verified_purchase: hasPurchase,
        reviewer_stake: userProfile.stake_info[0]?.amount_idr || BigInt(0),
        reviewer_tier: userProfile.stake_info[0]?.tier || { BasicReviewer: { stake: BigInt(0) } },
        helpful_votes: 0,
        reported_count: 0,
        ai_validated: false,
        review_date: BigInt(Date.now()),
        last_updated: BigInt(Date.now())
      };
      await actor.create_verified_review(fullReview);
    } catch (error) {
      console.error('Review error:', error);
      setErrorMessage('Failed to create review');
    }
  };

  const createTransaction = async (transaction) => {
    try {
      const fullTransaction = {
        ...transaction,
        unit_price_idr: BigInt(transaction.unit_price_idr || 0),
        commission_rate: transaction.commission_rate || 0.02,
        commission_amount: BigInt(0), // Backend calculates
        transaction_tier: { Standard: null }, // Determine based on total_amount_idr
        escrow_locked: true,
        payment_method: 'Plug Wallet',
        shipping_address: 'Default Address', // Placeholder
        completed_at: []
      };
      await actor.create_transaction(fullTransaction);
      // Send analytics event
      await fetch(`${AGENT_ENDPOINTS.analytics}/analytics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userPrincipal, event_type: 'checkout_success' })
      });
      await loadOrders(userPrincipal);
    } catch (error) {
      console.error('Transaction error:', error);
      setErrorMessage('Failed to create transaction');
    }
  };

  // User Settings Modal (with profile upload placeholder - assume backend upload endpoint)
  const UserSettingsModal = () => (
    <div className={`modal-overlay ${showUserSettings ? 'active' : ''}`}>
      <div className="modal-content">
        <h2>User Settings</h2>
        {profileLoading ? <LoadingSpinner /> : (
          <>
            <input 
              type="text" 
              value={userProfile?.username || ''} 
              onChange={(e) => updateUserProfile({ username: e.target.value })}
              placeholder="Username"
            />
            <input type="file" hidden onChange={(e) => {
              // Upload logic: send to backend upload endpoint, get URL, then update profile
              const file = e.target.files[0];
              // Placeholder: assume upload returns URL
              const uploadedUrl = URL.createObjectURL(file); // Simulate
              updateUserProfile({ profile_image: uploadedUrl });
            }} />
            <button>Upload Profile Image</button>
            <div className="subscription-section">
              <h3>Subscribe to Tier</h3>
              <button onClick={() => subscribeToTier('Basic Reviewer')}>Basic Reviewer (300k IDR)</button>
              {/* Add other tiers */}
              <button onClick={claimRewards}>Claim Rewards</button>
            </div>
          </>
        )}
        <button onClick={() => setShowUserSettings(false)}>Close</button>
      </div>
    </div>
  );

  // Cart Modal (with full transaction creation)
  const CartModal = () => (
    <div className={`modal-overlay ${showCart ? 'active' : ''}`}>
      <div className="modal-content">
        <h2>Shopping Cart</h2>
        {cart.map(item => (
          <div key={item.id}>
            <p>{item.name} - Rp {item.price_idr}</p>
          </div>
        ))}
        <button onClick={() => {
          cart.forEach(item => createTransaction({
            buyer_id: userPrincipal,
            seller_id: item.seller_id,
            product_id: item.id,
            quantity: 1,
            total_amount_idr: BigInt(item.price_idr)
          }));
        }}>Checkout</button>
        <button onClick={() => setShowCart(false)}>Close</button>
      </div>
    </div>
  );

  // AI Consultation Modal
  const AIConsultationModal = () => (
    <div className={`modal-overlay ${showAIConsultation ? 'active' : ''}`}>
      <div className="modal-content">
        <h2>AI Consultation</h2>
        <div className="chat-window">
          {consultationMessages.map((msg, idx) => (
            <p key={idx} className={msg.role}>{msg.content}</p>
          ))}
        </div>
        <input 
          type="text" 
          onKeyPress={(e) => e.key === 'Enter' && sendConsultationMessage(e.target.value)}
          placeholder="Type your message..."
        />
        {consultationLoading && <LoadingSpinner />}
        <button onClick={() => setShowAIConsultation(false)}>Close</button>
      </div>
    </div>
  );

  // Product Detail Modal (with reviews)
  const ProductDetailModal = () => (
    <div className={`modal-overlay ${showProductDetail ? 'active' : ''}`}>
      <div className="modal-content">
        {selectedProduct && (
          <>
            <h2>{selectedProduct.name}</h2>
            {/* Reviews */}
            <button onClick={() => createReview({ product_id: selectedProduct.id, overall_rating: 5, detailed_review: 'Great!' })}>Submit Review</button>
          </>
        )}
        <button onClick={() => setShowProductDetail(false)}>Close</button>
      </div>
    </div>
  );

  // Order History Modal
  const OrderHistoryModal = () => (
    <div className={`modal-overlay ${showOrderHistory ? 'active' : ''}`}>
      <div className="modal-content">
        <h2>Order History</h2>
        {ordersLoading ? <LoadingSpinner /> : (
          orders.map(order => (
            <div key={order.transaction_id}>
              <p>Product: {order.product_id} - Status: {Object.keys(order.status)[0]}</p>
            </div>
          ))
        )}
        <button onClick={() => setShowOrderHistory(false)}>Close</button>
      </div>
    </div>
  );

  // Subscription Modal
  const SubscriptionModal = () => (
    <div className={`modal-overlay ${showSubscription ? 'active' : ''}`}>
      <div className="modal-content">
        <h2>Subscription Tiers</h2>
        {/* Tier options with subscribeToTier calls */}
        <button onClick={() => setShowSubscription(false)}>Close</button>
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
        </div>
      </div>
    );
  }

  return (
    <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
      <ErrorToast message={errorMessage} />
      
      {/* Navbar (with search bar) */}
      <nav className="navbar">
        <div className="navbar-content">
          <div className="logo-section">
            <div className="logo-link">
              <img src="./src/log1_.png" alt="Aromance" className="logo-image" />
              <span className="brand-name">Aromance</span>
            </div>
          </div>
          
          <input 
            type="text" 
            className="search-bar" 
            placeholder="Search by personality or family..." 
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
          />
          
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
            <button className="cta-button" onClick={handleWalletConnect}>
              <CustomIcons.Wallet /> Connect Wallet to Start
            </button>
          </div>
        )}

        {walletConnected && !consultationCompleted && (
          <div className="welcome-section">
            <h1>Get Started with AI Consultation</h1>
            <p>Let our AI analyze your personality and find the perfect fragrance for you</p>
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

        {/* AI Recommendations Section */}
        {consultationCompleted && (
          <ProductSection 
            title="AI Recommendations for You"
            products={aiRecommendations}
            isRecommended={true}
            showAIBadge={true}
            icon={CustomIcons.Robot}
            isLoading={recommendationsLoading}
          />
        )}

        {/* Personalized Products */}
        {consultationCompleted && personalizedProducts.length > 0 && (
          <ProductSection 
            title="You Might Like"
            products={personalizedProducts}
            icon={CustomIcons.Star}
            isLoading={recommendationsLoading}
          />
        )}

        {/* All Products */}
        <ProductSection 
          title="Other Products"
          products={otherProducts}
          icon={CustomIcons.Flower}
          showRefresh={true}
          onRefresh={handleRefreshOther}
          isLoading={recommendationsLoading}
        />

        {/* Platform Status (with agent health) */}
        <div className="platform-status">
          <h3>Platform Status</h3>
          <div className="status-grid">
            <div className="status-card">
              <CustomIcons.Robot />
              <h4>AI Agents</h4>
              <p>{backendConnected ? 'Ready' : 'Initializing'}</p>
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
          </div>
        </div>
      </main>

      {/* Modals */}
      <UserSettingsModal />
      <CartModal />
      <AIConsultationModal />
      <ProductDetailModal />
      <OrderHistoryModal />
      <SubscriptionModal />

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-brand">
              <img src="./src/log1_.png" alt="Aromance" className="footer-logo" />
              <span className="footer-brand-text">Aromance</span>
            </div>
            <div className="footer-copyright">
              © Aromance 2025 
            </div>
          </div>
          
          <div className="footer-center">
            <div className="footer-links">
              <a href="#" className="footer-link">Terms of Use</a>
              <a href="#" className="footer-link">Privacy Policy</a>
              <a href="#" className="footer-link">Protocol</a>
            </div>
          </div>
          
          <div className="footer-right">
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