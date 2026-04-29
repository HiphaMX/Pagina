'use client';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import styles from './Slider.module.css';

const slides = [
  {
    id: 1,
    title: 'Cáncer de próstata',
    description: 'Alrededor de 6 de 10 casos se diagnostican en hombres de 65 años o más. La detección oportuna salva vidas.',
    link: '/diagnostico/cancer-de-prostata',
    desktopImg: '/assets/slider/Sliderescritorio01.jpg',
    mobileImg: '/assets/slider/slidermovil1.jpg'
  },
  {
    id: 2,
    title: 'Cirugía de mínima invasión',
    description: 'Hoy en día, se pueden realizar muchos procedimientos urológicos con incisiones mínimas, reduciendo el dolor y el tiempo de recuperación.',
    link: '/tipos-de-cirugia',
    desktopImg: '/assets/slider/Sliderescritorio2.jpg',
    mobileImg: '/assets/slider/slidermovil2.jpg'
  },
  {
    id: 3,
    title: 'Cirugía Robótica',
    description: 'El sistema quirúrgico da Vinci le brinda a su cirujano una vista 3D de alta definición ampliada para mayor precisión y control.',
    link: '/cirugia-robotica',
    desktopImg: '/assets/slider/Sliderescritorio3.jpg',
    mobileImg: '/assets/slider/slidermovil3.jpg'
  },
  {
    id: 4,
    title: 'Cuidamos tu salud',
    description: 'En Uro Oncology cuidamos la salud de tus vías urinarias con el pulso humano y profesional que necesitas.',
    link: '/diagnostico',
    desktopImg: '/assets/slider/Sliderescritorio4.jpg',
    mobileImg: '/assets/slider/slidermovil4.jpg'
  },
  {
    id: 5,
    title: 'Cuidamos tu salud urológica',
    description: 'Descubre los diferentes padecimientos en los que nos especializamos con la más avanzada tecnología y calidez.',
    link: '/equipo-medico',
    desktopImg: '/assets/slider/Sliderescritorio5.jpg',
    mobileImg: '/assets/slider/slidermovil5.jpg'
  }
];

export default function Slider() {
  const [currentSlide, setCurrentSlide] = useState(0);

  // Autoplay
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
    }, 6000); // 6 seconds per slide
    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => setCurrentSlide(currentSlide === slides.length - 1 ? 0 : currentSlide + 1);
  const prevSlide = () => setCurrentSlide(currentSlide === 0 ? slides.length - 1 : currentSlide - 1);

  return (
    <div className={styles.sliderContainer}>
      {slides.map((slide, index) => (
        <div 
          key={slide.id} 
          className={`${styles.slide} ${index === currentSlide ? styles.active : ''}`}
        >
          {/* Responsive Background using Picture */}
          <picture className={styles.background}>
            <source media="(max-width: 768px)" srcSet={slide.mobileImg} />
            <source media="(min-width: 769px)" srcSet={slide.desktopImg} />
            <img src={slide.desktopImg} alt={slide.title} className={styles.bgImage} />
          </picture>
          
          <div className={styles.overlay}>
            <div className={`container ${styles.slideContent}`}>
              <h2>{slide.title}</h2>
              <p>{slide.description}</p>
              <Link href={slide.link} className="btn btn-outline">
                Más información
              </Link>
            </div>
          </div>
        </div>
      ))}

      {/* Dots */}
      <div className={styles.dots}>
        {slides.map((_, idx) => (
          <span 
            key={idx} 
            className={`${styles.dot} ${idx === currentSlide ? styles.activeDot : ''}`}
            onClick={() => setCurrentSlide(idx)}
          />
        ))}
      </div>
    </div>
  );
}
