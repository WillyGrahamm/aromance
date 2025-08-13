import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import './App.css';

// ICP Backend Integration
const CANISTER_ID = process.env.CANISTER_ID_AROMANCE_BACKEND || 'bkyz2-fmaaa-aaaaa-qaaaq-cai';
const HOST = process.env.DFX_NETWORK === 'ic' ? 'https://icp-api.io' : 'http://localhost:4943';

// Main Wallet Address for all transactions
const MAIN_WALLET_ADDRESS = "afa05153e88aa30ec9af2ff13617ea9e57f47083ee67bfb62b6ad17b6097f390";

// IDL Factory for backend canister
const idlFactory = ({ IDL }) => {
  const Product = IDL.Record({
    'id': IDL.Text,
    'name': IDL.Text,
    'brand': IDL.Text,
    'price_idr': IDL.Nat64,
    'fragrance_family': IDL.Text,
    'top_notes': IDL.Vec(IDL.Text),
    'middle_notes': IDL.Vec(IDL.Text),
    'base_notes': IDL.Vec(IDL.Text),
    'occasion': IDL.Vec(IDL.Text),
    'season': IDL.Vec(IDL.Text),
    'description': IDL.Text,
    'halal_certified': IDL.Bool,
    'image_urls': IDL.Vec(IDL.Text),
    'stock': IDL.Nat32,
    'verified': IDL.Bool,
    'ai_analyzed': IDL.Bool,
    'personality_matches': IDL.Vec(IDL.Text),
    'seller_id': IDL.Text,
    'created_at': IDL.Nat64,
    'updated_at': IDL.Nat64,
  });

  const AIRecommendation = IDL.Record({
    'recommendation_id': IDL.Text,
    'user_id': IDL.Text,
    'product_id': IDL.Text,
    'match_score': IDL.Float64,
    'reasoning': IDL.Text,
    'confidence_level': IDL.Float64,
    'generated_at': IDL.Nat64,
  });

  return IDL.Service({
    'get_products': IDL.Func([], [IDL.Vec(Product)], ['query']),
    'get_recommendations_for_user': IDL.Func([IDL.Text], [IDL.Vec(AIRecommendation)], ['query']),
    'greet': IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_aromance_info': IDL.Func([], [IDL.Text], ['query']),
  });
};

