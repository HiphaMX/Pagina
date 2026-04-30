'use client';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import styles from './InsuranceSlider.module.css';

const images = [
  '/assets/seguros/slider-seguros-1.png',
  '/assets/seguros/slider-seguros-2.png',
  '/assets/seguros/slider-seguros-3.png'
];

export default function InsuranceSlider() {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((prev) => (prev === images.length - 1 ? 0 : prev + 1));
    }, 4000); // Change image every 4 seconds
    return () => clearInterval(timer);
  }, []);

  return (
    <section className={styles.insuranceSection}>
      <div className="container">
        <div className={styles.content}>
          <div className={styles.textSection}>
            <h2>Convenio con todas las aseguradoras</h2>
            <p>
              Es común contratar un servicio de gastos médicos para recibir atención en los hospitales y con los especialistas que tu desees, en Uro-Oncology tenemos convenio con las todas las aseguradoras de México.
            </p>
          </div>
          <div className={styles.sliderContainer}>
            {images.map((img, index) => (
              <div 
                key={index} 
                className={`${styles.slide} ${index === current ? styles.active : ''}`}
              >
                <img src={img} alt={`Seguros médicos ${index + 1}`} className={styles.image} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
