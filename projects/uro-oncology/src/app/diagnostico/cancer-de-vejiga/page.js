import styles from '../../page.module.css';

export const metadata = {
  title: 'Cáncer de Vejiga | Uro-Oncology',
  description: 'Diagnóstico y tratamiento del cáncer de vejiga.',
};

import Image from 'next/image';

export default function CancerDeVejigaPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              El cáncer de vejiga se origina cuando las células que componen la vejiga urinaria comienzan a crecer en forma descontrolada. Conforme se desarrollan más células cancerosas, estas pueden formar un tumor y con el pasar del tiempo extenderse a otras áreas del cuerpo. La vejiga es un órgano hueco que se encuentra en la parte inferior de la pelvis. Este órgano tiene paredes musculares flexibles que pueden estirarse para almacenar la orina y contraerse para expulsarla del cuerpo. La función principal de la vejiga es almacenar la orina. Cuando usted orina, los músculos en la vejiga se contraen, y la orina sale de la vejiga a través de un conducto llamado uretra.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-vejiga/cancer-de-vejiga1.jpg" 
                alt="Paciente adulto mayor consultando con un especialista" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology te acompaña. Las personas mayores de 55 años requieren atención especializada y revisiones urológicas constantes para preservar su salud integral.</figcaption>
            </figure>

            <h3>Riesgo de padecer cáncer de vejiga</h3>
            <p>
              El cáncer de vejiga principalmente ocurre en las personas de edad avanzada. Alrededor de 9 de 10 personas con este cáncer tienen más de 55 años de edad. La edad promedio al momento de realizarse el diagnóstico es de 73 años. En general, la probabilidad de que los hombres padezcan este cáncer durante el transcurso de sus vidas es de alrededor de 1 en 27, para las mujeres, la probabilidad es de alrededor de 1 en 89.
            </p>
            <p>
              Un factor de riesgo es todo aquello que afecta su probabilidad de padecer una enfermedad, como el cáncer, los distintos tipos de cáncer tienen diferentes factores de riesgo, puedes cambiar algunos factores de riesgo, como dejar de fumar o mantener un peso saludable; pero algunos otros, como la edad o los antecedentes familiares, no los podrás cambiar.
            </p>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-vejiga/cancer-de-vejiga2.jpg" 
                alt="Salud urológica para hombres mayores" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>En Uro Oncology evaluamos tus factores de riesgo de manera personalizada, brindándote tranquilidad con un diagnóstico certero.</figcaption>
            </figure>

            <p><strong>Factores de riesgo que puedes cambiar:</strong></p>
            <ul>
              <li>Tabaquismo</li>
              <li>Exposición a ciertas sustancias químicas</li>
              <li>No beber suficientes líquidos</li>
            </ul>
            <p><strong>Factores de riesgo que no puedes cambiar:</strong></p>
            <ul>
              <li>Edad, se reporta que alrededor de 9 de 10 personas que tienen cáncer de vejiga son mayores de 55 años</li>
              <li>Sexo, es mucho más frecuente en los hombres que en las mujeres</li>
              <li>Irritación e infección crónica de la vejiga</li>
              <li>Defectos congénitos de la vejiga</li>
              <li>Antecedente familiar y genética</li>
            </ul>
            <p>
              No obstante, si se tiene uno, o hasta muchos factores de riesgo, no necesariamente significa que se padecerá la enfermedad, muchas personas con uno o más factores de riesgo nunca padecen cáncer de vejiga, mientras que otras que ya tienen la enfermedad pueden tener pocos o ningún factor de riesgo conocidos, por lo que no es considerado una regla general.
            </p>

            <h3>Signos y síntomas del cáncer de vejiga</h3>
            <p>
              A menudo, el cáncer de vejiga se puede encontrar temprano, ya que causa que haya sangre en la orina u otros síntomas urinarios que provocan acudir al médico, algunos de los síntomas son:
            </p>
            <ul>
              <li>Sangre en la orina</li>
              <li>Orinar con más frecuencia de lo habitual</li>
              <li>Dolor o ardor al orinar</li>
              <li>Sensación de que necesita orinar inmediatamente, incluso cuando su vejiga no está llena</li>
              <li>Tener problemas para orinar o tener un flujo débil de orina</li>
              <li>Tener que levantarse para orinar muchas veces durante la noche</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-vejiga/cancer-de-vejiga3.jpg" 
                alt="Nutrición y dieta saludable para prevenir el cáncer" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Cuidar tu alimentación es el primer escudo contra las enfermedades urológicas. Uro Oncology te invita a adoptar un estilo de vida más saludable.</figcaption>
            </figure>

            <p>En casos donde el cáncer de vejiga ha crecido mucho o se ha propagado a otras partes del cuerpo pueden a veces causar otros síntomas, tal como:</p>
            <ul>
              <li>No poder orinar</li>
              <li>Dolor en un lado de la espalda baja</li>
              <li>Pérdida de apetito y pérdida de peso</li>
              <li>Cansancio o debilidad</li>
              <li>Hinchazón en los pies</li>
              <li>Dolor en los huesos</li>
            </ul>

            <h3>¿Se puede prevenir el cáncer de vejiga?</h3>
            <p>
              No existe una manera segura de prevenir el cáncer vejiga. Algunos factores de riesgo, tales como la edad, el género, la raza, y el historial familiar no se pueden controlar. No obstante, puede que existan algunas medidas que pueda tomar para ayudar a reducir su riesgo:
            </p>
            <ul>
              <li><strong>No fumar:</strong> Se cree que fumar causa aproximadamente la mitad de todos los cáncer de vejiga. (Esto incluye fumar cigarrillos, cigarros, o pipas).</li>
              <li><strong>Limita la exposición a ciertas sustancias químicas:</strong> Los trabajadores de industrias que utilizan ciertos productos químicos orgánicos presentan un mayor riesgo de cáncer de vejiga.</li>
              <li><strong>Bebe mucho líquido:</strong> Hay evidencia que sugiere que beber mucho líquido, principalmente agua, puede reducir el riesgo individual de padecer cáncer de vejiga.</li>
              <li><strong>Come muchas frutas y verduras:</strong> Algunos estudios han sugerido que una alimentación con muchas frutas y vegetales puede ayudar a proteger contra el cáncer de vejiga, pero no todos los estudios confirman esto. Aun así, adoptar una alimentación saludable ha demostrado ofrecer muchos beneficios.</li>
            </ul>

            <figure className={styles.imageFigure}>
              <Image 
                src="/assets/diagnostico/cancer-de-vejiga/cancer-de-vejiga4.jpg" 
                alt="Estilo de vida activo y saludable después de los 55 años" 
                width={850} 
                height={450} 
                className={styles.contentImage} 
              />
              <figcaption className={styles.imageCaption}>Uro Oncology fomenta el envejecimiento activo y saludable. Un check-up anual oportuno es la mejor decisión para tu salud integral.</figcaption>
            </figure>

            <p>
              Tener un estilo de vida saludable, puede disminuir en gran medida padecer muchas enfermedades, más no específicamente el cáncer, pero si además mantenemos hábitos como un Check Up Masculino, cualquier padecimiento que se pueda llegarse a presentar estará en una etapa temprana y te brindará más opciones de tratamiento, si tienes algún síntoma o inquietud, lo mejor será visitar un especialista, el síntoma más peligroso es ignorar cualquier posible síntoma.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
