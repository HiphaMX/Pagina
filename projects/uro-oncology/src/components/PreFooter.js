import Image from 'next/image';
import Link from 'next/link';
import InsuranceSlider from './InsuranceSlider';
import styles from './PreFooter.module.css';

export default function PreFooter() {
  return (
    <>
      {/* About Doctor Section */}
      <section className={styles.aboutDoctor}>
        <div className="container">
          <div className={styles.aboutDoctorGrid}>
            <div className={styles.doctorImageWrapper}>
              <Image src="/assets/home/foto-adal.jpeg" alt="Dr. Adalberto Castro Alfaro" width={300} height={300} className={styles.doctorImage} />
            </div>
            <div className={styles.doctorInfo}>
              <h3>DR. ADALBERTO CASTRO ALFARO | URÓLOGO</h3>
              <a href="mailto:adal@uro-oncology.com.mx" className={styles.doctorEmail}>adal@uro-oncology.com.mx</a>
              <p>Es uno de los pocos urólogos en México en tener doble una especialidad, lo que le permite ofrecer atención médica integral a cualquier padecimiento oncológico en las vías urinarias, actualmente es director del programa de Cirugía Robótica del Hospital Real San José y miembro del staff de Cirugía Robótica del Hospital Ángeles Lomas en CDMX.</p>
              <Link href="/equipo-medico" className={styles.doctorLink}>CONOCER MÁS</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Insurance Slider */}
      <InsuranceSlider />

      {/* Contact Section */}
      <section className={styles.contactSection}>
        <div className="container">
          <div className={styles.sectionHeader} style={{ marginBottom: '4rem', textAlign: 'center' }}>
            <h2 className={styles.contactTitle}>Contáctanos</h2>
          </div>
          <div className={styles.contactGrid}>
            <div className={styles.contactInfo}>
              <h3>CENTRO MÉDICO REAL SAN JOSÉ<br/>VALLE REAL</h3>
              <p>
                Av. Central 911, Torre de consultorios<br/>
                Piso 7, consultorio 7-B, C.P. 45136<br/>
                Zapopan, Jalisco
              </p>
              <a href="https://goo.gl/maps/jpEH1og1R52CnmXm7" target="_blank" rel="noopener noreferrer" className={styles.contactLinkCyan}>
                VER CÓMO LLEGAR
              </a>
              
              <h3 className={styles.phoneLabel}>TELÉFONO PARA CITAS</h3>
              <a href="tel:3316013840" className={styles.contactLinkCyan}>
                33 1601 3840
              </a>
            </div>
            <div className={styles.contactMap}>
              <iframe 
                src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3410.1775499216697!2d-103.42961092639379!3d20.72094415934757!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0xfca64d39009b54de!2sHospital%20Real%20San%20Jose%20Valle%20Real!5e0!3m2!1ses-419!2smx!4v1591656707981!5m2!1ses-419!2smx" 
                width="100%" 
                height="250" 
                frameBorder="0" 
                style={{border: 0}} 
                allowFullScreen="" 
                aria-hidden="false" 
                tabIndex="0">
              </iframe>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
