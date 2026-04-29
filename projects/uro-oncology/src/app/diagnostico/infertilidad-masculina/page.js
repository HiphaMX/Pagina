import Image from 'next/image';
import styles from '../../page.module.css';

export const metadata = {
  title: 'Infertilidad Masculina | Uro-Oncology',
  description: 'Diagnóstico y tratamiento de la infertilidad masculina y el varicocele.',
};

export default function InfertilidadMasculinaPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              Los hombres también pueden contribuir a la infertilidad en una pareja, de hecho, en aproximadamente el 40 % de los casos, los hombres son la única causa o una causa contribuyente de la infertilidad en la pareja, se denomina infertilidad masculina después de un año sin poder lograr el embarazo con actividad sexual sin protección.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/infertilidad-masculina/Infertilidad masculina00.jpg" 
                alt="Pareja conversando sobre fertilidad" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Hablarlo es el primer paso. En Uro Oncology abordamos la infertilidad masculina con empatía, profesionalismo y las mejores opciones de tratamiento.</figcaption>
            </figure>

            <p>
              Aproximadamente el 15 % de las parejas tiene algún problema de fertilidad. La infertilidad masculina puede deberse a cuentas bajas o nulas de espermatozoides, poca movilidad de los mismos, o forma anormal del espermatozoide, además de problemas obstructivos que imposibiliten su paso adecuado, las venas agrandadas alteran el flujo sanguíneo del testículo y provocan un aumento de la temperatura, lo cual afecta negativamente la producción de espermatozoides.
            </p>

            <h3>Varicocele, la causa más común</h3>
            <p>
              Una de las razones más frecuentes de la infertilidad, es un padecimiento que se le conoce como varicocele, se forma cuando las válvulas dentro de las venas que hay a lo largo del cordón espermático impiden que la sangre circule apropiadamente. La sangre se acumula, lo que lleva a una hinchazón y dilatación de dichas venas, muy similar a las venas varicosas en las piernas. La mayoría de las veces, los varicoceles se desarrollan lentamente, son más comunes en hombres entre 15 y 25 años de edad y se observan con más frecuencia en el lado izquierdo del escroto.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/infertilidad-masculina/infertilidadmasculina1.jpg" 
                alt="Médico dando diagnóstico de varicocele" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>La infertilidad no es un diagnóstico definitivo, es una condición tratable. Uro Oncology te ofrece soluciones avanzadas para alcanzar tu sueño de ser padre.</figcaption>
            </figure>

            <h3>Signos o síntomas de varicocele</h3>
            <p>
              En muchos de los casos no se presenta ningún síntoma y se detecta por la disminución del conteo de espermatozoides, algunos de los signos o síntomas de este padecimiento incluyen:
            </p>
            <ul>
              <li>Venas agrandadas y retorcidas en el escroto</li>
              <li>Dolor o incomodidad</li>
              <li>Tumor testicular indoloro, inflamación del escroto o protuberancia dentro del escroto</li>
              <li>Posibles problemas de infertilidad o disminución del conteo de espermatozoides</li>
            </ul>

            <p>
              En la mayoría de los casos, las causas de infertilidad masculina son tratables, sin embargo, esto puede representar estrés y frustración en la vida de pareja, ahora sabes que un especialista puede ayudarte a solucionarlo, lo mejor es hablar con tu pareja y juntos enfrentar este contratiempo, el primer paso será programar una cita de valoración.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