// Plug Wallet Integration
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
  Search: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14Z" fill="currentColor"/>
    </svg>
  ),
  Robot: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H14A7,7 0 0,1 21,14H22A1,1 0 0,1 23,15V18A1,1 0 0,1 22,19H21A7,7 0 0,1 14,26H10A7,7 0 0,1 3,19H2A1,1 0 0,1 1,18V15A1,1 0 0,1 2,14H3A7,7 0 0,1 10,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M12,4A0.5,0.5 0 0,0 11.5,4.5A0.5,0.5 0 0,0 12,5A0.5,0.5 0 0,0 12.5,4.5A0.5,0.5 0 0,0 12,4M10,9A5,5 0 0,0 5,14V17A5,5 0 0,0 10,22H14A5,5 0 0,0 19,17V14A5,5 0 0,0 14,9H10M8.5,11A1.5,1.5 0 0,1 10,12.5A1.5,1.5 0 0,1 8.5,14A1.5,1.5 0 0,1 7,12.5A1.5,1.5 0 0,1 8.5,11M15.5,11A1.5,1.5 0 0,1 17,12.5A1.5,1.5 0 0,1 15.5,14A1.5,1.5 0 0,1 14,12.5A1.5,1.5 0 0,1 15.5,11M12,16.5C13.25,16.5 14.29,17.17 14.71,18.1C14.21,18.5 13.64,18.75 13,18.75H11C10.36,18.75 9.79,18.5 9.29,18.1C9.71,17.17 10.75,16.5 12,16.5Z" fill="currentColor"/>
    </svg>
  ),
  Star: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.46,13.97L5.82,21L12,17.27Z" fill="currentColor"/>
    </svg>
  ),
  Flower: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,2A3,3 0 0,1 15,5C15,5.8 14.7,6.5 14.2,7C15.3,7.3 16,8.3 16,9.5A3.5,3.5 0 0,1 12.5,13H12.35C12.75,13.6 13,14.3 13,15A3,3 0 0,1 10,18C9.2,18 8.5,17.7 8,17.2C7.7,18.3 6.7,19 5.5,19A3.5,3.5 0 0,1 2,15.5C2,14.4 2.7,13.4 3.8,13.1C3.3,12.4 3,11.7 3,11A3,3 0 0,1 6,8C6.8,8 7.5,8.3 8,8.8C8.3,7.7 9.3,7 10.5,7A3.5,3.5 0 0,1 14,10.5C14,11.6 13.3,12.6 12.2,12.9C12.7,13.6 13,14.3 13,15A3,3 0 0,1 10,18L12,2Z" fill="currentColor"/>
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
    <svg viewBox="0 24 24" className="custom-icon">
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
      <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.98C19.47,12.66 19.5,12.34 19.5,12C19.5,11.66 19.47,11.34 19.43,11.02L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.65 15.48,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.52,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11.02C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.66 4.57,12.98L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.52,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.48,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.98Z" fill="currentColor"/>
    </svg>
  ),
  Notification: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M21,19V20H3V19L5,17V11C5,7.9 7.03,5.17 10,4.29C10,4.19 10,4.1 10,4A2,2 0 0,1 12,2A2,2 0 0,1 14,4C14,4.1 14,4.19 14,4.29C16.97,5.17 19,7.9 19,11V17L21,19M14,21A2,2 0 0,1 12,23A2,2 0 0,1 10,21" fill="currentColor"/>
    </svg>
  ),
  Privacy: () => (
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V16H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z" fill="currentColor"/>
    </svg>
  )
};

