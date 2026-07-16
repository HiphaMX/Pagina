import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Leaf, Droplets, HeartPulse, Activity, ShieldCheck, ShoppingCart, X, Plus, Minus, Trash2, ArrowLeft, FileText, ChevronRight, Mail, TrendingUp, Megaphone, Award, Users, MapPin, Search } from 'lucide-react';

const POINTS_OF_SALE = [
  {
    id: 1,
    name: "Pulse Fitness Gym",
    lat: 20.62356,
    lon: -103.2486672,
    giro: "Gimnasio",
    location: "ZMG - Tonalá",
    url: "https://maps.app.goo.gl/hQJzKaSfgcqGhfZeA"
  },
  {
    id: 2,
    name: "Kong Gym",
    lat: 20.6301138,
    lon: -103.239392,
    giro: "Gimnasio",
    location: "ZMG - Tonalá",
    url: "https://maps.app.goo.gl/fRsL7wQm6sGaYBJG6"
  },
  {
    id: 3,
    name: "La chingada fitness",
    lat: 20.4784056,
    lon: -103.2694154,
    giro: "Gimnasio",
    location: "ZMG - Tlajomulco",
    url: "https://maps.app.goo.gl/YTDytqFfhTnzYnKG8"
  },
  {
    id: 4,
    name: "Axis transform nutrition",
    lat: 20.6345828,
    lon: -103.3726858,
    giro: "Consultorio",
    location: "ZMG - Tlaquepaque",
    url: "https://maps.app.goo.gl/KGMgcr6n6W2duc9E6"
  },
  {
    id: 5,
    name: "Fitness Lab",
    lat: 20.5812594,
    lon: -103.3820933,
    giro: "Gimnasio",
    location: "ZMG - Tlaquepaque",
    url: "https://maps.app.goo.gl/dxVDcBJzGCXai5sx9"
  },
  {
    id: 6,
    name: "Gym Total Sport",
    lat: 20.6705998,
    lon: -103.222803,
    giro: "Gimnasio",
    location: "ZMG - Tonalá",
    url: "https://maps.app.goo.gl/9P4xtCFHv2zaCG997"
  },
  {
    id: 7,
    name: "We Fitness",
    lat: 20.6371802,
    lon: -103.3732717,
    giro: "Gimnasio",
    location: "ZMG - Tlaquepaque",
    url: "https://maps.app.goo.gl/Axs9ncVBDDtWzr429"
  },
  {
    id: 8,
    name: "Live Gym",
    lat: 20.6667415,
    lon: -103.214601,
    giro: "Gimnasio",
    location: "ZMG - Tonalá",
    url: "https://maps.app.goo.gl/XoDREWAvuFxE6jfK6"
  },
  {
    id: 9,
    name: "Max Gym",
    lat: 20.605715,
    lon: -103.2582835,
    giro: "Gimnasio",
    location: "ZMG - El Salto",
    url: "https://maps.app.goo.gl/P1t9gjdbBhbchY2V8"
  },
  {
    id: 10,
    name: "Aesthetic fitness (Ubicación 1)",
    lat: 20.5135085,
    lon: -103.1839763,
    giro: "Gimnasio",
    location: "Jalisco - El Salto",
    url: "https://maps.app.goo.gl/Yqa8SwZjFbFcvJKH7"
  },
  {
    id: 11,
    name: "Aesthetic fitness Arvento (Ubicación 2)",
    lat: 20.4385524,
    lon: -103.3100586,
    giro: "Gimnasio",
    location: "ZMG - Tlajomulco",
    url: "https://maps.app.goo.gl/Gp3rpFkFT2zkKED86"
  },
  {
    id: 12,
    name: "Rush Training Centro",
    lat: 20.682523,
    lon: -103.3484635,
    giro: "Gimnasio",
    location: "ZMG - Guadalajara",
    url: "https://maps.app.goo.gl/pkSt1oavzpwmzjCD6"
  },
  {
    id: 13,
    name: "Rush Training Santa Margarita",
    lat: 20.7307109,
    lon: -103.4178619,
    giro: "Gimnasio",
    location: "ZMG - Zapopan",
    url: "https://maps.app.goo.gl/3rZFg54vhD7Mdrad9"
  },
  {
    id: 14,
    name: "Gym Time Fit",
    lat: 20.4197381,
    lon: -103.3948962,
    giro: "Gimnasio",
    location: "ZMG - Tlajomulco",
    url: "https://maps.app.goo.gl/eQtQ7UbAZL3RZ3dD8"
  },
  {
    id: 15,
    name: "Camarons gym",
    lat: 20.2960293,
    lon: -102.7025079,
    giro: "Gimnasio",
    location: "Jalisco - Ocotlán",
    url: "https://maps.app.goo.gl/U8Q4BCc9TNi3d51d7"
  }
];

