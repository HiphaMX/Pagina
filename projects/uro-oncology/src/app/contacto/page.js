import styles from '../tipos-de-cirugia/page.module.css'; // Reutilizamos estilos de cabecera

export const metadata = {
  title: 'Contacto | Uro-Oncology',
  description: 'Agenda tu cita con el Dr. Adalberto Castro Alfaro en el Centro Médico Real San José Valle Real, Zapopan, Jalisco.',
};

export default function Contacto() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className="container">
          <h1>Contacto y Ubicación</h1>
          <p>Estamos listos para atenderte y resolver todas tus dudas sobre tu salud urológica.</p>
        </div>
      </header>
      
      <section className={styles.content}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'start' }}>
            <div>
              <h2 style={{ color: 'var(--primary)', marginBottom: '1.5rem', fontSize: '2rem' }}>Información de Contacto</h2>
              <p style={{ marginBottom: '2rem', lineHeight: '1.6', opacity: 0.8 }}>
                Agenda tu cita o comunícate con nosotros para cualquier consulta médica. Aceptamos todas las principales tarjetas de crédito y seguros de gastos médicos mayores.
              </p>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>Teléfono para Citas</h3>
                <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>33 1594 7175</p>
              </div>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>Correo Electrónico</h3>
                <p>adal@uro-oncology.com.mx</p>
              </div>
              
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>Ubicación</h3>
                <p><strong>Centro Médico Real San José Valle Real</strong></p>
                <p>Av. Central 911, Torre de consultorios</p>
                <p>Piso 7, consultorio 7-B</p>
                <p>Zapopan, Jalisco</p>
              </div>
              
              <a href="https://wa.me/523315947175" className="btn btn-accent" target="_blank" rel="noopener noreferrer">
                Escríbenos por WhatsApp
              </a>
            </div>
            
            <div style={{ background: 'white', padding: '1rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
              {/* Mapa embebido de Google Maps como placeholder */}
              <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3731.5471465977937!2d-103.4429910240974!3d20.72857438084594!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8428a8d11c107bfb%3A0xc6652433ecbc67a7!2sHospital%20Real%20San%20Jos%C3%A9%20Valle%20Real!5e0!3m2!1sen!2smx!4v1700000000000!5m2!1sen!2smx" 
                width="100%" 
                height="450" 
                style={{ border: 0, borderRadius: '15px' }} 
                allowFullScreen="" 
                loading="lazy" 
                referrerPolicy="no-referrer-when-downgrade"
              ></iframe>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
