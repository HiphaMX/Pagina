import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Leaf, Droplets, HeartPulse, Activity, ShieldCheck, ShoppingCart, X, Plus, Minus, Trash2 } from 'lucide-react';

const FlavorCard = ({ flavor, idx, onAddToCart }) => {
  const [selectedLine, setSelectedLine] = useState('Fit 0');
  const price = selectedLine === 'Fit 0' ? 45 : 55;

  return (
    <motion.div 
      style={{ 
        padding: '2rem 1rem', textAlign: 'center', 
        background: 'rgba(255, 255, 255, 0.5)', 
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        border: '1px solid rgba(255, 255, 255, 0.8)',
        borderRadius: '24px', 
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.05)', 
        display: 'flex', flexDirection: 'column', alignItems: 'center' 
      }}
      whileHover={{ scale: 1.05, boxShadow: '0 20px 25px -5px rgba(31, 38, 135, 0.1)' }}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: idx * 0.1 }}
    >
      <motion.div 
        style={{ width: '100%', height: '240px', marginBottom: '1.5rem', position: 'relative' }}
        animate={{ y: [-10, 10, -10] }}
        transition={{ repeat: Infinity, duration: 4 + (idx % 3), ease: "easeInOut" }}
      >
        {flavor.image ? (
           <img src={flavor.image} alt={flavor.name} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 20px 30px rgba(0,0,0,0.2))' }} />
        ) : (
          <div style={{ width: '100%', height: '100%', background: flavor.color, borderRadius: '40px' }}></div>
        )}
      </motion.div>
      <h3 style={{ fontSize: '1.5rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, color: '#101729', marginBottom: '1rem' }}>{flavor.name}</h3>
      
      {/* Selector de Línea y Precio */}
      <div style={{ width: '100%', background: '#f8fafc', padding: '1rem', borderRadius: '16px', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <button 
            onClick={() => setSelectedLine('Fit 0')}
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.875rem', fontWeight: 600, borderRadius: '8px', border: '1px solid #98BC3C', background: selectedLine === 'Fit 0' ? '#98BC3C' : 'transparent', color: selectedLine === 'Fit 0' ? 'white' : '#98BC3C', cursor: 'pointer', transition: 'all 0.2s' }}
          >Fit 0</button>
          <button 
            onClick={() => setSelectedLine('ProT')}
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.875rem', fontWeight: 600, borderRadius: '8px', border: '1px solid var(--primary)', background: selectedLine === 'ProT' ? 'var(--primary)' : 'transparent', color: selectedLine === 'ProT' ? 'white' : 'var(--primary)', cursor: 'pointer', transition: 'all 0.2s' }}
          >ProT</button>
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#101729' }}>${price}.00 <span style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: 400 }}>MXN</span></div>
      </div>

      <button 
        onClick={() => onAddToCart({ ...flavor, line: selectedLine, price })}
        className="btn btn-primary"
        style={{ width: '100%', padding: '0.875rem', borderRadius: '999px', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
      >
        <ShoppingCart size={18} /> Añadir
      </button>
    </motion.div>
  );
};

function App() {
  const [scrolled, setScrolled] = useState(false);
  const dragConstraintsRef = useRef(null);
  const [hoveredPopsicle, setHoveredPopsicle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ nombre: '', email: '', telefono: '', mensaje: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [legalModal, setLegalModal] = useState(null); // 'privacy' or 'terms'
  
  // Cart state
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const addToCart = (item) => {
    setCart(prev => {
      const existing = prev.find(i => i.name === item.name && i.line === item.line);
      if (existing) {
        return prev.map(i => i === existing ? { ...i, quantity: i.quantity + 1 } : i);
      }
      return [...prev, { ...item, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  const updateCartQuantity = (idx, delta) => {
    setCart(prev => {
      const newCart = [...prev];
      newCart[idx].quantity += delta;
      if (newCart[idx].quantity <= 0) {
        newCart.splice(idx, 1);
      }
      return newCart;
    });
  };

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);


  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await fetch('https://www.hipha.mx/api/contact/healthyice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        setSubmitSuccess(true);
        setTimeout(() => {
          setIsModalOpen(false);
          setSubmitSuccess(false);
          setFormData({ nombre: '', email: '', telefono: '', mensaje: '' });
        }, 3000);
      } else {
        alert('Hubo un error al enviar tus datos. Por favor, intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Hubo un problema de conexión. Por favor revisa tu internet e intenta de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const flavors = [
    { name: "Fresa", color: "#ff4d6d", image: "/paleta_fresa.png" },
    { name: "Chocolate", color: "#5c4033", image: "/paleta_chocolate.png" },
    { name: "Café", color: "#8c6239", image: "/paleta_cafe.png" },
    { name: "Vainilla", color: "#f3e5ab", image: "/paleta_vainilla.png" },
    { name: "Cookies & Cream", color: "#475569", image: "/paleta_cookies_cream.png" }
  ];

  const heroPopsiclesData = isMobile ? [
    { 
      id: 'fresa', name: 'FRESA', image: '/paleta_fresa_full.png',
      desc: 'Dulzor natural y vibrante.', tags: ['Sin Calorías Extra', 'Hecha con Fruta Natural', 'Increíble Sabor'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [-10, 10, -10], initialRotate: [10, 15, 10],
      style: { top: '10%', right: '-5%', width: '280px', height: '420px', zIndex: 5 },
      boxSide: 'left'
    },
    { 
      id: 'chocolate', name: 'CHOCOLATE', image: '/paleta_chocolate.png',
      desc: 'El boost perfecto post-entreno.', tags: ['Textura Cremosa', 'Sabor Intenso', 'Eleva tu Energía'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [-15, 15, -15], initialRotate: [-5, 0, -5],
      style: { bottom: '5%', left: '50%', transform: 'translateX(-50%)', width: '320px', height: '480px', zIndex: 10 },
      boxSide: 'right'
    }
  ] : [
    { 
      id: 'fresa', name: 'FRESA', image: '/paleta_fresa.png',
      desc: 'Dulzor natural y vibrante.', tags: ['Sin Calorías Extra', 'Hecha con Fruta Natural', 'Increíble Sabor'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [-20, 20, -20], initialRotate: [10, 15, 10],
      style: { top: '5%', left: '5%', width: '280px', height: '420px', zIndex: 5 },
      boxSide: 'right'
    },
    { 
      id: 'vainilla', name: 'VAINILLA', image: '/paleta_vainilla.png',
      desc: 'Clásico puro desde el origen.', tags: ['El Postre de Rutina', 'Sabor Refrescante', 'Una Delicada Textura'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [15, -15, 15], initialRotate: [-25, -20, -25],
      style: { bottom: '5%', left: '18%', width: '300px', height: '450px', zIndex: 6 },
      boxSide: 'right'
    },
    { 
      id: 'chocolate', name: 'CHOCOLATE', image: '/paleta_chocolate.png',
      desc: 'El boost perfecto post-entreno.', tags: ['Textura Cremosa', 'Sabor Intenso', 'Eleva tu Energía'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [-25, 25, -25], initialRotate: [-2, 2, -2],
      style: { top: '15%', left: '42%', transform: 'translateX(-50%)', width: '400px', height: '600px', zIndex: 10 },
      boxSide: 'right'
    },
    { 
      id: 'cookies', name: 'COOKIES & CREAM', image: '/paleta_cookies_cream.png',
      desc: 'Cremosidad irresistible.', tags: ['La Combinación Perfecta', 'Sin Calorías Extra', 'Tu Snack Ideal'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [20, -20, 20], initialRotate: [20, 25, 20],
      style: { bottom: '10%', right: '15%', width: '300px', height: '450px', zIndex: 7 },
      boxSide: 'left'
    },
    { 
      id: 'cafe', name: 'CAFÉ', image: '/paleta_cafe.png',
      desc: 'Energía y sabor intenso.', tags: ['Café Mexicano', 'Un shot de energía', 'Ideal para el antojo'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PROT'],
      initialY: [-15, 15, -15], initialRotate: [-15, -10, -15],
      style: { top: '10%', right: '5%', width: '250px', height: '380px', zIndex: 4 },
      boxSide: 'left'
    }
  ];

  return (
    <>
      {/* Navigation */}
      <nav className={`nav-bar ${scrolled ? 'nav-scrolled' : ''}`}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', zIndex: 60 }}>
            {/* The Logo from assets folder */}
            <img src="/logo.svg" alt="HealthyIce Logo" className="nav-logo" style={{ height: '48px', objectFit: 'contain' }} />
          </div>
          <div className="desktop-links" style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <a href="#void-fall" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>¿Por qué HealthyIce?</a>
            <a href="#lineas" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Nuestras Líneas</a>
            <a href="#sabores" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Sabores</a>
          </div>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-primary nav-cta-btn" style={{ padding: '0.75rem 1.5rem', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px', zIndex: 60 }}>
            Hacer mi pedido
          </button>
        </div>
      </nav>

      {/* Scientific Hero Section */}
      <section className="hero-scientific" ref={dragConstraintsRef} style={{ overflow: 'hidden' }}>
        <div className="hero-grid-bg"></div>
        <div className="hero-crosshair-x"></div>
        <div className="hero-crosshair-y"></div>

        <div className="container hero-scientific-container" style={{ position: 'relative', width: '100%', height: '100%' }}>
          
          <motion.div 
            className="hero-scientific-title"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            style={{ zIndex: 20, pointerEvents: 'none' }}
          >
            <h1>
              PLACER<br/>SIN<br/>CULPA.
            </h1>
            <p>
              <span className="pulse-dot"></span>
              [ HLY-ICE // V.1.0_PRO ]
            </p>
          </motion.div>

          <div className="popsicles-wrapper" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
          {/* Draggable Collage of 5 Popsicles */}
          {heroPopsiclesData.map((item, idx) => (
            <motion.div
              key={item.id}
              drag
              dragConstraints={dragConstraintsRef}
              whileDrag={{ zIndex: 50, scale: 1.15, cursor: 'grabbing' }}
              onHoverStart={() => setHoveredPopsicle(item.id)}
              onHoverEnd={() => setHoveredPopsicle(null)}
              animate={{ y: item.initialY }}
              transition={{ duration: 6 + idx, repeat: Infinity, ease: "easeInOut", delay: idx * 0.5 }}
              style={{ position: 'absolute', cursor: 'grab', ...item.style, zIndex: hoveredPopsicle === item.id ? 100 : (item.style?.zIndex || 1) }}
            >
              {/* Popsicle Image with Rotation and Hover Scale */}
              <motion.div
                animate={{ rotateZ: item.initialRotate }}
                transition={{ duration: 6 + idx, repeat: Infinity, ease: "easeInOut", delay: idx * 0.5 }}
                whileHover={{ scale: 1.1, transition: { duration: 0.3 } }}
                style={{ width: '100%', height: '100%' }}
              >
                <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.5))', pointerEvents: 'none' }} />
              </motion.div>
              
              <AnimatePresence>
                {hoveredPopsicle === item.id && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, filter: 'blur(8px)', x: item.boxSide === 'right' ? 20 : -20 }}
                    animate={{ opacity: 1, scale: 1, filter: 'blur(0px)', x: 0 }}
                    exit={{ opacity: 0, scale: 0.95, filter: 'blur(8px)', x: item.boxSide === 'right' ? 10 : -10 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    style={{
                      position: 'absolute', 
                      top: '30%', 
                      [item.boxSide === 'right' ? 'left' : 'right']: '50%', 
                      [item.boxSide === 'right' ? 'marginLeft' : 'marginRight']: '120px', 
                      width: '280px', 
                      pointerEvents: 'none',
                      zIndex: 100
                    }}
                  >
                     {/* SVG Connecting Line with Center Dot */}
                     <svg style={{ 
                       position: 'absolute', 
                       top: '20px', 
                       [item.boxSide === 'right' ? 'left' : 'right']: '-120px', 
                       width: '120px', 
                       height: '20px', 
                       overflow: 'visible' 
                     }}>
                       <motion.circle 
                         cx={item.boxSide === 'right' ? '0' : '120'} 
                         cy="0" 
                         r="5" 
                         fill="#101729"
                         initial={{ scale: 0 }}
                         animate={{ scale: 1 }}
                         transition={{ duration: 0.3, type: "spring" }}
                       />
                       <motion.line 
                         x1={item.boxSide === 'right' ? '0' : '120'} 
                         y1="0" 
                         x2={item.boxSide === 'right' ? '120' : '0'} 
                         y2="0" 
                         stroke="#101729" 
                         strokeWidth="2" 
                         strokeDasharray="4 4"
                         initial={{ pathLength: 0, opacity: 0 }}
                         animate={{ pathLength: 1, opacity: 1 }}
                         transition={{ duration: 0.4, ease: "easeOut", delay: 0.1 }}
                       />
                     </svg>

                     {/* Annotation Card */}
                     <div className="anno-box" style={{ 
                       position: 'relative', 
                       background: 'rgba(255, 255, 255, 0.85)', 
                       backdropFilter: 'blur(16px)',
                       WebkitBackdropFilter: 'blur(16px)',
                       border: '1px solid rgba(255, 255, 255, 0.8)',
                       borderLeft: item.boxSide === 'right' ? '4px solid #98BC3C' : '1px solid rgba(255, 255, 255, 0.8)',
                       borderRight: item.boxSide === 'left' ? '4px solid #98BC3C' : '1px solid rgba(255, 255, 255, 0.8)',
                       boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
                       color: '#1e293b',
                       padding: '1.25rem',
                       borderRadius: '8px'
                     }}>
                       <div className="anno-header" style={{ color: '#101729', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '0.5rem', marginBottom: '0.5rem', fontSize: '1.25rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '1px' }}>{item.name}</div>
                       <div className="anno-body" style={{ color: '#475569', fontSize: '0.95rem', lineHeight: 1.4 }}>
                          {item.desc}<br/><br/>
                          {item.tags.map(tag => (
                            <span key={tag} style={{ display: 'flex', alignItems: 'center', color: '#1e293b', marginBottom: '6px', fontFamily: "'Quicksand', sans-serif", fontWeight: 700 }}>
                              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#98BC3C', marginRight: '8px' }}></div>
                              {tag}
                            </span>
                          ))}

                       </div>
                     </div>
                  </motion.div>
                )}
              </AnimatePresence>

            </motion.div>
          ))}
          </div>

        </div>
      </section>

      {/* Caída al Vacío Sequence */}
      <section id="void-fall" className="void-fall-section" style={{ background: '#020617', color: 'white', position: 'relative', overflow: 'hidden', paddingTop: '15vh' }}>
        {/* Galaxy / Nebula Backgrounds */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundImage: 'radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '40px 40px', zIndex: 0 }}></div>
        <div style={{ position: 'absolute', top: '10%', left: '10%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(120,0,255,0.15) 0%, transparent 70%)', filter: 'blur(80px)', zIndex: 0, pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', top: '40%', right: '5%', width: '60vw', height: '60vw', background: 'radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 70%)', filter: 'blur(100px)', zIndex: 0, pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', bottom: '10%', left: '20%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(255,0,128,0.1) 0%, transparent 70%)', filter: 'blur(90px)', zIndex: 0, pointerEvents: 'none' }}></div>

        {[
          { name: "Fresa", image: "/paleta_fresa.png", fullImage: "/paleta_fresa_full.png", highlight: "Sin Azúcar", desc: "Dulzor vibrante sin alterar tus niveles de glucosa." },
          { name: "Chocolate", image: "/paleta_chocolate.png", fullImage: "/paleta_chocolate_full.png", highlight: "Alta en Proteína", desc: "Tu mejor aliado para la recuperación muscular." },
          { name: "Café", image: "/paleta_cafe.png", fullImage: "/paleta_cafe_full.png", highlight: "Sin Sellos", desc: "Cumplimiento total con la NOM-051." },
          { name: "Vainilla", image: "/paleta_vainilla.png", fullImage: "/paleta_vainilla_full.png", highlight: "Ingredientes Naturales", desc: "Calidad pura, formulada desde el origen." },
          { name: "Cookies & Cream", image: "/paleta_cookies_cream.png", fullImage: "/paleta_cookies_cream_full.png", highlight: "Placer sin Culpa", desc: "Delicioso sabor y cremosidad extraordinaria." }
        ].map((item, idx) => (
          <div key={idx} className="void-fall-item" style={{ minHeight: '120vh', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', zIndex: 1, padding: '4rem 0' }}>
            <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: idx % 2 === 0 ? 'flex-start' : 'flex-end', width: '100%', position: 'relative' }}>
              
              <motion.div 
                className="void-fall-text"
                initial={{ opacity: 0, x: idx % 2 === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: false, margin: "-10%" }}
                transition={{ duration: 0.8, delay: 0.3 }}
                style={{ width: '40%', zIndex: 10, textAlign: idx % 2 === 0 ? 'left' : 'right' }}
              >
                <div style={{ fontSize: '1rem', color: '#00e5ff', fontFamily: 'monospace', marginBottom: '1rem', letterSpacing: '0.1em' }}>[ ¿POR QUÉ HEALTHYICE? ]</div>
                <h2 style={{ fontSize: 'clamp(2.5rem, 5vw, 5rem)', lineHeight: 1, marginBottom: '1rem', color: 'white', textTransform: 'uppercase', textShadow: '0 0 20px rgba(255,255,255,0.2)' }}>{item.highlight}</h2>
                <p style={{ fontSize: '1.25rem', color: '#cbd5e1', maxWidth: '400px', marginLeft: idx % 2 === 0 ? '0' : 'auto' }}>{item.desc}</p>
              </motion.div>

              <motion.div 
                className="void-fall-image"
                style={{ position: 'absolute', left: '50%', top: '50%', marginLeft: '-300px', marginTop: '-450px', width: '600px', height: '900px', zIndex: 5, pointerEvents: 'none' }}
                initial={{ y: -200, opacity: 0, rotateZ: idx % 2 === 0 ? -25 : 25 }}
                whileInView={{ y: 0, opacity: 1, rotateZ: idx % 2 === 0 ? 5 : -5 }}
                viewport={{ once: false, margin: "10%" }}
                transition={{ type: "spring", bounce: 0.4, duration: 1.8 }}
              >
                <motion.div
                  animate={{ y: [-20, 20, -20] }}
                  transition={{ repeat: Infinity, duration: 5 + (idx % 2), ease: "easeInOut" }}
                  style={{ width: '100%', height: '100%', position: 'relative' }}
                >
                  {/* Bitten image (hidden initially) */}
                  <motion.img 
                    src={item.image} 
                    alt={`${item.name} mordida`} 
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1, scale: [1, 0.95, 1.05, 1] }}
                    viewport={{ once: false, margin: "0px" }}
                    transition={{ 
                      opacity: { delay: 1.2, duration: 0.01 },
                      scale: { delay: 1.2, duration: 0.3 }
                    }}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 50px 60px rgba(0,0,0,0.6))' }} 
                  />
                  {/* Full image (visible initially, hides exactly when bitten image appears) */}
                  <motion.img 
                    src={item.fullImage} 
                    alt={`${item.name} completa`} 
                    initial={{ opacity: 1 }}
                    whileInView={{ opacity: 0 }}
                    viewport={{ once: false, margin: "0px" }}
                    transition={{ delay: 1.2, duration: 0.01 }}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 50px 60px rgba(0,0,0,0.6))' }} 
                  />
                </motion.div>
              </motion.div>

            </div>
          </div>
        ))}
      </section>

      {/* Nuestras Lineas */}
      <section id="lineas" className="section" style={{ background: 'white' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '3rem', marginBottom: '1rem', color: '#101729', textTransform: 'uppercase' }}>Dos Formas de Refrescarte</h2>
            <p style={{ fontSize: '1.125rem', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>
              Adaptamos nuestro delicioso sabor a lo que tu cuerpo necesita. Encuentra tu paleta ideal.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '3rem', flexWrap: 'wrap' }}>
            {/* Linea Fit 0 */}
            <motion.div 
              style={{ flex: '1 1 45%', padding: '3rem', borderRadius: '32px', border: '1px solid #e2e8f0', background: '#ffffff', position: 'relative', overflow: 'hidden' }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-xl)' }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '200px', height: '200px', background: '#98BC3C', opacity: 0.1, borderRadius: '50%', filter: 'blur(30px)' }}></div>
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'var(--text-dark)' }}>Línea <span style={{ color: '#98BC3C' }}>Fit 0</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#475569', marginBottom: '2rem' }}>
                El equilibrio perfecto entre dulzura y ligereza. Pensada para disfrutar sin compromisos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="#98BC3C" /> Sin azúcar</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Leaf color="#98BC3C" /> Ingredientes Naturales</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Droplets color="#98BC3C" /> Refrescante y Ligera</li>
              </ul>
            </motion.div>

            {/* Linea Pro */}
            <motion.div 
              style={{ flex: '1 1 45%', padding: '3rem', borderRadius: '32px', border: '1px solid #e2e8f0', background: '#0f172a', color: 'white', position: 'relative', overflow: 'hidden' }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-xl)' }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '200px', height: '200px', background: 'var(--primary)', opacity: 0.2, borderRadius: '50%', filter: 'blur(30px)' }}></div>
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'white' }}>Línea <span style={{ color: 'var(--primary)' }}>ProT</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#94a3b8', marginBottom: '2rem' }}>
                Potencia tu recuperación y bienestar. La paleta definitiva para estilos de vida activos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="var(--primary)" /> Sin azúcar</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><HeartPulse color="var(--primary)" /> Alta en Proteína</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Activity color="var(--primary)" /> Cero sellos (Norma Oficial)</li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Sabores */}
      <section id="sabores" className="section" style={{ background: 'var(--bg-color)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '3rem', marginBottom: '1rem', color: '#101729', textTransform: 'uppercase' }}>Tus Sabores Favoritos</h2>
            <p style={{ fontSize: '1.125rem', color: '#64748b', maxWidth: '800px', margin: '0 auto' }}>
              Todos los sabores de nuestras paletas los puedes adquirir en ambas líneas Fit 0 y ProT, de acuerdo a tus necesidades tenemos una alternativa que te ayudará para alcanzar tus objetivos.
            </p>
          </div>

          <div className="product-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
            {flavors.map((flavor, idx) => (
              <FlavorCard key={idx} flavor={flavor} idx={idx} onAddToCart={addToCart} />
            ))}
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="section" style={{ position: 'relative', overflow: 'hidden', background: '#f8fafc' }}>
        <div className="hero-grid-bg"></div>
        <div className="hero-crosshair-x"></div>
        <div className="hero-crosshair-y"></div>
        <div className="container" style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
          <h2 style={{ fontSize: '3.5rem', marginBottom: '1.5rem', color: '#101729' }}>¿Listo para el cambio?</h2>
          <p style={{ fontSize: '1.25rem', marginBottom: '2.5rem', opacity: 0.9, maxWidth: '600px', margin: '0 auto 2.5rem auto', color: '#101729' }}>
            Únete a la revolución de los postres saludables. Prueba la línea de paletas HealthyIce hoy mismo y sorpréndete.
          </p>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-primary" style={{ padding: '1.25rem 3rem', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, borderRadius: '9999px' }}>
            Hacer mi pedido
          </button>
        </div>
      </section>
      
      {/* Footer */}
      <footer style={{ padding: '3rem 0', background: '#0f172a', color: 'white', textAlign: 'center' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
            <img src="/logo.svg" alt="HealthyIce Logo" style={{ height: '40px', filter: 'brightness(0) invert(1)' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '2rem' }}>
            <a href="#" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
            </a>
            <a href="https://www.facebook.com/profile.php?id=61576515668699" target="_blank" rel="noopener noreferrer" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>
            </a>
            <a href="https://wa.me/523334996922?text=vi%20sus%20paletas%20en%20su%20p%C3%A1gina%20web%20y%20necesito%20informes" target="_blank" rel="noopener noreferrer" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
            </a>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <a href="mailto:hola@healthyice.mx" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600, fontFamily: "'Quicksand', sans-serif" }}>hola@healthyice.mx</a>
          </div>
          <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => setLegalModal('privacy')} style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}>Aviso de Privacidad</button>
            <button onClick={() => setLegalModal('terms')} style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}>Términos y Condiciones</button>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>© 2026 HealthyIce. Todos los derechos reservados.</p>
        </div>
      </footer>
      {/* Floating Cart Button */}
      <button 
        onClick={() => setIsCartOpen(true)}
        style={{ position: 'fixed', bottom: '2rem', right: '2rem', width: '64px', height: '64px', borderRadius: '50%', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, boxShadow: '0 10px 25px rgba(0,229,255,0.4)', border: 'none', cursor: 'pointer', transition: 'transform 0.2s' }}
        onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
        onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
      >
        <ShoppingCart size={28} />
        {cart.length > 0 && (
          <span style={{ position: 'absolute', top: 0, right: 0, background: '#ff4d6d', color: 'white', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 'bold', border: '2px solid white' }}>
            {cart.reduce((acc, item) => acc + item.quantity, 0)}
          </span>
        )}
      </button>

      {/* Cart Modal */}
      <AnimatePresence>
        {isCartOpen && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1000, display: 'flex', justifyContent: 'flex-end', background: 'rgba(0,0,0,0.5)' }} onClick={() => setIsCartOpen(false)}>
            <motion.div 
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              style={{ width: '100%', maxWidth: '400px', height: '100%', background: 'white', padding: '2rem', display: 'flex', flexDirection: 'column', boxShadow: '-10px 0 25px rgba(0,0,0,0.1)' }}
              onClick={e => e.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#101729', margin: 0 }}>Tu Carrito</h2>
                <button onClick={() => setIsCartOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}><X size={24} /></button>
              </div>

              <div style={{ flex: 1, overflowY: 'auto' }}>
                {cart.length === 0 ? (
                  <p style={{ color: '#64748b', textAlign: 'center', marginTop: '2rem' }}>Tu carrito está vacío</p>
                ) : (
                  cart.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center', background: '#f8fafc', padding: '1rem', borderRadius: '12px' }}>
                      <img src={item.image} alt={item.name} style={{ width: '60px', height: '60px', objectFit: 'contain' }} />
                      <div style={{ flex: 1 }}>
                        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#101729' }}>{item.name}</h4>
                        <div style={{ fontSize: '0.875rem', color: item.line === 'Fit 0' ? '#98BC3C' : 'var(--primary)', fontWeight: 600 }}>Línea {item.line}</div>
                        <div style={{ fontSize: '0.875rem', color: '#64748b' }}>${item.price}.00 MXN</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <button onClick={() => updateCartQuantity(idx, -1)} style={{ padding: '0.25rem', border: '1px solid #cbd5e1', background: 'white', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Minus size={16} /></button>
                        <span style={{ fontWeight: 600, width: '20px', textAlign: 'center' }}>{item.quantity}</span>
                        <button onClick={() => updateCartQuantity(idx, 1)} style={{ padding: '0.25rem', border: '1px solid #cbd5e1', background: 'white', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Plus size={16} /></button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {cart.length > 0 && (
                <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 800, color: '#101729' }}>
                    <span>Total:</span>
                    <span>${cart.reduce((acc, item) => acc + (item.price * item.quantity), 0)}.00 MXN</span>
                  </div>
                  <button 
                    onClick={() => {
                      const orderDetails = cart.map(item => `${item.quantity}x Paleta ${item.name} (Línea ${item.line}) - $${item.price * item.quantity}`).join('\n');
                      const total = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
                      const message = `Hola, me gustaría hacer el siguiente pedido:\n\n${orderDetails}\n\nTotal: $${total}.00 MXN\n\nQuedo atento(a) para coordinar el pago y envío.`;
                      const encodedMessage = encodeURIComponent(message);
                      window.open(`https://wa.me/523334996922?text=${encodedMessage}`, '_blank');
                      setIsCartOpen(false);
                    }}
                    style={{ width: '100%', padding: '1rem', background: '#101729', color: 'white', fontWeight: 700, borderRadius: '999px', border: 'none', cursor: 'pointer', fontSize: '1.125rem', transition: 'background 0.2s' }}
                    onMouseEnter={e => e.currentTarget.style.background = '#1e293b'}
                    onMouseLeave={e => e.currentTarget.style.background = '#101729'}
                  >
                    Hacer mi pedido
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Pop-up Form (Modal) */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsModalOpen(false)}
          >
            <motion.div 
              style={{
                background: '#f8fafc',
                borderRadius: '24px',
                padding: '2rem',
                width: '90%',
                maxWidth: '500px',
                maxHeight: '90vh',
                overflowY: 'auto',
                position: 'relative',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                border: '1px solid rgba(255, 255, 255, 0.4)'
              }}
              initial={{ scale: 0.9, y: 30, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 30, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button 
                onClick={() => setIsModalOpen(false)}
                style={{
                  position: 'absolute',
                  top: '20px',
                  right: '20px',
                  background: 'transparent',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#64748b'
                }}
              >
                ✕
              </button>
              
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '2rem', color: '#101729', marginBottom: '0.25rem', letterSpacing: '-0.5px' }}>¿Listo para el cambio?</h2>
                <p style={{ color: '#64748b', fontSize: '1rem' }}>Déjanos tus datos y nos pondremos en contacto contigo lo antes posible.</p>
              </div>

              <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }} onSubmit={handleFormSubmit}>
                {submitSuccess ? (
                  <div style={{ textAlign: 'center', padding: '2rem 0', color: '#98BC3C' }}>
                    <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>¡Gracias!</h3>
                    <p style={{ color: '#64748b' }}>Hemos recibido tus datos y te contactaremos a la brevedad.</p>
                  </div>
                ) : (
                  <>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Nombre Completo</label>
                      <input type="text" required value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Juan Pérez" />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Correo Electrónico</label>
                      <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="juan@ejemplo.com" />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Teléfono</label>
                      <input type="tel" required value={formData.telefono} onChange={e => setFormData({...formData, telefono: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="55 1234 5678" />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.5rem' }}>Línea de Interés</label>
                      <select onChange={e => setFormData({...formData, mensaje: `Línea de interés: ${e.target.value}\n\n${formData.mensaje.split('Línea de interés:')[0]}`})} style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem', background: 'white' }}>
                        <option value="Línea Fit 0">Línea Fit 0</option>
                        <option value="Línea ProT">Línea ProT</option>
                        <option value="Ambas">Ambas</option>
                      </select>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.5rem' }}>Mensaje Personalizado</label>
                      <textarea rows="3" value={formData.mensaje.split('\n\n').pop()} onChange={e => {
                        const baseMsg = formData.mensaje.includes('Línea de interés:') ? formData.mensaje.split('\n\n')[0] + '\n\n' : '';
                        setFormData({...formData, mensaje: baseMsg + e.target.value});
                      }} style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem', resize: 'none' }} placeholder="Escribe aquí tu duda o comentario..."></textarea>
                    </div>
                    <button type="submit" disabled={isSubmitting} className="btn btn-primary" style={{ width: '100%', padding: '1.25rem', marginTop: '0.5rem', fontSize: '1.125rem', borderRadius: '9999px', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, opacity: isSubmitting ? 0.7 : 1 }}>
                      {isSubmitting ? 'Enviando...' : 'Hacer mi pedido'}
                    </button>
                  </>
                )}
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legal Modals */}
      <AnimatePresence>
        {legalModal && (
          <motion.div 
            style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(10px)', zIndex: 10000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLegalModal(null)}
          >
            <motion.div 
              style={{ background: 'white', borderRadius: '24px', padding: '2rem', width: '100%', maxWidth: '800px', maxHeight: '80vh', overflowY: 'auto', position: 'relative' }}
              onClick={e => e.stopPropagation()}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              <button onClick={() => setLegalModal(null)} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}><X size={24} /></button>
              
              {legalModal === 'privacy' && (
                <div style={{ color: '#101729' }}>
                  <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem', fontFamily: "'Quicksand', sans-serif" }}>Aviso de Privacidad</h2>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>En HealthyIce estamos comprometidos con la protección y privacidad de sus datos personales. De conformidad con lo establecido en la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP), ponemos a su disposición nuestro Aviso de Privacidad.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>1. Identidad y Domicilio del Responsable</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>HealthyIce, con operaciones en México, es responsable de recabar sus datos personales, del uso que se le dé a los mismos y de su protección.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>2. Finalidad del Tratamiento de Datos</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Los datos que recopilamos (como nombre, correo electrónico y teléfono) serán utilizados exclusivamente para gestionar sus pedidos, responder dudas y comentarios a través de nuestros medios de contacto, y enviarle información relevante sobre nuestros productos, si así lo autoriza.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>3. Derechos ARCO</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Usted tiene derecho de Acceder, Rectificar y Cancelar sus datos personales, así como de Oponerse al tratamiento de los mismos (Derechos ARCO), enviando un correo a hola@healthyice.mx indicando su solicitud.</p>
                  <p style={{ marginTop: '2rem', fontSize: '0.875rem', color: '#64748b' }}>Última actualización: Mayo 2026</p>
                </div>
              )}

              {legalModal === 'terms' && (
                <div style={{ color: '#101729' }}>
                  <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem', fontFamily: "'Quicksand', sans-serif" }}>Términos y Condiciones</h2>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Bienvenido al sitio web de HealthyIce. El uso de este sitio y la compra de nuestros productos implica la aceptación incondicional de los siguientes términos y condiciones.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>1. Uso del Sitio</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>El contenido de esta página está destinado exclusivamente a uso informativo y transaccional personal. No se permite la reproducción, distribución o uso comercial del contenido (textos, gráficos, logotipos) sin el consentimiento explícito de HealthyIce.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>2. Pedidos y Precios</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Todos los pedidos están sujetos a disponibilidad del producto. Los precios mostrados en el sitio web están en pesos mexicanos (MXN) e incluyen impuestos correspondientes, pero no necesariamente los gastos de envío, los cuales se calcularán antes de finalizar la transacción a través de WhatsApp o correo electrónico.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>3. Políticas de Devolución</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Dado que nuestros productos son alimentos perecederos, no aceptamos devoluciones una vez entregados, salvo en casos de que el producto llegue en mal estado, para lo cual debe notificar a nuestro equipo (hola@healthyice.mx) el mismo día de la recepción con evidencia fotográfica.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>4. Zona de Cobertura</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Nuestros servicios de envío y entrega están limitados exclusivamente a la Zona Metropolitana de Guadalajara (ZMG). Pedidos solicitados fuera de esta área de cobertura podrían no ser procesados o estar sujetos a acuerdos especiales de envío.</p>
                  <p style={{ marginTop: '2rem', fontSize: '0.875rem', color: '#64748b' }}>Última actualización: Mayo 2026</p>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default App;
