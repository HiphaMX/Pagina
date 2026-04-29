'use client';
import { useState } from 'react';
import Link from 'next/link';
import styles from './FaqAccordion.module.css';

const faqs = [
  {
    question: '¿LOS SERVICIOS DE UN URÓLOGO SON EXCLUSIVOS PARA EL SEXO MASCULINO?',
    answer: 'No, siempre se ha dado por hecho que los urólogos atienen principalmente a personas del sexo masculino, pero la realidad es que es una afirmación incorrecta, los padecimientos urológicos afectan a personas de cualquier sexo y se pueden presentar en distintas etapas de la vida.'
  },
  {
    question: '¿CÓMO PUEDO PROGRAMAR UNA CITA?',
    answer: 'Existen diferentes maneras, puedes llamar al teléfono 331 6013 840, dejarnos tus datos en nuestro formulario o escribirnos por whatsapp, nos contactaremos contigo para indicarte los días y horarios disponibles para confirmar tu cita.'
  },
  {
    question: '¿PUEDO UTILIZAR MI SEGURO DE GASTOS MÉDICOS?',
    answer: 'Si, tenemos convenio con las mejores aseguradoras del país, al momento de programar tu cirugía, te recomendamos mencionar que cuentas con un seguro de gastos médicos para revisar si tenemos convenio vigente.'
  },
  {
    question: '¿ACEPTAN PAGO CON TARJETA DE CRÉDITO O DÉBITO?',
    answer: 'Si, para tu comodidad, habilitamos el servicio de pago con tarjeta de crédito o débito, visa, máster card o american express.'
  },
  {
    question: '¿QUÉ PUEDO HACER EN CASO DE UNA EMERGENCIA UROLÓGICA?',
    answer: 'Lo más recomendable es llamar inmediatamente al teléfono 331 6013 840 para revisar alternativas, cualquier abuso será reportado a las autoridades correspondientes.'
  },
  {
    question: 'YA TENGO UN DIAGNÓSTICO, PERO NO ESTOY CONVENCIDO ¿PUEDO PROGRAMAR UNA CITA PARA UNA SEGUNDA OPINIÓN?',
    answer: 'Si, nuestro compromiso es ofrecer siempre un diagnóstico oportuno y acertado, si tienes un diagnóstico que no de deja satisfecho, puedes programar tu cita de diagnóstico, revisaremos tus síntomas para que puedas confirmar tu padecimiento o tener un diagnóstico alternativo.'
  },
  {
    question: '¿QUE MANEJO LE DARÁN A LOS DATOS RECABADOS EN LA PÁGINA WEB?',
    answer: (
      <>
        Puedes tener la seguridad de que tus datos están seguros, por ninguna razón compartimos información, consideramos que tus datos son personales y únicamente los utilizamos como método de contacto, puedes revisar nuestro <Link href="/aviso-de-privacidad" className={styles.faqLink}>aviso de privacidad aquí</Link>.
      </>
    )
  }
];

export default function FaqAccordion() {
  const [openIndex, setOpenIndex] = useState(0); // Primera abierta por defecto

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? -1 : index);
  };

  return (
    <div className={styles.faqContainer}>
      {faqs.map((faq, index) => {
        const isOpen = openIndex === index;
        return (
          <div key={index} className={`${styles.faqItem} ${isOpen ? styles.open : ''}`}>
            <button 
              className={styles.faqQuestion} 
              onClick={() => toggleAccordion(index)}
              aria-expanded={isOpen}
            >
              <span>{faq.question}</span>
              <div className={styles.iconWrapper}>
                <span className={styles.icon}>{isOpen ? '−' : '+'}</span>
              </div>
            </button>
            <div className={styles.faqAnswerContainer} style={{ maxHeight: isOpen ? '500px' : '0' }}>
              <div className={styles.faqAnswer}>
                {faq.answer}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
