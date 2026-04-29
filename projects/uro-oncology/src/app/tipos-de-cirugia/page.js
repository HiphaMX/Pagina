import styles from '../page.module.css';

export const metadata = {
  title: 'Tipos de Cirugía | Uro-Oncology',
  description: 'Conoce los tipos de cirugía que realizamos, incluyendo cirugía robótica y de mínima invasión.',
};

import Image from 'next/image';
import Link from 'next/link';

export default function CirugiasPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent} style={{ maxWidth: '1000px', textAlign: 'center' }}>
            <p style={{ fontSize: '1.2rem', color: '#555' }}>
              En Uro Oncology, nos especializamos en las cirugías de mínima invasión, que ofrecen una pronta recuperación y heridas mucho más pequeñas, utilizando lo último en tecnología a nivel mundial brindamos a nuestros pacientes diferentes alternativas para los diferentes padecimientos.
            </p>
          </div>

          <div className={styles.surgeryCardsContainer}>
            <div className={styles.diagnosticoGrid}>
              
              <Link href="/cirugia-robotica" className={styles.surgeryCard}>
                <Image 
                  src="/assets/tipos-de-cirugia/robótica.jpg" 
                  alt="Cirugía Robótica" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CIRUGÍA ROBÓTICA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/cirugia-laparoscopica" className={styles.surgeryCard}>
                <Image 
                  src="/assets/tipos-de-cirugia/laparoscópico00.jpg" 
                  alt="Cirugía Laparoscópica" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CIRUGÍA LAPAROSCÓPICA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/cirugia-endourologica" className={styles.surgeryCard}>
                <Image 
                  src="/assets/tipos-de-cirugia/Endourologia.jpg" 
                  alt="Cirugía Endourológica" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CIRUGÍA ENDOUROLÓGICA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
