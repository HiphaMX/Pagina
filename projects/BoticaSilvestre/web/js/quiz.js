const PRODUCTS_DB = {
  step1: [
    { id: 'focus', label: 'Focus', product: 'Focus (Microdosis de Melena de León)', desc: 'Claridad mental y neuroplasticidad.', price: 490, image: 'assets/images/Product Shots/Focus 01.webp' },
    { id: 'balance', label: 'Balance', product: 'Balance (Microdosis de Reishi)', desc: 'Homeostasis y regulación del cortisol.', price: 490, image: 'assets/images/Product Shots/Balance 01.webp' },
    { id: 'energy', label: 'Energy+', product: 'Energy+ (Microdosis de Cordyceps)', desc: 'Oxigenación celular y vigor.', price: 490, image: 'assets/images/Product Shots/Energy 01.webp' },
    { id: 'emuna', label: 'Emuná', product: 'Emuná (Microdosis de Cola de Pavo)', desc: 'Inteligencia inmunológica.', price: 490, image: 'assets/images/Product Shots/Emuna 01.webp' },
    { id: 'mindii', label: 'Mindii', product: 'Mindii (Microdosis de Melena + Mucuna + AMLA)', desc: 'Sinergia dopaminérgica y cognitiva.', price: 490, image: 'assets/images/Product Shots/Mindii 01.webp' },
    { id: 'smile', label: 'Smile', product: 'Smile (Microdosis de Psilocibina)', desc: 'Bienestar emocional y apertura.', price: 690, image: 'assets/images/Product Shots/Smile 01.webp' },
    { id: 'mystic', label: 'Mystic', product: 'Mystic (Dosis concentrada de Psilocibina)', desc: 'Exploración profunda del ser.', price: 990, image: 'assets/images/Product Shots/Mystic 01.webp' },
  ],
  step2: [
    { id: 'rana', product: 'Colita de Rana', subtitle: 'Aceite de coco + Cera de abeja + Herbolaria', icon: 'activity', desc: 'Dolor muscular después de ir al gym', price: 190, image: 'https://placehold.co/400x500/E8E6E1/40534C?text=Foto+Pendiente' },
    { id: 'descansa', product: 'Descansa', subtitle: 'Aceite de coco + Cera de abeja + Herbolaria', icon: 'wind', desc: 'Piernas cansadas por el trabajo diario', price: 190, image: 'https://placehold.co/400x500/E8E6E1/40534C?text=Foto+Pendiente' },
    { id: 'abacho', product: 'Abacho', subtitle: 'Aceite de coco + Cera de abeja + Herbolaria', icon: 'heart', desc: 'Reconexión con mi verdadera esencia', price: 190, image: 'https://placehold.co/400x500/E8E6E1/40534C?text=Foto+Pendiente' },
    { id: 'piel', product: 'Piel Silvestre', subtitle: 'Aceite de coco + Cera de abeja + Herbolaria', icon: 'sun', desc: 'Mi piel es delicada y necesita una caricia', price: 250, image: 'https://placehold.co/400x500/E8E6E1/40534C?text=Foto+Pendiente' },
    { id: 'alivia', product: 'Alivia', subtitle: 'Aceite de coco + Cera de abeja + Herbolaria', icon: 'zap', desc: 'Dolor en las articulaciones', price: 190, image: 'https://placehold.co/400x500/E8E6E1/40534C?text=Foto+Pendiente' },
  ],
  step3: [
    { id: 'yes', product: 'Armonizador', subtitle: 'Spray Energético', icon: 'sparkles', desc: 'Spray aerobeo ambiental con salvia, ruda y pirul para disipar energías hostiles.', price: 59, image: 'assets/images/Product Shots/Armonizador1.webp' },
    { id: 'no', product: 'Omitir armonización', subtitle: 'Continuar sin sellar', icon: 'x', desc: 'Prefiero no añadir esta frecuencia por ahora.' }
  ]
};

