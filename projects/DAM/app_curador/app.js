document.addEventListener('DOMContentLoaded', () => {
    // Definimos las 3 zonas
    const slots = [
        { id: 'insp', required: true },
        { id: 'piso', required: false },
        { id: 'comp', required: false }
    ];

    const filesData = {
        insp: null,
        piso: null,
        comp: null
    };

    const analyzeBtn = document.getElementById('analyze-btn');
    const loader = document.getElementById('loader');
    const results = document.getElementById('results');
    const emptyState = document.getElementById('empty-state');
    
    // Bindear eventos para cada slot
    slots.forEach(slot => {
        const dropZone = document.getElementById(`drop-zone-${slot.id}`);
        const fileInput = document.getElementById(`file-${slot.id}`);
        const previewImage = document.getElementById(`preview-${slot.id}`);
        const dropContent = document.getElementById(`drop-content-${slot.id}`);

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                handleFile(e.dataTransfer.files[0], slot.id, previewImage, dropContent);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFile(fileInput.files[0], slot.id, previewImage, dropContent);
            }
        });
    });

    function handleFile(file, slotId, previewImage, dropContent) {
        if (!file.type.startsWith('image/')) {
            alert('Por favor selecciona una imagen válida.');
            return;
        }

        filesData[slotId] = file;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
            dropContent.classList.add('hidden');
            checkReadyState();
        };
        
        reader.readAsDataURL(file);
    }

    // El botón se activa solo si la inspiración base está lista
    function checkReadyState() {
        if (filesData.insp) {
            analyzeBtn.disabled = false;
        } else {
            analyzeBtn.disabled = true;
        }
    }

    // --- API Interaction ---
    analyzeBtn.addEventListener('click', async () => {
        if (!filesData.insp) return;

        // UI Reset
        emptyState.classList.add('hidden');
        results.classList.add('hidden');
        loader.classList.remove('hidden');
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append('file_insp', filesData.insp);
        
        if (filesData.piso) formData.append('file_piso', filesData.piso);
        if (filesData.comp) formData.append('file_comp', filesData.comp);

        const contextInput = document.getElementById('context-input');
        if (contextInput && contextInput.value.trim() !== '') {
            formData.append('context', contextInput.value.trim());
        }

        try {
            // Generación Directa a través de la API Nano Banana Mock/Real
            const response = await fetch('/api/dam/analyze-inspiration', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al generar la imagen directo.');

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Hubo un error al conectar con el servidor de renderizado.');
            loader.classList.add('hidden');
            emptyState.classList.remove('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function renderResults(data) {
        // Hide loader, show results
        loader.classList.add('hidden');
        results.classList.remove('hidden');
        analyzeBtn.disabled = false; // allow new analysis

        const { curador_data, prompt_final } = data;

        // Vibe & Style
        document.getElementById('style-badge').textContent = curador_data.estilo_detectado;
        document.getElementById('vibe-text').textContent = curador_data.vibra;

        // Catalog Items (Just for context)
        const catalogList = document.getElementById('catalog-list');
        catalogList.innerHTML = '';
        
        curador_data.productos_seleccionados.forEach(item => {
            const li = document.createElement('li');
            li.className = 'catalog-item';
            li.innerHTML = `
                <div class="item-header">
                    <div class="item-info">
                        <h4>${item.nombre}</h4>
                        <span>${item.marca} | ${item.formato}</span>
                    </div>
                </div>
                <div class="item-reason">${item.razon}</div>
            `;
            catalogList.appendChild(li);
        });

        // Opción A: Mostrar el Súper Prompt
        const promptBox = document.getElementById('final-prompt');
        if (promptBox && prompt_final) {
            promptBox.textContent = prompt_final;
        }

        // Copy Button logic
        const copyBtn = document.getElementById('copy-btn');
        if (copyBtn) {
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(promptBox.textContent).then(() => {
                    const originalHTML = copyBtn.innerHTML;
                    copyBtn.innerHTML = '¡Copiado!';
                    setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
                });
            };
        }
    }
});
