import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import './App.css';

// ICP Backend Integration
const CANISTER_ID = process.env.CANISTER_ID_AROMANCE_BACKEND || 'bkyz2-fmaaa-aaaaa-qaaaq-cai';
const HOST = process.env.DFX_NETWORK === 'ic' ? 'https://icp-api.io' : 'http://localhost:4943';

// Main Wallet Address for all transactions
const MAIN_WALLET_ADDRESS = "afa05153e88aa30ec9af2ff13617ea9e57f47083ee67bfb62b6ad17b6097f390";

// AI Agent Endpoints
const AGENT_ENDPOINTS = {
  coordinator: 'http://127.0.0.1:8000',
  consultation: 'http://127.0.0.1:8001',
  recommendation: 'http://127.0.0.1:8002',
  analytics: 'http://127.0.0.1:8004',
  inventory: 'http://127.0.0.1:8005'
};

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
  )
};

const App = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showAIConsultation, setShowAIConsultation] = useState(false);
  const [showProductDetail, setShowProductDetail] = useState(false);
  const [showOrderHistory, setShowOrderHistory] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [userProfile, setUserProfile] = useState({
    username: '',
    profileImage: '',
    verificationTier: null
  });
  
  const [products, setProducts] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [personalizedProducts, setPersonalizedProducts] = useState([]);
  const [otherProducts, setOtherProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [actor, setActor] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [userWallet, setUserWallet] = useState(null);
  const [userDID, setUserDID] = useState(null);
  const [consultationCompleted, setConsultationCompleted] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Initialize ICP agent
  useEffect(() => {
    const initBackend = async () => {
      try {
        const agent = new HttpAgent({ host: HOST });
        
        if (process.env.DFX_NETWORK !== 'ic') {
          await agent.fetchRootKey();
        }

        const backendActor = Actor.createActor(idlFactory, {
          agent,
          canisterId: CANISTER_ID,
        });

        setActor(backendActor);

        const greeting = await backendActor.greet('Aromance User');
        console.log('Backend connection successful:', greeting);
        setBackendConnected(true);

        await loadBackendData(backendActor);
        
      } catch (error) {
        console.error('Failed to connect to backend:', error);
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
      
      const backendProducts = await backendActor.get_products();
      
      if (backendProducts && backendProducts.length > 0) {
        setProducts(backendProducts);
        setOtherProducts(backendProducts);
        
        if (userDID) {
          try {
            const recommendations = await backendActor.get_recommendations_for_user(userDID);
            if (recommendations && recommendations.length > 0) {
              setAiRecommendations(recommendations);
              
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
      setUserProfile(prev => ({
        ...prev,
        username: `User_${principal.slice(0, 8)}`
      }));
      console.log('Connected to wallet:', principal);
    }
  };

  const startAIConsultation = async () => {
    if (!walletConnected) {
      alert('Please connect your wallet first');
      return;
    }
    
    try {
      const userId = userWallet;
      const newSessionId = `session_${userId}_${Date.now()}`;
      setSessionId(newSessionId);
      
      // Start consultation with AI agent
      const response = await fetch(`${AGENT_ENDPOINTS.consultation}/consultation/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: newSessionId
        })
      });
      
      if (response.ok) {
        setShowAIConsultation(true);
      } else {
        console.error('Failed to start consultation');
        // Simulate consultation for demo
        setShowAIConsultation(true);
      }
    } catch (error) {
      console.error('Error starting consultation:', error);
      // Simulate consultation for demo
      setShowAIConsultation(true);
    }
  };

  const completeConsultation = async () => {
    setConsultationCompleted(true);
    setShowAIConsultation(false);
    
    // Simulate DID creation
    const simulatedDID = `did:aromance:${userWallet.slice(0, 8)}`;
    setUserDID(simulatedDID);
    
    // Generate AI recommendations (simulate)
    if (products.length > 0) {
      const shuffled = [...products].sort(() => 0.5 - Math.random());
      const recommendations = shuffled.slice(0, 5);
      const personalized = shuffled.slice(5, 10);
      
      setAiRecommendations(recommendations);
      setPersonalizedProducts(personalized);
    }
  };

  const refreshOtherProducts = () => {
    if (products.length > 0) {
      const shuffled = [...products].sort(() => 0.5 - Math.random());
      setOtherProducts(shuffled);
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

  const purchaseProduct = (product) => {
    // Create order
    const newOrder = {
      id: `order_${Date.now()}`,
      product,
      quantity: 1,
      total: product.price_idr,
      date: new Date().toISOString(),
      status: 'completed',
      canReview: true
    };
    
    setOrders([newOrder, ...orders]);
    
    // Remove from cart if exists
    removeFromCart(product.id);
    
    alert('Purchase successful! Check your order history.');
  };

  const checkout = () => {
    cart.forEach(item => {
      const newOrder = {
        id: `order_${Date.now()}_${item.id}`,
        product: item,
        quantity: item.quantity,
        total: item.price_idr * item.quantity,
        date: new Date().toISOString(),
        status: 'completed',
        canReview: true
      };
      setOrders(prev => [newOrder, ...prev]);
    });
    
    setCart([]);
    setShowCart(false);
    alert('Checkout successful! Check your order history.');
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

  const openProductDetail = (product) => {
    setSelectedProduct(product);
    setShowProductDetail(true);
  };

  const updateUserProfile = (field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const subscribeToTier = (tier) => {
    setUserProfile(prev => ({
      ...prev,
      verificationTier: tier
    }));
    setShowSubscriptionModal(false);
    alert(`Successfully subscribed to ${tier} tier!`);
  };

  const ProductCard = ({ product, isRecommended = false, showAIBadge = false }) => (
    <div className={`product-card ${isRecommended ? 'recommended' : ''}`}>
      <div className="product-image" onClick={() => openProductDetail(product)}>
        <img src={product.image_urls?.[0] || '/api/placeholder/300/300'} alt={product.name} />
        {showAIBadge && (
          <div className="ai-badge">
            <CustomIcons.Robot />
            <span>AI Pick</span>
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
        <div className="product-price">{formatPrice(product.price_idr)}</div>
        <div className="product-stock">Stock: {product.stock}</div>
        <div className="product-actions">
          <button 
            className="add-to-cart-btn"
            onClick={() => addToCart(product)}
          >
            <CustomIcons.Plus />
            <span>Add to Cart</span>
          </button>
          <button 
            className="buy-now-btn"
            onClick={() => purchaseProduct(product)}
          >
            Buy Now
          </button>
        </div>
      </div>
    </div>
  );

  const ProductSection = ({ title, products, isRecommended = false, showAIBadge = false, icon: Icon, showRefresh = false }) => (
    <div className="product-section">
      <div className="section-header">
        <h2 className="section-title">
          {Icon && <Icon />}
          {title}
        </h2>
        {showRefresh && (
          <button className="refresh-btn" onClick={refreshOtherProducts}>
            <CustomIcons.Refresh />
            <span>Refresh</span>
          </button>
        )}
      </div>
      <div className="products-container">
        <div className="products-scroll">
          {products.length > 0 ? products.map(product => (
            <ProductCard 
              key={product.id} 
              product={product} 
              isRecommended={isRecommended}
              showAIBadge={showAIBadge}
            />
          )) : (
            <div className="empty-products">
              <p>Platform sedang dalam tahap produksi.</p>
            </div>
          )}
        </div>
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
                <img src={selectedProduct.image_urls?.[0] || '/api/placeholder/400/400'} alt={selectedProduct.name} />
              </div>
              <div className="product-detail-info">
                <h3>{selectedProduct.brand}</h3>
                <h2>{selectedProduct.name}</h2>
                <div className="product-price-large">{formatPrice(selectedProduct.price_idr)}</div>
                <div className="product-details">
                  <p><strong>Fragrance Family:</strong> {selectedProduct.fragrance_family}</p>
                  <p><strong>Top Notes:</strong> {selectedProduct.top_notes?.join(', ')}</p>
                  <p><strong>Middle Notes:</strong> {selectedProduct.middle_notes?.join(', ')}</p>
                  <p><strong>Base Notes:</strong> {selectedProduct.base_notes?.join(', ')}</p>
                  <p><strong>Occasions:</strong> {selectedProduct.occasion?.join(', ')}</p>
                  <p><strong>Description:</strong> {selectedProduct.description}</p>
                  <p><strong>Stock:</strong> {selectedProduct.stock}</p>
                </div>
                <div className="product-actions-large">
                  <button 
                    className="add-to-cart-btn-large"
                    onClick={() => addToCart(selectedProduct)}
                  >
                    <CustomIcons.Plus />
                    Add to Cart
                  </button>
                  <button 
                    className="buy-now-btn-large"
                    onClick={() => purchaseProduct(selectedProduct)}
                  >
                    Buy Now
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Reviews Section - Only for purchased items */}
          <div className="reviews-section">
            <h3>Reviews</h3>
            {orders.some(order => order.product.id === selectedProduct?.id) ? (
              <div className="review-form">
                <textarea placeholder="Write your review here..." rows="4"></textarea>
                <div className="rating-input">
                  <span>Rating: </span>
                  {[1,2,3,4,5].map(star => (
                    <CustomIcons.Star key={star} className="star-input" />
                  ))}
                </div>
                <button className="submit-review-btn">Submit Review</button>
              </div>
            ) : (
              <p>You can only review products you've purchased.</p>
            )}
            
            <div className="existing-reviews">
              <div className="review-item">
                <div className="reviewer-info">
                  <strong>User123</strong>
                  <div className="rating">
                    {[1,2,3,4,5].map(star => (
                      <CustomIcons.Star key={star} className="star filled" />
                    ))}
                  </div>
                </div>
                <p>Great fragrance! Long-lasting and perfect for daily wear.</p>
              </div>
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
          {orders.length === 0 ? (
            <div className="empty-orders">
              <CustomIcons.Orders />
              <p>No orders yet</p>
              <p>Start shopping to see your orders here</p>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map(order => (
                <div key={order.id} className="order-item">
                  <img src={order.product.image_urls?.[0] || '/api/placeholder/80/80'} alt={order.product.name} />
                  <div className="order-info">
                    <h4>{order.product.name}</h4>
                    <p>{order.product.brand}</p>
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
          </div>
          
          <div className="subscription-tiers">
            <div className="tier-section">
              <h3>Reviewer Tiers</h3>
              <div className="tier-cards">
                <div className="tier-card">
                  <h4>Basic Reviewer</h4>
                  <div className="tier-price">Rp 300,000</div>
                  <div className="tier-return">6% Annual Return</div>
                  <ul>
                    <li>Write verified reviews</li>
                    <li>Basic trust badge</li>
                    <li>Community access</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Basic Reviewer')}
                  >
                    Subscribe
                  </button>
                </div>
                
                <div className="tier-card premium">
                  <h4>Premium Reviewer</h4>
                  <div className="tier-price">Rp 950,000</div>
                  <div className="tier-return">7.5% Annual Return</div>
                  <ul>
                    <li>All Basic features</li>
                    <li>Premium trust badge</li>
                    <li>Higher review priority</li>
                    <li>Early access to products</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Premium Reviewer')}
                  >
                    Subscribe
                  </button>
                </div>
                
                <div className="tier-card elite">
                  <h4>Elite Reviewer</h4>
                  <div className="tier-price">Rp 1,900,000</div>
                  <div className="tier-return">9% Annual Return</div>
                  <ul>
                    <li>All Premium features</li>
                    <li>Elite trust badge</li>
                    <li>Influence on platform</li>
                    <li>Exclusive events</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Elite Reviewer')}
                  >
                    Subscribe
                  </button>
                </div>
              </div>
            </div>
            
            <div className="tier-section">
              <h3>Seller Tiers</h3>
              <div className="tier-cards">
                <div className="tier-card">
                  <h4>Basic Seller</h4>
                  <div className="tier-price">Rp 500,000</div>
                  <div className="tier-return">6% Annual Return</div>
                  <ul>
                    <li>Sell products</li>
                    <li>Basic analytics</li>
                    <li>Standard commission</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Basic Seller')}
                  >
                    Subscribe
                  </button>
                </div>
                
                <div className="tier-card premium">
                  <h4>Premium Seller</h4>
                  <div className="tier-price">Rp 1,500,000</div>
                  <div className="tier-return">7.5% Annual Return</div>
                  <ul>
                    <li>All Basic features</li>
                    <li>Advanced analytics</li>
                    <li>Reduced commission</li>
                    <li>Priority support</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Premium Seller')}
                  >
                    Subscribe
                  </button>
                </div>
                
                <div className="tier-card elite">
                  <h4>Elite Seller</h4>
                  <div className="tier-price">Rp 3,000,000</div>
                  <div className="tier-return">9% Annual Return</div>
                  <ul>
                    <li>All Premium features</li>
                    <li>Lowest commission</li>
                    <li>Featured placement</li>
                    <li>White-label options</li>
                  </ul>
                  <button 
                    className="tier-btn"
                    onClick={() => subscribeToTier('Elite Seller')}
                  >
                    Subscribe
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="payment-info">
            <p><strong>Payment Address:</strong> {MAIN_WALLET_ADDRESS}</p>
            <p>All payments are processed through your connected wallet and staked on ICP blockchain.</p>
          </div>
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
          {/* Profile Section */}
          {walletConnected && (
            <div className="settings-section">
              <h3>Profile</h3>
              <div className="profile-edit">
                <div className="profile-image-edit">
                  <img 
                    src={userProfile.profileImage || '/api/placeholder/100/100'} 
                    alt="Profile" 
                    className="profile-image"
                  />
                  <button className="edit-image-btn">
                    <CustomIcons.Settings />
                  </button>
                </div>
                <div className="profile-info-edit">
                  <label>Username:</label>
                  <input 
                    type="text"
                    value={userProfile.username}
                    onChange={(e) => updateUserProfile('username', e.target.value)}
                    placeholder="Enter username"
                  />
                  {userProfile.verificationTier && (
                    <div className="verification-badge">
                      <CustomIcons.Crown />
                      <span>{userProfile.verificationTier}</span>
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
              <CustomIcons.Orders /> View Order History
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

              <div className="consultation-status">
                <p>🤖 AI Consultation System Ready...</p>
                <p>🔐 Creating your Decentralized Identity...</p>
                <p>✨ Preparing personalized recommendations...</p>
                <div className="loading-bar">
                  <div className="loading-progress"></div>
                </div>
              </div>

              <button 
                className="consultation-btn"
                onClick={completeConsultation}
              >
                Complete AI Consultation
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
                <p>Payment to: {MAIN_WALLET_ADDRESS.slice(0, 20)}...</p>
                <button className="checkout-btn" onClick={checkout}>
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
            <img src="./src/log1_.png" alt="Aromance" style={{ width: "67px", height: "67px" }} />
          </div>
          <div className="loading-text">Loading The App..</div>
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
              <img src="./src/log1_.png" alt="Aromance" className="logo-image" />
              <span className="brand-name">Aromance</span>
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
            <button className="cta-button" onClick={startAIConsultation}>
              <CustomIcons.Robot /> Start AI Consultation
            </button>
          </div>
        )}

        {/* AI Recommendations Section */}
        {consultationCompleted && aiRecommendations.length > 0 && (
          <ProductSection 
            title="AI Recommendations for You"
            products={aiRecommendations}
            isRecommended={true}
            showAIBadge={true}
            icon={CustomIcons.Robot}
          />
        )}

        {/* Personalized Products */}
        {consultationCompleted && personalizedProducts.length > 0 && (
          <ProductSection 
            title="You Might Like"
            products={personalizedProducts}
            icon={CustomIcons.Star}
          />
        )}

        {/* All Products */}
        <ProductSection 
          title="Other Products"
          products={otherProducts}
          icon={CustomIcons.Flower}
          showRefresh={true}
        />

        {/* Platform Status */}
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