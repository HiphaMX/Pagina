import styles from '../page.module.css';
import FaqAccordion from '@/components/FaqAccordion';

export const metadata = {
  title: 'Preguntas Frecuentes | Uro-Oncology',
  description: 'Resolvemos tus dudas sobre nuestros tratamientos y procedimientos.',
};

export default function PreguntasFrecuentesPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <FaqAccordion />
        </div>
      </section>
    </div>
  );
}
