import styles from '../../page.module.css';

export const metadata = {
  title: 'Cáncer de Testículo | Uro-Oncology',
  description: 'Diagnóstico y tratamiento del cáncer de testículo.',
};

import Image from 'next/image';

export default function CancerDeTesticuloPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              El cáncer que se origina en los testículos se denomina cáncer de testículo, para entender este cáncer, resulta útil conocer sobre la estructura normal y la función de los testículos.
            </p>

            <h3>¿Qué son los testículos?</h3>
            <p>
              Los testículos son parte del sistema reproductor masculino, los dos órganos son normalmente cada uno un poco más pequeños que una pelota de golf en los varones adultos. Se mantienen dentro de un saco de piel llamado escroto. El escroto cuelga debajo de la base del pene. Los testículos tienen dos funciones principales:
            </p>
            <ul>
              <li>Producen las hormonas masculinas (andrógenos), como la testosterona</li>
              <li>Producen espermatozoides, las células masculinas necesarias para fertilizar la célula sexual femenina (óvulo), y así comenzar un embarazo.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-testiculo/Cancer de testiculo1.jpg" 
                alt="Prevención del cáncer de testículo y salud reproductiva" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology protege tu bienestar integral. Entender la anatomía y función de tu cuerpo es el primer paso hacia una salud preventiva sólida.</figcaption>
            </figure>

            <h3>¿Es común el cáncer de testículo?</h3>
            <p>
              Para el año 2020, los cálculos de la Sociedad Americana Contra el Cáncer para este cáncer en los Estados Unidos son:
            </p>
            <ul>
              <li>Se diagnosticarán alrededor de 9,610 nuevos casos de cáncer de testículo.</li>
              <li>Alrededor de 440 hombres morirán de cáncer de testículo.</li>
            </ul>
            <p>
              La tasa de incidencia del cáncer de testículo ha estado aumentando en los Estados Unidos y en muchos otros países durante varias décadas. Los expertos no han podido identificar los motivos para este aumento. No obstante, la tasa de aumento ha disminuido recientemente. El cáncer de testículo no es común; aproximadamente 1 de cada 250 varones padecerá cáncer de testículo en algún momento de su vida.
            </p>
            <p>
              La edad promedio al momento de realizarse el diagnóstico de cáncer de testículo es de aproximadamente 33 años. Esta enfermedad afecta principalmente a los hombres jóvenes y de mediana edad, aunque alrededor de 6% de los casos ocurre en niños y adolescentes, y alrededor de 8% ocurre en hombres mayores de 55 años. Debido a que usualmente el cáncer de testículo se puede tratar con éxito, el riesgo de que un hombre muera a causa de este cáncer es muy bajo: alrededor de 1 en 5,000.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-testiculo/Cancer de testiculo2.jpg" 
                alt="Detección temprana del cáncer de testículo en adultos jóvenes" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Un diagnóstico a tiempo es sinónimo de cura. En Uro Oncology brindamos esperanza y tratamientos altamente efectivos para hombres jóvenes y adultos.</figcaption>
            </figure>

            <h3>¿Se puede encontrar el cáncer de testículo en sus comienzos?</h3>
            <p>
              La mayoría de este tipo de cáncer se puede detectar en etapas tempranas, cuando todavía son pequeños y no se han propagado. En algunos hombres, el cáncer de testículo durante las primeras etapas puede causar síntomas que propician que se busque atención médica. La mayoría de las veces se presenta un abultamiento en el testículo como primer síntoma, o el testículo podría estar hinchado o más grande de lo normal. Sin embargo, puede que algunos tipos de cáncer de testículo no causen síntomas hasta que ya han alcanzado una etapa avanzada.
            </p>
            <p>
              Algunos médicos recomiendan que todos los hombres examinen sus testículos mensualmente después de la pubertad sin embargo, el autoexamen mensual de los testículos es una decisión personal. Además de esto, si tienes ciertos factores de riesgo que aumenten sus probabilidades de cáncer de testículo (como un testículo que no descendió, tumor previo de las células germinales en un testículo o antecedentes familiares), debe considerar seriamente hacerse el autoexamen mensualmente y hablar con un especialista sobre esto en particular.
            </p>

            <h3>Autoexamen testicular</h3>
            <p>
              El mejor momento para hacerse el examen de sus testículos es durante o después de un baño o ducha, cuando la piel del escroto está relajada.
            </p>
            <ul>
              <li>Procure mantener su pene apartado durante el examen de cada testículo por separado.</li>
              <li>Sostenga su testículo entre sus pulgares y los dedos con ambas manos y ruédelo lentamente entre los dedos.</li>
              <li>Busque y sienta cualquier abultamiento duro o nódulo (masa redonda uniforme) o cualquier cambio en el tamaño, forma o consistencia de los testículos.</li>
            </ul>
            <p>
              Resulta normal que un testículo esté ligeramente más grande que el otro, y que uno cuelgue más abajo que el otro. Además, debe tener en cuenta que por naturaleza, cada testículo tiene un pequeño tubo enrollado (llamado epidídimo) que se puede sentir como una pequeña protuberancia en la parte exterior media o superior del testículo. Los testículos normales también contienen vasos sanguíneos, tejidos de soporte y conductos por donde pasa el semen. Al principio, algunos hombres podrían confundir esto con abultamientos anormales. Si tiene inquietudes, puede preguntar a un especialista.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-testiculo/Cancer de testiculo3.jpg" 
                alt="Técnica de autoexploración testicular preventiva" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology fomenta el autoexamen mensual. Tomarte unos minutos durante la ducha puede marcar la diferencia y salvar tu vida.</figcaption>
            </figure>

            <h3>Signos y síntomas de cáncer de testículo</h3>
            <p>
              Es más probable que muchos de estos síntomas sean por otra causa y no por cáncer de testículo. Hay ciertas afecciones no cancerosas, tales como las lesiones o inflamación testicular, que pueden causar síntomas muy similares a los del cáncer testicular. Algunos hombres con cáncer de testículo no presentan síntoma alguno y su cáncer se detecta durante pruebas médicas para otras enfermedades. Por ejemplo, a veces los estudios por imágenes realizados para determinar la causa de infertilidad pueden ser descubiertos.
            </p>
            <ul>
              <li><strong>Masa o hinchazón en el testículo:</strong> Con más frecuencia, el primer síntoma de cáncer de testículo consiste en una masa o abultamiento en el testículo, o el testículo podría estar hinchado o más grande. (Es normal que un testículo esté ligeramente más grande que el otro, y que uno cuelgue más abajo que el otro). Algunos tumores testiculares pueden causar dolor, pero la mayoría de las veces no se siente dolor. Los hombres con cáncer de testículo también pueden presentar una sensación de pesadez o dolor en la parte baja del vientre (abdomen) o en el escroto.</li>
              <li><strong>Irritación o crecimiento de los senos:</strong> En pocos casos, los tumores de células germinales pueden causar que los senos crezcan o presenten irritación. Esto ocurre porque ciertos tipos de tumores de las células germinales segregan altos niveles de una hormona llamada gonadotropina coriónica humana (HCG, por sus siglas en inglés), que estimula el crecimiento de los senos pueden producir estrógenos (hormonas sexuales femeninas), lo que puede causar crecimiento de los senos o pérdida de deseo sexual.</li>
              <li><strong>Pubertad temprana:</strong> los tumores productores de andrógenos pueden no causar síntomas en los hombres, pero en los niños pueden causar signos de pubertad a una edad anormalmente temprana, como voz más profunda y crecimiento del vello facial y del cuerpo.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-testiculo/Cancer de testiculo4.jpg" 
                alt="Síntomas iniciales del cáncer testicular en jóvenes" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Si notas un abultamiento o sientes dolor en el abdomen bajo, actúa hoy. En Uro Oncology ofrecemos chequeos completos con tecnología indolora y precisa.</figcaption>
            </figure>

            <h3>Síntomas del cáncer de testículo avanzado</h3>
            <p>
              Aun cuando el cáncer testicular se haya propagado a otras partes del cuerpo, es posible que muchos hombres no presenten síntomas inmediatamente. Sin embargo, algunos hombres podrían presentar algunos de los siguientes:
            </p>
            <ul>
              <li>Dolor en la espalda baja: provocado por la propagación del cáncer a los ganglios linfáticos en la parte trasera del vientre</li>
              <li>Dificultad para respirar, dolor en el pecho o tos: (incluso toser sangre) se puede presentar a causa de la propagación del cáncer a los pulmones</li>
              <li>Dolor en el vientre: ya sea a causa de ganglios linfáticos agrandados o porque el cáncer se ha propagado al hígado</li>
              <li>Dolores de cabeza o confusión: debido a la propagación del cáncer al cerebro</li>
            </ul>

            <h3>Factores de riesgo para el cáncer de testículo</h3>
            <p>
              Un factor de riesgo es todo aquello que afecta su probabilidad de padecer una enfermedad, como por ejemplo el cáncer. Los distintos tipos de cáncer tienen diferentes factores de riesgo. Algunos factores de riesgo, como el fumar y la alimentación, pueden cambiarse. Otros factores, como la edad o los antecedentes familiares, no se pueden cambiar.
            </p>
            <p>
              No obstante, si se tiene uno, o hasta muchos factores de riesgo, no necesariamente significa que se padecerá la enfermedad. Asimismo, si no presenta ningún factor de riesgo, esto no significa que no padecerá la enfermedad. Además, algunas personas que padecen la enfermedad pueden no tener factores de riesgo conocidos. Aun cuando una persona con cáncer testicular tenga un factor de riesgo, a menudo es muy difícil saber cuánto contribuyó ese factor de riesgo al cáncer.
            </p>
            <p>
              Los científicos han descubierto pocos factores de riesgo que aumentan las probabilidades de que alguien padezca cáncer de testículo. La mayoría de los niños y los hombres con cáncer testicular no presentan ninguno de los factores de riesgo conocidos. Algunos factores de riesgo para el cáncer de testículo son:
            </p>
            <ul>
              <li><strong>Testículo no descendido:</strong> Uno de los factores de riesgo principales para el cáncer testicular es una afección llamada criptorquidia, que significa que uno o ambos testículos no bajaron del abdomen hasta el escroto antes del nacimiento. Los hombres con criptorquidia son muchas veces más propensos a padecer cáncer de testículo que aquellos cuyos testículos han descendido normalmente.</li>
              <li><strong>Antecedentes familiares de cáncer testicular:</strong> Tener un padre o hermano con cáncer testicular aumenta el riesgo de que usted también lo padezca. No obstante, un pequeño número de cánceres de testículo ocurre entre las familias. La mayoría de los hombres con cáncer de testículo no tiene antecedentes familiares de esta enfermedad.</li>
              <li><strong>Infección por VIH:</strong> Cierta evidencia ha demostrado que los hombres infectados con el virus de inmunodeficiencia humana (VIH), en especial los que tienen el síndrome de inmunodeficiencia adquirida (SIDA), tienen un mayor riesgo de padecer cáncer de testículo.</li>
              <li><strong>Haber tenido cáncer de testículo antes:</strong> Un historial personal de cáncer testicular es otro factor de riesgo. Alrededor del 3% o 4% de los hombres que se han curado de cáncer en un testículo padecerán en algún momento de cáncer en el otro testículo.</li>
              <li><strong>Pertenecer a determinada raza o grupo étnico:</strong> El riesgo del cáncer testicular entre los hombres de raza blanca es aproximadamente de 4 a 5 veces mayor que el de los de raza negra y que el de los hombres asiático-americanos.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-testiculo/Cancer de testiculo5.jpg" 
                alt="Atención médica oncológica ante factores de riesgo hereditarios" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Cuidar tu salud es amar tu vida. Si tienes antecedentes familiares o algún factor de riesgo, Uro Oncology está aquí para guiarte en tu prevención.</figcaption>
            </figure>

            <h3>¿Se puede prevenir el cáncer de testículo?</h3>
            <p>
              Muchos hombres con cáncer testicular no presentan factores de riesgo conocidos. Además, muchos de los factores de riesgo conocidos no se pueden cambiar. Por estas razones, no es posible prevenir la mayoría de los casos de esta enfermedad, mantener una vida saludable y un control de salud general de manera rutinaria, será la mejor manera de prevenir y detectar el cáncer de testículo, lo más importante es que si tienes algún síntoma o algo que te preocupe respecto a tu salud urinaria, acudas de inmediato con un especialista.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
