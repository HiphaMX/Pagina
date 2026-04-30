import Image from 'next/image';
import styles from '../page.module.css';

export const metadata = {
  title: 'Cirugía Endourológica | Uro-Oncology',
  description: 'Especialistas en cirugía endourológica y de mínima invasión.',
};

export default function CirugiaEndourologicaPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              Una endoscopía es un procedimiento que permite que el médico vea el interior de su cuerpo. Utiliza un instrumento llamado endoscopio o tubo visor. Los endoscopios tienen una cámara diminuta unida a un tubo largo y delgado. El médico lo mueve a través de un túnel o apertura del cuerpo para ver el interior de un órgano.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/endourologica/5ed40777ec5df2ec35fb4d68_endourologica-00.jpg" 
                alt="Cirugía endourológica de mínima invasión" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Regresa a casa el mismo día. La cirugía endourológica en Uro Oncology es un procedimiento de mínima invasión con un impacto mínimo en tu cuerpo.</figcaption>
            </figure>

            <p>
              La endourología es la rama de la urología, la cual se encuentra especializada en la resolución de enfermedades de las vías urinarias mediante la aplicación de un tratamiento de mínima invasión, utilizando diferentes métodos avanzados tales como el láser y técnicas de mínima invasión como la cirugía robótica, laparascópica y endourológica. La endourología nace gracias al aporte de diversos médicos especialistas en urología que se han encargado de desarrollar avances tecnológicos, dentro de los cuales han surgido excelentes instrumentos sumamente sofisticados que pueden entrar y desplazarse por todo el sistema urinario, identificando y tratando cualquier tipo de piedras urinarias, tumores, cicatrices y muchas otras patologías sin la necesidad de realizar una incisión (herida quirúrgica).
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/endourologica/5ed407f4a90a9c09c2204e2e_Endourológica02.jpg" 
                alt="Instrumental de alta tecnología en endourología" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Dile adiós a las cirugías abiertas. Uro Oncology pone a tu disposición tecnología láser de vanguardia para tratar padecimientos sin cortes extensos.</figcaption>
            </figure>

            <p>
              Gracias los avances tecnológicos que ha presentado la endourología en su campo, hoy en día es muy raro realizar una cirugía abierta para extraer cualquier tipo de cálculo en el tracto urinario, así como gran cantidad de patologías del aparato urinario, tales como la hipertrofia prostática (hiperplasia benigna de próstata) y la vejiga neurogénica (vejiga hiperactiva).
            </p>

            <h3>Principales ventajas:</h3>
            <ul>
              <li>Menos dolor</li>
              <li>Menor sangrado</li>
              <li>Menor riesgo de complicaciones sobre todo en la herida quirúrgica</li>
              <li>Recuperación más rápida y menos días de hospitalización</li>
              <li>Genera menos estrés en el paciente</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/tipos-de-cirugia/endourologica/5ed40983a0977fb3f34b56ff_Endourológica04.jpg" 
                alt="Recuperación rápida y sin estrés" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology te devuelve a tu vida cotidiana. Olvida las semanas de recuperación y retoma tu ritmo casi de forma inmediata.</figcaption>
            </figure>

            <p>
              Las personas que son sometidas a cirugía endourológica pueden salir del hospital en menos de 24 hrs. y regresan a su vida cotidiana casi de forma inmediata a diferencia de una cirugía convencional abierta en la cual pueden tardar hasta semanas.
            </p>
            <p>
              En Uro Oncology nos especializamos en el tratamiento de diferentes padecimientos mediante la cirugía endourológica, estar especializados en cirugías de mínima invasión significa que podemos ofrecer una alternativa a la cirugía tradicional abierta, pero de acuerdo a las circunstancias específicas de cada caso y en busca de ofrecer una solución para todos nuestros pacientes, también podemos realizar procedimientos quirúrgicos tradicionales, puedes tener tranquilidad de que estarás en las mejores manos.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