const QUIZ_QUESTIONS = [
  { id: 1, text: "¿Qué nivel de estrés percibes en tu día a día?", labelMin: "POCO", labelMax: "DEMASIADO", targets: { balance: 1.5, smile: 1.2, mystic: 1 } },
  { id: 2, text: "¿Cómo calificarías tu calidad de descanso?", labelMin: "MALO", labelMax: "EXCELENTE", targets: { balance: 1.5, smile: 1.2, mystic: 1 }, inverse: true },
  { id: 3, text: "¿Cómo está tu nivel de energía física al despertar?", labelMin: "MUY BAJA", labelMax: "AL MÁXIMO", targets: { energy: 1.5 }, inverse: true },
  { id: 4, text: "¿Sientes que te falta enfoque o tienes 'niebla mental'?", labelMin: "CASI NUNCA", labelMax: "MUCHAS VECES", targets: { focus: 1.5, mindii: 1.2 } },
  { id: 5, text: "¿Con qué frecuencia sientes tus defensas bajas?", labelMin: "CASI NUNCA", labelMax: "TODO EL TIEMPO", targets: { emuna: 2 } },
  { id: 6, text: "¿Qué tan presente está la ansiedad rumiante?", labelMin: "CASI NUNCA", labelMax: "MUY PRESENTE", targets: { balance: 1.2, smile: 1.2 } },
  { id: 7, text: "¿Te sientes desconectado de tu propósito?", labelMin: "CASI NUNCA", labelMax: "MUCHAS VECES", targets: { mystic: 2, smile: 0.8 } },
  { id: 8, text: "¿Sientes fatiga muscular o pesadez física?", labelMin: "CASI NUNCA", labelMax: "MUCHAS VECES", targets: { energy: 1, emuna: 0.5 } },
  { id: 9, text: "¿Necesitas impulsar tu creatividad y abrirte a cosas nuevas?", labelMin: "CASI NUNCA", labelMax: "MUCHAS VECES", targets: { mindii: 1, smile: 1.5, mystic: 1.2 } },
  { id: 10, text: "¿Te permites sentir plenamente y expresas tus emociones?", labelMin: "CASI NUNCA", labelMax: "TODO EL TIEMPO", targets: { balance: 1.5, smile: 1 }, inverse: true },
];

let state = {
    view: 'intro',
    name: '',
    dob: '',
    format: null,
    quizIdx: 0,
    answers: [],
    selections: { step1: [], step2: null, step3: null }
};

