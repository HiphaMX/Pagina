'use client';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import styles from './ContactPopup.module.css';

const RECAPTCHA_SITE_KEY = '';

export default function ContactPopup({ isOpen, onClose }) {
  useEffect(() => {
    if (RECAPTCHA_SITE_KEY) {
      const script = document.createElement('script');
      script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`;
      script.async = true;
      document.body.appendChild(script);
      return () => {
        document.body.removeChild(script);
      };
    }
  }, []);

  const executeRecaptcha = (actionName) => {
    return new Promise((resolve) => {
      if (typeof window.grecaptcha !== 'undefined' && RECAPTCHA_SITE_KEY) {
        window.grecaptcha.ready(() => {
          window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: actionName })
            .then(resolve)
            .catch((err) => {
              console.warn("reCAPTCHA execution error:", err);
              resolve('');
            });
        });
      } else {
        resolve('');
      }
    });
  };
  const [isMounted, setIsMounted] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isMounted) return null;
  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const recaptchaToken = await executeRecaptcha('submit_contact');
    const formData = new FormData(e.target);
    const data = {
      nombre: formData.get('nombre'),
      apellido: formData.get('apellido'),
      telefono: formData.get('telefono'),
      email: formData.get('email'),
      mensaje: formData.get('mensaje'),
      honeypot: formData.get('confirm_email'),
      recaptcha_token: recaptchaToken
    };

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (response.ok) {
        alert('¡Mensaje enviado con éxito! Nos pondremos en contacto contigo pronto.');
        onClose();
      } else {
        alert('Ocurrió un error al enviar el mensaje. Intenta nuevamente.');
        console.error(result.error);
      }
    } catch (error) {
      alert('Ocurrió un error de conexión.');
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.popupContainer} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Cerrar">
          &times;
        </button>

        <div className={styles.popupHeader}>
          <Image 
            src="/assets/logotipo/logo-light.svg" 
            alt="Uro-oncology Logo" 
            width={200} 
            height={64} 
            className={styles.logo} 
          />
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div style={{ position: 'absolute', left: '-9999px', top: '-9999px', width: '1px', height: '1px', overflow: 'hidden' }} aria-hidden="true">
            <input type="text" id="confirm_email" name="confirm_email" tabIndex="-1" autoComplete="off" />
          </div>
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="nombre">NOMBRE</label>
              <input type="text" id="nombre" name="nombre" placeholder="Ingresa tu nombre" required />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="apellido">APELLIDO</label>
              <input type="text" id="apellido" name="apellido" placeholder="Escribe tu apellido" required />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="telefono">TELÉFONO</label>
            <input type="tel" id="telefono" name="telefono" placeholder="Teléfono de contacto (10 dígitos)" required pattern="[0-9]{10}" />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="email">CORREO ELECTRÓNICO</label>
            <input type="email" id="email" name="email" placeholder="Ingresa tu e-mail" required />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="mensaje">MENSAJE</label>
            <textarea id="mensaje" name="mensaje" placeholder="Escribe tu mensaje (opcional)" rows="4"></textarea>
          </div>

          <div className={styles.checkboxGroup}>
            <input type="checkbox" id="newsletter" name="newsletter" defaultChecked />
            <label htmlFor="newsletter">ACEPTO RECIBIR INFORMACIÓN DE URO-ONCOLOGY</label>
          </div>

          <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
            {isSubmitting ? 'ENVIANDO...' : 'ENVIAR'}
          </button>
        </form>
      </div>
    </div>
  );
}
