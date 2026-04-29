import styles from '../../page.module.css';
import Image from 'next/image';

export const metadata = {
  title: 'Checkup Masculino | Uro-Oncology',
  description: 'Información sobre el checkup masculino.',
};

export default function CheckUpMasculinoPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              Se sabe que el temor y la no aceptación de los cambios físicos y psicológicos son los principales factores que evitan que los hombres pongan un pie en el consultorio, la mayoría de ellos se justifica con falta de tiempo y sólo visitan al especialista cuando los dolores o la enfermedad los obliga. En la actualidad se sabe que el promedio general de vida de los varones es de dos a tres años menor que el de las mujeres, sin duda esto se debe en gran medida, a la falta, desde la infancia, de una cultura de prevención entorno a su salud.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/chekup-masculino/Checkup masculino1.jpg" 
                alt="Consulta preventiva y chequeo de salud para hombres" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Deja las excusas a un lado. Uro Oncology te ofrece un entorno seguro, confidencial y profesional para cuidar de tu salud como te mereces.</figcaption>
            </figure>

            <h3>¿Cuándo es recomendable realizarlo?</h3>
            <p>
              En general, se recomienda realizar chequeos de rutina, pero si tienes de 40 años en adelante, el Check Up masculino se vuelve muy relevante para cuidar tu salud urológica principalmente, las vías urinarias son las primeras en sufrir los estragos del paso del tiempo, solamente deberás programar una cita de valoración para la realización de exámenes de detección oportuna de cáncer de próstata, valorar tu función sexual y el estado de la dinámica miccional, en caso de detectar alguna anormalidad, estaremos a tiempo para ofrecer un manejo preventivo o correctivo de la mayoría de los casos.
            </p>
            <p>
              El Check Up masculino comprende exámenes clínicos y procedimientos de tecnología con los que podrás evaluar el estado de salud urológica actual, con ello podrás tomar acciones de tratamiento que eviten o retarden la presencia de enfermedades que al no detectarse a tiempo, podrán afectar tu calidad de vida a corto, mediano o largo plazo.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/chekup-masculino/Checkup masculino2.jpg" 
                alt="Hombre mayor sonriendo y disfrutando de un estado de salud óptimo" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Si tienes más de 40 años, tu salud debe ser tu prioridad. Uro Oncology cuenta con la tecnología para realizar un diagnóstico completo y oportuno.</figcaption>
            </figure>

            <h3>¿Por qué hacérmelo?</h3>
            <p>
              Es muy común presentar malestares constantes o dolores crónicos que comúnmente asociamos con estrés o como algo pasajero y suelen volverse parte de nuestra vida cotidiana. Sin embargo, al realizarnos un Check-up masculino se pueden diagnosticar enfermedades que se han denominado “asesinos silenciosos” la formación de tumores e incluso hasta el cáncer.
            </p>

            <h3>¿Por qué es importante?</h3>
            <p>
              Algunos de los padecimientos más graves en urología pueden no presentar síntomas en sus inicios, es por eso que detectar cualquier anomalía de manera oportuna, aumentan las probabilidades de éxito del tratamiento. Además, el tiempo de uso del tratamiento será menor y la recuperación será más rápida.
            </p>
            <p>
              Es recomendable que si tienes más de 40 años y no te haz preocupado por tu salud en años anteriores, sin pretexto alguno se practiquen un Check Up masculino programando una valoración médica lo antes posible, en Uro Oncology fomentamos la cultura de la prevención y somos especialistas en los diferentes padecimientos urológicos que con el avance de la edad, la probabilidad de presentarlos aumenta dramáticamente, no pierdas el tiempo y programa tu cita.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/chekup-masculino/Checkup masculino3.jpg" 
                alt="Paciente hablando abiertamente de sus síntomas con el médico" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Adelántate a los padecimientos silenciosos. Agenda hoy tu Check Up Masculino en Uro Oncology y toma el control absoluto de tu bienestar.</figcaption>
            </figure>
          </div>
        </div>
      </section>
    </div>
  );
}