function getNumerologyMessage(dobStr, name) {
    if (!dobStr) return "";
    const parts = dobStr.split('-');
    if(parts.length !== 3) return "";
    let sum = parts.join('').split('').reduce((a, b) => a + parseInt(b), 0);
    
    while (sum > 9 && sum !== 11 && sum !== 22 && sum !== 33) {
        sum = sum.toString().split('').reduce((a, b) => a + parseInt(b), 0);
    }
    
    const messages = {
        1: [
            "tu numerología indica una fuerza creadora inmensa, pero a veces cargas con el peso del mundo solo. Es momento de permitirte recibir y reconectar con tu paz interior.",
            "como pionero nato, sueles abrir caminos para otros mientras descuidas tu propia tierra. Este ritual te invita a plantar semillas de cuidado en tu propio ser.",
            "tu energía individualista es poderosa, pero el exceso de independencia puede aislarte. Permítete sostenerte por la magia reparadora de la naturaleza.",
            "tienes la valentía de los inicios, aunque esto a menudo drena tu vitalidad. Es hora de pausar y nutrir la raíz antes de emprender tu próximo vuelo.",
            "tu alma líder te impulsa siempre hacia adelante, olvidando a veces disfrutar el presente. Este es tu momento sagrado para detenerte y simplemente ser."
        ],
        2: [
            "tu numerología indica que eres propenso a preocuparte profundamente por los demás, dejándote a un lado. Llegó el momento de ser tu propia prioridad y nutrir tu esencia.",
            "tu don es la empatía y la conexión, pero absorber la energía de otros agota la tuya. Permite que estas medicinas limpien tu campo y te devuelvan tu centro.",
            "eres el pacificador natural en tu entorno, a costa de tu propia paz mental. Este ritual te ayudará a establecer límites amorosos y recuperar tu calma.",
            "la sensibilidad que posees es tu mayor regalo, aunque te hace vulnerable al estrés externo. Es tiempo de crear un escudo suave pero firme para tu energía.",
            "buscas constantemente la armonía a tu alrededor, olvidando a veces la armonía interna. Reconecta contigo y descubre el equilibrio desde tu propio núcleo."
        ],
        3: [
            "tu sensibilidad y expresión son tus mayores dones, pero la mente dispersa puede agotarte. Es tiempo de enraizar tu energía y enfocar tu luz.",
            "tu creatividad ilumina a quienes te rodean, aunque la inspiración constante consume tus reservas. Permítete un momento de vacío fértil para regenerarte.",
            "la alegría y el optimismo son tus sellos, pero también necesitas permiso para sentir el cansancio. Este ritual es un bálsamo para calmar el ritmo de tu espíritu.",
            "tienes una gran capacidad para comunicar y sentir, lo que puede sobreestimular tu sistema. Encuentra en la botánica el anclaje necesario para estabilizar tus emociones.",
            "tu energía es vibrante y expansiva, a veces difícil de contener. Utiliza este instante para condensar esa magia hacia adentro y nutrir tu paz."
        ],
        4: [
            "tu numerología refleja una lealtad y resistencia inquebrantables, pero la rigidez puede generar tensión física y mental. Mereces soltar el control y fluir con suavidad.",
            "eres la roca para muchos, soportando estructuras pesadas día a día. Es hora de liberar esa rigidez muscular y emocional, permitiéndote ser vulnerable y descansar.",
            "tu enfoque en el trabajo y el deber te ha alejado de tu propio disfrute. Este es tu permiso divino para detener la máquina y simplemente respirar.",
            "construyes bases sólidas para el futuro, pero a menudo sacrificas tu bienestar presente. Este ritual aflojará las tensiones que guardas en secreto.",
            "la disciplina y el orden son tus aliados, pero el exceso de perfección agota tu alma. Entrégate a la sabiduría imperfecta y sanadora de las plantas."
        ],
        5: [
            "tu alma anhela libertad y experiencia, llevándote a veces al límite de tu energía. Este es tu momento para pausar, estabilizarte y encontrar la libertad en la calma.",
            "el cambio constante y la aventura son tu motor, lo que puede causar desorden en tu sistema nervioso. Encuentra en este ritual el enraizamiento que tanto necesitas.",
            "vives a un ritmo acelerado, buscando siempre nuevos horizontes. Deja que esta alquimia frene el tiempo por un instante, devolviéndote al momento presente.",
            "tu curiosidad no tiene límites, pero tu cuerpo sí. Es hora de recargar tus baterías internas para que puedas seguir explorando el mundo con vitalidad.",
            "eres el movimiento puro, aunque el descanso es el secreto para la verdadera libertad. Permite que estas medicinas anclen tu espíritu y restauren tu cuerpo."
        ],
        6: [
            "tu naturaleza es nutrir y armonizar tu entorno, a menudo vaciando tu propia copa. Este ritual es tu permiso sagrado para nutrirte a ti primero.",
            "el amor y la familia son el centro de tu vida, pero cuidar a todos menos a ti es insostenible. Recibe este abrazo botánico para sanar al sanador.",
            "tu corazón maternal o paternal siempre busca proteger, asumiendo cargas que no te corresponden. Suelta ese peso y permítete ser contenido y abrazado.",
            "tu hogar es tu refugio y el de muchos, pero has olvidado hacer de tu cuerpo tu propio templo. Dedica este espacio para restaurar tu propio santuario.",
            "la responsabilidad emocional que cargas es enorme y a veces silenciosa. Deja que este momento actúe como un bálsamo de amor incondicional hacia ti mismo."
        ],
        7: [
            "tu mente profunda siempre busca respuestas y verdades ocultas, lo que puede sobrecargar tu sistema nervioso. Es el instante perfecto para dejar de analizar y empezar a sentir.",
            "tu mundo interior es vasto y misterioso, llevándote a aislarte en tus pensamientos. Este ritual te conectará suavemente de vuelta con tu cuerpo y la tierra.",
            "la búsqueda espiritual y el intelecto constante te generan fatiga mental. Permite que la sabiduría de la naturaleza calme el incesante diálogo de tu cabeza.",
            "eres un analista natural, pero no todo necesita ser comprendido para ser sanado. Ríndete a la intuición y deja que la magia actúe sin filtros racionales.",
            "tu alma solitaria necesita a veces el roce suave de la contención. Encuentra en estas plantas un acompañante silencioso que entiende tus profundidades."
        ],
        8: [
            "tu fuerza impulsora te permite lograr grandes cosas, pero la búsqueda constante puede desconectarte de tu centro. Reconecta con tu poder desde la serenidad, no desde el agotamiento.",
            "el éxito y la abundancia son tu lenguaje, aunque el estrés del logro pasa factura a tu cuerpo. Es tiempo de que el verdadero lujo sea tu paz mental.",
            "eres el ejecutivo y el manifestador, acostumbrado a dirigir y controlar. Este ritual te enseña el inmenso poder que existe en saber delegar al universo.",
            "tu capacidad de materializar es brillante, pero la auto-exigencia te exprime. Afloja la tensión de tus metas y permite que tu cuerpo se recupere en calma.",
            "la balanza entre lo espiritual y lo material a menudo se inclina hacia el estrés. Restaura tu equilibrio interno para que tu autoridad provenga de un lugar de amor."
        ],
        9: [
            "tu numerología muestra un alma vieja que comprende el dolor del mundo. Sin embargo, para seguir sanando a otros, debes permitir que la naturaleza te sane a ti.",
            "tu compasión no conoce fronteras, llevándote al agotamiento empático. Este es tu escudo y tu bálsamo para limpiar tu campo y fortalecer tu espíritu.",
            "estás cerrando ciclos kármicos profundos, un proceso que requiere mucha energía vital. Encuentra en esta alquimia el sostén para soltar lo que ya no es tuyo.",
            "el idealismo y la entrega desinteresada te hacen olvidar tus necesidades humanas. Es hora de recibir, de anclarte en lo físico y recuperar tu fuerza vital.",
            "tu capacidad de perdonar y soltar es enorme, pero tu cuerpo guarda las memorias del proceso. Usa este ritual para liberar la tensión acumulada y renacer."
        ],
        11: [
            "tu intuición y sensibilidad energética son extraordinarias, pero pueden sobreestimularte fácilmente. Este ritual te ayudará a sellar tu campo áurico y proteger tu luz.",
            "eres un puente entre mundos, canalizando alta frecuencia constantemente. Necesitas este enraizamiento para que tu sistema nervioso no colapse ante tanta energía.",
            "la luz de tu alma ilumina a muchos, pero te vuelve hiper-susceptible al caos del entorno. Encuentra en estas medicinas el ancla de paz que tu espíritu maestro requiere.",
            "tienes el don de ver más allá de las ilusiones, lo que a menudo te hace sentir incomprendido. Refúgiate en este abrazo botánico para restaurar tu centro.",
            "tu vibración maestra te exige mucho a nivel emocional y espiritual. Permítete un descanso profundo, sabiendo que la sabiduría también habita en el silencio."
        ],
        22: [
            "tienes el potencial de materializar grandes visiones, pero el estrés de las expectativas es alto. Encuentra tu centro espiritual para que tus creaciones nazcan desde la paz.",
            "eres el arquitecto de nuevos paradigmas, una labor que pesa sobre tus hombros. Este ritual aliviará la tensión de sostener el mundo y te devolverá a la tierra.",
            "la magnitud de tus proyectos suele devorar tu tiempo personal y tu salud. Es imprescindible que detengas la obra un instante y cuides del maestro constructor.",
            "tu mente pragmática y espiritual trabaja a mil por hora, generando fatiga profunda. Permite que la naturaleza estabilice tu frecuencia y renueve tu visión.",
            "el poder de tus sueños te empuja sin descanso. Este es el momento de pausar, integrar lo aprendido y descansar en la certeza de que todo está en orden."
        ],
        33: [
            "tu capacidad de amor incondicional es inmensa, pero requiere un profundo anclaje emocional. Permítete recibir el mismo amor y cuidado que entregas al mundo.",
            "eres un sanador y maestro de maestros, soportando el peso de guiar a otros. Encuentra en la herbolaria sagrada la sanación que mereces para ti mismo.",
            "tu alma irradia compasión, convirtiéndote en un faro que a veces se queda sin aceite. Recarga tu luz y sana tus heridas antes de seguir iluminando el camino.",
            "la responsabilidad espiritual que sientes por la humanidad puede desestabilizar tu cuerpo físico. Este ritual es tu recordatorio de que tu propio cuidado es vital.",
            "tu amor universal es tu mayor fuerza, pero también tu mayor desafío. Ríndete a la dulzura del descanso y permite que el universo te sostenga por un momento."
        ]
    };
    
    const msgArray = messages[sum] || messages[sum % 9 || 9];
    const msg = msgArray[Math.floor(Math.random() * msgArray.length)];
    return `${name}, ${msg}`;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

function initApp() {
    render();
}

function setView(newView) {
    state.view = newView;
    render();
}

function handlePrev() {
    if (state.view === 'quiz') {
        if (state.quizIdx > 0) {
            state.quizIdx--;
            state.answers.pop();
            render();
        } else {
            setView('format');
        }
    } else if (state.view === 'format') {
        setView('personalData');
    } else if (state.view === 'personalData') {
        setView('intro');
    } else if (state.view === 'step2') {
        state.quizIdx = QUIZ_QUESTIONS.length - 1;
        state.answers.pop(); // Remove the last answer so user can re-select
        setView('quiz');
    } else if (state.view === 'step3') {
        setView('step2');
    }
}

function calculateScores() {
    let scores = { focus: 0, balance: 0, energy: 0, emuna: 0, mindii: 0, smile: 0, mystic: 0 };
    state.answers.forEach((val, idx) => {
        const question = QUIZ_QUESTIONS[idx];
        if(!question) return;
        Object.entries(question.targets).forEach(([key, points]) => {
            const weight = question.inverse ? (6 - val) : val;
            scores[key] += weight * points;
        });
    });
    return scores;
}

function selectValue(val) {
    // Visual feedback immediately
    const nodes = document.querySelectorAll('.scale-btn');
    nodes.forEach((node, i) => {
        if(i + 1 === val) node.classList.add('active');
        else node.classList.remove('active');
    });

    // Wait a brief moment then advance automatically
    setTimeout(() => {
        state.answers[state.quizIdx] = val;
        
        if (state.quizIdx < QUIZ_QUESTIONS.length - 1) {
            state.quizIdx++;
            render();
        } else {
            // Process Step 1 Winner
            const finalScores = calculateScores();
            const sorted = Object.entries(finalScores).sort((a, b) => b[1] - a[1]);
            
            const primaryProduct = PRODUCTS_DB.step1.find(p => p.id === sorted[0][0]);
            let results = [primaryProduct];
            
            // Allow recommending up to 2 adaptogens if the secondary is close enough
            if (sorted.length > 1 && sorted[1][1] > 2 && (sorted[0][1] - sorted[1][1] <= 1.8)) {
                const secondaryProduct = PRODUCTS_DB.step1.find(p => p.id === sorted[1][0]);
                results.push(secondaryProduct);
            }
            
            state.selections.step1 = results;
            setView('step2');
        }
    }, 500);
}

window.alquimia = {
    handleManualSelection: (step, valueId) => {
        const item = PRODUCTS_DB[step].find(x => x.id === valueId);
        state.selections[step] = item;
        
        if (step === 'step2') {
            state.view = 'step3';
        } else if (step === 'step3') {
            state.view = 'result';
        }
        render();
        window.lucide.createIcons();
    },

    addRitualToCart: () => {
        const { step1, step2, step3 } = state.selections;
        
        if (typeof window.addToCart === 'function' && typeof window.openCartView === 'function') {
            if (step1 && step1.length > 0) {
                step1.forEach(p => {
                    const productNameWithFormat = `${p.product} (${state.format})`;
                    if (p.price) window.addToCart(productNameWithFormat, p.price, p.image);
                });
            }
            if (step2 && step2.price) {
                window.addToCart(step2.product, step2.price, step2.image);
            }
            if (step3 && step3.id !== 'no' && step3.price) {
                window.addToCart(step3.product, step3.price, step3.image);
            }
            window.openCartView();
        } else {
            alert("El carrito no está inicializado. Asegúrate de tener el carrito funcionando.");
        }
    },
    submitPersonalData: () => {
        const nameEl = document.getElementById('alquimia-name');
        const dobEl = document.getElementById('alquimia-dob');
        if(nameEl && nameEl.value && dobEl && dobEl.value) {
            state.name = nameEl.value;
            state.dob = dobEl.value;
            setView('format');
        } else {
            alert("Por favor ingresa tu nombre y fecha de nacimiento.");
        }
    },
    selectFormat: (format) => {
        state.format = format;
        setView('quiz');
    },
    setView: setView,
    selectValue: selectValue,
    handlePrev: handlePrev,
    resetApp: resetApp,
    getWhatsAppUrl: getWhatsAppUrl
};

function resetApp() {
    state = {
        view: 'intro',
        name: '',
        dob: '',
        format: null,
        quizIdx: 0,
        answers: [],
        selections: { step1: [], step2: null, step3: null }
    };
    render();
}

function getWhatsAppUrl() {
    const { step1, step2, step3 } = state.selections;
    
    let text = "✨ *Hola Botica Silvestre, este es mi Ritual de Reconexión:*\n\n";
    
    if (step1 && step1.length > 0) {
        text += "🌿 *Tintura Ideal:*\n";
        step1.forEach(p => {
            text += `- ${p.product} (${state.format})\n`;
        });
        text += "\n";
    }
    
    if (step2) {
        text += "🤲 *Conexión Corporal:*\n";
        text += `- ${step2.product}\n\n`;
    }
    
    if (step3) {
        text += "🪄 *Sellado Energético:*\n";
        text += `- ${step3.product}\n\n`;
    }
    
    text += "Me gustaría recibir más información para adquirir mi ritual.";
    
    // Replace with the actual Botica Silvestre WhatsApp number (including country code, e.g. 521 for MX)
    const phone = "523314199842"; 
    return `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
}

function render() {
    const wrapper = document.getElementById('soulshine-test-wrapper');
    if (!wrapper) return;

    let html = '';

    if (state.view === 'intro') {
        html = `
            <div class="view-intro view-active">
                <div class="intro-divider"></div>
                <h1 class="hero-title" style="font-weight: 300; font-size: clamp(3rem, 6vw, 4.5rem); letter-spacing: -0.02em; margin-bottom: 1rem;">Regresa a tu esencia</h1>
                <p class="intro-subtitle font-sans">Un diálogo entre tu alma y la energía sagrada de la tierra.</p>
                <div class="alquimia-controls">
                    <button onclick="window.alquimia.setView('personalData')" class="btn btn-primary btn-large" style="display:inline-flex; align-items:center; gap:0.5rem;">
                        <span>Iniciar Introspección</span>
                        <i data-lucide="chevron-right" style="width:18px;height:18px;"></i>
                    </button>
                </div>
            </div>
        `;
    } 
    else if (state.view === 'personalData') {
        html = `
            <div class="view-intro view-active">
                <div class="intro-divider"></div>
                <h2 class="quiz-question-text font-serif">Para comenzar, cuéntanos de ti</h2>
                <div style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <div style="margin-bottom: 1.5rem;">
                        <label class="quiz-input-label">Tu nombre</label>
                        <input type="text" id="alquimia-name" placeholder="Ej. Pablo" value="${state.name}" class="quiz-input">
                    </div>
                    <div style="margin-bottom: 2rem;">
                        <label class="quiz-input-label">Tu fecha de nacimiento</label>
                        <input type="date" id="alquimia-dob" value="${state.dob}" class="quiz-input">
                    </div>
                </div>
                <div class="alquimia-controls" style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button onclick="window.alquimia.handlePrev()" class="btn btn-quiz-outline btn-large">
                        <i data-lucide="chevron-left" style="width:18px;height:18px;"></i>
                        <span>Volver</span>
                    </button>
                    <button onclick="window.alquimia.submitPersonalData()" class="btn btn-quiz-primary btn-large">
                        <span>Siguiente</span>
                        <i data-lucide="chevron-right" style="width:18px;height:18px;"></i>
                    </button>
                </div>
            </div>
        `;
    }
    else if (state.view === 'format') {
        html = `
            <div class="view-quiz view-active">
                <span class="quiz-step-label">Preparación</span>
                <h2 class="quiz-question-text font-serif">¿Qué nivel de intensidad buscas en tu proceso?</h2>
                
                <div class="options-grid" style="display: grid; grid-template-columns: 1fr; gap: 1rem; max-width: 500px; margin: 2rem auto;">
                    <button class="option-btn" onclick="window.alquimia.selectFormat('Tintura')">
                        <h4>Mayor intensidad (Tintura)</h4>
                        <p>Resultados más directos y rápidos. Extracción alcohólica pura.</p>
                    </button>
                    <button class="option-btn" onclick="window.alquimia.selectFormat('Oleato')">
                        <h4>Más suave (Oleato)</h4>
                        <p>Un proceso más gentil y paulatino. Extracción sin alcohol (base aceite).</p>
                    </button>
                </div>
                <div class="alquimia-controls" style="margin-top: 2rem;">
                    <button onclick="window.alquimia.handlePrev()" class="btn btn-quiz-outline btn-large">
                        <i data-lucide="chevron-left" style="width:18px;height:18px;"></i>
                        <span>Volver</span>
                    </button>
                </div>
            </div>
        `;
    }
    else if (state.view === 'quiz') {
        const q = QUIZ_QUESTIONS[state.quizIdx];
        
        html = `
            <div class="view-quiz view-active">
                <span class="quiz-step-label">Sintonización ${state.quizIdx + 1}/10</span>
                <h2 class="quiz-question-text font-serif">${q.text}</h2>

                <div class="scale-buttons-container">
                    <button class="scale-btn" onclick="window.alquimia.selectValue(1)">1</button>
                    <button class="scale-btn" onclick="window.alquimia.selectValue(2)">2</button>
                    <button class="scale-btn" onclick="window.alquimia.selectValue(3)">3</button>
                    <button class="scale-btn" onclick="window.alquimia.selectValue(4)">4</button>
                    <button class="scale-btn" onclick="window.alquimia.selectValue(5)">5</button>
                </div>
                
                <div class="scale-labels">
                    <span>${q.labelMin || 'Menos'}</span>
                    <span>${q.labelMax || 'Más'}</span>
                </div>

                <div class="alquimia-controls">
                    <button onclick="window.alquimia.handlePrev()" class="btn btn-quiz-outline" style="font-size: 0.9rem; padding: 0.75rem 2rem;">
                        <i data-lucide="chevron-left" style="width:16px;height:16px;"></i>
                        <span>Volver</span>
                    </button>
                </div>
            </div>
        `;
    }
    else if (state.view === 'step2') {
        let cardsHtml = PRODUCTS_DB.step2.map(opt => `
            <button class="card-btn" onclick="window.alquimia.handleManualSelection('step2', '${opt.id}')">
                <div class="card-icon"><i data-lucide="${opt.icon}"></i></div>
                <p class="card-desc">${opt.desc}</p>
            </button>
        `).join('');

        html = `
            <div class="view-step2 view-active">
                <span class="quiz-step-label">Conexión Corporal</span>
                <h2 class="step3-title font-serif">¿Qué es lo que más necesita tu cuerpo?</h2>
                <div class="grid-cards">
                    ${cardsHtml}
                </div>
                
                <div class="alquimia-controls" style="margin-top: 4rem;">
                    <button onclick="window.alquimia.handlePrev()" class="btn btn-quiz-outline" style="font-size: 0.9rem; padding: 0.75rem 2rem;">
                        <i data-lucide="chevron-left" style="width:16px;height:16px;"></i>
                        <span>Volver</span>
                    </button>
                </div>
            </div>
        `;
    }
    else if (state.view === 'step3') {
        let cardsHtml = PRODUCTS_DB.step3.map(opt => `
            <button class="card-btn" onclick="window.alquimia.handleManualSelection('step3', '${opt.id}')">
                <div class="card-icon"><i data-lucide="${opt.icon}"></i></div>
                <h4 class="card-title">${opt.product}</h4>
                <div class="card-subtitle">${opt.subtitle}</div>
                <p class="card-desc">${opt.desc}</p>
            </button>
        `).join('');

        html = `
            <div class="view-step3 view-active">
                <span class="quiz-step-label">Sello del Ritual</span>
                <h2 class="step3-title font-serif">¿Deseas armonizar energéticamente tu espacio físico para sellar el ritual?</h2>
                
                <div class="grid-cards-2">
                    ${cardsHtml}
                </div>
                
                <div class="alquimia-controls" style="margin-top: 4rem;">
                    <button onclick="window.alquimia.handlePrev()" class="btn btn-quiz-outline" style="font-size: 0.9rem; padding: 0.75rem 2rem;">
                        <i data-lucide="chevron-left" style="width:16px;height:16px;"></i>
                        <span>Volver</span>
                    </button>
                </div>
            </div>
        `;
    }
    else if (state.view === 'result') {
        const { step1, step2, step3 } = state.selections;
        const numerologyText = getNumerologyMessage(state.dob, state.name);
        
        let step1Html = '';
        if (step1 && step1.length > 0) {
            step1.forEach(p => {
                step1Html += `
                    <div class="result-item-content">
                        <div>
                            <h3 class="result-item-title font-serif">${p.product}</h3>
                            <div class="result-item-subtitle">Formato: ${state.format || 'Tintura'}</div>
                            <p class="result-item-desc">${p.desc}</p>
                        </div>
                        <i data-lucide="check" class="result-check-icon"></i>
                    </div>
                `;
            });
        }

        let itemsHtml = `
            <div class="result-item">
                <span class="result-item-label">Tintura Ideal</span>
                ${step1Html}
            </div>
            <div class="result-item">
                <span class="result-item-label">Conexión Corporal</span>
                <div class="result-item-content">
                    <div>
                        <h3 class="result-item-title font-serif">${step2.product}</h3>
                        <div class="result-item-subtitle">${step2.subtitle}</div>
                        <p class="result-item-desc">${step2.desc}</p>
                    </div>
                    <i data-lucide="check" class="result-check-icon"></i>
                </div>
            </div>
        `;

        if (step3) {
            itemsHtml += `
            <div class="result-item">
                <span class="result-item-label">Sellado Energético</span>
                <div class="result-item-content">
                    <div>
                        <h3 class="result-item-title font-serif">${step3.product}</h3>
                        <p class="result-item-desc">${step3.desc}</p>
                    </div>
                    <i data-lucide="check" class="result-check-icon"></i>
                </div>
            </div>
            `;
        }

        let age = 0;
        if (state.dob) {
            const birthDate = new Date(state.dob);
            const today = new Date();
            age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
        }
        const isMinor = age > 0 && age < 18;

        if (isMinor) {
            // Hide floating WhatsApp button for minors
            setTimeout(() => {
                const waFloat = document.querySelector('.whatsapp-float');
                if (waFloat) waFloat.style.display = 'none';
            }, 0);

            html = `
                <div class="view-result view-active">
                    <div class="result-card">
                        <div class="result-card-top-line"></div>
                        
                        <header class="result-header">
                            <h1 class="result-title font-serif">Tu Mensaje</h1>
                            <p class="result-subtitle">Botica Silvestre</p>
                        </header>

                        ${numerologyText ? `
                        <div class="result-message">
                            <p>"${numerologyText}"</p>
                        </div>
                        ` : ''}
                        
                        <div class="result-footer" style="border-top: none; padding-top: 1rem;">
                            <p class="result-footer-quote">Escucha a tu cuerpo, él guarda toda la sabiduría.</p>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html = `
                <div class="view-result view-active">
                    <div class="result-card">
                        <div class="result-card-top-line"></div>
                        
                        <header class="result-header">
                            <h1 class="result-title font-serif">Tu Ritual de Reconexión</h1>
                            <p class="result-subtitle">Botica Silvestre</p>
                        </header>

                        ${numerologyText ? `
                        <div class="result-message">
                            <p>"${numerologyText}"</p>
                        </div>
                        ` : ''}

                        <div class="result-list">
                            ${itemsHtml}
                        </div>

                        <div class="result-footer">
                            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; flex-direction: column; align-items: center;">
                                <button onclick="window.alquimia.addRitualToCart()" class="btn btn-quiz-primary btn-large" style="width: 100%; max-width: 350px; justify-content: center;">
                                    <i data-lucide="shopping-cart" style="width:18px;height:18px;"></i>
                                    <span>Añadir mi ritual al carrito</span>
                                </button>
                                <a href="botica.html" class="btn btn-quiz-outline btn-large" style="width: 100%; max-width: 350px; justify-content: center;">
                                    <i data-lucide="compass" style="width:18px;height:18px;"></i>
                                    <span>Descubrir la botica</span>
                                </a>
                                <a href="${getWhatsAppUrl()}" target="_blank" class="btn btn-quiz-outline btn-large" style="width: 100%; max-width: 350px; justify-content: center; color: #25D366; border-color: rgba(37, 211, 102, 0.5);">
                                    <i data-lucide="message-circle" style="width:18px;height:18px;"></i>
                                    <span>Consulta por WhatsApp</span>
                                </a>
                            </div>
                            <div class="result-divider"></div>
                            <p class="result-footer-quote">Escucha a tu cuerpo, él guarda toda la sabiduría.</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    wrapper.innerHTML = `<div class="ritual-wrapper">${html}</div>`;

    if (window.lucide) {
        window.lucide.createIcons();
    }
}

