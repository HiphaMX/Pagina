// Base de Datos Centralizada de Propiedades - Jessica Mendoza Real Estate
(function() {
    window.PROPERTIES_DB = [
        // 1. UNA CASA (ZMG)
        {
            id: 1,
            title: "Residencia de Autor - Valle Imperial",
            municipio: "Zapopan",
            zona: "Valle Imperial",
            operacion: "Compra",
            tipo: "Casa",
            precio: 6850000,
            habitaciones: 3,
            condicion: "Listo para estrenar",
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
        // 2. UN DEPARTAMENTO NUEVO (ZMG)
        {
            id: 2,
            title: "Loft Boutique - Providencia",
            municipio: "Guadalajara",
            zona: "Providencia",
            operacion: "Venta",
            tipo: "Departamento",
            precio: 4950000,
            habitaciones: 2,
            condicion: "Listo para estrenar",
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
        // 3. UN TERRENO (PLAYA YUCATÁN)
        {
            id: 3,
            title: "Lote Residencial Sunset - Telchac",
            municipio: "Telchac",
            zona: "Telchac Puerto",
            operacion: "Compra",
            tipo: "Terreno",
            precio: 1450000,
            habitaciones: 0,
            condicion: "N/A",
            isPlaya: true,
            descripcion: "Terreno totalmente plano y regular a solo 200 metros de la orilla de playa en la zona de mayor crecimiento y plusvalía de Telchac. Listo para escriturar y comenzar un proyecto residencial costero privado con certeza legal garantizada.",
            image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
            imagenes: [
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80",
                "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80"
            ],
            amenidades: ["A 200m de Playa", "Certeza Jurídica", "Servicios de Agua y Luz", "Vialidad de Arena Apisonada", "Mojoneras Delimitadas", "Club de Playa Cercano", "Sin Régimen Condominal", "Ubicación en Telchac", "Alta Plusvalía", "Listos para Escriturar"]
        }
    ];
})();
