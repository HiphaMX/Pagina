import Image from 'next/image';
import Link from 'next/link';
import Slider from '@/components/Slider';
import styles from './page.module.css';

export default function Home() {
  return (
    <div className={styles.page}>
      
      {/* Intro Section before Slider */}
      <section className={styles.introSection}>
        <div className="container">
          <h2>Tu salud urológica, nuestra misión</h2>
          <p>
            Los padecimientos de las vías urinarias no distinguen edad ni sexo, pueden llegar a presentarse en alguna etapa de la vida, déjanos encargarnos de tu salud urológica, para que tu puedas seguir disfrutando tu vida.
          </p>
        </div>
      </section>

      {/* Dynamic Slider */}
      <Slider />

      {/* Specialists Section */}
      <section className={styles.specialists}>
        <div className="container">
          <div className={styles.specialistsHeader}>
            <h2>Somos especialistas</h2>
            <p>
              Nos enfocamos en generar una experiencia agradable para nuestros pacientes la <strong>mejor experiencia en el cuidado de tu salud</strong>, con la tecnología más avanzada, brindando un seguimiento puntual desde el inicio hasta el fin de su tratamiento, estaremos ahí para recuperar tu tranquilidad.
            </p>
          </div>
        </div>
        <div className={styles.specialistsGrid}>
          <div className={styles.specialistCardCyan}>
            <div className={styles.specialistCardInner}>
              <h2>Urología + Oncología</h2>
              <p>
                Actualmente, somos pocos los urólogos en México en tener <strong>doble una especialidad</strong>, lo que nos permite ofrecer atención médica integral a cualquier <strong>padecimiento oncológico</strong> en las vías urinarias, además de los padecimientos normales.
              </p>
              <Link href="/equipo-medico" className={styles.btnOutlineDark}>
                Más información
              </Link>
            </div>
          </div>
          <div className={styles.specialistCardGray}>
            <div className={styles.specialistCardInner}>
              <h2>Cirugía robótica</h2>
              <p>
                Contamos con formación en <strong>Cirugía Robótica</strong> realizada en el extranjero (Francia) lo que nos permite marcar diferencia al ser especialistas en <strong>cirugías de mínima invasión</strong> brindando a nuestros pacientes una rápida recuperación.
              </p>
              <Link href="/cirugia-robotica" className={styles.btnOutlineDark}>
                Más información
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Diagnostic Section */}
      <section className={styles.diagnosticSection}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <h2>Diagnóstico a tiempo</h2>
            <p>Sabemos que tus amigos y familiares pueden crear muchas más dudas de las que ya tenemos, si tienes alguna sospecha sobre algún síntoma que te inquieta, elige la mejor alternativa.</p>
          </div>
          <div className={styles.diagnosticImageContainer}>
            <Image src="/assets/home/recurso-13.svg" alt="Preguntas y diagnóstico" width={800} height={400} className={styles.diagnosticImage} />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.cta}>
        <div className="container">
          <div className={styles.ctaContent}>
            <h2>¿Programamos una cita?</h2>
            <p>Puedes dejarnos tus datos incluyendo tus síntomas, revisaremos tus respuestas en cuanto antes y te contactaremos para revisar tu caso y definir si necesitamos realizar un diagnóstico presencial.</p>
            <a href="https://api.whatsapp.com/send?phone=523316013840" className={styles.btnOutlineCyan} target="_blank" rel="noopener noreferrer">
              Programar una cita
            </a>
          </div>
        </div>
      </section>

      {/* Services CTA Section */}
      <section className={styles.services}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <h2>¿Qué tipos de cirugía realizamos?</h2>
            <p style={{ maxWidth: '900px', margin: '0 auto', fontSize: '1.15rem' }}>
              Contamos con lo último en tecnología, nos especializamos en cirugías de mínima invasión, robótica, laparoscópica y endourológica, sin embargo, la infraestructura de la red de hospitales públicos y privados no es suficiente, por lo que también realizamos cirugías abiertas, adaptándonos a las necesidades de nuestros pacientes.
            </p>
          </div>
          <div className={styles.surgeryCtaGrid}>
            <div className={styles.surgeryCtaCard}>
              <div className={styles.surgeryLabel}>Cirugía robótica</div>
              <Image src="/assets/home/cirugia-robotica.jpg" alt="Cirugía Robótica" width={350} height={350} className={styles.surgeryImg} />
              <div className={styles.surgeryCtaContent}>
                <Link href="/cirugia-robotica" className={`${styles.surgeryBtn}`}>
                  Ver más
                </Link>
              </div>
            </div>
            <div className={styles.surgeryCtaCard}>
              <div className={styles.surgeryLabel}>Cirugía laparoscópica</div>
              <Image src="/assets/home/cirugia-laparoscopica.jpg" alt="Cirugía Laparoscópica" width={350} height={350} className={styles.surgeryImg} />
              <div className={styles.surgeryCtaContent}>
                <Link href="/cirugia-laparoscopica" className={`${styles.surgeryBtn}`}>
                  Ver más
                </Link>
              </div>
            </div>
            <div className={styles.surgeryCtaCard}>
              <div className={styles.surgeryLabel}>Cirugía endourológica</div>
              <Image src="/assets/home/cirugia-endourologica.jpg" alt="Cirugía Endourológica" width={350} height={350} className={styles.surgeryImg} />
              <div className={styles.surgeryCtaContent}>
                <Link href="/cirugia-endourologica" className={`${styles.surgeryBtn}`}>
                  Ver más
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className={styles.videoSection}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <h2>Conoce más sobre la Cirugía Robótica</h2>
            <p>Descubre cómo el sistema Da Vinci mejora significativamente la recuperación de nuestros pacientes.</p>
          </div>
        </div>
        <div className={styles.videoContainerFull}>
          <iframe 
            width="100%" 
            height="100%" 
            src="https://www.youtube.com/embed/Z6bLCj2cMV4" 
            title="YouTube video player" 
            frameBorder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
            referrerPolicy="strict-origin-when-cross-origin" 
            allowFullScreen>
          </iframe>
        </div>
      </section>

    </div>
  );
}