const App = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showAIConsultation, setShowAIConsultation] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [products, setProducts] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [personalizedProducts, setPersonalizedProducts] = useState([]);
  const [otherProducts, setOtherProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [actor, setActor] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [userWallet, setUserWallet] = useState(null);
  const [userDID, setUserDID] = useState(null);
  const [aiSettings, setAiSettings] = useState({
    personalizedRecommendations: true,
    dataSharing: false,
    aiTraining: true,
    contextualSuggestions: true
  });
  const [notificationSettings, setNotificationSettings] = useState({
    newRecommendations: true,
    priceDrops: true,
    orderUpdates: true,
    weeklyDigest: false,
    promotions: false
  });
  const [privacySettings, setPrivacySettings] = useState({
    profileVisibility: 'private',
    dataCollection: 'minimal',
    thirdPartySharing: false,
    analyticsOptOut: false
  });

  // Initialize ICP agent
  useEffect(() => {
    const initBackend = async () => {
      try {
        const agent = new HttpAgent({ host: HOST });
        
        // Fetch root key for local development
        if (process.env.DFX_NETWORK !== 'ic') {
          await agent.fetchRootKey();
        }

        const backendActor = Actor.createActor(idlFactory, {
          agent,
          canisterId: CANISTER_ID,
        });

        setActor(backendActor);

        // Test connection
        const greeting = await backendActor.greet('Aromance User');
        console.log('Backend connection successful:', greeting);
        setBackendConnected(true);

        // Load data from backend (will be empty for production)
        await loadBackendData(backendActor);
        
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        // No fallback data for production
        setProducts([]);
        setOtherProducts([]);
        setPersonalizedProducts([]);
      }
      setLoading(false);
    };

    initBackend();
  }, []);

  const loadBackendData = async (backendActor) => {
    try {
      setLoading(true);
      
      // Fetch products from backend
      const backendProducts = await backendActor.get_products();
      
      if (backendProducts && backendProducts.length > 0) {
        setProducts(backendProducts);
        setOtherProducts(backendProducts);
        
        // Try to get AI recommendations
        if (userDID) {
          try {
            const recommendations = await backendActor.get_recommendations_for_user(userDID);
            if (recommendations && recommendations.length > 0) {
              setAiRecommendations(recommendations);
              
              // Get recommended products
              const recProductIds = recommendations.map(r => r.product_id);
              const recProducts = backendProducts.filter(p => recProductIds.includes(p.id));
              setPersonalizedProducts(recProducts);
            }
          } catch (error) {
            console.log('No AI recommendations available yet');
          }
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading backend data:', error);
      setLoading(false);
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

  const handleAIConsultationStart = async () => {
    if (!walletConnected) {
      alert('Please connect your wallet first');
      return;
    }
    
    setShowAIConsultation(true);
    // Here we would normally trigger the Fetch.ai agents to start consultation
    // For now, we'll simulate creating a DID after consultation
    
    // Simulate DID creation after AI consultation
    setTimeout(() => {
      const simulatedDID = `did:aromance:${userWallet.slice(0, 8)}`;
      setUserDID(simulatedDID);
      console.log('User DID created:', simulatedDID);
    }, 3000);
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

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price_idr * item.quantity), 0);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(price);
  };

  const ProductCard = ({ product, isRecommended = false }) => (
    <div className={`product-card ${isRecommended ? 'recommended' : ''}`}>
      <div className="product-image">
        <img src={product.image_urls?.[0] || '/api/placeholder/300/300'} alt={product.name} />
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
        <h3 className="product-name">{product.name}</h3>
        <div className="product-family">{product.fragrance_family}</div>
        <div className="product-notes">
          <div className="notes-section">
            <span className="notes-label">Top:</span>
            <span className="notes-list">{product.top_notes?.slice(0, 2).join(', ') || 'N/A'}</span>
          </div>
        </div>
        <div className="product-price">{formatPrice(product.price_idr)}</div>
        <div className="product-stock">Stock: {product.stock}</div>
        <button 
          className="add-to-cart-btn"
          onClick={() => addToCart(product)}
        >
          <CustomIcons.Plus />
          <span>Tambah ke Keranjang</span>
        </button>
      </div>
    </div>
  );

  const ProductSection = ({ title, products, isRecommended = false, icon: Icon }) => (
    <div className="product-section">
      <h2 className="section-title">
        {Icon && <Icon />}
        {title}
      </h2>
      <div className="products-container">
        <div className="products-scroll">
          {products.length > 0 ? products.map(product => (
            <ProductCard 
              key={product.id} 
              product={product} 
              isRecommended={isRecommended}
            />
          )) : (
            <div className="empty-products">
              <p>Belum ada produk tersedia. Platform sedang dalam tahap produksi.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

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
            {!userDID ? (
              <button 
                className="setting-btn" 
                onClick={handleAIConsultationStart}
                disabled={!walletConnected}
              >
                <CustomIcons.Robot /> Start AI Consultation & Create Identity
              </button>
            ) : (
              <div className="setting-item">
                <div className="user-avatar">
                  <CustomIcons.Robot />
                </div>
                <div className="user-info">
                  <div className="user-name">Consultation Completed</div>
                  <div className="user-status">Identity Created: {userDID}</div>
                </div>
              </div>
            )}
          </div>
          
          {/* Identity & Verification */}
          <div className="settings-section">
            <h3>Identity & Verification</h3>
            <button className="setting-btn" disabled={!userDID}>
              Setup Proof of Stake Reviewer (Rp 300K - 1.9M)
            </button>
            <button className="setting-btn" disabled={!userDID}>
              Become Verified Seller (Rp 500K - 3M)
            </button>
            <button className="setting-btn" disabled={!userDID}>
              Export Decentralized Identity
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

          {/* AI Consultation Settings */}
          <div className="settings-section">
            <h3><CustomIcons.Robot /> AI Consultation Settings</h3>
            <div className="setting-toggle">
              <span>Personalized Recommendations</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={aiSettings.personalizedRecommendations}
                  onChange={(e) => setAiSettings({...aiSettings, personalizedRecommendations: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Allow Data Sharing for Better Recommendations</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={aiSettings.dataSharing}
                  onChange={(e) => setAiSettings({...aiSettings, dataSharing: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Help Train AI Models (Anonymous)</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={aiSettings.aiTraining}
                  onChange={(e) => setAiSettings({...aiSettings, aiTraining: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Contextual Suggestions</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={aiSettings.contextualSuggestions}
                  onChange={(e) => setAiSettings({...aiSettings, contextualSuggestions: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          {/* Notification Preferences */}
          <div className="settings-section">
            <h3><CustomIcons.Notification /> Notification Preferences</h3>
            <div className="setting-toggle">
              <span>New AI Recommendations</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notificationSettings.newRecommendations}
                  onChange={(e) => setNotificationSettings({...notificationSettings, newRecommendations: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Price Drop Alerts</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notificationSettings.priceDrops}
                  onChange={(e) => setNotificationSettings({...notificationSettings, priceDrops: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Order Updates</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notificationSettings.orderUpdates}
                  onChange={(e) => setNotificationSettings({...notificationSettings, orderUpdates: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Weekly Digest</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notificationSettings.weeklyDigest}
                  onChange={(e) => setNotificationSettings({...notificationSettings, weeklyDigest: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Promotions & Offers</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notificationSettings.promotions}
                  onChange={(e) => setNotificationSettings({...notificationSettings, promotions: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          {/* Data & Privacy */}
          <div className="settings-section">
            <h3><CustomIcons.Privacy /> Data & Privacy</h3>
            <div className="setting-item">
              <span>Profile Visibility</span>
              <select 
                value={privacySettings.profileVisibility} 
                onChange={(e) => setPrivacySettings({...privacySettings, profileVisibility: e.target.value})}
                className="setting-select"
              >
                <option value="private">Private</option>
                <option value="friends">Friends Only</option>
                <option value="public">Public</option>
              </select>
            </div>
            <div className="setting-item">
              <span>Data Collection Level</span>
              <select 
                value={privacySettings.dataCollection} 
                onChange={(e) => setPrivacySettings({...privacySettings, dataCollection: e.target.value})}
                className="setting-select"
              >
                <option value="minimal">Minimal</option>
                <option value="standard">Standard</option>
                <option value="enhanced">Enhanced (Better Recommendations)</option>
              </select>
            </div>
            <div className="setting-toggle">
              <span>Allow Third-Party Data Sharing</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={privacySettings.thirdPartySharing}
                  onChange={(e) => setPrivacySettings({...privacySettings, thirdPartySharing: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-toggle">
              <span>Opt-out of Analytics</span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={privacySettings.analyticsOptOut}
                  onChange={(e) => setPrivacySettings({...privacySettings, analyticsOptOut: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <button className="setting-btn">
              <CustomIcons.Privacy /> Export My Data
            </button>
            <button className="setting-btn">
              <CustomIcons.Delete /> Delete My Account & Data
            </button>
          </div>
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
                  <CustomIcons.Privacy />
                  <h4>Privacy Protected</h4>
                  <p>Your data is secured with Decentralized Identity</p>
                </div>
                <div className="info-card">
                  <CustomIcons.Star />
                  <h4>Verified Results</h4>
                  <p>Get recommendations from verified sellers only</p>
                </div>
              </div>

              <div className="consultation-status">
                <p>⏳ Connecting to Fetch.ai agents...</p>
                <p>🤖 Initializing AI consultation system...</p>
                <p>🔐 Preparing to create your Decentralized Identity...</p>
                <div className="loading-bar">
                  <div className="loading-progress"></div>
                </div>
              </div>

              <button 
                className="consultation-btn"
                onClick={() => {
                  // Here would integrate with Fetch.ai agents
                  alert('AI Consultation will be integrated with Fetch.ai agents system');
                  setShowAIConsultation(false);
                }}
              >
                Start Consultation with AI
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
            Keranjang Belanja
          </h2>
          <button className="close-btn" onClick={() => setShowCart(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          {cart.length === 0 ? (
            <div className="empty-cart">
              <CustomIcons.Cart />
              <p>Keranjang belanja masih kosong</p>
              <p>Platform sedang dalam tahap produksi</p>
              <button className="browse-btn" onClick={() => setShowCart(false)}>
                Jelajahi Platform
              </button>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <img src={item.image_urls?.[0] || '/api/placeholder/80/80'} alt={item.name} className="cart-item-image" />
                    <div className="cart-item-info">
                      <h4>{item.name}</h4>
                      <p>{item.brand}</p>
                      <p className="cart-item-price">{formatPrice(item.price_idr)}</p>
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
                <p>All payments go to main wallet: {MAIN_WALLET_ADDRESS.slice(0, 20)}...</p>
                <button className="checkout-btn">
                  <CustomIcons.Wallet />
                  Checkout with Plug Wallet
                </button>
              </div>
            </>
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
            <CustomIcons.Flower />
          </div>
          <div className="loading-text">Memuat Aromance Marketplace...</div>
          <div className="loading-bar">
            <div className="loading-progress"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-content">
          <div className="logo-section">
            <div className="logo-link">
              <img src="/log_.png" alt="Aromance" className="logo-image" />
              <span className="brand-name">Aromance</span>
            </div>
          </div>
          
          <div className="nav-center">
            <div className="search-bar">
              <input 
                type="text" 
                placeholder="Cari parfum, brand, atau aroma..."
                className="search-input"
              />
              <button className="search-btn">
                <CustomIcons.Search />
              </button>
            </div>
          </div>
          
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
        <div className="welcome-section">
          <h1>Selamat Datang di Aromance 🌸</h1>
          <p>Platform marketplace parfum terdesentralisasi dengan AI consultation</p>
          {!walletConnected && (
            <button className="cta-button" onClick={handleWalletConnect}>
              <CustomIcons.Wallet /> Connect Wallet to Start
            </button>
          )}
          {walletConnected && !userDID && (
            <button className="cta-button" onClick={handleAIConsultationStart}>
              <CustomIcons.Robot /> Start AI Consultation
            </button>
          )}
        </div>

        {/* AI Recommendations Section */}
        {aiRecommendations.length > 0 && (
          <ProductSection 
            title="Rekomendasi AI untuk Anda"
            products={aiRecommendations.map(rec => 
              products.find(p => p.id === rec.product_id)
            ).filter(Boolean)}
            isRecommended={true}
            icon={CustomIcons.Robot}
          />
        )}

        {/* Personalized Products */}
        {personalizedProducts.length > 0 && (
          <ProductSection 
            title="Yang Mungkin Anda Suka"
            products={personalizedProducts}
            icon={CustomIcons.Star}
          />
        )}

        {/* All Products */}
        <ProductSection 
          title="Parfum Tersedia"
          products={otherProducts}
          icon={CustomIcons.Flower}
        />

        {/* Platform Status */}
        <div className="platform-status">
          <h3>Status Platform</h3>
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
              <CustomIcons.Privacy />
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

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-brand">
              <img src="/log_.png" alt="Aromance" className="footer-logo" />
              <span className="footer-brand-text">Aromance</span>
            </div>
            <div className="footer-copyright">
              © Aromance 2025 - NextGen Agents Hackathon
            </div>
          </div>
          
          <div className="footer-center">
            <div className="footer-links">
              <a href="#" className="footer-link">Terms of Use</a>
              <a href="#" className="footer-link">Privacy Policy</a>
              <a href="#" className="footer-link">Protocols</a>
              <a href="#" className="footer-link">Fetch.ai Integration</a>
            </div>
          </div>
          
          <div className="footer-right">
            <a href="#" className="footer-social">
              <CustomIcons.Star />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;