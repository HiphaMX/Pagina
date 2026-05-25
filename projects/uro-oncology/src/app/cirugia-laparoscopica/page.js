import Image from 'next/image';
import styles from '../page.module.css';

export const metadata = {
  title: 'Cirugía Laparoscópica | Uro-Oncology',
  description: 'Tratamientos mediante cirugía laparoscópica de rápida recuperación.',
};

export default function CirugiaLaparoscopicaPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              La cirugía laparoscópica utiliza un tubo delgado llamado laparoscopio, que se inserta en el abdomen a través de una incisión pequeña. Una incisión es un corte pequeño que se hace en la piel durante una cirugía. El tubo tiene una cámara conectada que envía imágenes a un monitor de video. El laparoscopio transmite la imagen de los órganos internos a un monitor, a través del cual el cirujano puede guiarse para realizar diferentes procedimientos quirúrgicos. El laparoscopio magnifica la imagen varias veces respecto al tamaño real, permitiendo una mejor visión de los órganos abdominales, esto permite que un cirujano vea el interior del cuerpo sin causarle lesiones importantes al paciente.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/laparoscopica/5ed3e81697a20af8108e895f_laparoscopico01.jpg" 
                alt="Cirujano observando monitor durante cirugía laparoscópica" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Máxima precisión y cuidado. En Uro Oncology, la cirugía laparoscópica nos permite realizar intervenciones complejas con incisiones milimétricas.</figcaption>
            </figure>

            <p>
              Para poder realizar la cirugía es necesario insuflar la cavidad abdominal con gas (CO2), creando un espacio amplio en el cual se puede trabajar de manera cómoda. Gracias a la visión de alta definición de los equipos actuales se obtiene una mayor precisión y un manejo más delicado de los tejidos y órganos a tratar lo que se traduce en mejores resultados. Para darnos una idea, antiguamente se realizaban grandes incisiones de 20 cm o más, con recuperación por lo menos de 15 días, actualmente realizamos aproximadamente 4 incisiones pequeñas de 0.5 a 1 cm y que en algunos casos pueden salir del hospital al siguiente día de la cirugía.
            </p>
            <p>
              Este tipo de cirugías se pueden denominar como mínimamente invasiva, ya que permite que el tiempo que una persona tiene que pasar en el hospital sea más corto, una recuperación más rápida, menos dolor y cicatrices más pequeñas que con la cirugía tradicional (abierta).
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/laparoscopica/5ed3e836a553da8535e690a2_laparoscopico02.jpg" 
                alt="Instrumental laparoscópico moderno en quirófano" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>En Uro Oncology, evitamos las grandes cicatrices y largas estancias en el hospital, ofreciendo procedimientos de mínima invasión y máximo beneficio.</figcaption>
            </figure>

            <h3>Muy importante considerar:</h3>
            <p>
              Estar especializados en cirugías de mínima invasión significa que podemos ofrecer una alternativa a la cirugía tradicional abierta, pero de acuerdo a las circunstancias específicas de cada caso y en busca de ofrecer una solución para todos nuestros pacientes, también podemos realizar procedimientos quirúrgicos tradicionales, puedes tener tranquilidad de que estarás en las mejores manos.
            </p>

            <h3>Principales ventajas:</h3>
            <ul>
              <li>Menos dolor</li>
              <li>Menor sangrado</li>
              <li>Menor riesgo de complicaciones sobre todo en la herida quirúrgica</li>
              <li>Recuperación más rápida y menos días de hospitalización</li>
              <li>Heridas mínimas con mejores resultados estéticos</li>
              <li>Genera menos estrés en el paciente</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/laparoscopica/5ed3ea0d97a20a14b98e9597_laparoscopico03.jpg" 
                alt="Recuperación rápida post cirugía laparoscópica" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology se compromete con tu pronta recuperación. Retoma tu vida normal en tiempo récord con nuestros especialistas en laparoscopía.</figcaption>
            </figure>

            <p>
              Por medio de la laparoscopia se pueden realizar una serie de procedimientos urológicos que representan una excelente alternativa a los pacientes, entre las ventajas de la cirugía laparoscópica se encuentra el que los pacientes se recuperan con mayor prontitud que cuando son intervenidos con la cirugía tradicional abierta, en la que se hace una incisión grande. Debido a que el cirujano hace sólo unas pequeñas incisiones, en vez de una incisión grande, el dolor postoperatorio es, por lo general, menor. Es importante tomar en cuenta que no todos los pacientes son candidatos a la cirugía laparoscópica, cada persona presenta unas circunstancias únicas que tienen que ser consideradas individualmente.
            </p>
            <p>
              En Uro Oncology nos especializamos en el tratamiento de diferentes padecimientos mediante la cirugía laparoscópica, lo que nos permite marcar diferencia al ser especialistas en cirugías de mínima invasión brindando a nuestros pacientes una rápida recuperación.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
