import styles from '../../page.module.css';
import Image from 'next/image';

export const metadata = {
  title: 'Crecimiento de Próstata | Uro-Oncology',
  description: 'Diagnóstico y tratamiento del crecimiento de próstata.',
};

export default function CrecimientoDeProstataPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              La próstata es una glándula que forma parte del sistema reproductivo masculino, esta ayuda con la producción de semen, el fluido que contiene esperma, rodea el tubo que lleva la orina fuera del cuerpo. A medida que los hombres envejecen, la próstata se va agrandando, pero si se agranda demasiado, puede causar problemas. Esta afección también se conoce como hiperplasia prostática benigna (HPB). La mayoría de los hombres la padecerán al envejecer. Un agrandamiento de la próstata significa que la glándula se ha vuelto más grande y le sucede a casi todos los hombres cuando van envejeciendo, los síntomas comienzan después de los 50 años.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/crecimiento-de-prostata/Crecimiento de prostata1.jpg" 
                alt="Hombre experimentando síntomas de crecimiento prostático" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>No te acostumbres a las molestias. En Uro Oncology contamos con tratamientos avanzados para aliviar los síntomas de hiperplasia prostática benigna de manera segura y eficaz.</figcaption>
            </figure>

            <h3>Signos y síntomas del crecimiento de próstata</h3>
            <p>
              El crecimiento prostático no es una afección cancerosa y no se cree que aumente el riesgo de cáncer de próstata aunque los primeros síntomas sean los mismos, es momento de programar una cita:
            </p>
            <ul>
              <li>Goteo al final de la micción</li>
              <li>Incapacidad para orinar (retención urinaria)</li>
              <li>Vaciado incompleto de la vejiga</li>
              <li>Incontinencia</li>
              <li>Necesidad de orinar dos o más veces por noche</li>
              <li>Micción dolorosa u orina con sangre (pueden ser indicios de una infección)</li>
              <li>Dificultad o demora para comenzar a orinar</li>
              <li>Hacer fuerza al orinar</li>
              <li>Urgencia urinaria fuerte y repentina</li>
              <li>Chorro de orina débil</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/crecimiento-de-prostata/Crecimiento de prostata2.jpg" 
                alt="Adulto mayor saludable en un entorno de paz" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Cerca del 50% de los hombres mayores de 50 años presentan esta afección. Uro Oncology te devuelve el confort y el ritmo de tu vida.</figcaption>
            </figure>

            <h3>Síntomas leves ¿Qué hacer si se presentan?</h3>
            <ul>
              <li>Orine cuando apenas sienta ganas, vaya al baño cuando tenga la oportunidad, aun si no siente la necesidad de orinar.</li>
              <li>Evite el alcohol y la cafeína, especialmente después de la cena.</li>
              <li>No beba cantidades excesivas de líquidos de una sola vez, distribuya el consumo de líquidos durante el día, evite su ingesta 2 horas antes de acostarse.</li>
              <li>Trate de no tomar medicamentos de venta libre para el resfriado o sinusitis que contengan descongestionantes o antihistamínicos pues pueden incrementar los síntomas.</li>
              <li>Manténgase caliente y haga ejercicio regularmente, el clima frío y la falta de actividad física pueden empeorar los síntomas.</li>
              <li>Reduzca el estrés, el nerviosismo y la tensión pueden llevar a orinar más frecuentemente.</li>
            </ul>
            <p>
              Aún cuando sean síntomas leves, lo más recomendable es acudir con un especialista en cuanto antes, el agrandamiento de próstata grave puede causar serios problemas más adelante, como infecciones del tracto urinario y daño en la vejiga o en los riñones, pero si se detecta a tiempo, es probable evitar estos problemas, es preferible programar una cita de diagnóstico.
            </p>

            <h3>¿Qué causa el crecimiento prostático?</h3>
            <p>
              No se entiende cabalmente la causa exacta de la del crecimiento prostático, pero parece estar relacionada con el envejecimiento. El cambio en los niveles de hormonas masculinas a medida que un hombre envejece también puede ser una causa, alrededor del 50% de los hombres mayores de 50 años tienen esta afección e incrementa con el paso de los años, hasta el 90% de los hombres mayores de 80 años la tienen, algunos de los siguientes factores podrían aumentar el riesgo de padecerla:
            </p>
            <ul>
              <li>Tener 40 años o más.</li>
              <li>Antecedentes familiares.</li>
              <li>Sobrepeso.</li>
              <li>Tener enfermedades cardíacas y circulatorias.</li>
              <li>Padecer diabetes tipo 2.</li>
              <li>Falta de ejercicio.</li>
              <li>Tener disfunción eréctil.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/crecimiento-de-prostata/Crecimiento de prostata3.jpg" 
                alt="Prevención y estilo de vida activo para la salud de la próstata" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology recomienda mantener un peso ideal y dejar el cigarro para proteger tu próstata y mejorar tu vitalidad diariamente.</figcaption>
            </figure>

            <h3>¿Se puede prevenir el crecimiento prostático?</h3>
            <p>
              La mejor manera de reducir las probabilidades de padecer crecimiento prostático, es generando hábitos saludables, eliminando el tabaquismo y consumo de alcohol nos ayudarán a mantener nuestra salud urológica.
            </p>
            <ul>
              <li>Cuida tu alimentación, evita los alimentos picantes</li>
              <li>Deja de fumar</li>
              <li>Realiza alguna actividad física para mantenerte en tu peso ideal</li>
              <li>Disminuye el consumo de bebidas alcohólicas</li>
            </ul>
            <p>
              Si tuvieras alguna inquietud sobre tu estado de salud, lo más recomendable es que programes una cita en cuanto antes, si tienes más de 40 años, es un buen momento para realizar un check up médico y comenzar a cuidar tu salud urológico, cualquier padecimiento tiene mayores alternativas si se detecta a tiempo, no pongas en riesgo tu salud.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
