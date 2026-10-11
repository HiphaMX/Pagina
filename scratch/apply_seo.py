import json, re, glob, os

DOM_BASE = 'https://oncologia-robotica.com'
IMG_DEFAULT = f'{DOM_BASE}/assets/66a42ac7f96594abada73c07_DRA_Jacqueline.jpeg'

faq_items = [
    {
        'q': '¿Qué tipos de cirugía oncológica realizan?',
        'a': 'Realizamos cirugías para diversos tipos de cáncer, incluyendo cirugía mínimamente invasiva y cirugía robótica. Algunas de las que realizamos son: de colon y recto, de estómago, de hígado, de mama, de páncreas, de piel, de tiroides y ginecológico.'
    },
    {
        'q': '¿Cómo sé si necesito una cirugía para mi diagnóstico de cáncer?',
        'a': 'La necesidad de cirugía depende del tipo y estadio del cáncer. Evaluaremos tu caso específico y te recomendaremos el tratamiento más adecuado.'
    },
    {
        'q': '¿Es la cirugía curativa para el cáncer?',
        'a': 'La cirugía puede ser curativa en muchos casos, especialmente si el cáncer se detecta en una etapa temprana. Sin embargo, la eficacia depende de varios factores específicos de cada paciente.'
    },
    {
        'q': '¿Qué es la cirugía mínimamente invasiva y es adecuada para mí?',
        'a': 'La cirugía mínimamente invasiva utiliza técnicas avanzadas para reducir el tamaño de las incisiones y el tiempo de recuperación. Determinaremos si esta técnica es apropiada para tu caso.'
    },
    {
        'q': '¿Cuál es el proceso para programar una consulta con nosotros?',
        'a': 'Puedes programar una consulta llamando a nuestro número de contacto (33 1594 7175), enviando un WhatsApp (33 1108 5716) o llenando el formulario en línea en nuestro sitio web.'
    },
    {
        'q': '¿Cuáles son las opciones de tratamiento disponibles para mi tipo de cáncer?',
        'a': 'En consulta médica especializada discutiremos contigo las mejores opciones basadas en tu diagnóstico patológico y clínico.'
    },
    {
        'q': '¿Qué debo esperar durante mi primera consulta?',
        'a': 'Durante la primera consulta, revisaremos tu historial médico, realizaremos un examen físico y discutiremos los posibles tratamientos quirúrgicos u oncológicos.'
    },
    {
        'q': '¿Cuál es el pronóstico de mi enfermedad con el tratamiento propuesto?',
        'a': 'El pronóstico varía según el tipo de cáncer, su estadio y otros factores individuales. Te proporcionaremos una evaluación personalizada basada en tu situación clínica.'
    },
    {
        'q': '¿Cuánto tiempo tomará mi recuperación después de la cirugía?',
        'a': 'El tiempo de recuperación varía según el tipo de cirugía y tu estado de salud general. Existen procedimientos ambulatorios y de corta estancia (24 a 48 horas con cirugía robótica). Te daremos una estimación precisa para tu procedimiento.'
    },
    {
        'q': '¿Qué debo hacer si tengo síntomas o sospechas de cáncer?',
        'a': 'Si tienes síntomas o sospechas de cáncer, es crucial acudir de inmediato a un cirujano oncólogo certificado para una evaluación y diagnóstico oportuno.'
    }
]

