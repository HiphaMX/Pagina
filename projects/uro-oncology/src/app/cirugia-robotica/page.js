import Image from 'next/image';
import styles from '../page.module.css';

export const metadata = {
  title: 'Cirugía Robótica | Uro-Oncology',
  description: 'Tratamientos urológicos con el sistema quirúrgico da Vinci.',
};

export default function CirugiaRoboticaPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              El sistema quirúrgico da Vinci le brinda a su cirujano un conjunto avanzado de instrumentos para usar en la realización de cirugía de invasión mínima asistida por robot. El término "robótico" a menudo engaña a las personas, los robots no realizan cirugía, es el cirujano mediante el uso de sus instrumentos que guía los brazos robóticos a través de una consola.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/robotica/5ed32e61412d2b613ab027c9_da-vincy-componentes.jpg" 
                alt="Componentes del sistema quirúrgico da Vinci" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Tecnología de vanguardia a tu alcance. En Uro Oncology utilizamos el sistema da Vinci para realizar cirugías con una precisión superior.</figcaption>
            </figure>

            <p>
              En nuestros días los avances tecnológicos nos ofrecen innovadoras alternativas para el cuidado de la salud, en el caso de la urología, es una de las especialidades quirúrgicas que más ha sacado provecho al respecto gracias al sistema quirúrgico da Vinci , que ofrece la posibilidad de realizar tratamientos quirúrgicos, maximizando las habilidades del cirujano, con visión de alta definición y movimientos precisos, logrando un manejo excelente en los procedimientos a realizar.
            </p>

            <h3>La tecnología al cuidado de tu salud urológica</h3>
            <p>
              El sistema quirúrgico da Vinci traduce los movimientos de las manos de su cirujano en la consola en tiempo real, doblando y girando los instrumentos mientras realiza diferentes procedimientos. Los pequeños instrumentos se mueven como una mano humana, pero con un mayor rango de precisión y movimiento.
            </p>
            <p>
              El sistema de visión da Vinci también ofrece vistas 3D de alta definición altamente ampliadas del área quirúrgica, el tamaño del instrumental hace posible que los cirujanos operen a través de pequeñas incisiones, definiendo el término cirugía de mínima invasión.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/robotica/5ed330443b7997fcfc5581c6_davincysurgical.jpg" 
                alt="Cirujano operando en consola da Vinci" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Manos expertas, movimientos perfectos. Uro Oncology cuenta con certificación internacional para cuidar tu salud con las técnicas robóticas más avanzadas.</figcaption>
            </figure>

            <p>
              El sistema quirúrgico da Vinci se compone de 3 elementos, la consola del cirujano, en donde el cirujano se sienta y controla los instrumentos observando la anatomía del paciente en 3D de alta definición, el carro de pacientes que se ubica junto a la cama, sostiene la cámara y los instrumentos que el cirujano controla desde su consola y por último el carro de visión, componente que hace posible la comunicación entre los componentes y admite el sistema de visión 3D de alta definición.
            </p>

            <h3>Cirugías de mínima invasión</h3>
            <p>
              La especialidad de urología cubre las condiciones del sistema urinario masculino y femenino y el sistema reproductor masculino. El tracto urinario incluye los riñones, la vejiga y los tejidos y músculos conectivos asociados. El sistema reproductor masculino abarca la glándula prostática, el pene, los testículos y las estructuras conectivas asociadas. Las afecciones que causan problemas en estos sistemas incluyen, entre otras, agrandamiento de la próstata, tumores benignos y cáncer, pueden requerir atención médica. En el caso de cáncer o cuando los cambios en el estilo de vida, los medicamentos y otras opciones no alivian los síntomas de otras afecciones, su médico puede sugerir una cirugía.
            </p>
            <p>
              En el pasado, los cirujanos hicieron grandes incisiones en la piel y los músculos para poder ver y trabajar directamente en el área de interés, esto se llama cirugía abierta.
            </p>
            <p>
              Hoy en día, los médicos aún realizan cirugía abierta, pero también pueden realizar muchos procedimientos urológicos utilizando cirugía laparoscópica o asistida por robot mínimamente invasiva, posiblemente con la tecnología da Vinci. Ambas opciones quirúrgicas mínimamente invasivas requieren una o unas pocas incisiones pequeñas que los médicos utilizan para insertar equipos quirúrgicos y una cámara para su visualización. En la cirugía laparoscópica, los médicos usan herramientas especiales de mango largo para realizar la cirugía mientras ven imágenes ampliadas del laparoscopio (cámara) en una pantalla de video.
            </p>

            <div className={styles.videoContainer} style={{ marginBottom: '3rem', marginTop: '2rem' }}>
              <iframe 
                width="100%" 
                height="500" 
                src="https://www.youtube.com/embed/Z6bLCj2cMV4" 
                title="Procedimientos urológicos asistidos por robot - Uro-Oncology" 
                frameBorder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                allowFullScreen
                style={{ borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
              ></iframe>
            </div>

            <h3>Procedimientos urológicos asistidos por robot</h3>
            <p>
              El sistema quirúrgico da Vinci llego para revolucionar la forma de realizar los procedimientos de los principales padecimientos urológicos:
            </p>
            <ul>
              <li><strong>Prostatectomía:</strong> cirugía de próstata que requiere la extirpación de la próstata y las vesículas seminales junto con ganglios linfáticos en los casos indicados.</li>
              <li><strong>Nefrectomía parcial y total:</strong> esta es la cirugía usada para tratar el cáncer de riñón, dependiendo del tamaño y la localización del tumor, se podría extirpar únicamente el tumor, dejando el riñón no afectado por el tumor (nefrectomía parcial) o todo extirpar todo el riñón (nefrectomía radical).</li>
              <li><strong>Extracción de quiste:</strong> cirugía para extraer un quiste del riñón.</li>
              <li><strong>Cistectomía:</strong> cirugía de vejiga, utilizada para tratar el cáncer de vejiga infiltrante o de alto grado de malignidad.</li>
              <li><strong>Pieloplastia:</strong> reconstrucción quirúrgica de la pelvis renal, para evitar el deterioro de la función del riñón a mediano y largo plazo.</li>
              <li><strong>Implantación ureteral:</strong> fijación de los tubos que conectan la vejiga a los riñones.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/robotica/5ed338f64b317bcf9078bc41_pronta recuperación.jpg" 
                alt="Paciente de urología sonriendo tras pronta recuperación" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology prioriza tu rápida reintegración a la vida diaria con la mejor tecnología mínimamente invasiva del mundo.</figcaption>
            </figure>

            <h3>Principales ventajas</h3>
            <ul>
              <li>Menos riesgo de complicaciones</li>
              <li>Menor sangrado y menor tasa de transfusiones sanguíneas</li>
              <li>Reducción de los días de hospitalización</li>
              <li>Menor dolor post quirúrgico</li>
              <li>Recuperación más rápida y reincorporación a su vida cotidiana en un periodo de tiempo más corto</li>
              <li>Menor tasa de de secuelas propias del procedimiento como incontinencia urinaria o disfunción eréctil</li>
              <li>Heridas muy pequeñas</li>
              <li>Genera mayor confianza y menos estrés en el paciente</li>
            </ul>
            <p>
              En Uro Oncology nos especializamos en el tratamiento de diferentes padecimientos mediante la cirugía robótica con el sistema quirúrgico da Vinci, contamos con formación en Cirugía Robótica realizada en el extranjero (Francia) lo que nos permite marcar diferencia al ser especialistas en cirugías de mínima invasión brindando a nuestros pacientes una rápida recuperación.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