const PopsicleIcon = ({ color = "currentColor", size = 24 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 15V7A5 5 0 0 0 7 7v8a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2z" />
    <path d="M12 17v5" />
  </svg>
);

const FlavorCard = ({ flavor, idx, onPedir }) => {
  const [selectedLine, setSelectedLine] = useState('ProT Fit 0');
  const [selectedFormat, setSelectedFormat] = useState('1 pieza');
  const unitPrice = 60;
  const price = selectedFormat === '1 pieza' ? unitPrice : unitPrice * 5;

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
      
      {/* Selector de Línea, Formato y Precio */}
      <div style={{ width: '100%', background: '#f8fafc', padding: '1rem', borderRadius: '16px', marginBottom: '1.5rem' }}>
        {/* Selector de Línea */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <button 
            type="button"
            onClick={() => setSelectedLine('ProT Fit 0')}
            style={{ 
              flex: 1, padding: '0.6rem 0.25rem', fontSize: '0.9rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800, borderRadius: '12px', 
              border: selectedLine === 'ProT Fit 0' ? '2px solid transparent' : '2px solid transparent', 
              background: selectedLine === 'ProT Fit 0' ? 'white' : 'rgba(255, 255, 255, 0.4)', 
              boxShadow: selectedLine === 'ProT Fit 0' ? '0 4px 12px rgba(0,0,0,0.05)' : 'none',
              cursor: 'pointer', transition: 'all 0.2s', display: 'flex', justifyContent: 'center', gap: '0.3rem', alignItems: 'center'
            }}
          >
            <span style={{ color: selectedLine === 'ProT Fit 0' ? '#98BC3C' : '#64748b' }}>ProT Fit 0</span>
          </button>
          <button 
            type="button"
            onClick={() => setSelectedLine('ProT Light')}
            style={{ 
              flex: 1, padding: '0.6rem 0.25rem', fontSize: '0.9rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800, borderRadius: '12px', 
              border: selectedLine === 'ProT Light' ? '2px solid transparent' : '2px solid transparent', 
              background: selectedLine === 'ProT Light' ? '#101729' : 'rgba(255, 255, 255, 0.4)', 
              boxShadow: selectedLine === 'ProT Light' ? '0 4px 15px rgba(16,23,41,0.2)' : 'none',
              cursor: 'pointer', transition: 'all 0.2s', display: 'flex', justifyContent: 'center', gap: '0.3rem', alignItems: 'center'
            }}
          >
            <span style={{ color: selectedLine === 'ProT Light' ? 'var(--primary)' : '#64748b' }}>ProT Light</span>
          </button>
        </div>

        {/* Selector de Formato */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <button 
            type="button"
            onClick={() => setSelectedFormat('1 pieza')}
            style={{ 
              flex: 1, padding: '0.6rem 0.25rem', fontSize: '0.9rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800, borderRadius: '12px', 
              border: 'none',
              background: selectedFormat === '1 pieza' ? '#98BC3C' : 'rgba(255, 255, 255, 0.4)', 
              color: selectedFormat === '1 pieza' ? 'white' : '#64748b',
              boxShadow: selectedFormat === '1 pieza' ? '0 4px 12px rgba(152,188,60,0.2)' : 'none',
              cursor: 'pointer', transition: 'all 0.2s'
            }}
          >
            1 Pieza
          </button>
          <button 
            type="button"
            onClick={() => setSelectedFormat('pack de 5')}
            style={{ 
              flex: 1, padding: '0.6rem 0.25rem', fontSize: '0.9rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800, borderRadius: '12px', 
              border: 'none',
              background: selectedFormat === 'pack de 5' ? '#98BC3C' : 'rgba(255, 255, 255, 0.4)', 
              color: selectedFormat === 'pack de 5' ? 'white' : '#64748b',
              boxShadow: selectedFormat === 'pack de 5' ? '0 4px 12px rgba(152,188,60,0.2)' : 'none',
              cursor: 'pointer', transition: 'all 0.2s'
            }}
          >
            Pack 5 pzas
          </button>
        </div>

        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#101729' }}>${price}.00 <span style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: 400 }}>MXN</span></div>
      </div>

      <button 
        type="button"
        onClick={() => onPedir(flavor, selectedLine, selectedFormat, price)}
        className="btn btn-primary"
        style={{ width: '100%', padding: '0.875rem', borderRadius: '999px', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
      >
        Agregar al carrito
      </button>
    </motion.div>
  );
};

const SignatureCanvas = ({ onSave }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#0f172a';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
  }, []);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches && e.touches.length > 0 ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches && e.touches.length > 0 ? e.touches[0].clientY : e.clientY;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  };

  const startDrawing = (e) => {
    const coords = getCoordinates(e);
    const ctx = canvasRef.current.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    const coords = getCoordinates(e);
    const ctx = canvasRef.current.getContext('2d');
    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (isDrawing) {
      setIsDrawing(false);
      const canvas = canvasRef.current;
      onSave(canvas.toDataURL());
    }
  };

  const clear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    onSave('');
  };

  return (
    <div style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#101729' }}>Firma del Socio Comercial (Representante Legal) *</span>
        <button type="button" onClick={clear} style={{ fontSize: '0.75rem', color: '#ff3366', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>Limpiar firma</button>
      </div>
      <canvas
        ref={canvasRef}
        width={500}
        height={150}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
        style={{
          width: '100%',
          height: '150px',
          background: '#f8fafc',
          border: '2px dashed #cbd5e1',
          borderRadius: '12px',
          cursor: 'crosshair',
          touchAction: 'none'
        }}
      />
    </div>
  );
};

function App() {
  const [currentView, setCurrentView] = useState(() => {
    const path = window.location.pathname;
    const hash = window.location.hash;
    const search = window.location.search;
    if (path.includes('puntos-de-venta') || hash.includes('puntos-de-venta') || search.includes('puntos-de-venta')) {
      return 'puntos-de-venta';
    }
    return 'home';
  });

  useEffect(() => {
    const handleUrlChange = () => {
      const path = window.location.pathname;
      const hash = window.location.hash;
      const search = window.location.search;
      if (path.includes('puntos-de-venta') || hash.includes('puntos-de-venta') || search.includes('puntos-de-venta')) {
        setCurrentView('puntos-de-venta');
        window.scrollTo(0, 0);
      } else {
        setCurrentView('home');
      }
    };
    window.addEventListener('popstate', handleUrlChange);
    window.addEventListener('hashchange', handleUrlChange);
    return () => {
      window.removeEventListener('popstate', handleUrlChange);
      window.removeEventListener('hashchange', handleUrlChange);
    };
  }, []);

  const navigateToSection = (sectionId) => {
    if (currentView !== 'home') {
      setCurrentView('home');
      window.history.pushState(null, '', '/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 150);
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const [scrolled, setScrolled] = useState(false);
  const dragConstraintsRef = useRef(null);
  const [hoveredPopsicle, setHoveredPopsicle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ 
    nombre: '', 
    email: '', 
    telefono: '', 
    opcionInteres: 'ProT Fit 0', 
    producto: '', 
    mensaje: '' 
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [legalModal, setLegalModal] = useState(null); // 'privacy' or 'terms' or 'partners'
  const [vivoEnZMG, setVivoEnZMG] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('card'); // always 'card'
  const [checkoutStep, setCheckoutStep] = useState('details'); // 'details' or 'payment'
  const [paymentStatus, setPaymentStatus] = useState(null); // null, 'loading', 'approved', 'pending', 'rejected', 'error'
  const [paymentErrorMessage, setPaymentErrorMessage] = useState('');
  const [address, setAddress] = useState('');
  const [addressDetails, setAddressDetails] = useState({
    calleYNumero: '',
    interior: '',
    colonia: '',
    ciudad: ''
  });

  useEffect(() => {
    const parts = [
      addressDetails.calleYNumero,
      addressDetails.interior ? `Int. ${addressDetails.interior}` : '',
      addressDetails.colonia ? `Col. ${addressDetails.colonia}` : '',
      addressDetails.ciudad
    ].filter(Boolean);
    setAddress(parts.join(', '));
  }, [addressDetails]);

  useEffect(() => {
    if (!isModalOpen) {
      setVivoEnZMG(false);
      setPaymentMethod('card');
      setCheckoutStep('details');
      setPaymentStatus(null);
      setPaymentErrorMessage('');
      setAddress('');
      setAddressDetails({ calleYNumero: '', interior: '', colonia: '', ciudad: '' });
    }
  }, [isModalOpen]);

  // Calculator state
  const [calcMembers, setCalcMembers] = useState(400);
  const [calcRate, setCalcRate] = useState(0.10); // 0.05, 0.10, or 0.15


  // Partners contract form state
  const [partnerForm, setPartnerForm] = useState({
    nombre: '',
    razon_social: '',
    nombre_establecimiento: '',
    rfc: '',
    domicilio: '',
    email: '',
    telefono: '',
    tipo_alianza: 'Punto de Venta',
    firma: '',
    fecha: '',
    esquema_comercial: 'Compra directa',
    esquema_comercial_otro: '',
    frecuencia_pagos: 'Semanal',
    metodo_pago: 'Transferencia bancaria',
    metodo_pago_otro: '',
    vigencia_meses: 12,
    fecha_inicio_dia: '',
    fecha_inicio_mes: '',
    fecha_inicio_anio: '',
    ciudad_jurisdiccion: 'Guadalajara, Jalisco',
    representante_healthyice: 'FRANCISCO DELGADILLO',
    llenado_manual: false
  });
  const [isPartnerSubmitting, setIsPartnerSubmitting] = useState(false);
  const [partnerSubmitSuccess, setPartnerSubmitSuccess] = useState(false);
  const [partnerInputPassword, setPartnerInputPassword] = useState('');
  const [isPartnerUnlocked, setIsPartnerUnlocked] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const [activePartnerSection, setActivePartnerSection] = useState('menu'); // 'menu' or 'contract_form'

  useEffect(() => {
    if (legalModal !== 'partners') {
      setIsPartnerUnlocked(false);
      setPartnerInputPassword('');
      setPasswordError(false);
      setActivePartnerSection('menu');
    }
  }, [legalModal]);

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (partnerInputPassword === 'HealthyIce2026') {
      setIsPartnerUnlocked(true);
      setPasswordError(false);
    } else {
      setPasswordError(true);
    }
  };

  useEffect(() => {
    const today = new Date();
    const formattedDate = today.toLocaleDateString('es-MX', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
    const mes = today.toLocaleDateString('es-MX', { month: 'long' });
    setPartnerForm(prev => ({ 
      ...prev, 
      fecha: formattedDate,
      fecha_inicio_dia: prev.fecha_inicio_dia || today.getDate(),
      fecha_inicio_mes: prev.fecha_inicio_mes || mes,
      fecha_inicio_anio: prev.fecha_inicio_anio || today.getFullYear()
    }));
  }, [legalModal]);

  const handlePartnerSubmit = async (e) => {
    e.preventDefault();
    setIsPartnerSubmitting(true);
    
    if (partnerForm.llenado_manual) {
      try {
        const a = document.createElement('a');
        a.href = "/Formatos/Contrato de colaboración comercial.pdf";
        a.download = "Contrato_HealthyIce_Formato_Manual.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        setPartnerSubmitSuccess(true);
        setTimeout(() => {
          setLegalModal(null);
          setPartnerSubmitSuccess(false);
          setPartnerForm(prev => ({
            nombre: '',
            razon_social: '',
            nombre_establecimiento: '',
            rfc: '',
            domicilio: '',
            email: '',
            telefono: '',
            tipo_alianza: 'Punto de Venta',
            firma: '',
            fecha: prev.fecha,
            esquema_comercial: 'Compra directa',
            esquema_comercial_otro: '',
            frecuencia_pagos: 'Semanal',
            metodo_pago: 'Transferencia bancaria',
            metodo_pago_otro: '',
            vigencia_meses: 12,
            fecha_inicio_dia: new Date().getDate(),
            fecha_inicio_mes: new Date().toLocaleDateString('es-MX', { month: 'long' }),
            fecha_inicio_anio: new Date().getFullYear(),
            ciudad_jurisdiccion: 'Guadalajara, Jalisco',
            representante_healthyice: 'FRANCISCO DELGADILLO',
            llenado_manual: false
          }));
        }, 3000);
      } catch (error) {
        console.error('Error downloading manual contract:', error);
        alert('Hubo un problema al descargar el archivo. Por favor intenta de nuevo.');
      } finally {
        setIsPartnerSubmitting(false);
      }
      return;
    }

    // Convert all string fields to uppercase before sending
    const uppercasedForm = {};
    for (const key in partnerForm) {
      if (typeof partnerForm[key] === 'string') {
        uppercasedForm[key] = partnerForm[key].toUpperCase();
      } else {
        uppercasedForm[key] = partnerForm[key];
      }
    }

    try {
      const response = await fetch('https://hipha-mx-fastapi.vercel.app/api/contact/healthyice/contract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(uppercasedForm)
      });
      if (response.ok) {
        // Recibir como archivo blob e iniciar descarga
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const cleanRazonSocial = (partnerForm.razon_social || '').trim().replace(/\s+/g, '_');
        const filename = partnerForm.llenado_manual
          ? 'Contrato_HealthyIce_Formato_Manual.pdf'
          : `Contrato_HealthyIce_${cleanRazonSocial || 'Socio_Comercial'}.pdf`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        setPartnerSubmitSuccess(true);
        setTimeout(() => {
          setLegalModal(null);
          setPartnerSubmitSuccess(false);
          setPartnerForm(prev => ({
            nombre: '',
            razon_social: '',
            nombre_establecimiento: '',
            rfc: '',
            domicilio: '',
            email: '',
            telefono: '',
            tipo_alianza: 'Punto de Venta',
            firma: '',
            fecha: prev.fecha,
            esquema_comercial: 'Compra directa',
            esquema_comercial_otro: '',
            frecuencia_pagos: 'Semanal',
            metodo_pago: 'Transferencia bancaria',
            metodo_pago_otro: '',
            vigencia_meses: 12,
            fecha_inicio_dia: new Date().getDate(),
            fecha_inicio_mes: new Date().toLocaleDateString('es-MX', { month: 'long' }),
            fecha_inicio_anio: new Date().getFullYear(),
            ciudad_jurisdiccion: 'Guadalajara, Jalisco',
            representante_healthyice: 'FRANCISCO DELGADILLO',
            llenado_manual: false
          }));
        }, 8000);
      } else {
        alert('Hubo un error al procesar tu contrato. Por favor, intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Hubo un problema de conexión. Por favor revisa tu internet e intenta de nuevo.');
    } finally {
      setIsPartnerSubmitting(false);
    }
  };
  
  // Cart state
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const addToCart = (item) => {
    setCart(prev => {
      const existing = prev.find(i => i.name === item.name && i.line === item.line && i.format === item.format);
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

  const handleFlavorOrder = (flavor, line) => {
    setFormData({
      nombre: '',
      email: '',
      telefono: '',
      opcionInteres: line,
      producto: `Paleta sabor ${flavor.name}`,
      mensaje: ''
    });
    setIsModalOpen(true);
  };

  const handleB2BOrder = () => {
    const calculatedDaily = Math.round(calcMembers * calcRate);
    const calculatedMonthly = calculatedDaily * 30;
    const calculatedMargin = calcRate === 0.05 ? 13.50 : 14.50;
    const calculatedProfit = calculatedMonthly * calculatedMargin;

    const b2bDetails = `Distribución B2B (Gimnasio):\n- Socios Activos: ${calcMembers}\n- Escenario de Compra Diaria: ${calcRate * 100}%\n- Volumen Mensual Estimado: ${calculatedMonthly} paletas\n- Ganancia Mensual Estimada: $${calculatedProfit.toLocaleString('es-MX')} MXN`;

    setFormData({
      nombre: '',
      email: '',
      telefono: '',
      opcionInteres: 'Distribuir en Gimnasio (B2B)',
      producto: '',
      mensaje: b2bDetails
    });
    setIsModalOpen(true);
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

    const fullMessage = [
      formData.opcionInteres ? `Opción de Interés: ${formData.opcionInteres}` : '',
      formData.producto ? `Producto: ${formData.producto}` : '',
      address ? `Dirección de Envío:\n${address}` : '',
      formData.mensaje ? `Detalles / Mensaje:\n${formData.mensaje}` : ''
    ].filter(Boolean).join('\n\n');

    const payload = {
      nombre: formData.nombre,
      email: formData.email,
      telefono: formData.telefono,
      mensaje: fullMessage
    };

    try {
      const response = await fetch('https://hipha-mx-fastapi.vercel.app/api/contact/healthyice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        setSubmitSuccess(true);
        setTimeout(() => {
          setIsModalOpen(false);
          setSubmitSuccess(false);
          setFormData({ nombre: '', email: '', telefono: '', opcionInteres: 'ProT Fit 0', producto: '', mensaje: '' });
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

  const handleProceedToPayment = (e) => {
    e.preventDefault();
    if (!formData.nombre || !formData.email || !formData.telefono || !address) {
      alert("Por favor completa todos los campos del formulario, incluyendo tu dirección de envío.");
      return;
    }
    if (!vivoEnZMG) {
      alert("Por lanzamiento envío de pedidos únicamente en ZMG.");
      return;
    }
    setCheckoutStep('payment');
  };

  const handlePaymentResult = (result) => {
    if (result.status === 'approved') {
      setPaymentStatus('approved');
      setCart([]);
    } else if (result.status === 'in_process' || result.status === 'pending') {
      setPaymentStatus('pending');
      setCart([]);
    } else {
      setPaymentStatus('rejected');
      if (result.status_detail === 'cc_rejected_bad_filled_other') {
        setPaymentErrorMessage('Los datos de la tarjeta son incorrectos. Por favor verifícalos y vuelve a intentar.');
      } else if (result.status_detail === 'cc_rejected_insufficient_amount') {
        setPaymentErrorMessage('Tu tarjeta no cuenta con fondos suficientes para completar este pago.');
      } else {
        setPaymentErrorMessage('El pago fue rechazado. Por favor intenta con otra tarjeta o medio de pago.');
      }
    }
  };

  useEffect(() => {
    if (checkoutStep !== 'payment') return;

    let controller = null;

    const initMercadoPago = async () => {
      setPaymentStatus('loading');
      try {
        const configResponse = await fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/config?store=healthyice');
        if (!configResponse.ok) throw new Error('Error al obtener la configuración de pago');
        const configData = await configResponse.json();
        const publicKey = configData.public_key;

        if (!publicKey) {
          throw new Error('Clave pública de Mercado Pago no configurada');
        }

        const mp = new window.MercadoPago(publicKey, { locale: 'es-MX' });
        const bricksBuilder = mp.bricks();

        const cartItems = cart.map(item => ({
          name: `HealthyIce - ${item.name} (${item.format})`,
          price: item.price,
          quantity: item.quantity
        }));

        const payerInfo = {
          name: formData.nombre,
          email: formData.email,
          phone: formData.telefono,
          address: {
            street_name: address,
            zip_code: ""
          }
        };

        const prefResponse = await fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/create_preference', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: cartItems, payer: payerInfo, store: "healthyice" })
        });
        if (!prefResponse.ok) throw new Error('Error al crear la preferencia de pago');
        const prefData = await prefResponse.json();
        const preferenceId = prefData.id;

        let cartHtml = '<ul>';
        cartItems.forEach(item => {
          cartHtml += `<li>${item.quantity}x ${item.name} - $${item.price} MXN</li>`;
        });
        cartHtml += '</ul>';

        const settings = {
          initialization: {
            amount: totalAmountInCart,
            preferenceId: preferenceId,
            schema: {
              payer: {
                email: payerInfo.email,
              }
            }
          },
          customization: {
            paymentMethods: {
              creditCard: 'all',
              debitCard: 'all',
              ticket: 'all',
              bankTransfer: 'all',
              mercadoPago: 'all'
            },
            visual: {
              style: {
                theme: 'default'
              }
            }
          },
          callbacks: {
            onReady: () => {
              setPaymentStatus('ready');
            },
            onSubmit: ({ selectedPaymentMethod, formData: mpFormData }) => {
              mpFormData.additional_info = {
                payer_name: payerInfo.name,
                payer_phone: payerInfo.phone,
                address: address,
                cart_html: cartHtml
              };
              mpFormData.store = "healthyice";

              return new Promise((resolve, reject) => {
                fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/process_payment', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(mpFormData)
                })
                .then(response => {
                  if (!response.ok) throw new Error('Payment processing failed');
                  return response.json();
                })
                .then(result => {
                  resolve();
                  handlePaymentResult(result);
                })
                .catch(error => {
                  reject();
                  setPaymentStatus('error');
                  setPaymentErrorMessage('Hubo un error al procesar el pago con nuestro servidor. Por favor intenta de nuevo.');
                });
              });
            },
            onError: (error) => {
              console.error('Mercado Pago Brick error:', error);
              setPaymentStatus('error');
              setPaymentErrorMessage('Error en la pasarela de pagos. Por favor verifica tus datos e intenta de nuevo.');
            }
          }
        };

        controller = await bricksBuilder.create(
          'payment',
          'payment-brick_container',
          settings
        );

      } catch (err) {
        console.error('Mercado Pago initialization failed:', err);
        setPaymentStatus('error');
        setPaymentErrorMessage(`No se pudo cargar la pasarela de pagos. Detalle: ${err.message}`);
      }
    };

    initMercadoPago();

    return () => {
      if (controller && typeof controller.unmount === 'function') {
        controller.unmount();
      }
    };
  }, [checkoutStep]);

  const flavors = [
    { name: "Fresa", color: "#ff4d6d", image: "/paleta_fresa.webp" },
    { name: "Chocolate", color: "#5c4033", image: "/paleta_chocolate.webp" },
    { name: "Café", color: "#8c6239", image: "/paleta_cafe.webp" },
    { name: "Vainilla", color: "#f3e5ab", image: "/paleta_vainilla.webp" },
    { name: "Cookies & Cream", color: "#475569", image: "/paleta_cookies_cream.webp" },
    { name: "Rol de Canela", color: "#b87d4b", image: "/Paleta_roldecanela.webp" }
  ];

  const heroPopsiclesData = isMobile ? [
    { 
      id: 'fresa', name: 'FRESA', image: '/paleta_fresa_full.webp',
      desc: 'Dulzor natural y vibrante.', tags: ['Sin Calorías Extra', 'Hecha con Fruta Natural', 'Increíble Sabor'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [-10, 10, -10], initialRotate: [20, 25, 20],
      style: { top: '30%', right: '-5%', width: '235px', height: '350px', zIndex: 5 },
      boxSide: 'left'
    },
    { 
      id: 'chocolate', name: 'CHOCOLATE', image: '/paleta_chocolate.webp',
      desc: 'El boost perfecto post-entreno.', tags: ['Textura Cremosa', 'Sabor Intenso', 'Eleva tu Energía'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [-5, 5, -5], initialRotate: [0, 2, 0],
      style: { top: '15%', left: '-5%', width: '285px', height: '430px', zIndex: 10 },
      boxSide: 'right'
    }
  ] : [
    { 
      id: 'fresa', name: 'FRESA', image: '/paleta_fresa.webp',
      desc: 'Dulzor natural y vibrante.', tags: ['Sin Calorías Extra', 'Hecha con Fruta Natural', 'Increíble Sabor'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [-20, 20, -20], initialRotate: [10, 15, 10],
      style: { top: '5%', left: '5%', width: '280px', height: '420px', zIndex: 5 },
      boxSide: 'right'
    },
    { 
      id: 'vainilla', name: 'VAINILLA', image: '/paleta_vainilla.webp',
      desc: 'Clásico puro desde el origen.', tags: ['El Postre de Rutina', 'Sabor Refrescante', 'Una Delicada Textura'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [15, -15, 15], initialRotate: [-25, -20, -25],
      style: { bottom: '5%', left: '18%', width: '300px', height: '450px', zIndex: 6 },
      boxSide: 'right'
    },
    { 
      id: 'chocolate', name: 'CHOCOLATE', image: '/paleta_chocolate.webp',
      desc: 'El boost perfecto post-entreno.', tags: ['Textura Cremosa', 'Sabor Intenso', 'Eleva tu Energía'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [-25, 25, -25], initialRotate: [-2, 2, -2],
      style: { top: '15%', left: '42%', transform: 'translateX(-50%)', width: '400px', height: '600px', zIndex: 10 },
      boxSide: 'right'
    },
    { 
      id: 'cookies', name: 'COOKIES & CREAM', image: '/paleta_cookies_cream.webp',
      desc: 'Cremosidad irresistible.', tags: ['La Combinación Perfecta', 'Sin Calorías Extra', 'Tu Snack Ideal'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [20, -20, 20], initialRotate: [20, 25, 20],
      style: { bottom: '10%', right: '15%', width: '300px', height: '450px', zIndex: 7 },
      boxSide: 'left'
    },
    { 
      id: 'cafe', name: 'CAFÉ', image: '/paleta_cafe.webp',
      desc: 'Energía y sabor intenso.', tags: ['Café Mexicano', 'Un shot de energía', 'Ideal para el antojo'],
      linea: ['PROT FIT 0', 'PROT LIGHT'],
      initialY: [-15, 15, -15], initialRotate: [-15, -10, -15],
      style: { top: '10%', right: '5%', width: '250px', height: '380px', zIndex: 4 },
      boxSide: 'left'
    }
  ];

  const getPreviewVal = (field, fallback, manualFallback = '________________________') => {
    if (partnerForm.llenado_manual) {
      return manualFallback;
    }
    return partnerForm[field] || fallback;
  };

  const getEsquemaPreview = () => {
    if (partnerForm.llenado_manual) {
      return '________________________';
    }
    return partnerForm.esquema_comercial === 'Otro'
      ? (partnerForm.esquema_comercial_otro || 'Otro')
      : partnerForm.esquema_comercial;
  };

  const getMetodoPreview = () => {
    if (partnerForm.llenado_manual) {
      return '________________________';
    }
    return partnerForm.metodo_pago === 'Otro'
      ? (partnerForm.metodo_pago_otro || 'Otro')
      : partnerForm.metodo_pago;
  };

  const getFechaInicioDiaPreview = () => {
    if (partnerForm.llenado_manual) {
      return '____';
    }
    return partnerForm.fecha_inicio_dia || new Date().getDate();
  };

  const getFechaInicioMesPreview = () => {
    if (partnerForm.llenado_manual) {
      return '________________';
    }
    return partnerForm.fecha_inicio_mes || new Date().toLocaleDateString('es-MX', { month: 'long' });
  };

  const getFechaInicioAnioPreview = () => {
    if (partnerForm.llenado_manual) {
      return '________';
    }
    return partnerForm.fecha_inicio_anio || new Date().getFullYear();
  };

  const totalPopsiclesInCart = cart.reduce((sum, item) => sum + (item.format === '1 pieza' ? item.quantity : item.quantity * 5), 0);
  const totalAmountInCart = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <>
      {/* Announcement Banner */}
      <div 
        className="announcement-banner"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '40px',
          background: '#101729',
          color: '#cbd5e1',
          display: scrolled ? 'none' : 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.85rem',
          fontFamily: "'Outfit', sans-serif",
          fontWeight: 600,
          zIndex: 99,
          gap: '0.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          padding: '0 1rem',
          textAlign: 'center'
        }}
      >
        <MapPin size={16} style={{ color: '#98BC3C' }} />
        <span>Por lanzamiento envío de pedidos únicamente en <strong>ZMG</strong>, pregunta por la zona de cobertura.</span>
      </div>

      {/* Navigation */}
      <nav className={`nav-bar ${scrolled ? 'nav-scrolled' : ''}`} style={{ top: scrolled ? 0 : '40px' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', zIndex: 60 }}>
            {/* The Logo from assets folder */}
            <img 
              src="/logo.svg" 
              alt="HealthyIce Logo" 
              className="nav-logo" 
              style={{ height: '48px', objectFit: 'contain', cursor: 'pointer' }} 
              onClick={() => {
                setCurrentView('home');
                window.history.pushState(null, '', '/');
                window.scrollTo(0, 0);
              }}
            />
          </div>
          <div className="desktop-links" style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <a href="#void-fall" onClick={(e) => { e.preventDefault(); navigateToSection('void-fall'); }} style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>¿Por qué HealthyIce?</a>
            <a href="#sabores" onClick={(e) => { e.preventDefault(); navigateToSection('sabores'); }} style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Sabores</a>
            <a href="#hazte-socio" onClick={(e) => { e.preventDefault(); navigateToSection('hazte-socio'); }} style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Hazte Socio</a>
            <a 
              href="/puntos-de-venta" 
              onClick={(e) => { 
                e.preventDefault(); 
                setCurrentView('puntos-de-venta'); 
                window.history.pushState(null, '', '/puntos-de-venta'); 
                window.scrollTo(0, 0); 
              }} 
              style={{ 
                textDecoration: 'none', 
                color: currentView === 'puntos-de-venta' ? '#98BC3C' : 'var(--text-dark)', 
                fontFamily: "'Quicksand', sans-serif", 
                fontWeight: 700, 
                letterSpacing: '0.5px',
                borderBottom: currentView === 'puntos-de-venta' ? '2px solid #98BC3C' : 'none',
                paddingBottom: '2px'
              }}
            >
              Puntos de Venta
            </a>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', zIndex: 60 }}>
            {/* Mobile / Floating Puntos de Venta Button */}
            <button 
              type="button"
              onClick={() => {
                setCurrentView('puntos-de-venta');
                window.history.pushState(null, '', '/puntos-de-venta');
                window.scrollTo(0, 0);
              }}
              style={{
                background: currentView === 'puntos-de-venta' ? '#98BC3C' : 'rgba(255,255,255,0.8)',
                border: '1px solid #cbd5e1',
                borderRadius: '50%',
                width: '44px',
                height: '44px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: currentView === 'puntos-de-venta' ? 'white' : '#101729',
                transition: 'all 0.2s',
                boxShadow: currentView === 'puntos-de-venta' ? '0 4px 12px rgba(152,188,60,0.3)' : 'none'
              }}
              title="Puntos de venta"
            >
              <MapPin size={20} />
            </button>

            <button 
              type="button"
              onClick={() => setIsCartOpen(true)}
              style={{
                background: 'rgba(255,255,255,0.8)',
                border: '1px solid #cbd5e1',
                borderRadius: '50%',
                width: '44px',
                height: '44px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                position: 'relative',
                color: '#101729',
                transition: 'all 0.2s'
              }}
            >
              <ShoppingCart size={20} />
              {cart.length > 0 && (
                <span style={{
                  position: 'absolute',
                  top: '-4px',
                  right: '-4px',
                  background: '#98BC3C',
                  color: 'white',
                  borderRadius: '50%',
                  width: '18px',
                  height: '18px',
                  fontSize: '0.7rem',
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {totalPopsiclesInCart}
                </span>
              )}
            </button>
            <button onClick={() => setIsModalOpen(true)} className="btn btn-primary nav-cta-btn" style={{ padding: '0.75rem 1.5rem', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>
              Hacer mi pedido
            </button>
          </div>
        </div>
      </nav>

      {currentView === 'home' ? (
        <>
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
              PROTEÍNA<br/>FRÍA PARA<br/>RECUPERACIÓN<br/>MUSCULAR.
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
          { name: "Fresa", image: "/paleta_fresa.webp", fullImage: "/paleta_fresa_full.webp", highlight: "Sin Azúcar", desc: "Dulzor vibrante sin alterar tus niveles de glucosa." },
          { name: "Chocolate", image: "/paleta_chocolate.webp", fullImage: "/paleta_chocolate_full.webp", highlight: "Alta en Proteína", desc: "Tu mejor aliado para la recuperación muscular." },
          { name: "Café", image: "/paleta_cafe.webp", fullImage: "/paleta_cafe_full.webp", highlight: "Sin Sellos", desc: "Cumplimiento total con la NOM-051." },
          { name: "Vainilla", image: "/paleta_vainilla.webp", fullImage: "/paleta_vainilla_full.webp", highlight: "Ingredientes Naturales", desc: "Calidad pura, formulada desde el origen." },
          { name: "Cookies & Cream", image: "/paleta_cookies_cream.webp", fullImage: "/paleta_cookies_cream_full.webp", highlight: "No es solo un snack", desc: "Es nutrición para tus músculos" },
          { name: "Rol de Canela", image: "/Paleta_roldecanela.webp", fullImage: "/Paleta_roldecanelafull.webp", highlight: "Sabor Irresistible", desc: "La perfecta armonía del rol de canela en una versión saludable." }
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
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'var(--text-dark)' }}><span style={{ color: '#98BC3C' }}>ProT Fit 0</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#475569', marginBottom: '2rem' }}>
                El equilibrio perfecto entre dulzura y ligereza. Pensada para disfrutar sin compromisos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Leaf color="#98BC3C" /> Ingredientes Naturales</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="#98BC3C" /> Sin azúcar añadida</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Activity color="#98BC3C" /> Cero sellos (Norma Oficial)</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><PopsicleIcon color="#98BC3C" /> Antojo aliado de tus objetivos</li>
              </ul>
            </motion.div>

            {/* Linea Pro */}
            <motion.div 
              style={{ flex: '1 1 45%', padding: '3rem', borderRadius: '32px', border: '1px solid #e2e8f0', background: '#0f172a', color: 'white', position: 'relative', overflow: 'hidden' }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-xl)' }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '200px', height: '200px', background: 'var(--primary)', opacity: 0.2, borderRadius: '50%', filter: 'blur(30px)' }}></div>
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'white' }}><span style={{ color: 'var(--primary)' }}>ProT Light</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#94a3b8', marginBottom: '2rem' }}>
                Potencia tu recuperación y bienestar. La paleta definitiva para estilos de vida activos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><HeartPulse color="var(--primary)" /> Alto en proteína</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="var(--primary)" /> Sin azúcar añadida</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Droplets color="var(--primary)" /> El lado fit del placer</li>
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
              Todos los sabores de nuestras paletas los puedes adquirir en ambas opciones ProT Fit 0 y ProT Light, de acuerdo a tus necesidades tenemos una alternativa que te ayudará para alcanzar tus objetivos.
            </p>
          </div>

          <div className="product-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
            {flavors.map((flavor, idx) => (
              <FlavorCard key={idx} flavor={flavor} idx={idx} onPedir={(flavor, line, format, price) => addToCart({ name: flavor.name, line, format, price, color: flavor.color, image: flavor.image })} />
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
          <h2 style={{ fontSize: '3.5rem', marginBottom: '1.5rem', color: '#101729' }}>¿Listo para hacer tu pedido?</h2>
          <p style={{ fontSize: '1.25rem', marginBottom: '2.5rem', opacity: 0.9, maxWidth: '600px', margin: '0 auto 2.5rem auto', color: '#101729' }}>
            Únete a la revolución de los postres saludables. Prueba la línea de paletas HealthyIce hoy mismo y sorpréndete.
          </p>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-primary" style={{ padding: '1.25rem 3rem', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, borderRadius: '9999px' }}>
            Hacer mi pedido
          </button>
        </div>
      </section>

      {/* Hazte Socio Section */}
      <section id="hazte-socio" className="section" style={{ background: '#020617', color: 'white', position: 'relative', overflow: 'hidden', borderTop: '1px solid rgba(255, 255, 255, 0.05)', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
        {/* Futuristic Background grid & lights */}
        <div className="hero-grid-bg" style={{ opacity: 0.1, backgroundImage: 'radial-gradient(rgba(255,255,255,0.15) 1.5px, transparent 1.5px)' }}></div>
        <div style={{ position: 'absolute', top: '20%', left: '10%', width: '400px', height: '400px', background: '#0077ff', opacity: 0.05, borderRadius: '50%', filter: 'blur(100px)' }}></div>
        <div style={{ position: 'absolute', bottom: '20%', right: '10%', width: '400px', height: '400px', background: '#00e5ff', opacity: 0.05, borderRadius: '50%', filter: 'blur(100px)' }}></div>

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: 'clamp(2.25rem, 4vw, 3.5rem)', fontWeight: 800, color: 'white', marginBottom: '1.25rem', letterSpacing: '-1px', textTransform: 'uppercase' }}>
              <span style={{ color: '#00e5ff' }}>HealthyIce</span> en tu Gimnasio
            </h2>
            <p style={{ fontSize: '1.125rem', color: '#94a3b8', maxWidth: '800px', margin: '0 auto', lineHeight: 1.6 }}>
              Conviértete en socio comercial y aumenta tus ingresos de forma orgánica ofreciendo a tus miembros el snack de proteína post-entrenamiento número uno.
            </p>
          </div>

          {/* Calculator and Form Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '3rem', marginBottom: '5rem', alignItems: 'start' }}>
            
            {/* Interactive Calculator Card */}
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '32px', padding: '2.5rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
              <h3 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'white', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Calculadora de Ganancias</h3>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginBottom: '2rem' }}>
                Ajusta los parámetros para ver una estimación del beneficio mensual de tu gimnasio.
              </p>

              {/* Members Slider */}
              <div style={{ marginBottom: '2.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <label style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0' }}>Socios Activos:</label>
                  <span style={{ fontSize: '1.5rem', fontWeight: 800, color: '#00e5ff', background: 'rgba(0, 229, 255, 0.1)', padding: '0.25rem 1rem', borderRadius: '12px', border: '1px solid rgba(0, 229, 255, 0.2)' }}>
                    {calcMembers}
                  </span>
                </div>
                <input 
                  type="range" 
                  min="50" 
                  max="1000" 
                  step="10"
                  value={calcMembers} 
                  onChange={e => setCalcMembers(parseInt(e.target.value))}
                  style={{ 
                    width: '100%', 
                    height: '8px', 
                    borderRadius: '999px', 
                    background: 'rgba(255,255,255,0.1)', 
                    outline: 'none', 
                    cursor: 'pointer', 
                    accentColor: '#00e5ff'
                  }} 
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#64748b', marginTop: '0.5rem' }}>
                  <span>50</span>
                  <span>500</span>
                  <span>1000+</span>
                </div>
              </div>

              {/* Purchase Rate Cards */}
              <div style={{ marginBottom: '2.5rem' }}>
                <label style={{ display: 'block', fontSize: '1rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '1rem' }}>
                  Escenario de Compra Diaria:
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {[
                    { rate: 0.05, label: '5% (Conservador)', desc: 'Venta de 5 paletas por cada 100 socios activos', margin: 13.50 },
                    { rate: 0.10, label: '10% (Moderado)', desc: 'Venta de 10 paletas por cada 100 socios activos', margin: 14.50 },
                    { rate: 0.15, label: '15% (Optimista)', desc: 'Venta de 15 paletas por cada 100 socios activos', margin: 14.50 }
                  ].map((item) => (
                    <button
                      key={item.rate}
                      type="button"
                      onClick={() => setCalcRate(item.rate)}
                      style={{
                        textAlign: 'left',
                        padding: '1rem',
                        borderRadius: '16px',
                        border: calcRate === item.rate ? '2px solid #00e5ff' : '1px solid rgba(255, 255, 255, 0.08)',
                        background: calcRate === item.rate ? 'rgba(0, 229, 255, 0.08)' : 'rgba(255, 255, 255, 0.01)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        width: '100%'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <span style={{ fontWeight: 700, color: calcRate === item.rate ? '#00e5ff' : '#e2e8f0', fontSize: '1rem' }}>{item.label}</span>
                        <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>Margen: ${item.margin.toFixed(2)} / u</span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: '#64748b', margin: 0 }}>{item.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Calculator Output Displays */}
              <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '20px', padding: '1.5rem', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.75rem' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Venta diaria promedio:</span>
                  <span style={{ fontWeight: 700, color: 'white' }}>{Math.round(calcMembers * calcRate)} paletas / día</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Volumen mensual (30 días):</span>
                  <span style={{ fontWeight: 700, color: 'white', background: 'rgba(255,255,255,0.05)', padding: '0.1rem 0.5rem', borderRadius: '6px' }}>{Math.round(calcMembers * calcRate) * 30} paletas</span>
                </div>
                
                {/* Projected Profit Glowing Box */}
                <div style={{ textAlign: 'center', background: 'linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 119, 255, 0.05) 100%)', border: '1px solid rgba(0, 229, 255, 0.3)', borderRadius: '16px', padding: '1.5rem', boxShadow: '0 0 20px rgba(0, 229, 255, 0.15)' }}>
                  <span style={{ display: 'block', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#00e5ff', fontWeight: 700, marginBottom: '0.5rem' }}>
                    GANANCIA ESTIMADA MENSUAL
                  </span>
                  <h4 style={{ fontSize: '2.5rem', fontWeight: 900, color: 'white', letterSpacing: '-1px', margin: 0 }}>
                    ${(Math.round(calcMembers * calcRate) * 30 * (calcRate === 0.05 ? 13.50 : 14.50)).toLocaleString('es-MX', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} <span style={{ fontSize: '1rem', fontWeight: 600, color: '#94a3b8' }}>MXN</span>
                  </h4>
                  <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                    *Precio de venta sugerido por paleta: $60 MXN
                  </span>
                </div>
              </div>
            </div>

            {/* B2B Lead CTA Card */}
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '32px', padding: '2.5rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'white', marginBottom: '1rem', textTransform: 'uppercase', fontFamily: "'Outfit', sans-serif" }}>Distribuye HealthyIce</h3>
                <p style={{ color: '#94a3b8', fontSize: '1rem', marginBottom: '2rem', lineHeight: 1.6 }}>
                  Conviértete en socio comercial y aumenta tus ingresos de forma orgánica. Al unirte, tendrás acceso a precios especiales de distribuidor, apoyo en marketing, material de punto de venta y más.
                </p>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2.5rem' }}>
                  {[
                    'Margen de ganancia de hasta 29% por paleta.',
                    'Equipo de congelación sin costo de arrendamiento.',
                    'Activación y promoción de marca en tu gimnasio.'
                  ].map((benefit, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ minWidth: '8px', height: '8px', borderRadius: '50%', background: '#00e5ff' }} />
                      <span style={{ color: '#cbd5e1', fontSize: '0.95rem' }}>{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button 
                onClick={handleB2BOrder}
                className="btn"
                style={{ 
                  width: '100%', 
                  padding: '1.25rem', 
                  borderRadius: '999px', 
                  background: 'linear-gradient(135deg, #0077ff 0%, #00e5ff 100%)', 
                  color: 'white', 
                  border: 'none', 
                  fontSize: '1.125rem', 
                  fontWeight: 700, 
                  cursor: 'pointer', 
                  boxShadow: '0 8px 24px rgba(0, 119, 255, 0.3)',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Quicksand', sans-serif",
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 12px 30px rgba(0, 119, 255, 0.5)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 119, 255, 0.3)';
                }}
              >
                Hacer mi pedido
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Beneficios Section */}
      <section className="section" style={{ background: 'var(--bg-color)', borderBottom: '1px solid rgba(0, 0, 0, 0.05)' }}>
        <div className="container">
          <h3 style={{ fontSize: '2.5rem', fontWeight: 800, textAlign: 'center', color: '#101729', marginBottom: '4rem', textTransform: 'uppercase' }}>
            Beneficios de ser Socio <span style={{ color: 'var(--secondary)' }}>HealthyIce</span>
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
            {[
              {
                icon: <ShieldCheck size={28} color="var(--secondary)" />,
                title: 'Sin inversión en desarrollo',
                desc: 'Obtén de manera inmediata un snack formulado con la más alta tecnología alimentaria y listo para su distribución.'
              },
              {
                icon: <Activity size={28} color="var(--secondary)" />,
                title: 'Producto de alta rotación',
                desc: 'Los snacks congelados ricos en proteína representan una de las categorías de mayor crecimiento y consumo recurrente en centros deportivos.'
              },
              {
                icon: <TrendingUp size={28} color="var(--secondary)" />,
                title: 'Margen de ganancia creciente',
                desc: 'Maximiza el retorno de flujo de efectivo al coordinarse directamente con los niveles escalonados de compra de tu gimnasio.'
              },
              {
                icon: <Megaphone size={28} color="var(--secondary)" />,
                title: 'Apoyo promocional continuo',
                desc: 'Facilitamos material visual y activaciones de marca directo en tu sucursal para detonar el interés de tus socios desde el primer día.'
              },
              {
                icon: <Award size={28} color="var(--secondary)" />,
                title: 'Efecto KD (Recomendado)',
                desc: 'Contamos con el apoyo y recomendación de Kevin Dino "Mr. México juvenil absoluto 2026", quien visitará periódicamente las sucursales de los socios.'
              }
            ].map((benefit, idx) => (
              <motion.div 
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.5)',
                  backdropFilter: 'blur(24px)',
                  WebkitBackdropFilter: 'blur(24px)',
                  border: '1px solid rgba(255, 255, 255, 0.8)',
                  borderRadius: '24px',
                  padding: '2.5rem',
                  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                whileHover={{ 
                  scale: 1.03, 
                  background: 'rgba(255, 255, 255, 0.8)', 
                  borderColor: 'var(--secondary)',
                  boxShadow: '0 12px 30px rgba(31, 38, 135, 0.1)' 
                }}
              >
                <div style={{ marginBottom: '1.25rem', background: 'rgba(0, 119, 255, 0.05)', width: '52px', height: '52px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {benefit.icon}
                </div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#101729', marginBottom: '0.75rem' }}>{benefit.title}</h4>
                <p style={{ color: '#475569', fontSize: '0.925rem', lineHeight: 1.5, margin: 0 }}>{benefit.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
        </>
      ) : (
        <PuntosDeVenta setCurrentView={setCurrentView} />
      )}
      
      {/* Footer */}
      <footer style={{ padding: '3rem 0', background: '#0f172a', color: 'white', textAlign: 'center' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
            <img src="/logo.svg" alt="HealthyIce Logo" style={{ height: '40px', filter: 'brightness(0) invert(1)' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '2rem' }}>
            <a href="https://www.instagram.com/healthyicemx/" target="_blank" rel="noopener noreferrer" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
            </a>
            <a href="https://www.facebook.com/profile.php?id=61576515668699" target="_blank" rel="noopener noreferrer" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>
            </a>
            <a href="https://wa.me/523334996922?text=vi%20sus%20paletas%20en%20su%20p%C3%A1gina%20web%20y%20necesito%20informes" target="_blank" rel="noopener noreferrer" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
            </a>
            <a href="mailto:contacto@healthyice.mx" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <Mail size={24} />
            </a>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <a href="mailto:contacto@healthyice.mx" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600, fontFamily: "'Quicksand', sans-serif" }}>contacto@healthyice.mx</a>
          </div>
          <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button 
              onClick={() => {
                setCurrentView('puntos-de-venta');
                window.history.pushState(null, '', '/puntos-de-venta');
                window.scrollTo(0, 0);
              }} 
              style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}
            >
              Puntos de Venta
            </button>
            <button onClick={() => setLegalModal('privacy')} style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}>Aviso de Privacidad</button>
            <button onClick={() => setLegalModal('terms')} style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}>Términos y Condiciones</button>
            <button onClick={() => setLegalModal('partners')} style={{ background: 'none', border: 'none', color: '#94a3b8', textDecoration: 'underline', cursor: 'pointer', fontSize: '0.875rem' }}>Socios comerciales</button>
          </div>
        </div>
      </footer>

      <div style={{ backgroundColor: '#0A0F1C', paddingTop: '0.875rem', paddingBottom: '0.875rem', borderTop: '1px solid rgba(255,255,255,0.05)', position: 'relative', zIndex: 10 }}>
        <div style={{ maxWidth: '80rem', marginLeft: 'auto', marginRight: 'auto', paddingLeft: '1.5rem', paddingRight: '1.5rem', display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', fontSize: '0.875rem', fontFamily: 'system-ui, -apple-system, sans-serif', flexWrap: 'wrap', textAlign: 'center' }}>
          <span>Copyright 2026 © HealthyIce | Diseño by</span>
          <a href="https://www.hipha.mx/" style={{ opacity: 0.8, transition: 'opacity 0.2s', display: 'inline-flex', alignItems: 'center' }} onMouseOver={(e) => e.currentTarget.style.opacity = '1'} onMouseOut={(e) => e.currentTarget.style.opacity = '0.8'}>
            <img src="/desarrollado-por.svg" alt="Hipha" style={{ height: '1.5rem', display: 'block' }} />
          </a>
        </div>
      </div>

      {/* Floating Shopping Cart Button */}
      <AnimatePresence>
        {cart.length > 0 && (
          <motion.button
            onClick={() => setIsCartOpen(true)}
            style={{
              position: 'fixed',
              bottom: '2rem',
              right: '2rem',
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: '#98BC3C',
              color: 'white',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 8px 32px rgba(152, 188, 60, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 9998,
              border: '2px solid white'
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
          >
            <ShoppingCart size={28} />
            <span style={{
              position: 'absolute',
              top: '-5px',
              right: '-5px',
              background: '#101729',
              color: 'white',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              fontSize: '0.8rem',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid white'
            }}>
              {totalPopsiclesInCart}
            </span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Cart Drawer */}
      <AnimatePresence>
        {isCartOpen && (
          <motion.div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(15, 23, 42, 0.4)',
              backdropFilter: 'blur(8px)',
              WebkitBackdropFilter: 'blur(8px)',
              zIndex: 9990,
              display: 'flex',
              justifyContent: 'flex-end'
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsCartOpen(false)}
          >
            <motion.div
              style={{
                background: 'rgba(255, 255, 255, 0.85)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                borderLeft: '1px solid rgba(255, 255, 255, 0.5)',
                width: '100%',
                maxWidth: '450px',
                height: '100%',
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '-10px 0 30px rgba(0,0,0,0.1)'
              }}
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '1px solid rgba(0,0,0,0.05)', paddingBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <ShoppingCart size={24} style={{ color: '#101729' }} />
                  <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#101729', margin: 0, fontFamily: "'Outfit', sans-serif" }}>Mi Carrito</h2>
                </div>
                <button 
                  onClick={() => setIsCartOpen(false)}
                  style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748b' }}
                >
                  ✕
                </button>
              </div>

              {/* Cart Items */}
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.5rem' }}>
                {cart.length === 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b' }}>
                    <ShoppingCart size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                    <p style={{ fontSize: '1.1rem', fontWeight: 600 }}>Tu carrito está vacío</p>
                    <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>¡Agrega deliciosas paletas para comenzar!</p>
                  </div>
                ) : (
                  cart.map((item, idx) => (
                    <div 
                      key={`${item.name}-${item.line}-${item.format}`}
                      style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.02)',
                        border: '1px solid rgba(0,0,0,0.03)'
                      }}
                    >
                      {item.image ? (
                        <img src={item.image} alt={item.name} style={{ width: '60px', height: '60px', objectFit: 'contain' }} />
                      ) : (
                        <div style={{ width: '60px', height: '60px', background: item.color, borderRadius: '12px' }}></div>
                      )}
                      <div style={{ flex: 1 }}>
                        <h4 style={{ margin: 0, fontSize: '1rem', color: '#101729', fontWeight: 700 }}>{item.name}</h4>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                          <span style={{ fontSize: '0.75rem', background: item.line === 'ProT Fit 0' ? '#f0fdf4' : '#f8fafc', color: item.line === 'ProT Fit 0' ? '#166534' : '#475569', padding: '0.1rem 0.4rem', borderRadius: '6px', fontWeight: 700 }}>
                            {item.line}
                          </span>
                          <span style={{ fontSize: '0.75rem', background: '#f1f5f9', color: '#475569', padding: '0.1rem 0.4rem', borderRadius: '6px', fontWeight: 700 }}>
                            {item.format === '1 pieza' ? '1 Pza' : 'Pack 5'}
                          </span>
                        </div>
                        <div style={{ marginTop: '0.5rem', fontSize: '1rem', fontWeight: 800, color: '#101729' }}>
                          ${item.price * item.quantity} MXN
                        </div>
                      </div>

                      {/* Quantity Controls */}
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', background: '#f1f5f9', borderRadius: '8px', padding: '0.25rem' }}>
                          <button 
                            type="button"
                            onClick={() => updateCartQuantity(idx, -1)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0.25rem', color: '#475569' }}
                          >
                            <Minus size={14} />
                          </button>
                          <span style={{ fontSize: '0.9rem', fontWeight: 700, padding: '0 0.5rem', minWidth: '20px', textAlign: 'center', color: '#101729' }}>{item.quantity}</span>
                          <button 
                            type="button"
                            onClick={() => updateCartQuantity(idx, 1)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0.25rem', color: '#475569' }}
                          >
                            <Plus size={14} />
                          </button>
                        </div>
                        <button 
                          type="button"
                          onClick={() => updateCartQuantity(idx, -item.quantity)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', fontWeight: 600 }}
                        >
                          <Trash2 size={12} /> Eliminar
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Footer / Checkout */}
              {cart.length > 0 && (
                <div style={{ borderTop: '1px solid rgba(0,0,0,0.05)', paddingTop: '1.5rem', marginTop: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', fontSize: '1.1rem' }}>
                    <span style={{ color: '#64748b', fontWeight: 600 }}>Total de artículos:</span>
                    <span style={{ fontWeight: 800, color: '#101729' }}>
                      {totalPopsiclesInCart} paletas
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
                    <span style={{ color: '#101729', fontWeight: 700 }}>Total:</span>
                    <span style={{ fontWeight: 900, color: '#98BC3C' }}>
                      ${totalAmountInCart}.00 MXN
                    </span>
                  </div>

                  {totalPopsiclesInCart < 5 && (
                    <div style={{
                      background: 'rgba(239, 68, 68, 0.08)',
                      border: '1px solid rgba(239, 68, 68, 0.2)',
                      borderRadius: '16px',
                      padding: '1rem',
                      marginBottom: '1.25rem',
                      fontSize: '0.9rem',
                      color: '#ef4444',
                      fontWeight: 600,
                      textAlign: 'center',
                      lineHeight: 1.4
                    }}>
                      ⚠️ El pedido mínimo es de 5 piezas (o 1 pack de 5). <br />
                      Te faltan <strong>{5 - totalPopsiclesInCart}</strong> paleta{5 - totalPopsiclesInCart > 1 ? 's' : ''} para completar tu pedido.
                    </div>
                  )}

                  <button 
                    disabled={totalPopsiclesInCart < 5}
                    onClick={() => {
                      setIsCartOpen(false);
                      const cartSummary = cart.map(item => `- ${item.name} (${item.line}) [${item.format}] x${item.quantity}: $${item.price * item.quantity} MXN`).join('\n');
                      
                      setFormData({
                        nombre: '',
                        email: '',
                        telefono: '',
                        opcionInteres: 'Pedido Personalizado',
                        producto: `${totalPopsiclesInCart} paletas`,
                        mensaje: `Detalle del Pedido:\n${cartSummary}\n\nTotal estimado: $${totalAmountInCart} MXN`
                      });
                      setIsModalOpen(true);
                    }}
                    className="btn btn-primary"
                    style={{ 
                      width: '100%', 
                      padding: '1rem', 
                      borderRadius: '999px', 
                      fontSize: '1.125rem', 
                      fontFamily: "'Quicksand', sans-serif", 
                      fontWeight: 700, 
                      border: 'none', 
                      cursor: totalPopsiclesInCart < 5 ? 'not-allowed' : 'pointer', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '0.5rem',
                      opacity: totalPopsiclesInCart < 5 ? 0.5 : 1,
                      transition: 'all 0.2s'
                    }}
                  >
                    Confirmar Pedido
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
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
                    {checkoutStep === 'details' ? (
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
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                          <div style={{ gridColumn: 'span 2' }}>
                            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Calle y Número</label>
                            <input type="text" required value={addressDetails.calleYNumero} onChange={e => setAddressDetails({...addressDetails, calleYNumero: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Av. Juárez 123" />
                          </div>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>No. Interior (opcional)</label>
                            <input type="text" value={addressDetails.interior} onChange={e => setAddressDetails({...addressDetails, interior: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Depto 4B" />
                          </div>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Colonia</label>
                            <input type="text" required value={addressDetails.colonia} onChange={e => setAddressDetails({...addressDetails, colonia: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Centro" />
                          </div>
                          <div style={{ gridColumn: 'span 2' }}>
                            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Ciudad / Municipio</label>
                            <input type="text" required value={addressDetails.ciudad} onChange={e => setAddressDetails({...addressDetails, ciudad: e.target.value})} style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Guadalajara" />
                          </div>
                        </div>
                        
                        {formData.producto && (
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(0, 229, 255, 0.08)', border: '1px solid rgba(0, 229, 255, 0.2)', padding: '0.75rem 1rem', borderRadius: '12px', marginTop: '0.25rem' }}>
                            <span style={{ fontSize: '0.9rem', color: '#101729', fontWeight: 600 }}>
                              Sabor seleccionado: <strong style={{ color: '#0077ff' }}>{formData.producto}</strong>
                            </span>
                            <button 
                              type="button" 
                              onClick={() => setFormData(prev => ({ ...prev, producto: '' }))} 
                              style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: '0.95rem', fontWeight: 700 }}
                            >
                              ✕
                            </button>
                          </div>
                        )}

                        <div>
                          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.5rem' }}>Mensaje Personalizado</label>
                          <textarea 
                            rows="4" 
                            value={formData.mensaje} 
                            onChange={e => setFormData({...formData, mensaje: e.target.value})} 
                            style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem', resize: 'none' }} 
                            placeholder="Escribe aquí tus dudas, comentarios o detalles del pedido..."
                          />
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
                          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 700, color: '#101729', cursor: 'pointer' }}>
                            <input 
                              type="checkbox" 
                              checked={vivoEnZMG} 
                              onChange={e => setVivoEnZMG(e.target.checked)} 
                              style={{ 
                                width: '18px', 
                                height: '18px', 
                                accentColor: '#98BC3C',
                                cursor: 'pointer' 
                              }} 
                            />
                            <span>Vivo en la ZMG (Zona Metropolitana de Guadalajara)</span>
                          </label>
                          
                          {!vivoEnZMG && (
                            <p style={{ 
                              fontSize: '0.825rem', 
                              color: '#ef4444', 
                              margin: '0.25rem 0 0 0', 
                              fontWeight: 600,
                              lineHeight: 1.4,
                              background: 'rgba(239, 68, 68, 0.08)',
                              border: '1px solid rgba(239, 68, 68, 0.2)',
                              padding: '0.75rem 1rem',
                              borderRadius: '12px'
                            }}>
                              ⚠️ Por lanzamiento envío de pedidos únicamente en ZMG, pregunta por la zona de cobertura.
                            </p>
                          )}
                        </div>

                        <button 
                          type="button" 
                          disabled={!vivoEnZMG} 
                          onClick={handleProceedToPayment}
                          className="btn btn-primary" 
                          style={{ 
                            width: '100%', 
                            padding: '1.25rem', 
                            marginTop: '0.5rem', 
                            fontSize: '1.125rem', 
                            borderRadius: '9999px', 
                            fontFamily: "'Quicksand', sans-serif", 
                            fontWeight: 700, 
                            opacity: !vivoEnZMG ? 0.5 : 1,
                            cursor: !vivoEnZMG ? 'not-allowed' : 'pointer',
                            transition: 'all 0.2s'
                          }}
                        >
                          Proceder al Pago
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          type="button" 
                          onClick={() => setCheckoutStep('details')}
                          style={{ background: 'none', border: 'none', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem', marginBottom: '1rem', padding: 0 }}
                        >
                          ← Volver a mis datos
                        </button>
                        <div style={{ background: 'rgba(152, 188, 60, 0.08)', border: '1px solid rgba(152, 188, 60, 0.2)', padding: '1rem', borderRadius: '16px', marginBottom: '1.5rem', textAlign: 'center' }}>
                          <span style={{ fontSize: '0.85rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.5px' }}>Total a Pagar</span>
                          <h4 style={{ fontSize: '2rem', fontWeight: 800, color: '#101729', margin: '0.25rem 0' }}>${totalAmountInCart}.00 MXN</h4>
                        </div>

                        {paymentStatus === 'approved' && (
                          <div style={{ textAlign: 'center', padding: '2rem 0', color: '#98BC3C' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✓</div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#101729', marginBottom: '0.5rem' }}>¡Pago Aprobado!</h3>
                            <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Tu pago ha sido procesado con éxito. Hemos enviado una confirmación a tu correo.</p>
                          </div>
                        )}
                        {paymentStatus === 'pending' && (
                          <div style={{ textAlign: 'center', padding: '2rem 0', color: '#f59e0b' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#101729', marginBottom: '0.5rem' }}>Pago Pendiente</h3>
                            <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Tu pago se encuentra en proceso o pendiente de acreditación. Recibirás un correo cuando se apruebe.</p>
                          </div>
                        )}
                        {paymentStatus === 'rejected' && (
                          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem', color: '#ef4444' }}>✕</div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#101729', marginBottom: '0.5rem' }}>Pago Rechazado</h3>
                            <p style={{ color: '#ef4444', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: 600 }}>{paymentErrorMessage}</p>
                            <button type="button" onClick={() => setCheckoutStep('details')} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', borderRadius: '9999px', fontSize: '0.95rem', border: 'none', cursor: 'pointer' }}>Intentar de nuevo</button>
                          </div>
                        )}
                        {paymentStatus === 'error' && (
                          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem', color: '#ef4444' }}>⚠️</div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#101729', marginBottom: '0.5rem' }}>Error de Conexión</h3>
                            <p style={{ color: '#ef4444', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: 600 }}>{paymentErrorMessage}</p>
                            <button type="button" onClick={() => setCheckoutStep('details')} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', borderRadius: '9999px', fontSize: '0.95rem', border: 'none', cursor: 'pointer' }}>Intentar de nuevo</button>
                          </div>
                        )}
                        {(paymentStatus === 'loading' || paymentStatus === 'ready') && (
                          <>
                            {paymentStatus === 'loading' && (
                              <div style={{ textAlign: 'center', padding: '2rem 0' }}>
                                <div style={{ border: '4px solid rgba(0,0,0,0.1)', width: '36px', height: '36px', borderRadius: '50%', borderLeftColor: '#98BC3C', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
                                <p style={{ marginTop: '1rem', color: '#64748b', fontSize: '0.9rem' }}>Cargando pasarela de pagos...</p>
                              </div>
                            )}
                            <div id="payment-brick_container" style={{ display: paymentStatus === 'loading' ? 'none' : 'block' }}></div>
                          </>
                        )}
                      </>
                    )}
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
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Usted tiene derecho de Acceder, Rectificar y Cancelar sus datos personales, así como de Oponerse al tratamiento de los mismos (Derechos ARCO), enviando un correo a contacto@healthyice.mx indicando su solicitud.</p>
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
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Dado que nuestros productos son alimentos perecederos, no aceptamos devoluciones una vez entregados, salvo en casos de que el producto llegue en mal estado, para lo cual debe notificar a nuestro equipo (contacto@healthyice.mx) el mismo día de la recepción con evidencia fotográfica.</p>
                  <h3 style={{ fontSize: '1.25rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>4. Zona de Cobertura</h3>
                  <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>Nuestros servicios de envío y entrega están limitados exclusivamente a la Zona Metropolitana de Guadalajara (ZMG). Pedidos solicitados fuera de esta área de cobertura podrían no ser procesados o estar sujetos a acuerdos especiales de envío.</p>
                  <p style={{ marginTop: '2rem', fontSize: '0.875rem', color: '#64748b' }}>Última actualización: Mayo 2026</p>
                </div>
              )}

              {legalModal === 'partners' && (
                <div style={{ color: '#101729' }}>
                  {!isPartnerUnlocked ? (
                    <div style={{ maxWidth: '400px', margin: '2rem auto', textAlign: 'center' }}>
                      <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800 }}>Acceso Restringido</h2>
                      <p style={{ color: '#64748b', marginBottom: '1.5rem', fontSize: '0.95rem', lineHeight: 1.5 }}>
                        Esta sección está protegida. Ingresa la contraseña para continuar
                      </p>
                      <form onSubmit={handlePasswordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <input
                          type="password"
                          placeholder="Contraseña"
                          required
                          value={partnerInputPassword}
                          onChange={e => {
                            setPartnerInputPassword(e.target.value);
                            setPasswordError(false);
                          }}
                          style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: passwordError ? '1.5px solid #ff3366' : '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem', textAlign: 'center' }}
                        />
                        {passwordError && (
                          <span style={{ color: '#ff3366', fontSize: '0.85rem', fontWeight: 600 }}>Contraseña incorrecta. Intenta de nuevo.</span>
                        )}
                        <button
                          type="submit"
                          className="btn btn-primary"
                          style={{ padding: '0.75rem 1.5rem', fontSize: '1rem', width: '100%', borderRadius: '12px', cursor: 'pointer' }}
                        >
                          Desbloquear
                        </button>
                      </form>
                    </div>
                  ) : (
                    <>
                      {activePartnerSection === 'menu' ? (
                        <div>
                          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800 }}>Socios Comerciales</h2>
                          <p style={{ color: '#64748b', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
                            Selecciona una opción para continuar:
                          </p>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                            <button
                              onClick={() => setActivePartnerSection('contract_form')}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid #cbd5e1',
                                background: '#f8fafc',
                                cursor: 'pointer',
                                textAlign: 'left',
                                transition: 'all 0.2s ease',
                                width: '100%',
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f1f5f9';
                                e.currentTarget.style.borderColor = '#98BC3C';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f8fafc';
                                e.currentTarget.style.borderColor = '#cbd5e1';
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <FileText size={24} color="#98BC3C" />
                                <div>
                                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>Contrato de colaboración comercial</h4>
                                  <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.25rem 0 0 0' }}>Genera y descarga el contrato personalizado para firmar</p>
                                </div>
                              </div>
                              <ChevronRight size={20} color="#64748b" />
                            </button>

                            {/* Button 2: Entrega mercancía a consigna */}
                            <a
                              href="/Formatos/Entrega de mercancía a consigna.pdf"
                              target="_blank"
                              rel="noopener noreferrer"
                              download="Entrega_de_mercancia_a_consigna.pdf"
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid #e2e8f0',
                                background: '#f8fafc',
                                cursor: 'pointer',
                                textDecoration: 'none',
                                color: '#101729',
                                transition: 'all 0.2s ease',
                                width: '100%'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f1f5f9';
                                e.currentTarget.style.borderColor = '#cbd5e1';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f8fafc';
                                e.currentTarget.style.borderColor = '#e2e8f0';
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <FileText size={24} color="#98BC3C" />
                                <div>
                                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>Entrega mercancía a consigna</h4>
                                  <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.25rem 0 0 0' }}>Descarga el formato de entrega de mercancía</p>
                                </div>
                              </div>
                              <ChevronRight size={20} color="#64748b" />
                            </a>

                            {/* Button 3: Cobro de mercancía */}
                            <a
                              href="/Formatos/Formato de cobro de mercancía.pdf"
                              target="_blank"
                              rel="noopener noreferrer"
                              download="Formato_de_cobro_de_mercancia.pdf"
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid #e2e8f0',
                                background: '#f8fafc',
                                cursor: 'pointer',
                                textDecoration: 'none',
                                color: '#101729',
                                transition: 'all 0.2s ease',
                                width: '100%'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f1f5f9';
                                e.currentTarget.style.borderColor = '#cbd5e1';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f8fafc';
                                e.currentTarget.style.borderColor = '#e2e8f0';
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <FileText size={24} color="#98BC3C" />
                                <div>
                                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>Cobro de mercancía</h4>
                                  <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.25rem 0 0 0' }}>Descarga el formato de cobro de mercancía</p>
                                </div>
                              </div>
                              <ChevronRight size={20} color="#64748b" />
                            </a>

                            {/* Button 4: Registro de socio de negocio */}
                            <a
                              href="/Formatos/Registro de socio de negocio.pdf"
                              target="_blank"
                              rel="noopener noreferrer"
                              download="Registro_de_socio_de_negocio.pdf"
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid #e2e8f0',
                                background: '#f8fafc',
                                cursor: 'pointer',
                                textDecoration: 'none',
                                color: '#101729',
                                transition: 'all 0.2s ease',
                                width: '100%'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f1f5f9';
                                e.currentTarget.style.borderColor = '#cbd5e1';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f8fafc';
                                e.currentTarget.style.borderColor = '#e2e8f0';
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <FileText size={24} color="#98BC3C" />
                                <div>
                                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>Registro de socio de negocio</h4>
                                  <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.25rem 0 0 0' }}>Descarga el formato de alta de socio comercial</p>
                                </div>
                              </div>
                              <ChevronRight size={20} color="#64748b" />
                            </a>

                            {/* Button 5: Responsiva de congelador */}
                            <a
                              href="/Formatos/Responsiva de congelador.pdf"
                              target="_blank"
                              rel="noopener noreferrer"
                              download="Responsiva_de_congelador.pdf"
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid #e2e8f0',
                                background: '#f8fafc',
                                cursor: 'pointer',
                                textDecoration: 'none',
                                color: '#101729',
                                transition: 'all 0.2s ease',
                                width: '100%'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f1f5f9';
                                e.currentTarget.style.borderColor = '#cbd5e1';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f8fafc';
                                e.currentTarget.style.borderColor = '#e2e8f0';
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <FileText size={24} color="#98BC3C" />
                                <div>
                                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>Responsiva de congelador</h4>
                                  <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.25rem 0 0 0' }}>Descarga la carta responsiva de equipo de frío</p>
                                </div>
                              </div>
                              <ChevronRight size={20} color="#64748b" />
                            </a>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <button
                            onClick={() => setActivePartnerSection('menu')}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              background: 'none',
                              border: 'none',
                              color: '#98BC3C',
                              fontWeight: 700,
                              cursor: 'pointer',
                              fontSize: '0.95rem',
                              marginBottom: '1rem',
                              padding: 0,
                              fontFamily: "'Quicksand', sans-serif"
                            }}
                          >
                            <ArrowLeft size={18} /> Volver al menú
                          </button>
                          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 800 }}>Socios Comerciales</h2>
                          <p style={{ color: '#64748b', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
                            Completa el formulario a continuación para generar tu contrato de distribución y alianza comercial de HealthyIce de forma digital.
                          </p>

                      {partnerSubmitSuccess ? (
                        <div style={{ textAlign: 'center', padding: '2rem 0', color: '#98BC3C' }}>
                          <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', fontWeight: 700 }}>¡Contrato Generado con Éxito!</h3>
                          <p style={{ color: '#64748b', lineHeight: 1.6 }}>
                            El contrato en formato PDF se ha generado e iniciado su descarga en tu navegador para su impresión y firma física. ¡Bienvenido a la red de socios comerciales de HealthyIce!
                          </p>
                        </div>
                      ) : (
                        <form onSubmit={handlePartnerSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                          {/* Checkbox de llenado manual */}
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            padding: '0.75rem 1rem',
                            background: '#f8fafc',
                            borderRadius: '12px',
                            border: '1px solid #cbd5e1',
                            cursor: 'pointer',
                            userSelect: 'none'
                          }} onClick={() => setPartnerForm(prev => ({ ...prev, llenado_manual: !prev.llenado_manual }))}>
                            <input
                              type="checkbox"
                              id="llenado_manual"
                              checked={partnerForm.llenado_manual}
                              onChange={e => {
                                e.stopPropagation();
                                setPartnerForm(prev => ({ ...prev, llenado_manual: e.target.checked }));
                              }}
                              style={{
                                width: '18px',
                                height: '18px',
                                cursor: 'pointer',
                                accentColor: '#98BC3C'
                              }}
                            />
                            <label htmlFor="llenado_manual" style={{ fontSize: '0.9rem', fontWeight: 600, color: '#1e293b', cursor: 'pointer', margin: 0 }}>
                              Descargar formato para llenado manual (campos en blanco)
                            </label>
                          </div>

                          <div className="partner-form-grid" style={{ opacity: partnerForm.llenado_manual ? 0.6 : 1, transition: 'opacity 0.25s ease' }}>
                            <div style={{ gridColumn: 'span 2' }}>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Razón Social / Nombre Comercial {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. Distribuidora del Occidente S.A."
                                value={partnerForm.razon_social}
                                onChange={e => setPartnerForm({ ...partnerForm, razon_social: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Representante Legal {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. Juan Pérez"
                                value={partnerForm.nombre}
                                onChange={e => setPartnerForm({ ...partnerForm, nombre: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Nombre del Establecimiento {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. Abarrotes El Puerto"
                                value={partnerForm.nombre_establecimiento}
                                onChange={e => setPartnerForm({ ...partnerForm, nombre_establecimiento: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>RFC {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. XAXX010101000"
                                value={partnerForm.rfc}
                                onChange={e => setPartnerForm({ ...partnerForm, rfc: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Teléfono {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="tel"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. 3312345678"
                                value={partnerForm.telefono}
                                onChange={e => setPartnerForm({ ...partnerForm, telefono: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div style={{ gridColumn: 'span 2' }}>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Domicilio Comercial Completo {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. Av. Vallarta 1234, Guadalajara, Jal."
                                value={partnerForm.domicilio}
                                onChange={e => setPartnerForm({ ...partnerForm, domicilio: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Correo Electrónico {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="email"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. contacto@socio.com"
                                value={partnerForm.email}
                                onChange={e => setPartnerForm({ ...partnerForm, email: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Ciudad Jurisdicción {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. Guadalajara, Jalisco"
                                value={partnerForm.ciudad_jurisdiccion}
                                onChange={e => setPartnerForm({ ...partnerForm, ciudad_jurisdiccion: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                            <div style={{ gridColumn: 'span 2' }}>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Representante HEALTHY ICE {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="text"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                placeholder="e.g. FRANCISCO DELGADILLO"
                                value={partnerForm.representante_healthyice}
                                onChange={e => setPartnerForm({ ...partnerForm, representante_healthyice: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>

                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Esquema Comercial {partnerForm.llenado_manual ? '' : '*'}</label>
                              <select
                                value={partnerForm.esquema_comercial}
                                disabled={partnerForm.llenado_manual}
                                onChange={e => setPartnerForm({ ...partnerForm, esquema_comercial: e.target.value })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem', background: 'white' }}
                              >
                                <option value="Compra directa">Compra directa</option>
                                <option value="Consignación">Consignación</option>
                                <option value="Otro">Otro</option>
                              </select>
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Frecuencia de Pagos {partnerForm.llenado_manual ? '' : '*'}</label>
                              <select
                                value={partnerForm.frecuencia_pagos}
                                disabled={partnerForm.llenado_manual}
                                onChange={e => setPartnerForm({ ...partnerForm, frecuencia_pagos: e.target.value })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem', background: 'white' }}
                              >
                                <option value="Semanal">Semanal</option>
                                <option value="Quincenal">Quincenal</option>
                                <option value="Mensual">Mensual</option>
                              </select>
                            </div>

                            {partnerForm.esquema_comercial === 'Otro' && (
                              <div style={{ gridColumn: 'span 2' }}>
                                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Especifique Esquema Comercial {partnerForm.llenado_manual ? '' : '*'}</label>
                                <input
                                  type="text"
                                  required={!partnerForm.llenado_manual}
                                  disabled={partnerForm.llenado_manual}
                                  placeholder="Escriba el esquema acordado"
                                  value={partnerForm.esquema_comercial_otro}
                                  onChange={e => setPartnerForm({ ...partnerForm, esquema_comercial_otro: e.target.value.toUpperCase() })}
                                  style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                                />
                              </div>
                            )}

                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Método de Pago {partnerForm.llenado_manual ? '' : '*'}</label>
                              <select
                                value={partnerForm.metodo_pago}
                                disabled={partnerForm.llenado_manual}
                                onChange={e => setPartnerForm({ ...partnerForm, metodo_pago: e.target.value })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem', background: 'white' }}
                              >
                                <option value="Transferencia bancaria">Transferencia bancaria</option>
                                <option value="Efectivo">Efectivo</option>
                                <option value="Depósito">Depósito</option>
                                <option value="Otro">Otro</option>
                              </select>
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Vigencia (Meses) {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="number"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                min="1"
                                value={partnerForm.vigencia_meses}
                                onChange={e => setPartnerForm({ ...partnerForm, vigencia_meses: parseInt(e.target.value) || 12 })}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>

                            {partnerForm.metodo_pago === 'Otro' && (
                              <div style={{ gridColumn: 'span 2' }}>
                                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Especifique Método de Pago {partnerForm.llenado_manual ? '' : '*'}</label>
                                <input
                                  type="text"
                                  required={!partnerForm.llenado_manual}
                                  disabled={partnerForm.llenado_manual}
                                  placeholder="Escriba el método de pago acordado"
                                  value={partnerForm.metodo_pago_otro}
                                  onChange={e => setPartnerForm({ ...partnerForm, metodo_pago_otro: e.target.value.toUpperCase() })}
                                  style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                                />
                              </div>
                            )}

                            <div style={{ gridColumn: 'span 2' }}>
                              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem', opacity: partnerForm.llenado_manual ? 0.6 : 1 }}>Fecha de Inicio de Operaciones {partnerForm.llenado_manual ? '' : '*'}</label>
                              <input
                                type="date"
                                required={!partnerForm.llenado_manual}
                                disabled={partnerForm.llenado_manual}
                                onChange={e => {
                                  if (!e.target.value) return;
                                  const selectedDate = new Date(e.target.value + 'T00:00:00');
                                  const day = selectedDate.getDate();
                                  const month = selectedDate.toLocaleDateString('es-MX', { month: 'long' });
                                  const year = selectedDate.getFullYear();
                                  setPartnerForm({
                                    ...partnerForm,
                                    fecha_inicio_dia: day,
                                    fecha_inicio_mes: month,
                                    fecha_inicio_anio: year
                                  });
                                }}
                                defaultValue={new Date().toISOString().split('T')[0]}
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '0.95rem' }}
                              />
                            </div>
                          </div>

                      {/* Dynamic Contract Preview */}
                      <div style={{ marginTop: '1rem' }}>
                        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#101729', display: 'block', marginBottom: '0.5rem' }}>Vista Previa del Contrato</span>
                        <div style={{
                          height: '220px',
                          overflowY: 'auto',
                          border: '1px solid #cbd5e1',
                          borderRadius: '12px',
                          padding: '1rem',
                          background: '#f8fafc'
                        }}>
                          <p style={{ fontWeight: 'bold', textAlign: 'center', marginBottom: '1rem' }}>CONTRATO DE COLABORACIÓN COMERCIAL</p>
                          {partnerForm.llenado_manual ? (
                            <p style={{ marginBottom: '1rem' }}>
                              CONTRATO DE COLABORACIÓN COMERCIAL que celebran por una parte HEALTHY ICE, representada por ________________________________, a quien en lo sucesivo se le denominará "HEALTHY ICE", y por la otra ________________________________ , representada por ___________________________________( Nombre del Establecimiento), a quien en lo sucesivo se le denominará "SOCIO DE NEGOCIO", al tenor de las siguientes declaraciones y cláusulas:
                            </p>
                          ) : (
                            <p style={{ marginBottom: '1rem' }}>
                              CONTRATO DE COLABORACIÓN COMERCIAL que celebran por una parte HEALTHY ICE, representada por <strong>{getPreviewVal('representante_healthyice', 'FRANCISCO DELGADILLO', '________________________')}</strong>, a quien en lo sucesivo se le denominará "HEALTHY ICE", y por la otra <strong>{getPreviewVal('razon_social', '[Razón Social / Nombre Comercial]', '________________________________________________')}</strong>, representada por <strong>{getPreviewVal('nombre', '[Nombre del Representante Legal]', '________________________________________________')}</strong> (Nombre del Establecimiento: <strong>{getPreviewVal('nombre_establecimiento', '[Nombre del Establecimiento]', '________________________________________________')}</strong>), a quien en lo sucesivo se le denominará "SOCIO DE NEGOCIO", al tenor de las siguientes declaraciones y cláusulas:
                            </p>
                          )}

                          <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>DECLARACIONES</p>
                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>I. DECLARA HEALTHY ICE:</p>
                          <p style={{ marginBottom: '0.25rem' }}>1. Que es una empresa dedicada a la fabricación, comercialización y distribución de paletas, helados y alimentos congelados con enfoque saludable.</p>
                          <p style={{ marginBottom: '0.25rem' }}>2. Que cuenta con capacidad legal para celebrar el presente contrato.</p>
                          <p style={{ marginBottom: '0.75rem' }}>3. Que tiene interés en comercializar sus productos a través de puntos de venta externos.</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>II. DECLARA EL SOCIO DE NEGOCIO:</p>
                          {partnerForm.llenado_manual ? (
                            <>
                              <p style={{ marginBottom: '0.25rem' }}>1. Que es propietario, representante o administrador del establecimiento denominado:<br/>_______________________________________________________</p>
                              <p style={{ marginBottom: '0.25rem' }}>1. Que cuenta con las instalaciones necesarias para la exhibición, conservación y venta de los productos HEALTHY ICE.</p>
                              <p style={{ marginBottom: '0.25rem' }}>2. Que tiene interés en comercializar los productos objeto de este contrato.</p>
                              <p style={{ marginBottom: '0.75rem' }}>3. Que cuenta con facultades suficientes para celebrar el presente acuerdo.</p>
                            </>
                          ) : (
                            <>
                              <p style={{ marginBottom: '0.25rem' }}>1. Que es propietario, representante o administrador del establecimiento denominado: <strong>{getPreviewVal('nombre_establecimiento', '[Nombre del Establecimiento]', '________________________________________________')}</strong></p>
                              <p style={{ marginBottom: '0.25rem' }}>2. Que cuenta con las instalaciones necesarias para la exhibición, conservación y venta de los productos HEALTHY ICE (incluyendo domicilio en <strong>{getPreviewVal('domicilio', '[Domicilio Comercial Completo]', '________________________________________________')}</strong> y RFC <strong>{getPreviewVal('rfc', '[RFC]', '________________________')}</strong>).</p>
                              <p style={{ marginBottom: '0.25rem' }}>3. Que tiene interés en comercializar los productos objeto de este contrato.</p>
                              <p style={{ marginBottom: '0.75rem' }}>4. Que cuenta con facultades suficientes para celebrar el presente acuerdo.</p>
                            </>
                          )}
                          <p style={{ marginBottom: '1rem' }}>Ambas partes manifiestan su voluntad para sujetarse a las siguientes:</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>CLÁUSULAS</p>
                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>PRIMERA. OBJETO</p>
                          <p style={{ marginBottom: '0.75rem' }}>
                            {partnerForm.llenado_manual ? (
                              <>
                                HEALTHY ICE entregará productos al SOCIO DE NEGOCIO para su comercialización dentro de su establecimiento bajo el esquema de:<br/>
                                ( ) Consignación<br/>
                                ( ) Compra directa<br/>
                                ( ) Otro: __________________________
                              </>
                            ) : (
                              <>
                                HEALTHY ICE entregará productos al SOCIO DE NEGOCIO para su comercialización dentro de su establecimiento bajo el esquema de: <strong>{getEsquemaPreview()}</strong>.
                              </>
                            )}
                          </p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>SEGUNDA. PRODUCTOS</p>
                          <p style={{ marginBottom: '0.75rem' }}>Los productos incluidos en este acuerdo serán aquellos comercializados por HEALTHY ICE, pudiendo modificarse, ampliarse o sustituirse mediante aviso entre las partes.</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>TERCERA. PRECIOS</p>
                          <p style={{ marginBottom: '0.75rem' }}>Las partes acuerdan que los precios de venta al SOCIO DE NEGOCIO serán establecidos por HEALTHY ICE mediante listas de precios vigentes. El precio público sugerido será comunicado por HEALTHY ICE para mantener la uniformidad comercial de la marca.</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>CUARTA. CONSERVACIÓN DEL PRODUCTO</p>
                          <p style={{ marginBottom: '0.75rem' }}>
                            El SOCIO DE NEGOCIO deberá mantener los productos a la temperatura adecuada para garantizar su calidad. Cualquier pérdida derivada de:<br/>
                            ● Desconexión del congelador.<br/>
                            ● Fallas eléctricas no reportadas.<br/>
                            ● Manejo inadecuado.<br/>
                            ● Negligencia operativa.<br/>
                            será responsabilidad del SOCIO DE NEGOCIO.
                          </p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>QUINTA. PAGOS</p>
                          <p style={{ marginBottom: '0.75rem' }}>
                            {partnerForm.llenado_manual ? (
                              <>
                                Los pagos deberán realizarse de forma:<br/>
                                ( ) Semanal<br/>
                                ( ) Quincenal<br/>
                                ( ) Mensual<br/>
                                Mediante:<br/>
                                ( ) Transferencia bancaria<br/>
                                ( ) Efectivo<br/>
                                ( ) Depósito<br/>
                                ( ) Otro: ___________________
                              </>
                            ) : (
                              <>
                                Los pagos deberán realizarse de forma: <strong>{getPreviewVal('frecuencia_pagos', 'Semanal', '________________________')}</strong>. Mediante: <strong>{getMetodoPreview()}</strong>.
                              </>
                            )}
                          </p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>SEXTA. PUBLICIDAD Y MARCA</p>
                          <p style={{ marginBottom: '0.75rem' }}>El SOCIO DE NEGOCIO podrá utilizar materiales promocionales proporcionados por HEALTHY ICE únicamente para promover los productos objeto de este contrato. Las marcas, logotipos, diseños e imagen comercial seguirán siendo propiedad exclusiva de HEALTHY ICE.</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>SÉPTIMA. VIGENCIA</p>
                          <p style={{ marginBottom: '0.75rem' }}>
                            {partnerForm.llenado_manual ? (
                              <>
                                El presente contrato tendrá una vigencia inicial de:<br/>
                                _______ meses.<br/>
                                Iniciando el día ____ de ______________ de _______.<br/>
                                Al concluir dicho plazo podrá renovarse por acuerdo entre las partes.
                              </>
                            ) : (
                              <>
                                El presente contrato tendrá una vigencia inicial de: <strong>{getPreviewVal('vigencia_meses', 12, '____')}</strong> meses. Iniciando el día <strong>{getFechaInicioDiaPreview()}</strong> de <strong>{getFechaInicioMesPreview()}</strong> de <strong>{getFechaInicioAnioPreview()}</strong>. Al concluir dicho plazo podrá renovarse por acuerdo entre las partes.
                              </>
                            )}
                          </p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>OCTAVA. TERMINACIÓN ANTICIPADA</p>
                          <p style={{ marginBottom: '0.75rem' }}>
                            Cualquiera de las partes podrá dar por terminado el contrato mediante aviso por escrito con al menos 15 días naturales de anticipación. Asimismo, HEALTHY ICE podrá rescindir inmediatamente el contrato por:<br/>
                            ● Falta de pago.<br/>
                            ● Uso indebido de la marca.<br/>
                            ● Alteración de productos.<br/>
                            ● Mal uso del equipo.<br/>
                            ● Información falsa.<br/>
                            ● Incumplimiento de las obligaciones establecidas.
                          </p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>NOVENA. CONFIDENCIALIDAD</p>
                          <p style={{ marginBottom: '0.75rem' }}>El SOCIO DE NEGOCIO se obliga a mantener confidencial cualquier información comercial, financiera, operativa o estratégica proporcionada por HEALTHY ICE.</p>

                          <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>DÉCIMA TERCERA. JURISDICCIÓN</p>
                          <p style={{ marginBottom: '1.5rem' }}>
                            {partnerForm.llenado_manual ? (
                              <>
                                Para la interpretación y cumplimiento del presente contrato, las partes se someten a las leyes y tribunales competentes de la ciudad de:<br/><br/>
                                renunciando a cualquier otro fuero que pudiera corresponderles.
                              </>
                            ) : (
                              <>
                                Para la interpretación y cumplimiento del presente contrato, las partes se someten a las leyes y tribunales competentes de la ciudad de: <strong>{getPreviewVal('ciudad_jurisdiccion', 'Guadalajara, Jalisco', '________________________')}</strong>, renunciando a cualquier otro fuero que pudiera corresponderles.
                              </>
                            )}
                          </p>

                          <p style={{ fontWeight: 'bold', textAlign: 'center', marginBottom: '1rem' }}>FIRMAS</p>
                          <p style={{ textAlign: 'center', fontSize: '0.75rem', color: '#64748b', marginBottom: '1.5rem' }}>
                            Leído que fue el presente contrato y enteradas las partes de su contenido y alcance legal, lo firman por duplicado.
                          </p>
                          {partnerForm.llenado_manual ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', fontSize: '0.75rem', lineHeight: 1.5, textAlign: 'left' }}>
                              <div>
                                <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>HEALTHY ICE</p>
                                <p>Nombre: ____________________________________</p>
                                <p>Cargo: ______________________________________</p>
                                <p>Firma: ______________________________________</p>
                                <p>Fecha: ______________________________________</p>
                              </div>
                              <div>
                                <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>SOCIO DE NEGOCIO</p>
                                <p>Razón Social / Nombre: ________________________</p>
                                <p>Representante: _______________________________</p>
                                <p>Firma: ______________________________________</p>
                                <p>Fecha: ______________________________________</p>
                              </div>
                              <div>
                                <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>TESTIGO 1</p>
                                <p>Nombre: ____________________________________</p>
                                <p>Firma: ______________________________________</p>
                              </div>
                              <div>
                                <p style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>TESTIGO 2</p>
                                <p>Nombre: ____________________________________</p>
                                <p>Firma: ______________________________________</p>
                              </div>
                            </div>
                          ) : (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.75rem', textAlign: 'center' }}>
                              <div>
                                <p style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '2.5rem', marginBottom: '0.25rem' }}></p>
                                <p style={{ fontWeight: 'bold' }}>HEALTHY ICE</p>
                                <p style={{ fontSize: '0.7rem', color: '#64748b' }}>Nombre: {getPreviewVal('representante_healthyice', 'FRANCISCO DELGADILLO')}</p>
                              </div>
                              <div>
                                <p style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '2.5rem', marginBottom: '0.25rem' }}></p>
                                <p style={{ fontWeight: 'bold' }}>SOCIO DE NEGOCIO</p>
                                <p style={{ fontSize: '0.7rem', color: '#64748b' }}>Nombre: {getPreviewVal('nombre', '[Nombre del Representante Legal]')}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Submit button */}
                      <button
                        type="submit"
                        disabled={isPartnerSubmitting}
                        className="btn btn-primary"
                        style={{ width: '100%', padding: '0.875rem', borderRadius: '999px', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: isPartnerSubmitting ? 0.6 : 1 }}
                      >
                        {isPartnerSubmitting ? 'Procesando contrato...' : (partnerForm.llenado_manual ? 'Descargar Formato para Llenado Manual' : 'Generar y Descargar Contrato')}
                      </button>
                      </form>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// ==========================================
// COMPONENTE: PUNTOS DE VENTA (MAPA + LISTADO)
// ==========================================
const PuntosDeVenta = ({ setCurrentView }) => {
  const L = window.L;
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGiro, setSelectedGiro] = useState('Todos');
  const [selectedPointId, setSelectedPointId] = useState(null);
  
  const mapRef = useRef(null);
  const markersRef = useRef([]);

  const filteredPoints = POINTS_OF_SALE.filter(pt => {
    const matchesSearch = pt.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          pt.location.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGiro = selectedGiro === 'Todos' || pt.giro === selectedGiro;
    return matchesSearch && matchesGiro;
  });

  useEffect(() => {
    if (!L) return;
    
    // Initialize map
    if (!mapRef.current) {
      const map = L.map('map-container', {
        center: [20.58, -103.35],
        zoom: 10,
        scrollWheelZoom: false
      });
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      mapRef.current = map;
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [L]);

  useEffect(() => {
    if (!L || !mapRef.current) return;
    const map = mapRef.current;

    // Clear old markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // Custom Icon (Popsicle teardrop green)
    const normalIcon = L.divIcon({
      className: 'custom-leaflet-marker',
      html: `
        <div style="
          position: relative;
          width: 32px;
          height: 32px;
          background: #98BC3C;
          border: 2px solid white;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg) translate(0px, 0px);
          box-shadow: 0 4px 10px rgba(0,0,0,0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease-in-out;
        ">
          <div style="
            width: 14px;
            height: 14px;
            background: white;
            border-radius: 50%;
            transform: rotate(45deg);
          "></div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32]
    });

    const activeIcon = L.divIcon({
      className: 'custom-leaflet-marker-active',
      html: `
        <div style="position: relative;">
          <!-- Pulsing Background Ripple -->
          <div style="
            position: absolute;
            top: -16px;
            left: -16px;
            width: 64px;
            height: 64px;
            background: rgba(152, 188, 60, 0.4);
            border-radius: 50%;
            animation: pulse-ring 1.5s cubic-bezier(0.215, 0.610, 0.355, 1) infinite;
          "></div>
          
          <div style="
            position: relative;
            width: 38px;
            height: 38px;
            background: #101729;
            border: 2px solid #98BC3C;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg) scale(1.1);
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
          ">
            <div style="
              width: 16px;
              height: 16px;
              background: #98BC3C;
              border-radius: 50%;
              transform: rotate(45deg);
            "></div>
          </div>
        </div>
      `,
      iconSize: [38, 38],
      iconAnchor: [19, 38],
      popupAnchor: [0, -38]
    });

    // Add new markers
    filteredPoints.forEach(pt => {
      const isSelected = selectedPointId === pt.id;
      const marker = L.marker([pt.lat, pt.lon], {
        icon: isSelected ? activeIcon : normalIcon
      }).addTo(map);

      marker.bindPopup(`
        <div style="font-family: 'Outfit', sans-serif; padding: 0.5rem; min-width: 180px;">
          <h4 style="margin: 0 0 0.3rem 0; font-size: 1rem; font-weight: 700; color: #101729; font-family: 'Quicksand', sans-serif;">\${pt.name}</h4>
          <span style="
            display: inline-block; 
            background: \${pt.giro === 'Gimnasio' ? '#98BC3C' : '#00e5ff'}; 
            color: \${pt.giro === 'Gimnasio' ? 'white' : '#101729'}; 
            font-size: 0.7rem; 
            padding: 0.15rem 0.5rem; 
            border-radius: 99px; 
            margin-bottom: 0.5rem; 
            font-weight: 800;
          ">
            \${pt.giro}
          </span>
          <div style="margin-bottom: 0.5rem; font-size: 0.8rem; color: #64748b;">\${pt.location}</div>
          <a href="\${pt.url}" target="_blank" rel="noopener noreferrer" style="
            display: inline-flex; 
            align-items: center; 
            justify-content: center; 
            background: #101729; 
            color: white; 
            text-decoration: none; 
            padding: 0.4rem 0.8rem; 
            border-radius: 8px; 
            font-size: 0.8rem; 
            font-weight: 700; 
            width: 100%; 
            box-sizing: border-box; 
            gap: 0.3rem;
            text-align: center;
          ">
            Cómo llegar →
          </a>
        </div>
      `);

      marker.on('click', () => {
        setSelectedPointId(pt.id);
        const cardEl = document.getElementById(`pos-card-\${pt.id}`);
        if (cardEl) {
          cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });

      markersRef.current.push(marker);

      if (isSelected) {
        marker.openPopup();
      }
    });

    // Fit bounds if we have points and not manually focusing a selected one
    if (filteredPoints.length > 0 && !selectedPointId) {
      const group = new L.featureGroup(markersRef.current);
      map.fitBounds(group.getBounds().pad(0.15));
    }
  }, [filteredPoints, selectedPointId, L]);

  const handleSelectCard = (pt) => {
    setSelectedPointId(pt.id);
    if (mapRef.current && L) {
      mapRef.current.setView([pt.lat, pt.lon], 15);
      // Find and open popup
      const markerIdx = filteredPoints.findIndex(p => p.id === pt.id);
      if (markerIdx !== -1 && markersRef.current[markerIdx]) {
        markersRef.current[markerIdx].openPopup();
      }
    }
  };

  return (
    <div style={{ paddingTop: '100px', minHeight: 'calc(100vh - 350px)', background: 'linear-gradient(to bottom, #f0fbff, #ffffff)' }}>
      {/* CSS Animation for active marker popup ring */}
      <style>{`
        @keyframes pulse-ring {
          0% { transform: scale(0.33); opacity: 1; }
          80%, 100% { opacity: 0; }
        }
        .custom-leaflet-marker:hover {
          transform: rotate(-45deg) scale(1.15) !important;
          z-index: 1000 !important;
        }
      `}</style>
      
      <div className="container" style={{ padding: '2rem 1.5rem 4rem 1.5rem' }}>
        {/* Header Block */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <motion.button
            onClick={() => {
              setCurrentView('home');
              window.history.pushState(null, '', '/');
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'none',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.95rem',
              marginBottom: '1rem',
              fontFamily: "'Outfit', sans-serif",
              transition: 'color 0.2s'
            }}
            onMouseEnter={e => e.currentTarget.style.color = '#101729'}
            onMouseLeave={e => e.currentTarget.style.color = '#64748b'}
          >
            <ArrowLeft size={16} /> Volver al Inicio
          </motion.button>
          
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ 
              fontFamily: "'Quicksand', sans-serif", 
              fontSize: '2.5rem', 
              color: '#101729', 
              marginBottom: '1rem',
              fontWeight: 800
            }}
          >
            Puntos de Venta
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ 
              maxWidth: '650px', 
              margin: '0 auto', 
              color: '#475569', 
              fontSize: '1.1rem',
              lineHeight: 1.6,
              fontFamily: "'Outfit', sans-serif"
            }}
          >
            Encuentra tus paletas HealthyIce favoritas en nuestros gimnasios y consultorios asociados autorizados en Jalisco.
          </motion.p>
        </div>

        {/* Directory & Map Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(320px, 400px) 1fr',
          gap: '2rem',
          alignItems: 'stretch'
        }} className="pos-grid">
          
          {/* Column 1: Directory */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Search and Filter Panel */}
            <div className="glass-card" style={{ padding: '1.5rem', borderRadius: '20px' }}>
              <div style={{ position: 'relative', marginBottom: '1rem' }}>
                <input
                  type="text"
                  placeholder="Buscar gimnasio o zona..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.85rem 1rem 0.85rem 2.5rem',
                    borderRadius: '12px',
                    border: '1px solid #cbd5e1',
                    background: 'white',
                    fontSize: '0.95rem',
                    fontFamily: "'Outfit', sans-serif",
                    outline: 'none',
                    transition: 'border-color 0.2s'
                  }}
                  onFocus={e => e.currentTarget.style.borderColor = '#98BC3C'}
                  onBlur={e => e.currentTarget.style.borderColor = '#cbd5e1'}
                />
                <Search size={18} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
              </div>
              
              {/* Giro Filters */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {['Todos', 'Gimnasio', 'Consultorio'].map(g => (
                  <button
                    key={g}
                    type="button"
                    onClick={() => { setSelectedGiro(g); setSelectedPointId(null); }}
                    style={{
                      flex: 1,
                      padding: '0.5rem 0.25rem',
                      fontSize: '0.85rem',
                      fontFamily: "'Outfit', sans-serif",
                      fontWeight: 700,
                      borderRadius: '8px',
                      border: 'none',
                      background: selectedGiro === g ? '#101729' : 'rgba(255,255,255,0.6)',
                      color: selectedGiro === g ? 'white' : '#64748b',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: selectedGiro === g ? '0 4px 10px rgba(16,23,41,0.15)' : 'none'
                    }}
                  >
                    {g === 'Todos' ? 'Todos' : g === 'Gimnasio' ? 'Gimnasios' : 'Consultorios'}
                  </button>
                ))}
              </div>
            </div>

            {/* List of points of sale */}
            <div style={{ 
              maxHeight: '480px', 
              overflowY: 'auto', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '1rem',
              paddingRight: '0.25rem'
            }} className="pos-list">
              {filteredPoints.length > 0 ? (
                filteredPoints.map(pt => {
                  const isSelected = selectedPointId === pt.id;
                  return (
                    <div
                      key={pt.id}
                      id={`pos-card-\${pt.id}`}
                      onClick={() => handleSelectCard(pt)}
                      className="glass-card"
                      style={{
                        padding: '1.25rem',
                        borderRadius: '16px',
                        cursor: 'pointer',
                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                        border: isSelected ? '2px solid #98BC3C' : '2px solid transparent',
                        background: isSelected ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.5)',
                        transform: isSelected ? 'translateY(-2px)' : 'none',
                        boxShadow: isSelected ? '0 8px 24px rgba(152,188,60,0.15)' : '0 4px 12px rgba(31,38,135,0.03)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: '#101729', fontFamily: "'Quicksand', sans-serif" }}>
                          {pt.name}
                        </h3>
                        <span style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          background: pt.giro === 'Gimnasio' ? 'rgba(152, 188, 60, 0.15)' : 'rgba(0, 229, 255, 0.15)',
                          color: pt.giro === 'Gimnasio' ? '#6f8b24' : '#0097a7',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '999px',
                          fontSize: '0.7rem',
                          fontWeight: 800
                        }}>
                          {pt.giro === 'Gimnasio' ? <Activity size={10} /> : <HeartPulse size={10} />}
                          {pt.giro}
                        </span>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#64748b', fontSize: '0.85rem', marginBottom: '0.85rem', fontFamily: "'Outfit', sans-serif" }}>
                        <MapPin size={14} style={{ color: '#cbd5e1' }} />
                        <span>{pt.location}</span>
                      </div>
                      
                      <a
                        href={pt.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()} // prevent card selection
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          color: '#101729',
                          textDecoration: 'none',
                          fontSize: '0.85rem',
                          fontWeight: 700,
                          background: '#cbd5e1',
                          padding: '0.5rem 1rem',
                          borderRadius: '8px',
                          fontFamily: "'Outfit', sans-serif",
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = '#98BC3C'; e.currentTarget.style.color = 'white'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = '#cbd5e1'; e.currentTarget.style.color = '#101729'; }}
                      >
                        Cómo llegar →
                      </a>
                    </div>
                  );
                })
              ) : (
                <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#94a3b8', fontFamily: "'Outfit', sans-serif" }}>
                  <p style={{ margin: 0, fontSize: '0.95rem' }}>No se encontraron ubicaciones para tu búsqueda.</p>
                </div>
              )}
            </div>
          </div>
          
          {/* Column 2: Leaflet Map */}
          <div style={{ position: 'relative', display: 'flex', flex1: 1 }} className="pos-map-col">
            <div className="glass-card" style={{ 
              width: '100%', 
              height: '560px', 
              borderRadius: '24px', 
              overflow: 'hidden',
              padding: '0.5rem',
              background: 'rgba(255, 255, 255, 0.4)'
            }}>
              <div id="map-container" style={{ 
                width: '100%', 
                height: '100%', 
                borderRadius: '20px', 
                overflow: 'hidden',
                background: '#e0f2fe',
                zIndex: 1
              }}></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Inline styles for responsive layout */}
      <style dangerouslySetInnerHTML={{__html: `
        @media (max-width: 768px) {
          .pos-grid {
            grid-template-columns: 1fr !important;
          }
          .pos-map-col {
            order: -1; /* Place map at the top on mobile */
          }
          .pos-map-col .glass-card {
            height: 380px !important;
          }
          .pos-list {
            max-height: 360px !important;
          }
        }
      `}} />
    </div>
  );
};

export default App;