def build_schema(rel_path, pdata):
    stype = pdata.get('schema_type', 'webpage')
    can_url = f"{DOM_BASE}{pdata['path']}"
    
    if stype == 'home':
        return [
            {
                '@context': 'https://schema.org',
                '@type': ['MedicalBusiness', 'Physician'],
                '@id': f'{DOM_BASE}/#organization',
                'name': 'Oncología Robótica - Dra. Jacqueline H. Díaz Garza',
                'alternateName': 'Centro de Cirugía Oncológica y Robótica Zapopan',
                'description': pdata['description'],
                'url': DOM_BASE,
                'telephone': '+523315947175',
                'priceRange': '$$',
                'image': IMG_DEFAULT,
                'address': {
                    '@type': 'PostalAddress',
                    'streetAddress': 'Av. Central Guillermo González Camarena 911, Consultorio 7-B',
                    'addressLocality': 'Zapopan',
                    'addressRegion': 'Jalisco',
                    'postalCode': '45136',
                    'addressCountry': 'MX'
                },
                'geo': {
                    '@type': 'GeoCoordinates',
                    'latitude': 20.7169,
                    'longitude': -103.4336
                },
                'openingHoursSpecification': {
                    '@type': 'OpeningHoursSpecification',
                    'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                    'opens': '09:00',
                    'closes': '19:00'
                },
                'medicalSpecialty': ['SurgicalOncology', 'OncologicSurgery'],
                'availableService': [
                    {'@type': 'MedicalProcedure', 'name': 'Cirugía Robótica Da Vinci'},
                    {'@type': 'MedicalProcedure', 'name': 'Cirugía Laparoscópica Avanzada'},
                    {'@type': 'MedicalProcedure', 'name': 'Cirugía Oncológica'}
                ],
                'sameAs': [
                    'https://wa.me/523311085716'
                ]
            },
            {
                '@context': 'https://schema.org',
                '@type': 'FAQPage',
                'mainEntity': [
                    {
                        '@type': 'Question',
                        'name': item['q'],
                        'acceptedAnswer': {
                            '@type': 'Answer',
                            'text': item['a']
                        }
                    } for item in faq_items
                ]
            }
        ]
    elif stype == 'physician':
        return {
            '@context': 'https://schema.org',
            '@type': 'Physician',
            'name': 'Dra. Jacqueline H. Díaz Garza',
            'medicalSpecialty': ['SurgicalOncology', 'OncologicSurgery'],
            'description': pdata['description'],
            'image': IMG_DEFAULT,
            'url': can_url,
            'worksFor': {
                '@type': 'MedicalBusiness',
                'name': 'Oncología Robótica',
                'url': DOM_BASE
            },
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': 'Av. Central Guillermo González Camarena 911, Consultorio 7-B',
                'addressLocality': 'Zapopan',
                'addressRegion': 'Jalisco',
                'postalCode': '45136',
                'addressCountry': 'MX'
            },
            'telephone': '+523315947175'
        }
    elif stype == 'procedure':
        pname = pdata.get('procedure_name', pdata['title'])
        return {
            '@context': 'https://schema.org',
            '@type': 'MedicalWebPage',
            'url': can_url,
            'name': pdata['title'],
            'description': pdata['description'],
            'about': {
                '@type': 'MedicalProcedure',
                'name': pname,
                'procedureType': 'Surgical',
                'performer': {
                    '@type': 'Physician',
                    'name': 'Dra. Jacqueline H. Díaz Garza'
                },
                'location': {
                    '@type': 'Hospital',
                    'name': 'Centro Médico Real San José Valle Real',
                    'address': 'Av. Central Guillermo González Camarena 911, Zapopan, Jalisco'
                }
            }
        }
    elif stype == 'condition':
        cname = pdata.get('condition_name', pdata['title'])
        return {
            '@context': 'https://schema.org',
            '@type': 'MedicalWebPage',
            'url': can_url,
            'name': pdata['title'],
            'description': pdata['description'],
            'about': {
                '@type': 'MedicalCondition',
                'name': cname,
                'possibleTreatment': {
                    '@type': 'MedicalProcedure',
                    'name': 'Cirugía Oncológica y Cirugía Robótica Da Vinci',
                    'performer': {
                        '@type': 'Physician',
                        'name': 'Dra. Jacqueline H. Díaz Garza'
                    }
                }
            }
        }
    elif stype == 'blog':
        return {
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            'mainEntityOfPage': {'@type': 'WebPage', '@id': can_url},
            'headline': pdata.get('headline', pdata['title']),
            'description': pdata['description'],
            'image': IMG_DEFAULT,
            'author': {
                '@type': 'Physician',
                'name': 'Dra. Jacqueline H. Díaz Garza'
            },
            'publisher': {
                '@type': 'MedicalBusiness',
                'name': 'Oncología Robótica',
                'logo': {'@type': 'ImageObject', 'url': f'{DOM_BASE}/assets/667b692b064159002216db76_logo1.svg'}
            },
            'datePublished': '2024-06-25T12:00:00+00:00',
            'dateModified': '2026-10-10T00:00:00+00:00'
        }
    elif stype == 'faq':
        return {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'name': pdata['title'],
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': item['q'],
                    'acceptedAnswer': {
                        '@type': 'Answer',
                        'text': item['a']
                    }
                } for item in faq_items
            ]
        }
    elif stype == 'medical_webpage':
        return {
            '@context': 'https://schema.org',
            '@type': 'MedicalWebPage',
            'url': can_url,
            'name': pdata['title'],
            'description': pdata['description']
        }
    else:
        return {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'url': can_url,
            'name': pdata['title'],
            'description': pdata['description']
        }

