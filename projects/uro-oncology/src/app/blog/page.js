import styles from '../tipos-de-cirugia/page.module.css'; // Reutilizamos estilos

export const metadata = {
  title: 'Blog | Uro-Oncology',
  description: 'Artículos, noticias y avances en urología y oncología.',
};

export default function Blog() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className="container">
          <h1>Blog Médico</h1>
          <p>Próximamente: Artículos y avances en urología oncológica y cirugía robótica.</p>
        </div>
      </header>
      
      <section className={styles.content} style={{ minHeight: '40vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="container text-center">
          <h2 style={{ color: 'var(--primary)' }}>Estamos preparando contenido de valor para ti.</h2>
          <p style={{ marginTop: '1rem', opacity: 0.8 }}>Vuelve pronto para leer nuestros últimos artículos médicos.</p>
        </div>
      </section>
    </div>
  );
}
