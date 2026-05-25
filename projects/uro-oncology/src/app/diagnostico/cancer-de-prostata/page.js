import styles from '../../page.module.css';

export const metadata = {
  title: 'Cáncer de Próstata | Uro-Oncology',
  description: 'Diagnóstico y tratamiento del cáncer de próstata.',
};

import Image from 'next/image';

export default function CancerDeProstataPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              La próstata está debajo de la vejiga (el órgano hueco donde se almacena la orina) y delante del recto (la última parte de los intestinos), justo detrás de la próstata se encuentran las glándulas llamadas vesículas seminales, las cuales producen la mayor parte del líquido del semen. La uretra, que es el conducto que transporta la orina y el semen fuera del cuerpo a través del pene, pasa por el centro de la próstata. El tamaño de la próstata puede cambiar a medida que el hombre envejece, en los hombres más jóvenes, la próstata es del tamaño aproximado de una nuez, sin embargo, puede ser mucho más grande en hombres de más edad.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-prostata/cancer-de-prostata1.jpg" 
                alt="Prevención del cáncer de próstata en hombres" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>En Uro Oncology fomentamos la prevención y detección temprana. Si tienes más de 40 años y algún síntoma te roba la tranquilidad, no esperes más y agenda tu cita de valoración.</figcaption>
            </figure>

            <h3>¿Es común el cáncer de próstata?</h3>
            <p>
              Aproximadamente uno de cada nueve hombres será diagnosticado con cáncer de próstata en el transcurso de su vida. De acuerdo con la Sociedad Americana Contra el Cáncer, en los Estados Unidos, el cáncer de próstata es el cáncer más común en los hombres después del cáncer de piel.
            </p>
            <p>
              Para el año 2020, la Sociedad Americana Contra el Cáncer calcula que en los Estados Unidos:
            </p>
            <ul>
              <li>Se diagnosticarán alrededor de 191,930 casos nuevos de cáncer de próstata</li>
              <li>Se reportarán 33,330 muertes a causa del cáncer de próstata</li>
            </ul>
            <p>
              El cáncer de próstata es más propenso a desarrollarse en hombres de edad avanzada y en hombres de la raza negra. Alrededor de 6 de 10 casos se diagnostican en hombres de 65 años o más, y en pocas ocasiones se presenta en hombres menores de 40 años. La edad media en el momento del diagnóstico es aproximadamente 66 años.
            </p>
            <p>
              El cáncer de próstata es la segunda causa principal de muerte en los hombres de los Estados Unidos, después del cáncer de pulmón, aproximadamente uno de cada 41 hombres morirá por cáncer de próstata, que puede ser una enfermedad grave, aunque la mayoría de los hombres diagnosticados con este cáncer no muere a causa de esta enfermedad, de hecho, en los Estados Unidos, más de 3.1 millones de hombres que han sido diagnosticados con cáncer de próstata en algún momento, siguen vivos hoy en día, por lo que es buena idea detectarlo a tiempo.
            </p>

            <h3>¿Se puede descubrir el cáncer de próstata en sus comienzos?</h3>
            <p>
              Las pruebas de detección tienen el objetivo de descubrir cáncer antes de que se presente algún síntoma, para algunos tipos de cáncer, las pruebas de detección pueden ayudar a encontrar cánceres en una etapa inicial cuando probablemente sean más fáciles de tratar.
            </p>
            <p>
              Frecuentemente se puede encontrar el cáncer de próstata en sus comienzos mediante el análisis del antígeno prostático específico (PSA) en la sangre de un hombre. El examen mediante tacto rectal (examen digital del recto, DRE) es otra manera de encontrar temprano el cáncer de próstata. Si los resultados de estas pruebas son anormales, a menudo se realizan pruebas adicionales (como una biopsia de la próstata) para saber si un hombre tiene cáncer y poder proceder a un tratamiento.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-prostata/cancer-de-prostata2.jpg" 
                alt="Detección oportuna del cáncer de próstata" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Detectar a tiempo salva vidas. En Uro Oncology contamos con la tecnología de vanguardia para brindarte un diagnóstico preciso y tranquilidad sobre tu salud.</figcaption>
            </figure>

            <h3>Signos y síntomas del cáncer de próstata</h3>
            <p>
              La mayoría de los cánceres de próstata se descubren a tiempo, a través de una detección oportuna al realizar revisiones rutinarias, por lo general, el cáncer de próstata en etapa inicial no causa síntomas. El cáncer de próstata en estados más avanzados a veces pueden causar síntomas, como:
            </p>
            <ul>
              <li>Problemas al orinar, incluyendo un flujo urinario lento o debilitado o necesidad de orinar con más frecuencia, especialmente de noche</li>
              <li>Sangre en la orina o el semen</li>
              <li>Dificultad para lograr una erección (disfunción eréctil)</li>
              <li>Dolor en las caderas, la espalda (columna vertebral), el tórax (costillas) u otras áreas debido a que el cáncer que se ha propagado a los huesos</li>
              <li>Debilidad o adormecimiento de las piernas o los pies, o incluso pérdida del control de la vejiga o los intestinos debido a que el cáncer comprime la médula espinal</li>
            </ul>
            <p>
              Es más probable que la mayoría de estos problemas sean por causa distinta al cáncer de próstata. Por ejemplo, la hiperplasia prostática benigna (un crecimiento no canceroso de la próstata) causa dificultad para orinar con mucha más frecuencia que el cáncer. Aun así, resulta importante que usted le informe a su médico si presenta cualquiera de estos síntomas para que la causa se encuentre y se trate, de ser necesario.
            </p>

            <h3>Factores de riesgo para el cáncer de próstata</h3>
            <p>
              Un factor de riesgo es todo aquello que aumenta el riesgo de padecer una enfermedad, como por ejemplo el cáncer. Los distintos tipos de cáncer tienen diferentes factores de riesgo. Algunos factores de riesgo, como el fumar, pueden cambiarse, pero otros factores, como la edad o los antecedentes familiares, no se pueden cambiar.
            </p>
            <p>
              Sin embargo, tener uno o incluso varios factores de riesgo no significa que usted padecerá la enfermedad. Muchas personas con uno o más factores de riesgo nunca padecen cáncer, mientras que otras que padecen la enfermedad puede que hayan tenido pocos factores de riesgo conocidos o ninguno de éstos, los investigadores han descubierto varios factores de riesgo que pueden afectar el riesgo de que un hombre padezca cáncer de próstata:
            </p>
            <ul>
              <li><strong>Edad:</strong> Es poco común que el cáncer de próstata afecte a los hombres menores de 40 años, pero la probabilidad de padecer cáncer de próstata aumenta rápidamente después de los 50 años, alrededor de 6 de 10 casos de cáncer de próstata se detectan en hombres mayores de 65 años.</li>
              <li><strong>Raza/grupo étnico:</strong> El cáncer de próstata ocurre con más frecuencia en los hombres de raza negra y en hombres del Caribe con ascendencia africana que en los hombres de otras razas, cuando se desarrolla en estos hombres, ellos tienden a ser más jóvenes. El cáncer de próstata ocurre con menos frecuencia en los hombres estadounidenses de raza oriental y en los hispanos/latinos que en los hombres blancos que no son de origen hispano. No están claras las razones de estas diferencias raciales y étnicas.</li>
              <li><strong>Geografía:</strong> El cáncer de próstata es más común en Norteamérica y en la región noroeste de Europa, Australia, y en las islas del Caribe. Es menos común en Asia, África, Centroamérica y Sudamérica.</li>
              <li><strong>Antecedentes familiares:</strong> Parece ser que el cáncer de próstata afecta más a algunas familias, lo cual sugiere que en algunos casos puede haber un factor hereditario o genético. Aun así, la mayoría de los cánceres de próstata ocurre en hombres que no tienen antecedentes familiares de este cáncer. Si el padre o el hermano de un hombre padecen cáncer de próstata, se duplica el riesgo de que este hombre padezca la enfermedad. (El riesgo es mayor para los hombres que tienen un hermano con la enfermedad que para aquellos con un padre que tiene este cáncer). De igual manera, el riesgo es mucho mayor en el caso de los hombres que tienen varios familiares afectados, particularmente si tales familiares eran jóvenes cuando se les encontró el cáncer.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-prostata/cancer-de-prostata3.jpg" 
                alt="Estilo de vida saludable y factores de riesgo en urología" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Cuidar tu salud no es una opción, es una prioridad. Uro Oncology te acompaña en cada paso para adoptar un estilo de vida saludable y minimizar factores de riesgo.</figcaption>
            </figure>

            <h3>¿Se puede prevenir el cáncer de próstata?</h3>
            <p>
              El cáncer de próstata no se puede prevenir de manera segura, muchos factores de riesgo, tales como la edad, la raza y el antecedente familiar no se pueden controlar. No obstante, existen algunas medidas que puedes tomar para tratar de reducir su riesgo de padecer cáncer de próstata.
            </p>
            <p><strong>Recomendaciones para reducir el riesgo:</strong></p>
            <ul>
              <li>No fumar</li>
              <li>Hacer ejercicio normalmente</li>
              <li>Una dieta saludable baja en grasa con muchos vegetales y frutas</li>
              <li>Mantener un peso saludable</li>
            </ul>
            <p>
              Podemos concluir con 2 poderosas ideas, tener un estilo de vida saludable, puede disminuir en gran medida padecer muchas enfermedades, más no específicamente el cáncer, pero si además mantenemos hábitos como un <strong>Check Up Masculino</strong>, cualquier padecimiento que se pueda llegarse a presentar estará en una etapa temprana y te brindará más opciones de tratamiento, lo más importante es cuidar tu salud y por ningún motivo automedicarte, si tienes algún síntoma o inquietud, lo mejor será visitar un especialista, el síntoma más peligroso es ignorar cualquier posible síntoma.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
