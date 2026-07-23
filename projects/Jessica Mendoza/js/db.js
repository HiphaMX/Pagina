// Base de Datos Centralizada de Propiedades - Jessica Mendoza Real Estate
(function() {
    window.PROPERTIES_DB = [
        // CATEGORÍA: ZMG (Guadalajara / Zapopan / Ribera de Chapala)
        {
            id: 1,
            title: "PH Vista Hermosa - Puerta de Hierro",
            municipio: "Zapopan",
            zona: "Puerta de Hierro",
            operacion: "Renta",
            tipo: "Departamento",
            precio: 45000,
            habitaciones: 3,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Espectacular Penthouse ubicado en la zona más exclusiva de Zapopan. Con una vista panorámica impresionante de la ciudad, este departamento de tres niveles ofrece acabados de mármol importado, carpintería fina y tecnología de hogar inteligente. Disfruta de un estilo de vida de altura con total seguridad y exclusividad.",
            image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1545464693-f1798a373343?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Vista Panorámica", "Elevador Directo", "Seguridad 24/7", "Gimnasio", "Alberca Infinity", "Sala de Cine", "Salón de Eventos", "3 Estacionamientos", "Aire Acondicionado", "Concierge"]
        },
        {
            id: 2,
            title: "Casa Bosques - Valle Imperial",
            municipio: "Zapopan",
            zona: "Valle Imperial",
            operacion: "Compra",
            tipo: "Casa",
            precio: 6850000,
            habitaciones: 3,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Residencia contemporánea a estrenar dentro de coto privado en Valle Imperial. Diseñada con un concepto abierto que integra la estancia, el comedor y una cocina equipada premium con barra de cuarzo. Cuenta con jardín posterior y acabados residenciales de primer nivel en todas sus áreas.",
            image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Coto Privado", "Seguridad 24/7", "Alberca Templada", "Terraza Club", "Área de Asadores", "Jardín Privado", "Estudio / Flex Room", "Cocina Equipada", "2 Estacionamientos", "Campo de Golf Cercano"]
        },
        {
            id: 3,
            title: "Residencia de Autor - Americana",
            municipio: "Guadalajara",
            zona: "Colonia Americana",
            operacion: "Compra",
            tipo: "Casa",
            precio: 11500000,
            habitaciones: 4,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Exclusiva casa de autor en el corazón de la Colonia Americana, galardonada como una de las zonas más vibrantes para vivir. Combina techos de doble altura, tragaluces arquitectónicos que inundan de luz natural la propiedad y detalles en concreto aparente con maderas finas.",
            image: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600566752355-35792bedcfea?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687644-c7171b42498f?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Diseño Arquitectónico", "Roof Garden", "Jardín Interior", "Cocina de Autor", "Cochera Cerrada", "Bodega", "Aire Acondicionado", "Área de Lavado", "Seguridad CCTV", "Pet Friendly"]
        },
        {
            id: 4,
            title: "Villa del Bosque - Bugambilias",
            municipio: "Zapopan",
            zona: "Bugambilias",
            operacion: "Compra",
            tipo: "Casa",
            precio: 14900000,
            habitaciones: 4,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Majestuosa residencia con colindancia directa al bosque en la sección alta de Bugambilias. Cuenta con una gran terraza equipada, amplio jardín arbolado, salón de juegos y habitaciones con vestidores de doble tamaño. Ideal para familias que valoran el contacto con la naturaleza sin salir de la ciudad.",
            image: "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Jardín de 200m²", "Terraza con Asador", "Salón de Juegos", "Cochera para 4 autos", "Bodega", "Sistema de Riego", "Seguridad 24/7", "Estudio / Despacho", "Jacuzzi", "Cuarto de Servicio"]
        },
        {
            id: 5,
            title: "Loft Moderno - Providencia",
            municipio: "Guadalajara",
            zona: "Providencia",
            operacion: "Renta",
            tipo: "Departamento",
            precio: 32000,
            habitaciones: 2,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Loft de estilo industrial-chic en Providencia. Cuenta con acabados de concreto pulido, ladrillo aparente y ventanales de piso a techo que otorgan una iluminación inigualable. Ubicado a unos pasos de los mejores restaurantes y parques del norte de Guadalajara.",
            image: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Seguridad 24/7", "Lobby / Recepción", "Elevador", "2 Estacionamientos", "Roof Garden Común", "Pet Friendly", "Cocina Integral", "Balcón", "Área de Lavado", "Bicicletero"]
        },
        {
            id: 6,
            title: "Terreno Residencial - Valle Imperial",
            municipio: "Zapopan",
            zona: "Valle Imperial",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 3200000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: false,
            descripcion: "Terreno totalmente plano y regular dentro de uno de los cotos más exclusivos de Valle Imperial. Orientación privilegiada ideal para desarrollar un proyecto de residencia a la medida. El coto cuenta con servicios ocultos y casa club en funcionamiento.",
            image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Seguridad 24/7", "Servicios Ocultos", "Casa Club con Alberca", "Gimnasio", "Canchas de Tenis", "Áreas Verdes", "Orientación Norte-Sur", "Ubicación en Coto", "Vialidades de Concreto", "Campo de Golf Cercano"]
        },
        {
            id: 7,
            title: "Villa Marina - Ajijic",
            municipio: "Ajijic",
            zona: "La Floresta",
            operacion: "Compra",
            tipo: "Casa",
            precio: 8500000,
            habitaciones: 3,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Encantadora villa de un solo nivel estilo colonial mexicano en el corazón de La Floresta, Ajijic. Ofrece techos de bóveda de pañuelo, una gran terraza con vista al jardín maduro y alberca privada. A solo unos pasos del malecón y los cafés locales.",
            image: "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Alberca Privada", "Jardín Maduro", "Bóvedas de Ladrillo", "Terraza Colonial", "Estacionamiento (2 autos)", "Cocina de Talavera", "Paneles Solares", "Bodega", "Aire Acondicionado", "Ubicación Céntrica"]
        },
        {
            id: 8,
            title: "Casa del Lago - Chapala",
            municipio: "Chapala",
            zona: "Centro",
            operacion: "Compra",
            tipo: "Casa",
            precio: 5200000,
            habitaciones: 2,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Casa de descanso con excelente vista al Lago de Chapala. Ofrece estancias muy iluminadas, terraza frontal y un jardín plano. Una propiedad de fácil mantenimiento ideal para disfrutar de los fines de semana o como inversión de retiro.",
            image: "https://images.unsplash.com/photo-1602941525421-8f8b81d3edbb?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1602941525421-8f8b81d3edbb?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Vista al Lago", "Terraza Panorámica", "Jardín Plano", "Cochera para 2 autos", "Cocina Abierta", "Área de Lavado", "Seguridad Portón", "Chimenea", "Alacena Grande", "Cercana a Malecón"]
        },
        {
            id: 9,
            title: "Quinta Campestre - Jocotepec",
            municipio: "Jocotepec",
            zona: "El Chante",
            operacion: "Compra",
            tipo: "Casa",
            precio: 9800000,
            habitaciones: 4,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Hermosa quinta con 1,200 metros de terreno en El Chante, Jocotepec. Cuenta con alberca templada por celdas solares, cancha de fútbol rápido, terraza de eventos integrada al jardín y árboles frutales. Una joya para el descanso familiar y la convivencia social.",
            image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Terreno de 1,200m²", "Alberca con Celdas", "Cancha de Fútbol", "Terraza para Eventos", "Cochera (6 autos)", "Árboles Frutales", "Pozo de Agua propio", "Casa de Huéspedes", "Seguridad Bardado", "Pet Friendly"]
        },
        {
            id: 10,
            title: "Residencia Loma Alta - Guadalajara",
            municipio: "Guadalajara",
            zona: "Colinas de San Javier",
            operacion: "Compra",
            tipo: "Casa",
            precio: 24500000,
            habitaciones: 5,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Espectacular mansión clásica en Colinas de San Javier. Diseñada por un renombrado arquitecto local, destaca por sus amplios vestíbulos con pisos de mármol de Carrara, acabados de caoba sólida, biblioteca privada, cava subterránea y un enorme jardín con alberca olímpica.",
            image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Alberca Olímpica", "Biblioteca / Cava", "Cochera para 8 autos", "Jardín Majestuoso", "Acabados de Caoba", "Cuartos de Servicio (2)", "Seguridad 24/7", "Gimnasio Privado", "Sala de Cine", "Estudio"]
        },
        {
            id: 11,
            title: "Departamento Loft - Americana",
            municipio: "Guadalajara",
            zona: "Colonia Americana",
            operacion: "Renta",
            tipo: "Departamento",
            precio: 28000,
            habitaciones: 1,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Moderno loft ejecutivo completamente amueblado y equipado en la Colonia Americana. Cuenta con diseño de espacio abierto ideal para solteros o parejas, balcón privado, acabados de lujo y amenidades tipo hotel boutique en la torre.",
            image: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Amueblado Premium", "Balcón Privado", "Seguridad 24/7", "Lobby Recepción", "Elevador", "Cajón de Estacionamiento", "Alberca en Rooftop", "Gimnasio", "Sala de Juntas", "Lavandería en Torre"]
        },
        {
            id: 12,
            title: "Terreno Campestre - Jocotepec",
            municipio: "Jocotepec",
            zona: "Monte Coxala",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 4100000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: false,
            descripcion: "Terreno campestre con topografía en desniveles suaves en la exclusiva zona residencial de Monte Coxala. Ofrece vistas impactantes al lago de Chapala y acceso a las aguas termales de la zona. Ideal para el desarrollo de una propiedad de descanso y meditación.",
            image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Vista al Lago", "Acceso Aguas Termales", "Seguridad Acceso Controlado", "Servicios a pie de lote", "Vialidades Empedradas", "Clima Privilegiado", "Zonas Verdes", "Senderismo Cercano", "Orientación Óptima", "Entorno Silencioso"]
        },
        {
            id: 13,
            title: "Penthouse Horizon - Puerta de Hierro",
            municipio: "Zapopan",
            zona: "Puerta de Hierro",
            operacion: "Compra",
            tipo: "Departamento",
            precio: 18900000,
            habitaciones: 3,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Impresionante Penthouse residencial de doble altura en Puerta de Hierro. Cuenta con ventanales a 6 metros de altura, terraza espectacular que domina el skyline corporativo de Zapopan, cocina italiana de diseño importada y acabados de lujo.",
            image: "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1545464693-f1798a373343?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Doble Altura (6m)", "Terraza Panorámica", "Cocina Italiana", "3 Estacionamientos", "Seguridad 24/7", "Alberca Infinity", "Gimnasio", "Sala de Cine", "Bodega", "Aire Centralizado"]
        },
        {
            id: 14,
            title: "Garden House - Providencia",
            municipio: "Guadalajara",
            zona: "Providencia",
            operacion: "Compra",
            tipo: "Departamento",
            precio: 8400000,
            habitaciones: 3,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Garden House residencial con amplia terraza/jardín privado de 80m² en Providencia. Combina la seguridad y practicidad de un departamento con el espacio exterior y comodidad de una casa. Acabados de madera de roble, granito y mármol.",
            image: "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Jardín Privado (80m²)", "Terraza con Barra", "Seguridad 24/7", "2 Estacionamientos", "Lobby", "Elevador", "Bodega", "Área de Asador", "Pet Friendly", "Cocina con Granito"]
        },
        {
            id: 15,
            title: "Loft Industrial - Colonia Americana",
            municipio: "Guadalajara",
            zona: "Colonia Americana",
            operacion: "Compra",
            tipo: "Departamento",
            precio: 5600000,
            habitaciones: 2,
            condicion: "A estrenar",
            isPlaya: false,
            descripcion: "Loft contemporáneo de diseño industrial en la zona de mayor frescura urbana de Guadalajara. Cuenta con acabados premium, techos de concreto aparente expuestos, ventanales de piso a techo y balcón corrido a lo largo de toda la estancia.",
            image: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Estilo Industrial", "Balcón Corrido", "Seguridad 24/7", "2 Estacionamientos", "Roof Top Común", "Elevador", "Pet Friendly", "Cocina Equipada", "Bicicletero", "Bodega"]
        },
        {
            id: 16,
            title: "Luxury Flat - Puerta de Hierro",
            municipio: "Zapopan",
            zona: "Puerta de Hierro",
            operacion: "Renta",
            tipo: "Departamento",
            precio: 38000,
            habitaciones: 2,
            condicion: "Pre-propiedad",
            isPlaya: false,
            descripcion: "Exclusivo departamento en torre de alta gama en Puerta de Hierro. Ofrece amplios espacios, acabados de mármol y madera de nogal, climatización central zonificada, cocina equipada con lavavajillas y una vista inigualable hacia el distrito financiero.",
            image: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Acabados de Mármol", "Clima Centralizado", "Vista Panorámica", "2 Estacionamientos", "Seguridad 24/7", "Alberca Templada", "Gimnasio", "Sala de Juntas", "Lavavajillas", "Bodega"]
        },

        // CATEGORÍA: PLAYAS (Yucatán)
        {
            id: 17,
            title: "Lote Premium Residencial - San Bruno",
            municipio: "San Bruno",
            zona: "Zona Beach Club",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 4800000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Terreno residencial premium de inmejorable ubicación en la exclusiva playa de San Bruno, Yucatán. A solo unos pasos del mar, dentro de un desarrollo boutique planeado con acceso privado, calles pavimentadas de concreto y club de playa completo en funcionamiento.",
            image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Acceso a Club de Playa", "Seguridad 24/7", "Servicios Subterráneos", "Vialidades de Concreto", "Áreas Verdes", "Alberca Común", "Canchas Deportivas", "Pet Park", "Luminarias LED", "Régimen en Condominio"]
        },
        {
            id: 18,
            title: "Terreno Residencial Marina - Telchac",
            municipio: "Telchac",
            zona: "Telchac Puerto",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 3200000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Lote exclusivo frente a la Marina en Telchac Puerto. Cuenta con canal de navegación directo, ideal para propietarios con yates o lanchas. El desarrollo incluye casa club de primer nivel, gimnasio y zona comercial planificada.",
            image: "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Frente a Marina", "Acceso Canal Navegación", "Casa Club con Alberca", "Gimnasio", "Seguridad 24/7", "Área Comercial", "Servicios de Marina", "Vialidades Empedradas", "Jardines", "Pet Friendly"]
        },
        {
            id: 19,
            title: "Lote de Playa Exclusive - Sisal",
            municipio: "Sisal",
            zona: "Pueblo Mágico",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 6500000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Lote residencial con acceso directo a las arenas blancas del Pueblo Mágico de Sisal. Cuenta con una topografía plana y servicios a pie de lote. Excelente oportunidad de inversión en una de las playas con mayor plusvalía y conservación ecológica de la península.",
            image: "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Acceso Directo a Playa", "Entorno Ecológico", "Servicios a pie de lote", "Ubicación en Sisal", "Vigilancia", "Vialidades Rústicas", "Zona de Alta Plusvalía", "Orientación Norte", "Cercano a Restaurantes", "Flora Endémica"]
        },
        {
            id: 20,
            title: "Lote Ecológico Oceanfront - Celestún",
            municipio: "Celestún",
            zona: "Reserva Natural",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 2100000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Lote residencial ecológico frente al mar dentro de la reserva de Celestún. Diseñado bajo lineamientos de bajo impacto ambiental para garantizar la conservación de la flora y fauna local (flamingos, dunas). El lote cuenta con servicios de energía ecológica solar.",
            image: "https://images.unsplash.com/photo-1473116763269-255ea7604bb6?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1473116763269-255ea7604bb6?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1506929562872-bb421503ef21?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Frente al Mar", "Sostenibilidad Ecológica", "Energía Solar Preparada", "Biodiversidad Natural", "Dunas Protegidas", "Acceso Controlado", "Bajo Impacto", "Vistas al Océano", "Ubicación Celestún", "Entorno Pacífico"]
        },
        {
            id: 21,
            title: "Terreno en Coto Privado - Chuburná",
            municipio: "Chuburná",
            zona: "Chuburná Puerto",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 1850000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Lote regular dentro de fraccionamiento privado en Chuburná. Cuenta con seguridad perimetral, casa club en desarrollo con alberca, servicios listos para conectarse y excelente cercanía al puerto de Chuburná y a solo 30 minutos de Mérida.",
            image: "https://images.unsplash.com/photo-1506929562872-bb421503ef21?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1506929562872-bb421503ef21?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1473116763269-255ea7604bb6?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Coto Privado", "Seguridad Vigilancia", "Casa Club Alberca", "Servicios Ocultos", "Vialidades Pavimentadas", "Cercano a Chuburná", "A 30m de Mérida", "Inversión Segura", "Régimen Condominio", "Áreas Deportivas"]
        },
        {
            id: 22,
            title: "Macrolote Premium - Chicxulub Puerto",
            municipio: "Chicxulub",
            zona: "Zona de Antros",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 5900000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Macrolote comercial y de servicios de excelente tamaño sobre la avenida principal de acceso a Chicxulub Puerto. Gran flujo vehicular y peatonal durante temporadas vacacionales. Ideal para el desarrollo de plaza comercial, departamentos vacacionales o club de playa.",
            image: "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1506929562872-bb421503ef21?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1473116763269-255ea7604bb6?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["Macrolote Comercial", "Esquina Principal", "Uso de Suelo Mixto", "Servicios de Alta Tensión", "Vialidades Principales", "Zona Turística", "Alta Rentabilidad", "Apie de Carretera", "Factibilidad de Agua", "Estacionamiento potencial"]
        }
    ];
})();
