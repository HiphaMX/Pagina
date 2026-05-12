import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Leaf, Snowflake, Droplets, ArrowRight, HeartPulse, ChevronRight, Activity, ShieldCheck, Coffee } from 'lucide-react';

function App() {
  const [scrolled, setScrolled] = useState(false);
  const dragConstraintsRef = useRef(null);
  const [hoveredPopsicle, setHoveredPopsicle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fadeIn = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.2 }
    }
  };

  const flavors = [
    { name: "Fresa", color: "#ff4d6d", image: "/paleta_fresa.png" },
    { name: "Chocolate", color: "#5c4033", image: "/paleta_chocolate.png" },
    { name: "Café", color: "#8c6239", image: "/paleta_cafe.png" },
    { name: "Vainilla", color: "#f3e5ab", image: "/paleta_vainilla.png" },
    { name: "Cookies & Cream", color: "#475569", image: "/paleta_cookies_cream.png" }
  ];

  const heroPopsiclesData = [
    { 
      id: 'fresa', name: 'FRESA', image: '/paleta_fresa.png',
      desc: 'Dulzor natural y vibrante.', tags: ['Sin Calorías Extra', 'Hecha con Fruta Natural', 'Increíble Sabor'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PRO'],
      initialY: [-20, 20, -20], initialRotate: [10, 15, 10],
      style: { top: '5%', left: '5%', width: '280px', height: '420px', zIndex: 5 },
      boxSide: 'right'
    },
    { 
      id: 'vainilla', name: 'VAINILLA', image: '/paleta_vainilla.png',
      desc: 'Clásico puro desde el origen.', tags: ['El Postre de Rutina', 'Sabor Refrescante', 'Una Delicada Textura'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PRO'],
      initialY: [15, -15, 15], initialRotate: [-25, -20, -25],
      style: { bottom: '5%', left: '18%', width: '300px', height: '450px', zIndex: 6 },
      boxSide: 'right'
    },
    { 
      id: 'chocolate', name: 'CHOCOLATE', image: '/paleta_chocolate.png',
      desc: 'El boost perfecto post-entreno.', tags: ['Textura Cremosa', 'Sabor Intenso', 'Eleva tu Energía'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PRO'],
      initialY: [-25, 25, -25], initialRotate: [-2, 2, -2],
      style: { top: '15%', left: '42%', transform: 'translateX(-50%)', width: '400px', height: '600px', zIndex: 10 },
      boxSide: 'right'
    },
    { 
      id: 'cookies', name: 'COOKIES & CREAM', image: '/paleta_cookies_cream.png',
      desc: 'Cremosidad irresistible.', tags: ['La Combinación Perfecta', 'Sin Calorías Extra', 'Tu Snack Ideal'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PRO'],
      initialY: [20, -20, 20], initialRotate: [20, 25, 20],
      style: { bottom: '10%', right: '15%', width: '300px', height: '450px', zIndex: 7 },
      boxSide: 'left'
    },
    { 
      id: 'cafe', name: 'CAFÉ', image: '/paleta_cafe.png',
      desc: 'Energía y sabor intenso.', tags: ['Café Mexicano', 'Un shot de energía', 'Ideal para el antojo'],
      linea: ['LÍNEA FIT 0', 'LÍNEA PRO'],
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
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {/* The Logo from assets folder */}
            <img src="/logo.svg" alt="HealthyIce Logo" style={{ height: '48px', objectFit: 'contain' }} />
          </div>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <a href="#void-fall" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>¿Por qué HealthyIce?</a>
            <a href="#lineas" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Nuestras Líneas</a>
            <a href="#sabores" style={{ textDecoration: 'none', color: 'var(--text-dark)', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>Sabores</a>
            <button onClick={() => setIsModalOpen(true)} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '1.125rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, letterSpacing: '0.5px' }}>
              Hacer mi pedido
            </button>
          </div>
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
              style={{ position: 'absolute', cursor: 'grab', ...item.style }}
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
      </section>

      {/* Caída al Vacío Sequence */}
      <section id="void-fall" className="void-fall-section" style={{ background: '#020617', color: 'white', position: 'relative', overflow: 'hidden', paddingTop: '15vh' }}>
        {/* Galaxy / Nebula Backgrounds */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundImage: 'radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '40px 40px', zIndex: 0 }}></div>
        <div style={{ position: 'absolute', top: '10%', left: '10%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(120,0,255,0.15) 0%, transparent 70%)', filter: 'blur(80px)', zIndex: 0, pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', top: '40%', right: '5%', width: '60vw', height: '60vw', background: 'radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 70%)', filter: 'blur(100px)', zIndex: 0, pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', bottom: '10%', left: '20%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(255,0,128,0.1) 0%, transparent 70%)', filter: 'blur(90px)', zIndex: 0, pointerEvents: 'none' }}></div>

        {[
          { name: "Fresa", image: "/paleta_fresa.png", highlight: "Sin Azúcar", desc: "Dulzor vibrante sin alterar tus niveles de glucosa." },
          { name: "Chocolate", image: "/paleta_chocolate.png", highlight: "Alta en Proteína", desc: "Tu mejor aliado para la recuperación muscular." },
          { name: "Café", image: "/paleta_cafe.png", highlight: "Sin Sellos", desc: "Cumplimiento total con la NOM-051." },
          { name: "Vainilla", image: "/paleta_vainilla.png", highlight: "Ingredientes Naturales", desc: "Calidad pura, formulada desde el origen." },
          { name: "Cookies & Cream", image: "/paleta_cookies_cream.png", highlight: "Placer sin Culpa", desc: "Delicioso sabor y cremosidad extraordinaria." }
        ].map((item, idx) => (
          <div key={idx} style={{ minHeight: '120vh', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', zIndex: 1, padding: '4rem 0' }}>
            <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: idx % 2 === 0 ? 'flex-start' : 'flex-end', width: '100%', position: 'relative' }}>
              
              <motion.div 
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
                style={{ position: 'absolute', left: '50%', top: '50%', marginLeft: '-300px', marginTop: '-450px', width: '600px', height: '900px', zIndex: 5, pointerEvents: 'none' }}
                initial={{ y: -1000, opacity: 0, rotateZ: idx % 2 === 0 ? -25 : 25 }}
                whileInView={{ y: 0, opacity: 1, rotateZ: idx % 2 === 0 ? 5 : -5 }}
                viewport={{ once: false, margin: "10%" }}
                transition={{ type: "spring", bounce: 0.4, duration: 1.8 }}
              >
                <motion.div
                  animate={{ y: [-20, 20, -20] }}
                  transition={{ repeat: Infinity, duration: 5 + (idx % 2), ease: "easeInOut" }}
                  style={{ width: '100%', height: '100%' }}
                >
                  <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 50px 60px rgba(0,0,0,0.6))' }} />
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
              style={{ flex: '1 1 45%', padding: '3rem', borderRadius: '32px', border: '1px solid #e2e8f0', background: 'linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)', position: 'relative', overflow: 'hidden' }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-xl)' }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '200px', height: '200px', background: 'var(--primary)', opacity: 0.1, borderRadius: '50%', filter: 'blur(30px)' }}></div>
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'var(--text-dark)' }}>Línea <span style={{ color: 'var(--secondary)' }}>Fit 0</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#475569', marginBottom: '2rem' }}>
                El equilibrio perfecto entre dulzura y ligereza. Pensada para disfrutar sin compromisos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="var(--primary)" /> 0% Azúcar Añadida</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Leaf color="var(--primary)" /> Ingredientes Naturales</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Droplets color="var(--primary)" /> Refrescante y Ligera</li>
              </ul>
            </motion.div>

            {/* Linea Pro */}
            <motion.div 
              style={{ flex: '1 1 45%', padding: '3rem', borderRadius: '32px', border: '1px solid #e2e8f0', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', color: 'white', position: 'relative', overflow: 'hidden' }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-xl)' }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '200px', height: '200px', background: '#98BC3C', opacity: 0.2, borderRadius: '50%', filter: 'blur(30px)' }}></div>
              <h3 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'white' }}>Línea <span style={{ color: '#98BC3C' }}>Pro</span></h3>
              <p style={{ fontSize: '1.25rem', color: '#94a3b8', marginBottom: '2rem' }}>
                Potencia tu recuperación y bienestar. La paleta definitiva para estilos de vida activos.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><HeartPulse color="#98BC3C" /> Alta en Proteína</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><Activity color="#98BC3C" /> 0 Sellos (Norma Oficial)</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.125rem', fontWeight: 600 }}><ShieldCheck color="#98BC3C" /> Sin Azúcar Añadida</li>
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
              Todos los sabores de nuestras paletas los puedes adquirir en ambas líneas Fit 0 y Pro, de acuerdo a tus necesidades tenemos una alternativa que te ayudará para alcanzar tus objetivos.
            </p>
          </div>

          <div className="product-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
            {flavors.map((flavor, idx) => (
              <motion.div 
                key={idx}
                style={{ padding: '2rem 0', textAlign: 'center', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
                whileHover={{ scale: 1.05 }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
              >
                {/* Visual Representation of flavor */}
                <motion.div 
                  style={{ 
                    width: '100%', 
                    height: '300px', 
                    marginBottom: '2rem', 
                    position: 'relative'
                  }}
                  animate={{ y: [-15, 15, -15] }}
                  transition={{ repeat: Infinity, duration: 4 + (idx % 3), ease: "easeInOut" }}
                >
                  {flavor.image ? (
                     <img src={flavor.image} alt={flavor.name} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 20px 30px rgba(0,0,0,0.3))' }} />
                  ) : (
                    <div style={{ width: '100%', height: '100%', background: flavor.color, borderRadius: '40px' }}></div>
                  )}
                </motion.div>
                <h3 style={{ fontSize: '1.5rem', fontFamily: "'Quicksand', sans-serif", fontWeight: 700, color: '#101729' }}>{flavor.name}</h3>
              </motion.div>
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
            <a href="#" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>
            </a>
            <a href="#" style={{ color: 'white', opacity: 0.8, transition: 'opacity 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.8}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
            </a>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <a href="mailto:hola@healthyice.mx" style={{ color: '#98BC3C', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600, fontFamily: "'Quicksand', sans-serif" }}>hola@healthyice.mx</a>
          </div>
          <p style={{ color: '#94a3b8' }}>© 2026 HealthyIce. Todos los derechos reservados.</p>
        </div>
      </footer>
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

              <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }} onSubmit={(e) => { e.preventDefault(); alert('¡Gracias! Hemos recibido tus datos.'); setIsModalOpen(false); }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Nombre Completo</label>
                  <input type="text" required style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="Juan Pérez" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Correo Electrónico</label>
                  <input type="email" required style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="juan@ejemplo.com" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.25rem' }}>Teléfono</label>
                  <input type="tel" required style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem' }} placeholder="55 1234 5678" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.5rem' }}>Línea de Interés</label>
                  <select style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem', background: 'white' }}>
                    <option>Línea Fit 0</option>
                    <option>Línea Pro</option>
                    <option>Ambas</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#101729', marginBottom: '0.5rem' }}>Mensaje Personalizado</label>
                  <textarea rows="3" style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '1rem', resize: 'none' }} placeholder="Escribe aquí tu duda o comentario..."></textarea>
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '1.25rem', marginTop: '0.5rem', fontSize: '1.125rem', borderRadius: '9999px', fontFamily: "'Quicksand', sans-serif", fontWeight: 700 }}>
                  Hacer mi pedido
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default App;
