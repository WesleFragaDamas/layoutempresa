document.addEventListener('DOMContentLoaded', function () {
    // --- Constantes Globais (Definidas no HTML via template Django) ---
    // CSRF_TOKEN, ATUALIZAR_POSICAO_URL, LAYOUT_PADRAO_URL, CRIAR_CHAMADO_URL
    // Estas são esperadas estarem disponíveis globalmente quando este script rodar.

    // --- Elementos do DOM ---
    const seletorPlanta = document.getElementById('seletor-planta');
    const maquinasPontos = document.querySelectorAll('.maquina-ponto'); // NodeList, pode ser vazia

    const detalhesModal = document.getElementById('detalhesModal');
    const closeDetalhesModalButton = document.getElementById('close-detalhes-modal'); // Botão X do modal de detalhes
    const fecharDetalhesModalBtns = document.querySelectorAll('.close-detalhes-modal-btn'); // Botões "Fechar"

    const btnReportarProblema = document.getElementById('btn-reportar-problema');
    const reportarProblemaModal = document.getElementById('reportarProblemaModal');
    const closeReportarModalButton = document.getElementById('close-reportar-modal'); // Botão X do modal de reporte
    const cancelReportarModalButton = reportarProblemaModal ? reportarProblemaModal.querySelector('.close-reportar-modal-btn') : null; // Botão "Cancelar"
    const formReportarProblema = document.getElementById('form-reportar-problema');
    const reportarMaquinaIdInput = document.getElementById('reportarMaquinaId');
    const reportarMaquinaNomeSpan = document.getElementById('reportarMaquinaNome');
    const problemaTituloInput = document.getElementById('problemaTitulo');
    const problemaDescricaoTextarea = document.getElementById('problemaDescricao');

    const layoutArea = document.getElementById('area-layout');
    const layoutContainer = document.getElementById('area-layout-container');
    const zoomInButton = document.getElementById('zoom-in');
    const zoomOutButton = document.getElementById('zoom-out');
    const zoomResetButton = document.getElementById('zoom-reset');
    const toggleEdicaoButton = document.getElementById('toggle-edicao-layout');
    const gridSnapToggle = document.getElementById('grid-snap-toggle');
    const savingIndicator = document.getElementById('saving-indicator');

    // Linhas Guia de Alinhamento de Bordas
    const hGuideTop = document.getElementById('h-guide-top');
    const hGuideCenter = document.getElementById('h-guide-center');
    const hGuideBottom = document.getElementById('h-guide-bottom');
    const vGuideLeft = document.getElementById('v-guide-left');
    const vGuideCenter = document.getElementById('v-guide-center');
    const vGuideRight = document.getElementById('v-guide-right');
    const allGuides = [hGuideTop, hGuideCenter, hGuideBottom, vGuideLeft, vGuideCenter, vGuideRight].filter(el => el !== null);

    // --- Configurações ---
    const SNAP_THRESHOLD_EDGE = 6;
    const GRID_SIZE = 20;

    // --- Variáveis de Estado ---
    let edicaoLayoutAtiva = false;
    let currentScale = 1; const scaleStep = 0.1;
    let currentTranslateX = 0; let currentTranslateY = 0;
    let isPanningLayout = false; let startLayoutPanX = 0; let startLayoutPanY = 0;
    let activeDraggedItem = null; let initialMouseX, initialMouseY, initialItemX, initialItemY;
    let isGridSnapActive = gridSnapToggle ? gridSnapToggle.checked : true;
    let currentMaquinaIdParaReporte = null; // Armazena o ID da máquina para o modal de reporte

    // --- Funções Auxiliares ---
    function hideAllGuides() { allGuides.forEach(guide => { if(guide) guide.style.display = 'none'; }); }
    function showHorizontalGuide(guideElement, yPos) { if (guideElement) { guideElement.style.top = `${yPos}px`; guideElement.style.display = 'block'; } }
    function showVerticalGuide(guideElement, xPos) { if (guideElement) { guideElement.style.left = `${xPos}px`; guideElement.style.display = 'block'; } }

    function updateEdicaoStatus() {
        if (!toggleEdicaoButton || !layoutArea) return;
        if (edicaoLayoutAtiva) {
            toggleEdicaoButton.textContent = 'Desativar Edição'; toggleEdicaoButton.classList.add('ativo');
            layoutArea.classList.add('edicao-ativa');
        } else {
            toggleEdicaoButton.textContent = 'Ativar Edição'; toggleEdicaoButton.classList.remove('ativo');
            layoutArea.classList.remove('edicao-ativa');
        }
    }

    function applyLayoutTransform() { if(layoutArea) layoutArea.style.transform = `translate(${currentTranslateX}px, ${currentTranslateY}px) scale(${currentScale})`; }

    // --- Event Listeners Iniciais ---
    if (seletorPlanta) {
        seletorPlanta.addEventListener('change', function() {
            const plantaIdSelecionada = this.value;
            if (plantaIdSelecionada) { window.location.href = `/app/layout/${plantaIdSelecionada}/`; }
            else if (this.options.length > 0 && this.options[0].value && typeof LAYOUT_PADRAO_URL !== 'undefined') { window.location.href = LAYOUT_PADRAO_URL; }
        });
    }

    if (toggleEdicaoButton) { updateEdicaoStatus(); toggleEdicaoButton.addEventListener('click', function() { edicaoLayoutAtiva = !edicaoLayoutAtiva; updateEdicaoStatus(); }); }
    if (gridSnapToggle) { gridSnapToggle.addEventListener('change', function() { isGridSnapActive = this.checked; }); }

    if (zoomInButton) zoomInButton.addEventListener('click', function() { currentScale += scaleStep; applyLayoutTransform(); });
    if (zoomOutButton) zoomOutButton.addEventListener('click', function() { if (currentScale - scaleStep >= 0.1) { currentScale -= scaleStep; applyLayoutTransform(); } });
    if (zoomResetButton) zoomResetButton.addEventListener('click', function() { currentScale = 1; currentTranslateX = 0; currentTranslateY = 0; applyLayoutTransform(); });

    if (layoutArea) {
        layoutArea.addEventListener('wheel', function(event) { event.preventDefault(); const delta = Math.sign(event.deltaY); if (delta < 0) { currentScale += scaleStep; } else { if (currentScale - scaleStep >= 0.1) { currentScale -= scaleStep; } } applyLayoutTransform(); });
        layoutArea.addEventListener('mousedown', function(event) { if (event.target === layoutArea) { isPanningLayout = true; layoutArea.classList.add('grabbing'); startLayoutPanX = event.clientX - currentTranslateX; startLayoutPanY = event.clientY - currentTranslateY; event.preventDefault(); } });
    }

    // --- Lógica de Arrastar e Soltar & Alinhamento ---
    document.addEventListener('mousemove', function(event) {
        if (isPanningLayout && layoutArea) { currentTranslateX = event.clientX - startLayoutPanX; currentTranslateY = event.clientY - startLayoutPanY; applyLayoutTransform(); }

        if (activeDraggedItem && edicaoLayoutAtiva && layoutArea && layoutContainer) {
            event.preventDefault(); hideAllGuides();
            let prospectiveX = initialItemX + (event.clientX - initialMouseX) / currentScale;
            let prospectiveY = initialItemY + (event.clientY - initialMouseY) / currentScale;
            const draggedItemWidth = activeDraggedItem.offsetWidth; const draggedItemHeight = activeDraggedItem.offsetHeight;
            const draggedEdges = { left: prospectiveX, hCenter: prospectiveX + draggedItemWidth / 2, right: prospectiveX + draggedItemWidth, top: prospectiveY, vCenter: prospectiveY + draggedItemHeight / 2, bottom: prospectiveY + draggedItemHeight };
            const layoutRect = layoutArea.getBoundingClientRect(); const containerRect = layoutContainer.getBoundingClientRect();
            let snappedToEdgeX = false; let snappedToEdgeY = false;

            maquinasPontos.forEach(otherItem => {
                if (otherItem === activeDraggedItem) return;
                const otherItemLeft = parseFloat(otherItem.style.left); const otherItemTop = parseFloat(otherItem.style.top);
                const otherItemWidth = otherItem.offsetWidth; const otherItemHeight = otherItem.offsetHeight;
                const otherEdges = { left: otherItemLeft, hCenter: otherItemLeft + otherItemWidth / 2, right: otherItemLeft + otherItemWidth, top: otherItemTop, vCenter: otherItemTop + otherItemHeight / 2, bottom: otherItemTop + otherItemHeight };

                if (Math.abs(draggedEdges.top - otherEdges.top) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.top; snappedToEdgeY=true; showHorizontalGuide(hGuideTop, (otherEdges.top * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }
                else if (Math.abs(draggedEdges.vCenter - otherEdges.vCenter) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.vCenter - draggedItemHeight / 2; snappedToEdgeY=true; showHorizontalGuide(hGuideCenter, (otherEdges.vCenter * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }
                else if (Math.abs(draggedEdges.bottom - otherEdges.bottom) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.bottom - draggedItemHeight; snappedToEdgeY=true; showHorizontalGuide(hGuideBottom, (otherEdges.bottom * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }

                if (Math.abs(draggedEdges.left - otherEdges.left) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.left; snappedToEdgeX=true; showVerticalGuide(vGuideLeft, (otherEdges.left * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
                else if (Math.abs(draggedEdges.hCenter - otherEdges.hCenter) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.hCenter - draggedItemWidth / 2; snappedToEdgeX=true; showVerticalGuide(vGuideCenter, (otherEdges.hCenter * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
                else if (Math.abs(draggedEdges.right - otherEdges.right) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.right - draggedItemWidth; snappedToEdgeX=true; showVerticalGuide(vGuideRight, (otherEdges.right * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
            });

            if (isGridSnapActive) {
                if (!snappedToEdgeX) prospectiveX = Math.round(prospectiveX / GRID_SIZE) * GRID_SIZE;
                if (!snappedToEdgeY) prospectiveY = Math.round(prospectiveY / GRID_SIZE) * GRID_SIZE;
            }

            let canMoveToProspective = true;
            for (const otherItem of maquinasPontos) {
                if (otherItem === activeDraggedItem) continue;
                const otherLeft = parseFloat(otherItem.style.left); const otherTop = parseFloat(otherItem.style.top);
                const otherWidth = otherItem.offsetWidth; const otherHeight = otherItem.offsetHeight;
                if (prospectiveX < otherLeft + otherWidth && prospectiveX + draggedItemWidth > otherLeft &&
                    prospectiveY < otherTop + otherHeight && prospectiveY + draggedItemHeight > otherTop) {
                    canMoveToProspective = false; break;
                }
            }

            if (canMoveToProspective) {
                prospectiveX = Math.max(0, Math.min(prospectiveX, layoutArea.offsetWidth - draggedItemWidth));
                prospectiveY = Math.max(0, Math.min(prospectiveY, layoutArea.offsetHeight - draggedItemHeight));
                activeDraggedItem.style.left = `${prospectiveX}px`; activeDraggedItem.style.top = `${prospectiveY}px`;
            }
        }
    });

    document.addEventListener('mouseup', function() {
        if (isPanningLayout && layoutArea) { isPanningLayout = false; layoutArea.classList.remove('grabbing'); }
        hideAllGuides();
        if (activeDraggedItem && edicaoLayoutAtiva) {
            activeDraggedItem.classList.remove('dragging');
            const maquinaId = activeDraggedItem.dataset.maquinaId;
            const finalX = parseFloat(activeDraggedItem.style.left);
            const finalY = parseFloat(activeDraggedItem.style.top);
            if(savingIndicator) savingIndicator.style.display = 'block';
            fetch(ATUALIZAR_POSICAO_URL, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' }, body: JSON.stringify({ id: maquinaId, posicao_x: Math.round(finalX), posicao_y: Math.round(finalY) }) })
            .then(response => response.json()).then(data => { if (data.status === 'success') { console.log('Posição salva:', data.message); } else { console.error('Erro ao salvar posição:', data.message); alert('Erro ao salvar posição: ' + data.message); } })
            .catch(error => { console.error('Erro na requisição fetch:', error); alert('Erro de comunicação ao salvar posição.'); })
            .finally(() => { if(savingIndicator) savingIndicator.style.display = 'none'; });
            activeDraggedItem = null;
        } else if (activeDraggedItem) { activeDraggedItem.classList.remove('dragging'); activeDraggedItem = null; }
        document.body.style.userSelect = '';
    });

    // --- Lógica dos Modais (Detalhes e Reportar Problema) ---
    maquinasPontos.forEach(maquinaPonto => {
        let clickPreventedByDrag = false;
        maquinaPonto.addEventListener('mousedown', function(event) {
            clickPreventedByDrag = false; // Reseta no mousedown
            if (event.button !== 0 || isPanningLayout || !edicaoLayoutAtiva) return;
            activeDraggedItem = this; this.classList.add('dragging');
            initialMouseX = event.clientX; initialMouseY = event.clientY;
            initialItemX = parseFloat(this.style.left); initialItemY = parseFloat(this.style.top);
            document.body.style.userSelect = 'none'; event.preventDefault();
        });
        maquinaPonto.addEventListener('mousemove', function() { if (activeDraggedItem === this && edicaoLayoutAtiva) { clickPreventedByDrag = true; } });
        maquinaPonto.addEventListener('click', function (event) {
            if (clickPreventedByDrag && edicaoLayoutAtiva) { event.preventDefault(); clickPreventedByDrag = false; return; }
            currentMaquinaIdParaReporte = this.dataset.maquinaId; // Define para o modal de reporte
            if(detalhesModal) {
                document.getElementById('modalNomeMaquina').textContent = 'Detalhes: ' + this.dataset.nome;
                document.getElementById('modalPatrimonio').textContent = this.dataset.nome;
                document.getElementById('modalMac').textContent = this.dataset.mac;
                document.getElementById('modalTipo').textContent = this.dataset.tipo;
                document.getElementById('modalSetor').textContent = this.dataset.setor;
                document.getElementById('modalUsuario').textContent = this.dataset.usuario;
                document.getElementById('modalObsHw').textContent = this.dataset.obsHw;
                document.getElementById('modalIp').textContent = this.dataset.ip;
                document.getElementById('modalHostname').textContent = this.dataset.hostname;
                document.getElementById('modalRamal').textContent = this.dataset.ramal;
                document.getElementById('modalSimo').textContent = this.dataset.simo;
                document.getElementById('modalLoginSrv').textContent = this.dataset.loginSrv;
                document.getElementById('modalObsCfg').textContent = this.dataset.obsCfg;
                detalhesModal.style.display = 'block';
            }
        });
    });

    // Fechar Modal de Detalhes
    if(closeDetalhesModalButton) { closeDetalhesModalButton.onclick = function () { if(detalhesModal) detalhesModal.style.display = 'none'; }}
    fecharDetalhesModalBtns.forEach(btn => { if(btn) btn.onclick = function() { if(detalhesModal) detalhesModal.style.display = 'none'; }});


    // Abrir Modal de Reportar Problema (a partir do Modal de Detalhes)
    if (btnReportarProblema && reportarProblemaModal && reportarMaquinaNomeSpan && reportarMaquinaIdInput && problemaTituloInput && problemaDescricaoTextarea) {
        btnReportarProblema.addEventListener('click', function() {
            if (currentMaquinaIdParaReporte) {
                const maquinaPonto = document.querySelector(`.maquina-ponto[data-maquina-id="${currentMaquinaIdParaReporte}"]`);
                reportarMaquinaNomeSpan.textContent = maquinaPonto ? maquinaPonto.dataset.nome : "Máquina";
                reportarMaquinaIdInput.value = currentMaquinaIdParaReporte;
                problemaTituloInput.value = '';
                problemaDescricaoTextarea.value = '';
                if (detalhesModal) detalhesModal.style.display = 'none';
                reportarProblemaModal.style.display = 'block';
            } else {
                alert("Nenhuma máquina selecionada para reportar problema.");
            }
        });
    }

    // Fechar Modal de Reportar Problema
    if (closeReportarModalButton && reportarProblemaModal) {
        closeReportarModalButton.onclick = function() { reportarProblemaModal.style.display = 'none'; }
    }
    if (cancelReportarModalButton && reportarProblemaModal) {
        cancelReportarModalButton.onclick = function() { reportarProblemaModal.style.display = 'none'; }
    }

    // Submeter Formulário de Reportar Problema
    if (formReportarProblema && reportarProblemaModal) {
        formReportarProblema.addEventListener('submit', function(event) {
            event.preventDefault();
            const maquinaId = reportarMaquinaIdInput.value;
            const titulo = problemaTituloInput.value;
            const descricao = problemaDescricaoTextarea.value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true; submitBtn.textContent = 'Enviando...';

            fetch(CRIAR_CHAMADO_URL, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' }, body: JSON.stringify({ maquina_id: maquinaId, titulo: titulo, descricao_problema: descricao }) })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Problema reportado com sucesso!');
                    reportarProblemaModal.style.display = 'none';
                    const maquinaPonto = document.querySelector(`.maquina-ponto[data-maquina-id="${maquinaId}"]`);
                    if (maquinaPonto) {
                        maquinaPonto.classList.add('com-alerta');
                        if (!maquinaPonto.querySelector('.alerta-icone')) {
                            const icone = document.createElement('span');
                            icone.classList.add('alerta-icone'); icone.innerHTML = '⚠';
                            icone.title = "Esta máquina possui chamados abertos!";
                            maquinaPonto.appendChild(icone);
                        }
                    }
                } else { alert('Erro ao reportar problema: ' + (data.message || 'Erro desconhecido')); }
            })
            .catch(error => { console.error('Erro no fetch do chamado:', error); alert('Erro de comunicação ao reportar problema.'); })
            .finally(() => { submitBtn.disabled = false; submitBtn.textContent = originalBtnText; });
        });
    }

    // Fechar modais ao clicar fora deles
    if(window) {
        window.onclick = function (event) {
            if (event.target == detalhesModal && detalhesModal) { detalhesModal.style.display = 'none'; }
            if (event.target == reportarProblemaModal && reportarProblemaModal) { reportarProblemaModal.style.display = 'none'; }
        }
    }
});