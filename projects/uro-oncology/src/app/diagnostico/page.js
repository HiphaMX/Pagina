import styles from '../page.module.css';

export const metadata = {
  title: 'Diagnóstico | Uro-Oncology',
  description: 'Diagnóstico oportuno de enfermedades urológicas y oncológicas.',
};

import Image from 'next/image';
import Link from 'next/link';

export default function DiagnosticoPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          
          <div className={styles.surgeryCardsContainer}>
            <div className={styles.diagnosticoGrid}>
              
              <Link href="/diagnostico/cancer-de-prostata" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/cáncerdepróstata.jpg" 
                  alt="Cáncer de Próstata" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CÁNCER DE PRÓSTATA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/cancer-de-rinon" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/Cancerderinon.jpg" 
                  alt="Cáncer de Riñón" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CÁNCER DE RIÑÓN</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/cancer-de-testiculo" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/cáncerdetesticulo.jpg" 
                  alt="Cáncer de Testículo" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CÁNCER DE TESTÍCULO</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/cancer-de-vejiga" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/Cáncerdevejiga.jpg" 
                  alt="Cáncer de Vejiga" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CÁNCER DE VEJIGA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/calculos-renales" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/cálculosrenaless.jpg" 
                  alt="Cálculos Renales" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CÁLCULOS RENALES</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/crecimiento-de-prostata" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/crecimientoprostatttico.jpg" 
                  alt="Crecimiento de Próstata" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CRECIMIENTO DE PRÓSTATA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/chekup-masculino" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/checkupmasculino.jpg" 
                  alt="Checkup Masculino" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>CHECKUP MASCULINO</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/infertilidad-masculina" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/infertilidadmasculina.jpg" 
                  alt="Infertilidad Masculina" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>INFERTILIDAD MASCULINA</h3>
                  <span className={styles.surgeryCardBtn}>Ver más</span>
                </div>
              </Link>

              <Link href="/diagnostico/vasectomia" className={styles.surgeryCard}>
                <Image 
                  src="/assets/diagnostico/vasectomía.jpg" 
                  alt="Vasectomía" 
                  fill
                  className={styles.surgeryCardImage} 
                />
                <div className={styles.surgeryCardOverlay}></div>
                <div className={styles.surgeryCardContent}>
                  <h3>VASECTOMÍA</h3>
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
