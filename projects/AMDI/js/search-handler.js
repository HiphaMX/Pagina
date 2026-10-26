document.addEventListener('DOMContentLoaded', function() {
    console.log("AMDI Search Handler Initialized.");
    
    // Comprehensive index of AMDI pages, projects, and blog articles
    var siteIndex = [
    {
        "title": "Inicio - Adriana Medina Diseño Interior",
        "url": "./",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Firma de diseño y arquitectura de interiores en Guadalajara y CDMX. Especialistas en interiorismo residencial y comercial de alta gama.",
        "keywords": "amdi inicio adriana medina diseño de interiores arquitectura guadalajara cdmx"
    },
    {
        "title": "Nosotros - Adriana Medina Diseño Interior",
        "url": "nosotros",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Conoce la visión y el equipo detrás de AMDI. Más de una década creando espacios únicos, atemporales y funcionales.",
        "keywords": "nosotros equipo adriana medina trayectoria historia valores interioristas"
    },
    {
        "title": "Servicios de Interiorismo Integral",
        "url": "servicios",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Servicios integrales desde el concepto, renderizado 3D y planos ejecutivos hasta la ejecución, supervisión de obra y estilismo.",
        "keywords": "servicios concepto propuesta ejecucion supervision proyectos integrales 3d planos"
    },
    {
        "title": "Diseño Residencial de Lujo",
        "url": "residencial",
        "image": "images/688bbb9c62901a9dcbbecf35_Capa_203.jpg",
        "desc": "Proyectos residenciales personalizados: salas, recámaras, comedores y áreas comunes con la máxima atención al detalle y acabados.",
        "keywords": "diseno residencial casas residencias departamentos salas recamaras lujo"
    },
    {
        "title": "Merchandising y Espacios Comerciales",
        "url": "merchandising",
        "image": "images/6700335859ea5fa35e5eb046_Plomeri_CC_81a_20Selecta_20SLP_20Chapultepec14.jpg",
        "desc": "Diseño estratégico de exhibición comercial, salas de venta, stands de exposición y showrooms que impulsan la experiencia de marca.",
        "keywords": "merchandising comercial showrooms tiendas exhibicion stands daltile ventas"
    },
    {
        "title": "Todos los Proyectos",
        "url": "proyectos",
        "image": "images/688bbb9c62901a9dcbbecf35_Capa_203.jpg",
        "desc": "Explora nuestro portafolio de proyectos residenciales, comerciales, stands en expo obra blanca y salas de exhibición.",
        "keywords": "proyectos portafolio galeria obras residencias corporativo comercial"
    },
    {
        "title": "Blog de Tendencias e Interiorismo",
        "url": "blog",
        "image": "images/62d5cced58fd61e25dc9fbc0_62b911c113d0faf1b9b12777_i_3_adobe_express.jpg",
        "desc": "Artículos, inspiración, tendencias de color, iluminación, materiales y recomendaciones de diseño de interiores de AMDI.",
        "keywords": "blog articulos noticias tendencias inspiracion pantone iluminacion interiorismo"
    },
    {
        "title": "Contáctanos",
        "url": "contacto",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Agenda una cita o solicita una cotización con el equipo de AMDI para comenzar tu próximo proyecto de diseño de interiores.",
        "keywords": "contacto cotizacion cita mensaje telefono correo direccion ubicacion presupuesto"
    },
    {
        "title": "Preguntas Frecuentes",
        "url": "preguntas-frecuentes",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Respuestas a las dudas más comunes sobre tiempos de entrega, etapas del proyecto, honorarios, presupuestos y metodología de AMDI.",
        "keywords": "preguntas frecuentes dudas faq metodologia etapas costos presupuesto cotizacion"
    },
    {
        "title": "Aviso de Privacidad",
        "url": "aviso-de-privacidad",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Consulta las políticas de privacidad y protección de datos personales de Adriana Medina Diseño Interior (AMDI).",
        "keywords": "aviso de privacidad datos politicas arco derechos"
    },
    {
        "title": "Términos y Condiciones",
        "url": "terminos-y-condiciones",
        "image": "images/62cdc1c03a88a6044b6f421f_URL.webp",
        "desc": "Términos, condiciones y lineamientos legales aplicables al uso del sitio web y servicios de AMDI.",
        "keywords": "terminos y condiciones legales contrato politicas"
    },
    {
        "title": "Residencia Antares, áreas comunes",
        "url": "proyectos/residencia-antares-areas-comunes",
        "image": "images/688bbb9c62901a9dcbbecf35_Capa_203.jpg",
        "desc": "Proyecto integral de diseño interior y mobiliario para las áreas sociales y comunes de Residencia Antares.",
        "keywords": "antares residencial sala comedor recepcion acabados lujo"
    },
    {
        "title": "Residencia Jesús María, áreas comunes",
        "url": "proyectos/residencia-jesus-maria-areas-comunes",
        "image": "images/62d5f0a4bd7e24ae2e26f11b_6111885b2fb8ec3fb7ce3aa7_Capa_209_20copia.jpg",
        "desc": "Diseño de interiores que conjuga armonía, calidez y sofisticación en recibidor, sala y comedor de Residencia Jesús María.",
        "keywords": "jesus maria areas comunes sala comedor residencial"
    },
    {
        "title": "Residencia Jesús María, cocina",
        "url": "proyectos/residencia-jesus-maria-cocina",
        "image": "images/62d5ec9dfe91cc85594e0dc4_61119a4d673831f947751cc7_Capa_207_20copia.jpg",
        "desc": "Cocina moderna de alto rendimiento con acabados de primera, isla central y almacenamiento optimizado.",
        "keywords": "jesus maria cocina isla mobiliario residencial acabados granito"
    },
    {
        "title": "Residencia Jesús María, habitación principal",
        "url": "proyectos/residencia-jesus-maria-habitacion-principal",
        "image": "images/62d5eb64173c0b166d1215b3_61119bb8547a80bf9b5620ac_Capa_2011_20copia.jpg",
        "desc": "Recámara principal diseñada para el máximo confort y descanso, con iluminación indirecta y texturas cálidas.",
        "keywords": "jesus maria habitacion recamara principal suite master"
    },
    {
        "title": "Residencia Jesús María, habitación Harry Potter",
        "url": "proyectos/residencia-jesus-maria-habitacion-harry-potter",
        "image": "images/62d5ef99fe91cca5b34e2ea8_611195b3b2af0b7ffbd225c9_Capa_2014_20copia.jpg",
        "desc": "Habitación temática infantil y juvenil inspirada en el universo de Harry Potter con elementos personalizados.",
        "keywords": "jesus maria harry potter tematica ninos juvenil habitacion"
    },
    {
        "title": "Residencia Jesús María, habitación music fan",
        "url": "proyectos/residencia-jesus-maria-habitacion-music-fan",
        "image": "images/62d5ed9b4b10a21d98ab36ef_61119896efa64218f5e107aa_Capa_2012_20copia.jpg",
        "desc": "Recámara juvenil para amantes de la música con acústica, espacio de instrumentos y diseño contemporáneo.",
        "keywords": "jesus maria music fan musica habitacion juvenil"
    },
    {
        "title": "Residencia Los Frailes, habitación principal",
        "url": "proyectos/residencia-los-frailes-habitacion-principal",
        "image": "images/62d5e4598a2ed9612944cbba_6111a60f2e069572928733e6_Capa_203_20copia.jpg",
        "desc": "Espacio íntimo, sofisticado y confortable desarrollado para la recámara principal de la Residencia Los Frailes.",
        "keywords": "los frailes habitacion principal recamara suite residencial"
    },
    {
        "title": "Residencia Firenzze, habitación principal",
        "url": "proyectos/residencia-firenzze-habitacion-principal",
        "image": "images/62d5ea77bb66bef2e3f1ec69_61119d5044576cdcad9d67cf_Capa_205_20copia.jpg",
        "desc": "Diseño de suite principal con paleta neutral refinada, carpintería a medida y vestidor.",
        "keywords": "firenzze habitacion principal recamara suite vestidor"
    },
    {
        "title": "Residencia Firenzze, habitación bebé",
        "url": "proyectos/residencia-firenzze-habitacion-bebe",
        "image": "images/62d5e90da5a70179b8a12e0f_61119eba72cbc7d7dec3442d_Capa_206_20copia.jpg",
        "desc": "Habitación infantil diseñada para recién nacido, combinando calidez, seguridad, funcionalidad y estilo.",
        "keywords": "firenzze habitacion bebe ninos cuna infantil"
    },
    {
        "title": "Residencia Vistas de la Catedral, habitación principal",
        "url": "proyectos/residencia-vistas-de-la-catedral-habitacion-principal",
        "image": "images/62d5e368173c0b25a011a06b_6111a7d8fc8b6b01b00e561e_Capa_201_20copia.jpg",
        "desc": "Recámara principal con vista panorámica, diseño elegante y equilibrio entre modernidad y confort.",
        "keywords": "vistas de la catedral habitacion principal recamara suite"
    },
    {
        "title": "Sala Daltile, Plomería Selecta sucursal Chapultepec",
        "url": "proyectos/sala-daltile-plomeria-selecta-sucursal-chapultepec",
        "image": "images/6700335859ea5fa35e5eb046_Plomeri_CC_81a_20Selecta_20SLP_20Chapultepec14.jpg",
        "desc": "Showroom comercial y sala de exhibición de recubrimientos cerámicos Daltile en San Luis Potosí.",
        "keywords": "daltile plomeria selecta chapultepec san luis potosi slp showroom exhibicion"
    },
    {
        "title": "Sala Daltile, Plomería Selecta sucursal Santos Degollado",
        "url": "proyectos/sala-daltile-plomeria-selecta-sucursal-santos-degollado",
        "image": "images/67003c7250ad7eed40cfeeff_Plomeria_20Selecta_20SLP_20Santos_20Degollado-31.jpg",
        "desc": "Exhibición integral de acabados y pisos Daltile en Plomería Selecta sucursal Santos Degollado.",
        "keywords": "daltile plomeria selecta santos degollado slp showroom exhibicion"
    },
    {
        "title": "Sala Daltile, sucursal DAM Home",
        "url": "proyectos/sala-daltile-sucursal-dam-home",
        "image": "images/6531773927b38c2303a477a3_DAM_20Home_20Tepic_20-_20Septiembre_202023-37.webp",
        "desc": "Diseño de showroom de acabados Daltile en DAM Home Tepic con áreas dinámicas de exhibición.",
        "keywords": "daltile dam home tepic showroom exhibicion acabados"
    },
    {
        "title": "Sala Daltile, sucursal DAM Mezcales",
        "url": "proyectos/sala-daltile-sucursal-dam-mezcales",
        "image": "images/62d5ded2524073eb42d45321_6111cd90e9c4653f06eff156_thumbnail_20mezcales.jpg",
        "desc": "Sala de exhibición comercial para recubrimientos Daltile en DAM Mezcales, Nayarit.",
        "keywords": "daltile dam mezcales nayarit showroom exhibicion"
    },
    {
        "title": "Sala Daltile, sucursal Plomería y Cerámica de Querétaro",
        "url": "proyectos/sala-daltile-sucursal-plomeria-y-ceramica-de-queretaro",
        "image": "images/6353eb335ee93e976189f251_Capa_204.jpg",
        "desc": "Showroom y sala de exhibición comercial de cerámicas Daltile en Querétaro.",
        "keywords": "daltile plomeria ceramica queretaro showroom exhibicion"
    },
    {
        "title": "Sala Daltile, sucursal DAM López Mateos",
        "url": "proyectos/sala-de-exhibicion-daltile-sucursal-dam-lopez-mateos",
        "image": "images/62d5cfbf3667e4d3759ecb80_6268253abe39c62f741f0dcd_thumbnail-AM.jpg",
        "desc": "Sala de exhibición Daltile en Guadalajara (DAM López Mateos) con ambientaciones reales.",
        "keywords": "daltile dam lopez mateos guadalajara showroom exhibicion"
    },
    {
        "title": "Expo Obra Blanca 2023, CDMX",
        "url": "proyectos/expo-obra-blanca-2023-cdmx",
        "image": "images/653027846b8d226e02aac306_Capa_208.webp",
        "desc": "Stand conceptual de vanguardia diseñado por AMDI para Expo Obra Blanca 2023 en Expo Santa Fe CDMX.",
        "keywords": "expo obra blanca 2023 cdmx stand arquitectura exhibicion"
    },
    {
        "title": "Expo Obra Blanca 2022, CDMX (Pabellón 1)",
        "url": "proyectos/expo-obra-blanca-2022-cdmx",
        "image": "images/63543c084f3fdf684a063498_Capa_2021.jpg",
        "desc": "Pabellón de exhibición en Expo Obra Blanca 2022 combinando geometría, iluminación y materiales innovadores.",
        "keywords": "expo obra blanca 2022 cdmx stand pabellon"
    },
    {
        "title": "Expo Obra Blanca 2022, CDMX (Pabellón 2)",
        "url": "proyectos/expo-obra-blanca-2022-cdmx-2",
        "image": "images/63543d1ba7b90c8b79bc7ec7_Capa_2030.jpg",
        "desc": "Segunda propuesta espacial para Expo Obra Blanca 2022 enfocada en experiencia inmersiva y textura.",
        "keywords": "expo obra blanca 2022 cdmx stand pabellon"
    },
    {
        "title": "Expo Obra Blanca 2021, CDMX (Edición 1)",
        "url": "proyectos/expo-obra-blanca-2021-cdmx",
        "image": "images/62d5d5bfbd7e2480ee252c2c_6166ea08efe5380ee1960bcb_Featured_20Imagen_20OBE01.jpg",
        "desc": "Diseño de stand experiencial en Expo Obra Blanca 2021 destacando formatos arquitectónicos.",
        "keywords": "expo obra blanca 2021 cdmx stand diseño"
    },
    {
        "title": "Expo Obra Blanca 2021, CDMX (Edición 2)",
        "url": "proyectos/expo-obra-blanca-2021-cdmx-2",
        "image": "images/62d5d2613f86ae065a92de50_6166ef2ba3ab7021ee4269e9_thumbnail_20OBE02.jpg",
        "desc": "Espacio de exposición en Expo Obra Blanca 2021 con interacción de luces y texturas continuas.",
        "keywords": "expo obra blanca 2021 cdmx stand diseño"
    },
    {
        "title": "Luz natural y artificial: el equilibrio perfecto",
        "url": "blog/luz-natural-y-artificial-el-equilibrio-perfecto",
        "image": "images/62d5cced58fd61e25dc9fbc0_62b911c113d0faf1b9b12777_i_3_adobe_express.jpg",
        "desc": "Cómo lograr la armonía lumínica ideal para tus espacios interiores, combinando luz de día con iluminación decorativa y funcional.",
        "keywords": "luz natural artificial iluminacion lamparas equilibrio ventanales calidez"
    },
    {
        "title": "Refleja tu personalidad en tu hogar",
        "url": "blog/refleja-tu-personalidad-en-tu-hogar",
        "image": "images/62d5cc725e9cd440c621c52f_62b8d3eac1ecc091ad95cc36_Mi_20proyecto_20_4_.jpg",
        "desc": "Tu hogar es tu santuario. Te contamos cómo plasmar tu esencia, gustos y estilo de vida en cada rincón de tu casa.",
        "keywords": "personalidad hogar santuario estilo muebles decoracion interiores"
    },
    {
        "title": "Trojena, un destino futurista",
        "url": "blog/trojena-un-destino-futurista",
        "image": "images/62fad6c92ab1e75460b352c6_62fad23fa2f45450feeee581_Capa_206.webp",
        "desc": "Descubre Trojena, el ambicioso proyecto urbano y turístico de montaña en Arabia Saudita que redefine el diseño vanguardista.",
        "keywords": "trojena futurista arabia saudita neom arquitectura vanguardia montanas"
    },
    {
        "title": "Viva Magenta, 2023 ya tiene color",
        "url": "blog/viva-magenta-2023-ya-tiene-color",
        "image": "images/639779a9e9db48b96644c1c6_Capa_206.jpg",
        "desc": "El color del año de Pantone: una propuesta vibrante que inyecta fuerza, dinamismo y optimismo al diseño de interiores.",
        "keywords": "viva magenta pantone color del ano tendencias interiorismo dinamismo"
    },
    {
        "title": "Grecia está de regreso",
        "url": "blog/grecia-esta-de-regreso",
        "image": "images/62d5cb58bd7e24293524a5d4_629d6f1270a3b2d241e5ae72_Mi_20proyecto_20_3_.jpg",
        "desc": "La influencia de la arquitectura y la estética clásica griega en las tendencias modernas de interiorismo.",
        "keywords": "grecia clasico columnas estetica mediterraneo tendencias"
    },
    {
        "title": "La realidad virtual llegó para revolucionar",
        "url": "blog/la-realidad-virtual-llego-para-revolucionar",
        "image": "images/62d5cbf24b10a21af0a915b2_629d7b71db408130127b353c_rv_4_adobe_express.jpg",
        "desc": "Cómo la tecnología de realidad virtual y visualización 3D transforma la forma de concebir y experimentar proyectos de interiorismo.",
        "keywords": "realidad virtual vr 3d render tecnologica arquitectura diseno"
    },
    {
        "title": "En 2021, sembramos esperanza",
        "url": "blog/en-2021-sembramos-esperanza",
        "image": "images/62d5c8b78a2ed99719433348_61c218ce8a6c4f639a9195ba_Sembrar_20esperanza.jpg",
        "desc": "Nuestra retrospectiva de proyectos y aprendizajes durante un año retador pero lleno de creatividad.",
        "keywords": "2021 sembramos esperanza retrospectiva proyectos amdi"
    },
    {
        "title": "Very Peri: Así es el color del 2022",
        "url": "blog/very-peri-asi-es-el-color-del-2022",
        "image": "images/62d5caee5e8aa4408c288d0c_61b3ec51b21347172ac4d374_cover_adobespark_20_1_.jpg",
        "desc": "Análisis y aplicación del tono Very Peri de Pantone en la decoración de recámaras, salas y áreas comunes.",
        "keywords": "very peri pantone 2022 color morado lavanda decoracion"
    },
    {
        "title": "Diseño de interiores, 7 momentos clave de un proyecto",
        "url": "blog/diseno-de-interiores-7-momentos-clave-de-un-proyecto",
        "image": "images/62d5c7144e05a0c422bc78b0_61479d8a72766fc509af1ec7_Featured.jpg",
        "desc": "Las fases indispensables para llevar a cabo una obra de interiorismo exitosa, desde el boceto inicial hasta la entrega final.",
        "keywords": "7 momentos clave fases etapas proceso diseno interiores proyecto obra"
    },
    {
        "title": "Nuestra nueva piel, la evolución de un concepto",
        "url": "blog/nuestra-nueva-piel-la-evolucion-de-un-concepto",
        "image": "images/62d5c9bf3f86ae7c5a927827_6262e693111fd4664fd34017_Main.jpg",
        "desc": "La evolución de la identidad de AMDI: madurez, sofisticación y nuevos horizontes creativos en arquitectura interior.",
        "keywords": "nueva piel evolucion marca identidad concepto adriana medina"
    },
    {
        "title": "El diseño es la respuesta, Design Week 2021",
        "url": "blog/el-diseno-es-la-respuesta-design-week-2021",
        "image": "images/62d5c836519fef6bbc2df8a9_617eccb58164cc102afdb2b0_FeaturedDesignweek.jpg",
        "desc": "Reflexiones y vivencias de AMDI en Design Week México 2021: innovación, materiales sustentables y creatividad.",
        "keywords": "design week mexico 2021 dwm eventos diseno exposicion"
    },
    {
        "title": "Tu oficina ya no volverá a ser igual",
        "url": "blog/tu-oficina-ya-no-volvera-a-ser-igual",
        "image": "images/62d5c66b189a039df28def08_613c627eee7de44820a27ba5_Fondo.jpg",
        "desc": "Diseño de espacios de trabajo contemporáneos: bienestar, flexibilidad y ergonomía en el entorno laboral.",
        "keywords": "oficina corporativo espacios de trabajo coworking ergonomia bienestar"
    }
];
    
    function normalize(str) {
        return (str || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[̀-ͯ]/g, '')
            .trim();
    }
    
    function escapeHtml(str) {
        return (str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
    
    var container = document.querySelector('.search-result-items');
    var heading = document.querySelector('.search-results-heading') || document.querySelector('h1.heading');
    
    function executeSearch(query, updateUrl) {
        var cleanQuery = normalize(query);
        
        // Sync all search inputs across the page
        var searchInputs = document.querySelectorAll('input[type="search"], input[name="query"], #search');
        searchInputs.forEach(function(input) {
            if (input.value !== query) {
                input.value = query;
            }
        });
        
        if (updateUrl && window.history && window.history.replaceState) {
            var newUrl = window.location.pathname + (query ? '?query=' + encodeURIComponent(query) : '');
            window.history.replaceState(null, '', newUrl);
        }
        
        if (!container) return;
        container.innerHTML = '';
        
        if (!cleanQuery) {
            if (heading) heading.textContent = 'Resultados';
            container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: #64748b; font-size: 1.05em;">Ingresa un término de búsqueda para comenzar.</div>';
            return;
        }
        
        var queryTokens = cleanQuery.split(/\s+/).filter(Boolean);
        var matches = siteIndex.filter(function(item) {
            var haystack = normalize(item.title + ' ' + item.desc + ' ' + (item.keywords || '') + ' ' + item.url);
            return queryTokens.every(function(token) {
                return haystack.indexOf(token) !== -1;
            });
        });
        
        if (heading) {
            heading.innerHTML = 'Resultados <span style="font-size: 0.6em; font-weight: 400; color: #64748b;">(' + matches.length + ' para "' + escapeHtml(query) + '")</span>';
        }
        
        if (matches.length === 0) {
            container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: #64748b; font-size: 1.05em;">No se encontraron resultados para "' + escapeHtml(query) + '".<br><span style="font-size: 0.9em; color: #94a3b8; display: inline-block; margin-top: 8px;">Intenta con palabras como "residencial", "cocina", "daltile", "luz" o "obra blanca".</span></div>';
            return;
        }
        
        matches.forEach(function(item) {
            var card = document.createElement('div');
            card.className = 'grid-vertical grid-border';
            card.innerHTML = 
                '<a href="' + item.url + '" class="article-link al-flex w-inline-block" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-radius: 8px;">' +
                '  <div>' +
                '    <div class="article-image" style="height: 180px; overflow: hidden; position: relative; border-radius: 6px; background: #000000;">' +
                '      <img alt="' + escapeHtml(item.title) + '" loading="lazy" src="' + item.image + '" class="cover-image" style="width: 100%; height: 100%; object-fit: cover;"/>' +
                '    </div>' +
                '    <p class="post-title in-search" style="font-size: 1.15em; font-weight: 600; margin-top: 14px; margin-bottom: 6px; color: #000000; line-height: 1.3;">' + escapeHtml(item.title) + '</p>' +
                '    <div class="paragraph in-search" style="font-size: 0.8em; color: #64748b; margin-bottom: 8px;">amdi.mx/' + item.url + '</div>' +
                '    <p style="font-size: 13px; line-height: 1.5; margin: 0 0 16px 0; color: #475569;">' + escapeHtml(item.desc) + '</p>' +
                '  </div>' +
                '  <p class="link-paragraph" style="margin-top: auto; font-weight: 600; color: #000000;">Ver más</p>' +
                '</a>';
            container.appendChild(card);
        });
    }
    
    // Parse query parameter on load
    var params = new URLSearchParams(window.location.search);
    var initialQuery = params.get('query') || '';
    executeSearch(initialQuery, false);
    
    // Live search input handling on search.html
    var pageInput = document.querySelector('.search-input-page');
    if (pageInput) {
        pageInput.addEventListener('input', function(e) {
            executeSearch(e.target.value, true);
        });
    }
    
    // Prevent reload on search form submissions if already on /search
    var searchForms = document.querySelectorAll('form.search, form.search-form');
    searchForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (window.location.pathname.indexOf('search') !== -1) {
                var input = form.querySelector('input[type="search"], input[name="query"], #search');
                if (input) {
                    e.preventDefault();
                    executeSearch(input.value, true);
                }
            }
        });
    });
});
