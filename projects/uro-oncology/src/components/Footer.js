import Link from 'next/link';
import Image from 'next/image';
import styles from './Footer.module.css';

export default function Footer() {
  return (
    <>
      <div className={styles.preFooter}>
        <div className="container">
          <h2 className={styles.preFooterTitle}>CIRUGÍAS DE MÍNIMA INVASIÓN Y TRATAMIENTOS UROLÓGICOS</h2>
          <div className={styles.linksGrid}>
            <div className={styles.linkColumn}>
              <Link href="/cirugia-robotica">+ CIRUGÍA ROBÓTICA</Link>
              <Link href="/cirugia-endourologica">+ CIRUGÍA ENDOUROLÓGICA</Link>
              <Link href="/cirugia-laparoscopica">+ CIRUGÍA LAPAROSCÓPICA</Link>
              <Link href="/diagnostico/cancer-de-prostata">+ CÁNCER DE PRÓSTATA</Link>
            </div>
            <div className={styles.linkColumn}>
              <Link href="/diagnostico/cancer-de-testiculo">+ CÁNCER DE TESTÍCULO</Link>
              <Link href="/diagnostico/cancer-de-rinon">+ CÁNCER DE RIÑÓN</Link>
              <Link href="/diagnostico/calculos-renales">+ CÁLCULOS RENALES</Link>
              <Link href="/diagnostico/cancer-de-vejiga">+ CÁNCER DE VEJIGA</Link>
            </div>
            <div className={styles.linkColumn}>
              <Link href="/diagnostico/chekup-masculino">+ CHECK UP MASCULINO</Link>
              <Link href="/diagnostico/crecimiento-de-prostata">+ CRECIMIENTO DE LA PRÓSTATA</Link>
              <Link href="/diagnostico/infertilidad-masculina">+ INFERTILIDAD MASCULINA</Link>
              <Link href="/diagnostico/vasectomia">+ VASECTOMÍA</Link>
            </div>
          </div>
          
          <div className={styles.cardsSection}>
            <div className={styles.cardLogos}>
              <Image src="/assets/iconos/tarjetas.png" alt="Tarjetas de crédito" width={150} height={25} style={{ objectFit: 'contain' }} />
            </div>
            <p>ACEPTAMOS TARJETAS DE CRÉDITO</p>
          </div>
        </div>
      </div>

      <footer className={styles.footer}>
        <div className={styles.container}>
          <div className={styles.logoSection}>
            <div className={styles.logo}>
              <Image src="/assets/logotipo/logo-dark.svg" alt="Uro-oncology" width={290} height={78} />
            </div>
            <div className={styles.socials}>
              {/* Instagram */}
              <a href="https://www.instagram.com/uro_oncology/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                <Image src="/assets/iconos/instagram.svg" alt="Instagram" width={30} height={30} />
              </a>
              {/* WhatsApp */}
              <a href="https://api.whatsapp.com/send?phone=523316013840" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">
                <Image src="/assets/iconos/whatsapp.svg" alt="WhatsApp" width={30} height={30} />
              </a>
              {/* Location (Ubicación) */}
              <a href="https://goo.gl/maps/jpEH1og1R52CnmXm7" target="_blank" rel="noopener noreferrer" aria-label="Ubicación">
                <Image src="/assets/iconos/ubicacion.svg" alt="Ubicación" width={30} height={30} />
              </a>
            </div>
            <p className={styles.copyright}>Todos los derechos reservados para Uro-Oncology 2026</p>
          </div>
          
          <div className={styles.bottomLinks}>
            <Link href="/diagnostico">DIAGNÓSTICO</Link>
            <span>|</span>
            <Link href="/tipos-de-cirugia">CIRUGÍAS</Link>
            <span>|</span>
            <Link href="/aviso-de-privacidad">AVISO DE PRIVACIDAD</Link>
            <span>|</span>
            <Link href="/preguntas-frecuentes">PREGUNTAS FRECUENTES</Link>
            <span>|</span>
            <Link href="/equipo-medico">EQUIPO MÉDICO</Link>
          </div>
        </div>
      </footer>

      <div style={{ backgroundColor: '#0A0F1C', paddingTop: '0.875rem', paddingBottom: '0.875rem', borderTop: '1px solid rgba(255,255,255,0.05)', position: 'relative', zIndex: 10 }}>
        <div style={{ maxWidth: '80rem', marginLeft: 'auto', marginRight: 'auto', paddingLeft: '1.5rem', paddingRight: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <a href="https://www.hipha.mx/" style={{ opacity: 0.8, transition: 'opacity 0.2s' }} onMouseOver={(e) => e.currentTarget.style.opacity = '1'} onMouseOut={(e) => e.currentTarget.style.opacity = '0.8'}>
            <img src="/assets/logotipo/desarrollado-por.svg" alt="Desarrollado por Hipha" style={{ height: '1.5rem', display: 'block' }} />
          </a>
        </div>
      </div>
    </>
  );
}