pages_data = {
    'index.html': {
        'path': '/',
        'title': 'Cirugía Oncológica y Robótica en Guadalajara | Dra. Jacqueline Díaz Garza',
        'description': 'Especialistas en cirugía oncológica y cirugía robótica Da Vinci en Zapopan y Guadalajara. Dra. Jacqueline Díaz Garza. Agenda tu consulta de valoración.',
        'og_type': 'website',
        'schema_type': 'home'
    },
    'jacqueline-diaz-garza.html': {
        'path': '/jacqueline-diaz-garza',
        'title': 'Dra. Jacqueline H. Díaz Garza | Cirujana Oncóloga y Robótica en Guadalajara',
        'description': 'Conoce la trayectoria de la Dra. Jacqueline Díaz Garza, especialista en Cirugía Oncológica y Cirugía Robótica Da Vinci en Real San José Valle Real.',
        'og_type': 'profile',
        'schema_type': 'physician'
    },
    'cirugia.html': {
        'path': '/cirugia',
        'title': 'Cirugía Oncológica y Robótica de Mínima Invasión | Zapopan, Jalisco',
        'description': 'Procedimientos avanzados en cirugía oncológica, laparoscópica y robótica Da Vinci. Mayor precisión quirúrgica, menor dolor y rápida recuperación.',
        'og_type': 'website',
        'schema_type': 'medical_webpage'
    },
    'tipos-de-cirugia/cirugia-robotica.html': {
        'path': '/tipos-de-cirugia/cirugia-robotica',
        'title': 'Cirugía Robótica Da Vinci en Guadalajara | Oncología Robótica',
        'description': 'Cirugía robótica con sistema Da Vinci Xi en Guadalajara. Visión 3D HD, precisión milimétrica y mínima invasión para erradicación tumoral completa.',
        'og_type': 'article',
        'schema_type': 'procedure',
        'procedure_name': 'Cirugía Robótica Da Vinci'
    },
    'tipos-de-cirugia/cirugia-laparoscopica-avanzada.html': {
        'path': '/tipos-de-cirugia/cirugia-laparoscopica-avanzada',
        'title': 'Cirugía Laparoscópica Avanzada Oncológica | Dra. Jacqueline Díaz',
        'description': 'Cirugía laparoscópica oncológica avanzada de mínima invasión. Incisiones menores a 1 cm, menor dolor postoperatorio y rápida recuperación en Guadalajara.',
        'og_type': 'article',
        'schema_type': 'procedure',
        'procedure_name': 'Cirugía Laparoscópica Avanzada'
    },
    'tipos-de-cirugia/cirugia-oncologica.html': {
        'path': '/tipos-de-cirugia/cirugia-oncologica',
        'title': 'Cirugía Oncológica Especializada en Guadalajara y Zapopan',
        'description': 'Cirugía oncológica con márgenes libres y vaciamiento ganglionar meticuloso bajo estándares internacionales para el control tumoral efectivo.',
        'og_type': 'article',
        'schema_type': 'procedure',
        'procedure_name': 'Cirugía Oncológica'
    },
    'diagnostico.html': {
        'path': '/diagnostico',
        'title': 'Diagnóstico Oportuno de Cáncer y Padecimientos Oncológicos | Zapopan',
        'description': 'Diagnóstico oportuno y tratamiento especializado para cáncer de mama, colon, estómago, tiroides, hígado, páncreas, ginecológico y de piel en Zapopan.',
        'og_type': 'website',
        'schema_type': 'medical_webpage'
    },
    'padecimientos/cancer-de-mama.html': {
        'path': '/padecimientos/cancer-de-mama',
        'title': 'Cáncer de Mama: Tratamiento y Cirugía Oncológica | Dra. Jacqueline Díaz',
        'description': 'Especialista en cáncer de mama en Guadalajara: tumorectomías, mastectomías conservadoras, ganglio centinela y cirugía oncoplástica de alta precisión.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Mama'
    },
    'padecimientos/cancer-de-colon-y-recto.html': {
        'path': '/padecimientos/cancer-de-colon-y-recto',
        'title': 'Cáncer de Colon y Recto: Cirugía de Mínima Invasión y Robótica',
        'description': 'Tratamiento quirúrgico para cáncer colorrectal con cirugía robótica y laparoscópica en Guadalajara. Preservación funcional y rápida recuperación.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Colon y Recto'
    },
    'padecimientos/cancer-de-estomago.html': {
        'path': '/padecimientos/cancer-de-estomago',
        'title': 'Cáncer de Estómago: Diagnóstico y Cirugía Oncológica en Guadalajara',
        'description': 'Gastrectomías parciales y totales con linfadenectomía D2 para cáncer gástrico. Valoración y tratamiento oncológico por la Dra. Jacqueline Díaz Garza.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Estómago'
    },
    'padecimientos/cancer-de-higado.html': {
        'path': '/padecimientos/cancer-de-higado',
        'title': 'Cáncer de Hígado: Cirugía Oncológica y Resección Hepática',
        'description': 'Cirugía de tumores hepáticos y metástasis en Guadalajara. Resecciones anatómicas con mínima invasión y control vascular especializado.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Hígado'
    },
    'padecimientos/cancer-de-pancreas.html': {
        'path': '/padecimientos/cancer-de-pancreas',
        'title': 'Cáncer de Páncreas: Cirugía de Whipple y Manejo Quirúrgico Avanzado',
        'description': 'Especialista en cirugía para cáncer de páncreas en Guadalajara. Procedimiento de Whipple y pancreatectomías distales con enfoque oncológico integral.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Páncreas'
    },
    'padecimientos/cancer-de-piel.html': {
        'path': '/padecimientos/cancer-de-piel',
        'title': 'Cáncer de Piel y Melanoma: Diagnóstico y Resección Oncológica',
        'description': 'Tratamiento quirúrgico de melanoma y carcinomas de piel con márgenes oncológicos y biopsia de ganglio centinela en Zapopan y Guadalajara.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Piel'
    },
    'padecimientos/cancer-de-tiroides.html': {
        'path': '/padecimientos/cancer-de-tiroides',
        'title': 'Cáncer de Tiroides: Tiroidectomía y Cirugía Oncológica en Zapopan',
        'description': 'Tiroidectomía total y vaciamiento cervical con neuromonitoreo del nervio laríngeo recurrente para cáncer de tiroides en Guadalajara.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Tiroides'
    },
    'padecimientos/cancer-ginecologico.html': {
        'path': '/padecimientos/cancer-ginecologico',
        'title': 'Cáncer Ginecológico: Cirugía Oncológica y Robótica Especializada',
        'description': 'Tratamiento de cáncer de ovario, endometrio y cérvix. Cirugía robótica y laparoscópica de mínima invasión con la Dra. Jacqueline Díaz Garza.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer Ginecológico'
    },
    'padecimientos/cancer-de-cabeza-y-cuello.html': {
        'path': '/padecimientos/cancer-de-cabeza-y-cuello',
        'title': 'Cáncer de Cabeza y Cuello: Cirugía Oncológica de Alta Precisión',
        'description': 'Cirugía de tumores en glándulas salivales, cavidad oral y cuello con vaciamiento cervical funcional y preservación de nervios en Guadalajara.',
        'og_type': 'article',
        'schema_type': 'condition',
        'condition_name': 'Cáncer de Cabeza y Cuello'
    },
    'blog/cuidados-despues-de-una-cirugia-oncologica.html': {
        'path': '/blog/cuidados-despues-de-una-cirugia-oncologica',
        'title': 'Cuidados Después de una Cirugía Oncológica | Guía Médica Postoperatoria',
        'description': 'Aprende los cuidados esenciales postoperatorios tras una cirugía de cáncer: manejo de apósitos, reposo, nutrición adecuada y signos de alarma.',
        'og_type': 'article',
        'schema_type': 'blog',
        'headline': 'Cuidados después de una cirugía oncológica'
    },
    'blog/guia-para-familiares-y-acompanantes.html': {
        'path': '/blog/guia-para-familiares-y-acompanantes',
        'title': 'Guía para Familiares de Pacientes Oncológicos | Dra. Jacqueline Díaz',
        'description': 'Consejos y recomendaciones prácticas para acompañantes y cuidadores de pacientes en tratamiento de cáncer y recuperación quirúrgica.',
        'og_type': 'article',
        'schema_type': 'blog',
        'headline': 'Guía para familiares y acompañantes de pacientes con cáncer'
    },
    'blog/que-son-los-cuidados-paliativos-conceptos-basicos.html': {
        'path': '/blog/que-son-los-cuidados-paliativos-conceptos-basicos',
        'title': 'Cuidados Paliativos en Oncología: Conceptos Básicos y Apoyo Integral',
        'description': 'Conoce qué son los cuidados paliativos, su importancia en la calidad de vida del paciente oncológico y cómo complementan el tratamiento médico.',
        'og_type': 'article',
        'schema_type': 'blog',
        'headline': '¿Qué son los cuidados paliativos? Conceptos básicos y apoyo'
    },
    'tipo/pacientes.html': {
        'path': '/tipo/pacientes',
        'title': 'Blog para Pacientes | Consejos y Guías Oncológicas',
        'description': 'Artículos y recomendaciones médicas para pacientes con cáncer: preparación para cirugías, cuidados en casa y recuperación.',
        'og_type': 'website',
        'schema_type': 'medical_webpage'
    },
    'tipo/prevencion.html': {
        'path': '/tipo/prevencion',
        'title': 'Prevención y Detección Temprana del Cáncer | Oncología Robótica',
        'description': 'Información y consejos médicos para la prevención y diagnóstico precoz de diferentes tipos de cáncer por especialistas certificados.',
        'og_type': 'website',
        'schema_type': 'medical_webpage'
    },
    'preguntas-frecuentes.html': {
        'path': '/preguntas-frecuentes',
        'title': 'Preguntas Frecuentes sobre Cirugía Oncológica y Robótica Da Vinci',
        'description': 'Respuestas a las dudas más comunes sobre procedimientos quirúrgicos oncológicos, preparación, candidatos a cirugía robótica y seguros médicos.',
        'og_type': 'website',
        'schema_type': 'faq'
    },
    'aviso-de-privacidad.html': {
        'path': '/aviso-de-privacidad',
        'title': 'Aviso de Privacidad | Oncología Quirúrgica y Robótica',
        'description': 'Consulta los términos del aviso de privacidad y protección de datos personales de la clínica de Oncología Quirúrgica & Robótica.',
        'og_type': 'website',
        'schema_type': 'webpage'
    },
    'gracias-formulario.html': {
        'path': '/gracias-formulario',
        'title': 'Gracias por Contactarnos | Oncología Quirúrgica y Robótica',
        'description': 'Hemos recibido tu solicitud de consulta. Nuestro equipo médico se pondrá en contacto contigo a la brevedad.',
        'og_type': 'website',
        'schema_type': 'webpage'
    },
    'gracias-email.html': {
        'path': '/gracias-email',
        'title': 'Mensaje Recibido | Oncología Quirúrgica y Robótica',
        'description': 'Gracias por contactarnos por correo electrónico. Te responderemos oportunamente.',
        'og_type': 'website',
        'schema_type': 'webpage'
    },
    'gracias-telefono.html': {
        'path': '/gracias-telefono',
        'title': 'Llamada Registrada | Oncología Quirúrgica y Robótica',
        'description': 'Gracias por comunicarte con nosotros. Estamos listos para atenderte.',
        'og_type': 'website',
        'schema_type': 'webpage'
    },
    'gracias-whatsapp.html': {
        'path': '/gracias-whatsapp',
        'title': 'WhatsApp Iniciado | Oncología Quirúrgica y Robótica',
        'description': 'Gracias por enviar tu mensaje por WhatsApp. En breve un especialista te atenderá.',
        'og_type': 'website',
        'schema_type': 'webpage'
    }
}

