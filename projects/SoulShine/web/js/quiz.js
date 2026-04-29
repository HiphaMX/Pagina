const questions = [
  {
    id: 1,
    question: "¿Cuál es tu principal preocupación en cuanto a tu bienestar?",
    options: [
      { text: "Problemas de concentración y memoria", scores: { lion: 3, turkey: 0, cordyceps: 1, reishi: 0, mindii: 3 } },
      { text: "Falta de energía y cansancio constante", scores: { lion: 0, turkey: 1, cordyceps: 3, reishi: 1, mindii: 1 } },
      { text: "Sistema inmune débil, me enfermo seguido", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 1, mindii: 0 } },
      { text: "Estrés y ansiedad constante", scores: { lion: 1, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Me siento desmotivado/a y sin ganas", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 2,
    question: "En tu día a día, ¿qué te resulta más difícil?",
    options: [
      { text: "Mantener la concentración por períodos largos", scores: { lion: 3, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } },
      { text: "Tener energía suficiente durante todo el día", scores: { lion: 0, turkey: 1, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Recuperarme de enfermedades rápidamente", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 1, mindii: 0 } },
      { text: "Manejar la presión y el estrés", scores: { lion: 1, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Sentir motivación y alegría", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 3,
    question: "¿Cómo describirías tu nivel de energía actual?",
    options: [
      { text: "Mental: baja, física: normal", scores: { lion: 3, turkey: 1, cordyceps: 1, reishi: 0, mindii: 3 } },
      { text: "Mental: normal, física: muy baja", scores: { lion: 1, turkey: 1, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Ambas bajas, me siento vulnerable", scores: { lion: 1, turkey: 3, cordyceps: 2, reishi: 1, mindii: 1 } },
      { text: "Energía normal pero muy estresado/a", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 3, mindii: 1 } },
      { text: "Tengo energía pero me falta motivación", scores: { lion: 2, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 4,
    question: "¿Con qué frecuencia te enfermas o sientes que tu sistema inmune no puede recuperar tu salud?",
    options: [
      { text: "Rara vez pero me siento muy bajoneado", scores: { lion: 2, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } },
      { text: "A veces y siento que me falta energía física", scores: { lion: 1, turkey: 0, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Frecuentemente cada cambio de estación", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 1, mindii: 0 } },
      { text: "Pocas veces, aunque siento que el estrés me debilita (y me estreso mucho)", scores: { lion: 1, turkey: 1, cordyceps: 0, reishi: 3, mindii: 1 } }
    ]
  },
  {
    id: 5,
    question: "¿Cómo es la calidad de tu sueño?",
    options: [
      { text: "Duermo bien pero despierto mentalmente nublado/a", scores: { lion: 3, turkey: 1, cordyceps: 0, reishi: 1, mindii: 3 } },
      { text: "Duermo bien pero despierto sin energía", scores: { lion: 0, turkey: 1, cordyceps: 3, reishi: 1, mindii: 1 } },
      { text: "Duermo regular, mi sistema se siente débil", scores: { lion: 1, turkey: 3, cordyceps: 1, reishi: 2, mindii: 0 } },
      { text: "Me cuesta dormir por estrés y ansiedad", scores: { lion: 0, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Duermo bien pero me despierto sin ganas", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 6,
    question: "¿Cuál de estos objetivos es más importante para ti?",
    options: [
      { text: "Mejorar mi rendimiento mental y creatividad", scores: { lion: 3, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } },
      { text: "Aumentar mi resistencia y energía física", scores: { lion: 0, turkey: 1, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Fortalecer mi sistema inmunológico", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 1, mindii: 0 } },
      { text: "Encontrar calma y equilibrio emocional", scores: { lion: 1, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Recuperar mi motivación y alegría de vivir", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 7,
    question: "En los días pesados, ¿qué es lo que más necesitas?",
    options: [
      { text: "Claridad mental y mejor memoria", scores: { lion: 3, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } },
      { text: "Energía sostenida para rendir al máximo", scores: { lion: 1, turkey: 1, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Sentirme fuerte y con mi sistema inmune listo para defenderme", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 2, mindii: 0 } },
      { text: "Mantener la calma y no sentirme abrumado/a", scores: { lion: 1, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Sentir esperanza y motivación para seguir", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  },
  {
    id: 8,
    question: "¿Qué aspecto de tu bienestar te gustaría transformar primero?",
    options: [
      { text: "Mi capacidad de aprender y recordar información", scores: { lion: 3, turkey: 0, cordyceps: 0, reishi: 1, mindii: 3 } },
      { text: "Mi resistencia física y vitalidad", scores: { lion: 0, turkey: 1, cordyceps: 3, reishi: 0, mindii: 1 } },
      { text: "Mi capacidad de defensa natural del cuerpo", scores: { lion: 0, turkey: 3, cordyceps: 1, reishi: 1, mindii: 0 } },
      { text: "Mi paz interior y manejo del estrés", scores: { lion: 0, turkey: 0, cordyceps: 0, reishi: 3, mindii: 1 } },
      { text: "Mi estado de ánimo y bienestar emocional", scores: { lion: 1, turkey: 0, cordyceps: 1, reishi: 1, mindii: 3 } }
    ]
  }
];

const adaptogenInfo = {
  lion: {
    name: "Melena de León",
    productName: "Focus",
    icon: "brain",
    color: "#059669",
    colorGradient: "linear-gradient(to right, #10b981, #0d9488)",
    benefits: [
      "Mejora la función cognitiva y la memoria",
      "Estimula la producción del factor de crecimiento nervioso (NGF)",
      "Protege las neuronas del daño oxidativo",
      "Mejora la concentración y el enfoque mental",
      "Puede ayudar con la neurogénesis"
    ],
    description: "La Melena de León es excepcional para la salud cerebral. Sus compuestos únicos, las hericenonas y erinacinas, cruzan la barrera hematoencefálica y estimulan la producción de NGF, esencial para el crecimiento y mantenimiento de las neuronas.",
    usage: "Ideal para estudiantes, profesionales que requieren alta concentración, y personas que buscan proteger su función cognitiva a largo plazo.",
    chartData: [
      { category: "Concentración", value: 95 },
      { category: "Memoria", value: 90 },
      { category: "Neuroprotección", value: 85 },
      { category: "Creatividad", value: 80 },
      { category: "Enfoque", value: 92 }
    ]
  },
  cordyceps: {
    name: "Cordyceps",
    productName: "Energy+",
    icon: "zap",
    color: "#f97316",
    colorGradient: "linear-gradient(to right, #f97316, #ef4444)",
    benefits: [
      "Aumenta la producción de ATP (energía celular)",
      "Mejora la resistencia y el rendimiento físico",
      "Optimiza el uso de oxígeno en el cuerpo",
      "Apoya la función pulmonar y cardiovascular",
      "Reduce la fatiga y acelera la recuperación"
    ],
    description: "El Cordyceps es conocido como el 'hongo de la energía'. Funciona a nivel mitocondrial, aumentando la producción de ATP y mejorando la eficiencia del oxígeno, lo que resulta en más energía sostenida sin los picos y caídas de los estimulantes.",
    usage: "Perfecto para atletas, personas con trabajos físicamente demandantes, o quienes experimentan fatiga crónica y necesitan energía natural y sostenida.",
    chartData: [
      { category: "Energía Física", value: 95 },
      { category: "Resistencia", value: 90 },
      { category: "Recuperación", value: 85 },
      { category: "Oxigenación", value: 88 },
      { category: "Vitalidad", value: 92 }
    ]
  },
  turkey: {
    name: "Cola de Pavo",
    productName: "Emuná",
    icon: "shield",
    color: "#3b82f6",
    colorGradient: "linear-gradient(to right, #3b82f6, #7c3aed)",
    benefits: [
      "Fortalece el sistema inmunológico",
      "Rico en polisacárido-K (PSK) y polisacárido-P (PSP)",
      "Propiedades antioxidantes potentes",
      "Apoya la salud intestinal y el microbioma",
      "Ayuda en la recuperación y resistencia a enfermedades"
    ],
    description: "La Cola de Pavo es uno de los adaptógenos más estudiados para el sistema inmune. Sus polisacáridos únicos actúan como inmunomoduladores, equilibrando la respuesta inmune sin sobre-estimularla.",
    usage: "Esencial para personas con sistemas inmunes debilitados, quienes se enferman frecuentemente, o buscan una defensa natural contra infecciones y estrés oxidativo.",
    chartData: [
      { category: "Sistema Inmune", value: 95 },
      { category: "Antioxidantes", value: 90 },
      { category: "Recuperación", value: 85 },
      { category: "Microbioma", value: 82 },
      { category: "Defensa Natural", value: 88 }
    ]
  },
  reishi: {
    name: "Reishi",
    productName: "Balance",
    icon: "moon",
    color: "#a855f7",
    colorGradient: "linear-gradient(to right, #a855f7, #4f46e5)",
    benefits: [
      "Reduce el cortisol y el estrés crónico",
      "Mejora la calidad del sueño y promueve la relajación",
      "Equilibra el sistema nervioso",
      "Propiedades adaptogénicas para el manejo del estrés",
      "Apoya la salud cardiovascular y hepática"
    ],
    description: "El Reishi, conocido como el 'hongo de la inmortalidad', es el adaptógeno maestro para el equilibrio. Sus triterpenos únicos ayudan a regular el eje hipotálamo-hipófisis-suprarrenal, reduciendo el estrés y promoviendo un estado de calma alerta.",
    usage: "Ideal para personas con estrés crónico, ansiedad, problemas de sueño, o quienes buscan equilibrio emocional y mayor resistencia al estrés diario.",
    chartData: [
      { category: "Manejo del Estrés", value: 95 },
      { category: "Calidad del Sueño", value: 90 },
      { category: "Equilibrio Emocional", value: 88 },
      { category: "Relajación", value: 92 },
      { category: "Adaptación", value: 85 }
    ]
  },
  mindii: {
    name: "Mindii",
    productName: "Mindii",
    icon: "smile",
    color: "#ec4899",
    colorGradient: "linear-gradient(to right, #ec4899, #f43f5e)",
    benefits: [
      "Combina los beneficios cognitivos de Melena de León",
      "Aumenta la dopamina natural a través de Mucuna Pruriens",
      "Rico en antioxidantes del Amla (vitamina C natural)",
      "Mejora el estado de ánimo y la motivación",
      "Apoya la función cerebral y el bienestar emocional"
    ],
    description: "Mindii es una fórmula única que combina Melena de León para la función cognitiva, Mucuna Pruriens como precursor natural de dopamina para la felicidad y motivación, y Amla por sus potentes antioxidantes. Esta sinergia crea el adaptógeno perfecto para el bienestar mental integral.",
    usage: "Ideal para personas que buscan mejorar su estado de ánimo, motivación y función cognitiva simultáneamente. Perfecto para quienes experimentan desmotivación, baja energía mental o necesitan un impulso natural de felicidad.",
    chartData: [
      { category: "Estado de Ánimo", value: 95 },
      { category: "Motivación", value: 92 },
      { category: "Concentración", value: 88 },
      { category: "Dopamina Natural", value: 90 },
      { category: "Bienestar Emocional", value: 93 }
    ]
  }
};

let currentQuestion = -1;
let answers = {};
let userName = '';
let quizResults = null;

document.addEventListener('DOMContentLoaded', () => {
    initQuiz();
});

function initQuiz() {
    const wrapper = document.getElementById('soulshine-test-wrapper');
    if (!wrapper) return;
    renderWelcomeScreen(wrapper);
}

function reInitIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function renderWelcomeScreen(wrapper) {
    wrapper.innerHTML = `
        <div class="quiz-card fade-in">
            <div class="quiz-header">
                <i data-lucide="sparkles" class="quiz-main-icon pulse"></i>
                <h3 class="quiz-title">¡Bienvenido/a al Test!</h3>
                <p>Para personalizar tu experiencia, compártenos tu nombre:</p>
            </div>
            
            <div class="quiz-input-group">
                <input type="text" id="quiz-username" placeholder="Escribe tu nombre aquí..." class="quiz-input" value="${userName}">
            </div>

            <button id="btn-start-quiz" class="btn btn-primary btn-large w-full" disabled>Hacer test</button>
        </div>
    `;
    reInitIcons();

    const input = document.getElementById('quiz-username');
    const btn = document.getElementById('btn-start-quiz');

    input.addEventListener('input', (e) => {
        userName = e.target.value;
        btn.disabled = userName.trim() === '';
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && userName.trim() !== '') {
            startQuiz(wrapper);
        }
    });

    btn.addEventListener('click', () => {
        startQuiz(wrapper);
    });
}

function startQuiz(wrapper) {
    currentQuestion = 0;
    renderQuestionScreen(wrapper);
}

function handleAnswer(wrapper, optionIndex) {
    answers[currentQuestion] = optionIndex;
    
    if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        renderQuestionScreen(wrapper);
    } else {
        calculateResults(wrapper);
    }
}

function goBack(wrapper) {
    if (currentQuestion > 0) {
        currentQuestion--;
        renderQuestionScreen(wrapper);
    } else if (currentQuestion === 0) {
        currentQuestion = -1;
        renderWelcomeScreen(wrapper);
    }
}

function restartQuiz(wrapper) {
    currentQuestion = -1;
    answers = {};
    userName = '';
    quizResults = null;
    renderWelcomeScreen(wrapper);
}

function renderQuestionScreen(wrapper) {
    const question = questions[currentQuestion];
    const progressPercent = Math.round(((currentQuestion) / questions.length) * 100);

    let optionsHtml = '';
    question.options.forEach((opt, index) => {
        optionsHtml += `
            <button class="quiz-option-btn" onclick="window.quizHandleAnswer(${index})">
                <span>${opt.text}</span>
                <i data-lucide="chevron-right" class="quiz-option-icon"></i>
            </button>
        `;
    });

    wrapper.innerHTML = `
        <div class="quiz-card fade-in">
            <div class="quiz-progress-bar">
                <div class="quiz-progress-text">
                    <span>Pregunta ${currentQuestion + 1} de ${questions.length}</span>
                    <span>${progressPercent}%</span>
                </div>
                <div class="quiz-progress-track">
                    <div class="quiz-progress-fill" style="width: ${progressPercent}%"></div>
                </div>
            </div>

            <h3 class="quiz-question-text">${question.question}</h3>

            <div class="quiz-options-list">
                ${optionsHtml}
            </div>

            <div class="quiz-navigation">
                <button class="btn-back" onclick="window.quizGoBack()">
                    <i data-lucide="arrow-left"></i>
                    ${currentQuestion === 0 ? 'Volver al inicio' : 'Pregunta anterior'}
                </button>
            </div>
        </div>
    `;

    // Bind global handlers for onclick attributes
    window.quizHandleAnswer = (index) => handleAnswer(wrapper, index);
    window.quizGoBack = () => goBack(wrapper);

    reInitIcons();
}

function calculateResults(wrapper) {
    const scores = { lion: 0, turkey: 0, cordyceps: 0, reishi: 0, mindii: 0 };
    
    Object.keys(answers).forEach(questionIndex => {
        const answerIndex = answers[questionIndex];
        const question = questions[questionIndex];
        const selectedOption = question.options[answerIndex];
        
        Object.keys(selectedOption.scores).forEach(adaptogen => {
            scores[adaptogen] += selectedOption.scores[adaptogen];
        });
    });

    const sortedResults = Object.entries(scores)
        .sort(([,a], [,b]) => b - a)
        .map(([key, score]) => ({ adaptogen: key, score }));

    quizResults = { primary: sortedResults[0], secondary: sortedResults[1], scores };
    renderResultsScreen(wrapper);
}

function renderResultsScreen(wrapper) {
    const primary = adaptogenInfo[quizResults.primary.adaptogen];
    const secondary = adaptogenInfo[quizResults.secondary.adaptogen];
    
    let primaryChartHtml = '';
    primary.chartData.forEach(item => {
        primaryChartHtml += `
            <div class="quiz-chart-row">
                <div class="quiz-chart-label">${item.category}</div>
                <div class="quiz-chart-track">
                    <div class="quiz-chart-fill" style="background: ${primary.colorGradient}; width: ${item.value}%"></div>
                </div>
                <div class="quiz-chart-value">${item.value}%</div>
            </div>
        `;
    });

    let secondaryHtml = '';
    if (quizResults.scores[quizResults.secondary.adaptogen] > 8) {
        let secondaryBenefits = '';
        secondary.benefits.slice(0, 3).forEach(b => {
            secondaryBenefits += `<li><div class="bullet-dot" style="background: ${secondary.color}"></div><span>${b}</span></li>`;
        });

        secondaryHtml = `
            <div class="quiz-secondary-result">
                <h4>Complemento Recomendado:</h4>
                <div class="secondary-header">
                    <div class="secondary-icon" style="background: ${secondary.colorGradient}">
                        <i data-lucide="${secondary.icon}"></i>
                    </div>
                    <h5>${secondary.name} / ${secondary.productName}</h5>
                </div>
                <p>Combinar con ${secondary.productName} puede potenciar tus resultados, abordando múltiples aspectos de tu bienestar de manera integral.</p>
                <div class="secondary-benefits">
                    <h6>Beneficios adicionales:</h6>
                    <ul>${secondaryBenefits}</ul>
                </div>
            </div>
        `;
    }

    const whatsappMessage = encodeURIComponent("¡Hola! Completé el test de adaptógenos en Soul Shine y me interesa conocer más sobre mis resultados 🍄✨");
    const whatsappLink = `https://wa.me/523314199842?text=${whatsappMessage}`;

    wrapper.innerHTML = `
        <div class="quiz-card results-card fade-in">
            <div class="results-hero">
                <div class="primary-icon-wrapper" style="background: ${primary.colorGradient}">
                    <i data-lucide="${primary.icon}"></i>
                </div>
                <h2>¡Hola ${userName}! Tu Adaptógeno Ideal</h2>
                <h3 style="color: ${primary.color}">${primary.name} / ${primary.productName}</h3>
            </div>

            <div class="results-description">
                <p>${primary.description}</p>
                <p class="usage-text"><em>${primary.usage}</em></p>
            </div>

            <div class="results-grid">
                <div class="results-benefits">
                    <h4>Beneficios Principales:</h4>
                    <ul>
                        ${primary.benefits.map(b => `<li><div class="bullet-dot" style="background: ${primary.color}"></div><span>${b}</span></li>`).join('')}
                    </ul>
                </div>
                <div class="results-chart">
                    <h4>Beneficios Proyectados:</h4>
                    ${primaryChartHtml}
                </div>
            </div>

            ${secondaryHtml}

            <div class="results-cta">
                <h3>¿Quieres una Consulta Personalizada?</h3>
                <p>Obtén recomendaciones específicas de dosificación, combinaciones y plan de seguimiento adaptado a tus necesidades únicas.</p>
                <div class="results-actions">
                    <a href="${whatsappLink}" target="_blank" class="btn btn-whatsapp">
                        <i data-lucide="message-circle"></i>
                        Contactar por WhatsApp
                    </a>
                    <a href="https://instagram.com/soul_shine_inside" target="_blank" class="btn btn-instagram">
                        <i data-lucide="instagram"></i>
                        Síguenos en Instagram
                    </a>
                </div>
            </div>

            <div class="results-footer">
                <button class="btn-restart" onclick="window.quizRestart()">
                    <i data-lucide="arrow-left"></i> Realizar el test nuevamente
                </button>
            </div>
        </div>
    `;

    window.quizRestart = () => restartQuiz(wrapper);
    reInitIcons();
}
