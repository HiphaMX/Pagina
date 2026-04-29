import styles from '../page.module.css';

export const metadata = {
  title: 'Equipo Médico | Uro-Oncology',
  description: 'Conoce a nuestro equipo médico especializado.',
};

import Image from 'next/image';

export default function EquipoMedicoPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              El Dr. Adalberto Castro Alfaro es uno de los pocos urólogos en México en tener doble una especialidad, lo que le permite ofrecer atención médica integral a cualquier padecimiento oncológico en las vías urinarias, además de los padecimientos normales, en mayo de 2019 fundo Uro Oncology "El pulso humano de la cirugía robótica" con la misión de ofrecer mejores tratamientos urológicos.
            </p>
            <p>
              Actualmente es director del programa de Cirugía Robótica del Hospital Real San José y miembro del staff de Cirugía Robótica del Hospital Ángeles Lomas en CDMX.
            </p>

            <h3>FORMACIÓN ACADÉMICA</h3>
            <ul>
              <li>Especialidad en Urología, Universidad de Guadalajara / ISSSTE Hospital Regional Dr. Valentín Gómez Farías, 2013</li>
              <li>Alta Especialidad en Urología Oncológica, UNAM / Instituto Nacional de Cancerología CDMX, 2014</li>
              <li>Fellowship en Enucleación Prostática con Láser Holmio, Hospital Central Militar, 2015</li>
              <li>Fellowship en Cirugía Robótica y laparoscopia avanzada, Universidad París Descartes / Institute Mutualiste Montsouris, Paris Francia, 2017</li>
              <li>Certificado por el Consejo Nacional Mexicano de Urología A.C. No. Certificación 947 / 2013-2018</li>
            </ul>

            <div className={styles.certificateImageWrapper}>
              <Image 
                src="/assets/home/certificado.jpeg" 
                alt="Certificado Dr. Adalberto Castro Alfaro" 
                width={800} 
                height={550} 
                className={styles.certificateImage} 
                priority
              />
            </div>

            <h3>ACTIVIDADES PROFESIONALES</h3>
            <ul>
              <li>Urólogo adscrito al servicio de Urología del Hospital Angeles del Carmen, Guadalajara, y Hospital Angeles Lomas, Ciudad de México.</li>
              <li>Miembro del Centro de Cirugía Robótica del Hospital Angeles del Carmen y Hospital Angeles Lomas.</li>
              <li>Cirugía Laser de Próstata (HoLEP Y GreenLight Laser)</li>
              <li>Terapias Focales para Cáncer de Próstata y Riñon (Cryo, NanoKnife, HiFU)</li>
              <li>Cirugía de Litiasis o Cálculos Renales y Ureterales con litotripsia intra y extracorpórea uso de laser.</li>
              <li>Cirugía Laparoscópica (Nefrectomía, Prostatectomía Radical, Quistes renales, cálculos urinarios).</li>
              <li>Circuncisión y Cirugía de escroto (varicocele, hidrocele, quistes de epidídimo, vasectomía).</li>
              <li>Cirugía de impotencia (cirugía vascular y colocación de prótesis peneanas).</li>
              <li>Infecciones urinarias: cistitis, uretritis, prostatitis, pielonefritis.</li>
              <li>Enfermedades de transmisión sexual: papiloma humano, clamydia, gonorrea, etc.</li>
              <li>Litiasis urinaria: cálculos en vejiga y uretra.</li>
              <li>Neoplasias: cáncer de próstata, riñón, testículo, pene, vejiga, suprarrenales.</li>
              <li>Crecimiento de la próstata: hiperplasia prostática benigna.</li>
              <li>Enfermedades del escroto: varicocele, hidrocele, quistes de epidídimo.</li>
              <li>Enfermedades en pene: fimosis (falta de retracción del prepucio), balanitis, disfunciones sexuales (disfunción eréctil, eyaculación precoz).</li>
            </ul>

            <h3>ACTIVIDADES ACADÉMICAS</h3>
            <ul>
              <li>Profesor en el curso taller de Cirugía Endoscópica y Percutánea Renal (curso teórico-práctico) Hospital Central Militar, Ciudad de México, 8 y 9 de octubre 2015.</li>
              <li>Profesor en el curso Internacional de Urología Oncológica, "Nuevas herramientas para la toma de decisiones para realización de biopsia de próstata". Hospital Central Militar, Ciudad de México, Sociedad Mexicana de Urología, 14 y 15 de abril de 2016.</li>
              <li>Profesor y coordinador del curso de Enucleación Prostática con Láser de Holmio y Actualidades en Cirugía Renal Percutánea y Flexible. ISSSTE, Guadalajara, Jal. México.Sociedad Mexicana de Urología, Colegio Mexicano de Urología Nacional, Consejo Nacional Mexicano de Urología, 22 y 23 abril de 2016</li>
              <li>Profesor titular del curso de HoLEP en el LXVII Congreso Internacional de la Sociedad Mexicana de Urología, Puerto Vallarta, Jalisco, 15 al 19 de noviembre de 2016</li>
              <li>Profesor del curso de HoLEP en el LXVIII Congreso Internacional de la Sociedad Mexicana de Urología, Acapulco, Gro, 14 al 19 de noviembre de 2017</li>
              <li>Profesor en el Curso Internacional de Mínima Invasión en Urología, "Técnicas presentes y futuras del manejo del crecimiento prostático benigno", Hospital Central Militar, 4-6 julio, 2018</li>
            </ul>

            <h3>DISTINCIONES</h3>
            <ul>
              <li>European Urological Association</li>
              <li>American Urological Association</li>
              <li>Sociedad Mexicana de Urología</li>
              <li>Colegio Mexicano de Urología A.C.</li>
              <li>Sociedad Médica del Hospital Angeles Lomas</li>
            </ul>

            <h3>PUBLICACIONES</h3>
            <ul>
              <li>CANCER OF THE PENIS: EXPERIENCE OF SINGLE INSTITUTION EUROPEAN UROLOGY SUPPLEMENTS", Noviembre, 2013.</li>
              <li>FACTORES PRONÓSTICOS DE RECURRENCIA Y PROGRESIÓN DEL CANCER SUPERFICIAL DE VEJIGA EN LA POBLACIÓN MEXICANA DEL INSTITUTO NACIONAL DE CANCEROLOGIA", LXIV Congreso de la Sociedad Mexicana de Urología, Mérida, Yucatán, 2013.</li>
              <li>"CARCINOMA DE DUCTO COLECTOR DE BELLINI: REPORTE DE UN CASO Y REVISIÓN DE LA LITERATURA". Revista Mexicana de Urología, 2013</li>
              <li>"METÁSTASIS DE CÁNCER RENAL A TESTÍCULO" Revista Mexicana de Urología, 2014.</li>
              <li>"COMPLICATIONS IN ROBOTIC UROLOGICAL SURGERIES AND HOW TO AVOID THEM: A SYSTEMATIC REVIEW". Arab Journal of Urology, Noviembre 2017</li>
              <li>"MODIFIED YORK MASON TECHNIQUE FOR REPAIR OF IATROGENIC RECTO-URINARY FISTULA: 20 YEARS OF THE MONTSOURIS EXPERIENCE." World Journal of Urology, Enero 2018</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
