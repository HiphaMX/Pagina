document.addEventListener('DOMContentLoaded', function() {
    console.log("AMDI Search Handler Initialized.");
    
    // Simple index of AMDI pages for search matching
    var siteIndex = [
        {
            title: "Luz natural y artificial: el equilibrio perfecto",
            url: "blog/luz-natural-y-artificial-el-equilibrio-perfecto",
            image: "images/62d5cced58fd61e25dc9fbc0_62b911c113d0faf1b9b12777_i_3_adobe_express.jpg",
            desc: "Cómo lograr la armonía lumínica ideal para tus espacios interiores, combinando luz de día con iluminación decorativa y funcional."
        },
        {
            title: "Refleja tu personalidad en tu hogar",
            url: "blog/refleja-tu-personalidad-en-tu-hogar",
            image: "images/62d5cc725e9cd440c621c52f_62b8d3eac1ecc091ad95cc36_Mi_20proyecto_20_4_.jpg",
            desc: "Tu hogar es tu santuario. Te contamos cómo plasmar tu esencia, gustos y estilo de vida en cada rincón de tu casa."
        },
        {
            title: "Trojena, un destino futurista",
            url: "blog/trojena-un-destino-futurista",
            image: "images/62fad6c92ab1e75460b352c6_62fad23fa2f45450feeee581_Capa_206.webp",
            desc: "Descubre Trojena, el ambicioso proyecto urbano y turístico de montaña en Arabia Saudita que redefine el diseño vanguardista."
        },
        {
            title: "Viva Magenta, 2023 ya tiene color",
            url: "blog/viva-magenta-2023-ya-tiene-color",
            image: "images/639779a9e9db48b96644c1c6_Capa_206.jpg",
            desc: "El color del año de Pantone: una propuesta vibrante que inyecta fuerza, dinamismo y optimismo al diseño de interiores."
        },
        {
            title: "Grecia está de regreso",
            url: "blog/grecia-esta-de-regreso",
            image: "images/62d5cb58bd7e24293524a5d4_629d6f1270a3b2d241e5ae72_Mi_20proyecto_20_3_.jpg",
            desc: "La influencia de la arquitectura y la estética clásica griega en las tendencias modernas de interiorismo."
        },
        {
            title: "En 2021, sembramos esperanza",
            url: "blog/en-2021-sembramos-esperanza",
            image: "images/62d5c8b78a2ed99719433348_61c218ce8a6c4f639a9195ba_Sembrar_20esperanza.jpg",
            desc: "Nuestra retrospectiva de proyectos y aprendizajes durante un año retador pero lleno de creatividad."
        },
        {
            title: "Very Peri: Así es el color del 2022",
            url: "blog/very-peri-asi-es-el-color-del-2022",
            image: "images/62d5caee5e8aa4408c288d0c_61b3ec51b21347172ac4d374_cover_adobespark_20_1_.jpg",
            desc: "Análisis y aplicación del tono Very Peri de Pantone en la decoración de recámaras, salas y áreas comunes."
        },
        {
            title: "Diseño de interiores, 7 momentos clave de un proyecto",
            url: "blog/diseno-de-interiores-7-momentos-clave-de-un-proyecto",
            image: "images/62d5c7144e05a0c422bc78b0_61479d8a72766fc509af1ec7_Featured.jpg",
            desc: "Las fases indispensables para llevar a cabo una obra de interiorismo exitosa, desde el boceto inicial hasta la entrega final."
        },
        {
            title: "Residencia Antares, áreas comunes",
            url: "proyectos/residencia-antares-areas-comunes",
            image: "images/688bbb9c62901a9dcbbecf35_Capa_203.jpg",
            desc: "Proyecto de diseño de interiores y equipamiento para las áreas comunes de la Residencia Antares."
        },
        {
            title: "Residencia Los Frailes, habitación principal",
            url: "proyectos/residencia-los-frailes-habitacion-principal",
            image: "images/62d5e4598a2ed9612944cbba_6111a60f2e069572928733e6_Capa_203_20copia.jpg",
            desc: "Espacio íntimo, sofisticado y confortable desarrollado para la recámara principal de la Residencia Los Frailes."
        },
        {
            title: "Residencia Jesús María, habitación principal",
            url: "proyectos/residencia-jesus-maria-habitacion-principal",
            image: "images/62d5eb64173c0b166d1215b3_61119bb8547a80bf9b5620ac_Capa_2011_20copia.jpg",
            desc: "Propuesta de estilo moderno, texturas cálidas e iluminación indirecta en recámara principal."
        },
        {
            title: "Residencia Jesús María, áreas comunes",
            url: "proyectos/residencia-jesus-maria-areas-comunes",
            image: "images/62d5f0a4bd7e24ae2e26f11b_6111885b2fb8ec3fb7ce3aa7_Capa_209_20copia.jpg",
            desc: "Proyecto integral que incluye sala de estar, comedor y recibidor unificados por un concepto de confort y amplitud."
        },
        {
            title: "Nosotros - Adriana Medina Diseño Interior",
            url: "nosotros",
            image: "images/62ccb83546527a47ccda9cbf_AMDI0.svg",
            desc: "Conoce al equipo de AMDI. Diseñamos una fórmula y reunimos el talento necesario para transformar tus ideas en proyectos factibles."
        },
        {
            title: "Servicios de Interiorismo Residencial y Comercial",
            url: "servicios",
            image: "images/62ccb83546527a47ccda9cbf_AMDI0.svg",
            desc: "Diseñamos distintos servicios que se ajustan a las necesidades de cada cliente: Concepto, Propuesta y Ejecución."
        }
    ];
    
    // Parse query parameter
    var params = new URLSearchParams(window.location.search);
    var query = params.get('query') || '';
    
    // Update inputs on the page with query value
    var searchInputs = document.querySelectorAll('input[type="search"], #search');
    searchInputs.forEach(function(input) {
        input.value = query;
    });
    
    var container = document.querySelector('.search-result-items');
    if (!container) return;
    
    // Clear static results in the container
    container.innerHTML = '';
    
    // Filter matching results
    var cleanedQuery = query.toLowerCase().trim();
    if (!cleanedQuery) {
        container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #64748b;">Ingresa un término de búsqueda para comenzar.</div>';
        return;
    }
    
    var matches = siteIndex.filter(function(item) {
        return item.title.toLowerCase().indexOf(cleanedQuery) !== -1 || 
               item.desc.toLowerCase().indexOf(cleanedQuery) !== -1;
    });
    
    // Display results
    if (matches.length === 0) {
        container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #64748b;">No se encontraron resultados para "' + query + '". Intenta con otras palabras.</div>';
        return;
    }
    
    matches.forEach(function(item) {
        var card = document.createElement('div');
        card.className = 'grid-vertical grid-border';
        
        var innerHTML = 
            '<a href="' + item.url + '" class="article-link al-flex w-inline-block">' +
            '  <div class="article-image">' +
            '    <img alt="' + item.title + '" loading="lazy" src="' + item.image + '" class="cover-image"/>' +
            '  </div>' +
            '  <p class="post-title in-search">AMDI | ' + item.title + '</p>' +
            '  <div class="paragraph in-search">www.amdi.mx/' + item.url + '</div>' +
            '  <p style="font-size: 13px; line-height: 1.5; margin: 8px 0 12px 0; color: #64748b;">' + item.desc + '</p>' +
            '  <p class="link-paragraph">Ver más</p>' +
            '</a>';
            
        card.innerHTML = innerHTML;
        container.appendChild(card);
    });
});
