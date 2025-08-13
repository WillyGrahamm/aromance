import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import './App.css';

// ICP Backend Integration
const CANISTER_ID = process.env.CANISTER_ID_AROMANCE_BACKEND || 'bkyz2-fmaaa-aaaaa-qaaaq-cai';
const HOST = process.env.DFX_NETWORK === 'ic' ? 'https://icp-api.io' : 'http://localhost:4943';

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
    <svg viewBox="0 0 24 24" className="custom-icon">
      <path d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z" fill="currentColor"/>
    </svg>
  )
};

const App = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [showCart, setShowCart] = useState(false);
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

        // Load data from backend
        await loadBackendData(backendActor);
        
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        // Fallback to sample data
        loadSampleData();
      }
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
        
        // Try to get AI recommendations (will fail if user not set up)
        try {
          const recommendations = await backendActor.get_recommendations_for_user('guest_user');
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
        
      } else {
        // If no products in backend, add sample data
        loadSampleData();
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading backend data:', error);
      loadSampleData();
    }
  };

  const loadSampleData = () => {
    // Sample data for testing when backend is empty
    const sampleProducts = [
      {
        id: 'prod_1',
        name: 'Eternal Bloom',
        brand: 'Nature Essence',
        price_idr: 450000,
        fragrance_family: 'Floral',
        top_notes: ['Rose', 'Jasmine', 'Bergamot'],
        middle_notes: ['Peony', 'Lily', 'Orange Blossom'],
        base_notes: ['Musk', 'Sandalwood', 'Vanilla'],
        occasion: ['Date', 'Evening', 'Special'],
        season: ['Spring', 'Summer'],
        description: 'Parfum floral yang elegan dengan sentuhan romantis untuk momen-momen istimewa.',
        halal_certified: true,
        image_urls: ['https://via.placeholder.com/300x300/ffc107/ffffff?text=Eternal+Bloom'],
        stock: 25,
        verified: true,
        ai_analyzed: true,
        seller_id: 'seller_1',
        personality_matches: ['Romantic', 'Elegant', 'Sophisticated'],
        created_at: Date.now(),
        updated_at: Date.now()
      },
      {
        id: 'prod_2', 
        name: 'Urban Mystic',
        brand: 'City Scents',
        price_idr: 320000,
        fragrance_family: 'Woody Oriental',
        top_notes: ['Lemon', 'Black Pepper', 'Pink Pepper'],
        middle_notes: ['Cedar', 'Vetiver', 'Geranium'],
        base_notes: ['Amber', 'Patchouli', 'Leather'],
        occasion: ['Office', 'Daily', 'Professional'],
        season: ['Autumn', 'Winter'],
        description: 'Parfum maskulin dengan karakter kuat untuk profesional muda yang percaya diri.',
        halal_certified: true,
        image_urls: ['https://via.placeholder.com/300x300/333333/ffffff?text=Urban+Mystic'],
        stock: 18,
        verified: true,
        ai_analyzed: true,
        seller_id: 'seller_2',
        personality_matches: ['Professional', 'Confident', 'Modern'],
        created_at: Date.now(),
        updated_at: Date.now()
      },
      {
        id: 'prod_3',
        name: 'Fresh Citrus Burst',
        brand: 'Tropical Vibes',
        price_idr: 280000,
        fragrance_family: 'Fresh Citrus',
        top_notes: ['Grapefruit', 'Lemon', 'Lime'],
        middle_notes: ['Mint', 'Green Apple', 'Sea Salt'],
        base_notes: ['White Musk', 'Cedarwood'],
        occasion: ['Daily', 'Sport', 'Casual'],
        season: ['Spring', 'Summer'],
        description: 'Parfum segar dan energik untuk aktivitas sehari-hari yang penuh semangat.',
        halal_certified: true,
        image_urls: ['https://via.placeholder.com/300x300/00bcd4/ffffff?text=Citrus+Burst'],
        stock: 32,
        verified: true,
        ai_analyzed: true,
        seller_id: 'seller_3',
        personality_matches: ['Energetic', 'Casual', 'Sporty'],
        created_at: Date.now(),
        updated_at: Date.now()
      }
    ];

    setProducts(sampleProducts);
    setOtherProducts(sampleProducts);
    setPersonalizedProducts(sampleProducts.slice(0, 2));
    setLoading(false);
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
        <img src={product.image_urls[0]} alt={product.name} />
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
            <span className="notes-list">{product.top_notes.slice(0, 2).join(', ')}</span>
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
          {products.map(product => (
            <ProductCard 
              key={product.id} 
              product={product} 
              isRecommended={isRecommended}
            />
          ))}
        </div>
      </div>
    </div>
  );

  const UserSettingsModal = () => (
    <div className={`modal-overlay fullscreen-modal ${showUserSettings ? 'active' : ''}`}>
      <div className="modal-content fullscreen-content">
        <div className="modal-header">
          <h2>User Settings</h2>
          <button className="close-btn" onClick={() => setShowUserSettings(false)}>
            <CustomIcons.Close />
          </button>
        </div>
        <div className="modal-body">
          <div className="settings-section">
            <h3>Connection Status</h3>
            <div className={`connection-status ${backendConnected ? 'connected' : 'disconnected'}`}>
              <div className="status-indicator"></div>
              <span>{backendConnected ? 'Connected to ICP Backend' : 'Backend Disconnected'}</span>
            </div>
          </div>
          
          <div className="settings-section">
            <h3>Profil</h3>
            <div className="setting-item">
              <div className="user-avatar">
                <CustomIcons.User />
              </div>
              <div className="user-info">
                <div className="user-name">Guest User</div>
                <div className="user-status">Belum Terverifikasi</div>
              </div>
            </div>
          </div>
          
          <div className="settings-section">
            <h3>Identity & Verification</h3>
            <button className="setting-btn">Setup Decentralized Identity</button>
            <button className="setting-btn">Setup Wallet Connection</button>
            <button className="setting-btn">Menjadi Proof of Stake Reviewer</button>
            <button className="setting-btn">Menjadi Verified Seller</button>
          </div>
          
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
            <button className="setting-btn">AI Consultation Settings</button>
            <button className="setting-btn">Notification Preferences</button>
          </div>
          
          <div className="settings-section">
            <h3>Data & Privacy</h3>
            <button className="setting-btn">Data Permissions</button>
            <button className="setting-btn">Privacy Settings</button>
            <button className="setting-btn">Export My Data</button>
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
              <button className="browse-btn" onClick={() => setShowCart(false)}>
                Jelajahi Produk
              </button>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <img src={item.image_urls[0]} alt={item.name} className="cart-item-image" />
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
                <button className="checkout-btn">
                  <CustomIcons.Star />
                  Checkout
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
              <CustomIcons.Flower />
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
          title="Parfum Lainnya"
          products={otherProducts}
          icon={CustomIcons.Flower}
        />
      </main>

      {/* Modals */}
      <UserSettingsModal />
      <CartModal />

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-brand">
              <CustomIcons.Flower />
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
              <a href="#" className="footer-link">Protocols</a>
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