base_dir = 'projects/OncologiaRobotica'
processed = 0

for rel_path, pdata in pages_data.items():
    file_path = os.path.join(base_dir, rel_path)
    if not os.path.isfile(file_path):
        print(f'File not found: {file_path}')
        continue
    
    with open(file_path, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    # 1. Update lang attribute to es
    content = re.sub(r'<html([^>]*)\slang="[^"]*"', r'<html\1 lang="es"', content)
    if 'lang="es"' not in content[:300]:
        content = re.sub(r'<html([^>]*)>', r'<html\1 lang="es">', content)
    
    # 2. Clean out old meta tags in <head>
    head_start = content.find('<head>')
    head_end = content.find('</head>')
    if head_start == -1 or head_end == -1:
        print(f'No head found in {rel_path}')
        continue
    
    head_content = content[head_start + 6:head_end]
    
    # Remove existing title, descriptions, canonicals, og/twitter tags, schema scripts
    head_content = re.sub(r'<title>.*?</title>', '', head_content, flags=re.IGNORECASE | re.DOTALL)
    head_content = re.sub(r'<meta[^>]*name=["\']description["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<meta[^>]*content=["\'][^"\']*["\'][^>]*name=["\']description["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<link[^>]*rel=["\']canonical["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<meta[^>]*property=["\']og:[^"\']*["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<meta[^>]*name=["\']twitter:[^"\']*["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<meta[^>]*content=["\'][^"\']*["\'][^>]*name=["\']twitter:[^"\']*["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<meta[^>]*name=["\']robots["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', '', head_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove pre-existing preconnects to fonts to avoid duplicates
    head_content = re.sub(r'<link[^>]*href=["\']https://fonts\.googleapis\.com["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    head_content = re.sub(r'<link[^>]*href=["\']https://fonts\.gstatic\.com["\'][^>]*>', '', head_content, flags=re.IGNORECASE)
    
    # Clean leading meta charset if repeated
    head_content = re.sub(r'^\s*<meta charset="utf-8"/>', '', head_content.strip(), flags=re.IGNORECASE)
    
    # Build schema
    schemas = build_schema(rel_path, pdata)
    if isinstance(schemas, list):
        schema_tags = '\n'.join([f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>' for s in schemas])
    else:
        schema_tags = f'<script type="application/ld+json">\n{json.dumps(schemas, ensure_ascii=False, indent=2)}\n</script>'
    
    can_url = f"{DOM_BASE}{pdata['path']}"
    title = pdata['title']
    desc = pdata['description']
    og_type = pdata['og_type']
    
    new_head_block = (
        '<meta charset="utf-8"/>\n'
        f'<title>{title}</title>\n'
        f'<meta name="description" content="{desc}"/>\n'
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"/>\n'
        f'<link rel="canonical" href="{can_url}"/>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"/>\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>\n'
        '<!-- OpenGraph / Facebook -->\n'
        '<meta property="og:locale" content="es_MX"/>\n'
        f'<meta property="og:type" content="{og_type}"/>\n'
        '<meta property="og:site_name" content="Oncología Robótica - Dra. Jacqueline H. Díaz Garza"/>\n'
        f'<meta property="og:title" content="{title}"/>\n'
        f'<meta property="og:description" content="{desc}"/>\n'
        f'<meta property="og:url" content="{can_url}"/>\n'
        f'<meta property="og:image" content="{IMG_DEFAULT}"/>\n'
        '<meta property="og:image:width" content="1200"/>\n'
        '<meta property="og:image:height" content="630"/>\n'
        '<!-- Twitter Cards -->\n'
        '<meta name="twitter:card" content="summary_large_image"/>\n'
        f'<meta name="twitter:title" content="{title}"/>\n'
        f'<meta name="twitter:description" content="{desc}"/>\n'
        f'<meta name="twitter:image" content="{IMG_DEFAULT}"/>\n'
        '<!-- Schema.org JSON-LD -->\n'
        f'{schema_tags}\n'
    )
    
    content = content[:head_start + 6] + new_head_block + head_content + content[head_end:]
    
    # 3. Optimize LCP image priorities
    if rel_path == 'index.html':
        content = re.sub(
            r'(<img[^>]*src=["\']assets/66a42ac7f96594abada73c07_DRA_Jacqueline\.jpeg["\'][^>]*?)loading=["\']lazy["\']',
            r'\1loading="eager" fetchpriority="high"',
            content
        )
        if 'fetchpriority="high"' not in content:
            content = re.sub(
                r'(<img[^>]*src=["\']assets/66a42ac7f96594abada73c07_DRA_Jacqueline\.jpeg["\'])',
                r'\1 fetchpriority="high"',
                content
            )
    else:
        # In interior pages, optimize the first large content image
        match = re.search(r'(<figure[^>]*><div><img[^>]*?)loading=["\']lazy["\']', content)
        if match:
            content = content[:match.start()] + match.group(1) + 'loading="eager" fetchpriority="high"' + content[match.end():]
        # Also ensure doctor avatar in author card has eager loading
        content = re.sub(
            r'(<img[^>]*src=["\']\.\./assets/66a42ac7f96594abada73c07_DRA_Jacqueline\.jpeg["\'][^>]*?)loading=["\']lazy["\']',
            r'\1loading="eager"',
            content
        )

    with open(file_path, 'w', encoding='utf-8') as fp:
        fp.write(content)
    processed += 1

print(f'Successfully updated {processed} files with complete SEO, OpenGraph, JSON-LD and CWV optimizations!')
