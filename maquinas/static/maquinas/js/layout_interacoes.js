document.addEventListener('DOMContentLoaded', function () {
    // --- Constantes Globais (Definidas no HTML via template Django) ---
    // CSRF_TOKEN, ATUALIZAR_POSICAO_URL, LAYOUT_PADRAO_URL, CRIAR_CHAMADO_URL
    // Estas são esperadas estarem disponíveis globalmente quando este script rodar.

    // --- Elementos do DOM ---
    const seletorPlanta = document.getElementById('seletor-planta');
    const maquinasPontos = document.querySelectorAll('.maquina-ponto');

    const detalhesModal = document.getElementById('detalhesModal');
    const closeDetalhesModalButton = document.getElementById('close-detalhes-modal');
    const fecharDetalhesModalBtns = document.querySelectorAll('.close-detalhes-modal-btn');

    const btnReportarProblema = document.getElementById('btn-reportar-problema');
    const reportarProblemaModal = document.getElementById('reportarProblemaModal');
    const closeReportarModalButton = document.getElementById('close-reportar-modal');
    const cancelReportarModalButton = reportarProblemaModal ? reportarProblemaModal.querySelector('.close-reportar-modal-btn') : null;
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

    const hGuideTop = document.getElementById('h-guide-top');
    const hGuideCenter = document.getElementById('h-guide-center');
    const hGuideBottom = document.getElementById('h-guide-bottom');
    const vGuideLeft = document.getElementById('v-guide-left');
    const vGuideCenter = document.getElementById('v-guide-center');
    const vGuideRight = document.getElementById('v-guide-right');
    const allGuides = [hGuideTop, hGuideCenter, hGuideBottom, vGuideLeft, vGuideCenter, vGuideRight].filter(el => el !== null);

    const SNAP_THRESHOLD_EDGE = 6;
    const GRID_SIZE = 20;
    const DESIRED_SPACING = 20;        // Espaçamento desejado entre itens
    const SNAP_THRESHOLD_SPACING = 6;  // Tolerância para o snap de espaçamento

    let edicaoLayoutAtiva = false;
    let currentScale = 1; const scaleStep = 0.1;
    let currentTranslateX = 0; let currentTranslateY = 0;
    let isPanningLayout = false; let startLayoutPanX = 0; let startLayoutPanY = 0;
    let activeDraggedItem = null; let initialMouseX, initialMouseY, initialItemX, initialItemY;
    let isGridSnapActive = gridSnapToggle ? gridSnapToggle.checked : true;
    let currentMaquinaIdParaReporte = null;

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

    document.addEventListener('mousemove', function(event) {
        if (isPanningLayout && layoutArea) { currentTranslateX = event.clientX - startLayoutPanX; currentTranslateY = event.clientY - startLayoutPanY; applyLayoutTransform(); }

        if (activeDraggedItem && edicaoLayoutAtiva && layoutArea && layoutContainer) {
            event.preventDefault();
            hideAllGuides();

            let prospectiveX = initialItemX + (event.clientX - initialMouseX) / currentScale;
            let prospectiveY = initialItemY + (event.clientY - initialMouseY) / currentScale;

            const draggedItemWidth = activeDraggedItem.offsetWidth;
            const draggedItemHeight = activeDraggedItem.offsetHeight;

            let snappedToEdgeX = false; let snappedToEdgeY = false;
            let snappedToSpacingX = false; let snappedToSpacingY = false;

            const layoutRect = layoutArea.getBoundingClientRect();
            const containerRect = layoutContainer.getBoundingClientRect();

            // 1. Tenta Snap às Bordas de Outros Itens
            maquinasPontos.forEach(otherItem => {
                if (otherItem === activeDraggedItem) return;
                const otherItemLeft = parseFloat(otherItem.style.left); const otherItemTop = parseFloat(otherItem.style.top);
                const otherItemWidth = otherItem.offsetWidth; const otherItemHeight = otherItem.offsetHeight;

                // Recalcula draggedEdges aqui, pois prospectiveX/Y podem mudar dentro deste loop se o snap ocorrer
                const currentDraggedEdges = { left: prospectiveX, hCenter: prospectiveX + draggedItemWidth / 2, right: prospectiveX + draggedItemWidth, top: prospectiveY, vCenter: prospectiveY + draggedItemHeight / 2, bottom: prospectiveY + draggedItemHeight };
                const otherEdges = { left: otherItemLeft, hCenter: otherItemLeft + otherItemWidth / 2, right: otherItemLeft + otherItemWidth, top: otherItemTop, vCenter: otherItemTop + otherItemHeight / 2, bottom: otherItemTop + otherItemHeight };

                if (Math.abs(currentDraggedEdges.top - otherEdges.top) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.top; snappedToEdgeY=true; showHorizontalGuide(hGuideTop, (otherEdges.top * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }
                else if (Math.abs(currentDraggedEdges.vCenter - otherEdges.vCenter) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.vCenter - draggedItemHeight / 2; snappedToEdgeY=true; showHorizontalGuide(hGuideCenter, (otherEdges.vCenter * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }
                else if (Math.abs(currentDraggedEdges.bottom - otherEdges.bottom) < SNAP_THRESHOLD_EDGE) { prospectiveY = otherEdges.bottom - draggedItemHeight; snappedToEdgeY=true; showHorizontalGuide(hGuideBottom, (otherEdges.bottom * currentScale + currentTranslateY) + layoutRect.top - containerRect.top); }

                if (Math.abs(currentDraggedEdges.left - otherEdges.left) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.left; snappedToEdgeX=true; showVerticalGuide(vGuideLeft, (otherEdges.left * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
                else if (Math.abs(currentDraggedEdges.hCenter - otherEdges.hCenter) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.hCenter - draggedItemWidth / 2; snappedToEdgeX=true; showVerticalGuide(vGuideCenter, (otherEdges.hCenter * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
                else if (Math.abs(currentDraggedEdges.right - otherEdges.right) < SNAP_THRESHOLD_EDGE) { prospectiveX = otherEdges.right - draggedItemWidth; snappedToEdgeX=true; showVerticalGuide(vGuideRight, (otherEdges.right * currentScale + currentTranslateX) + layoutRect.left - containerRect.left); }
            });

            // 2. SE NÃO HOUVE SNAP À BORDA, tenta Snap de Espaçamento
            const draggedEdgesForSpacing = { left: prospectiveX, hCenter: prospectiveX + draggedItemWidth / 2, right: prospectiveX + draggedItemWidth, top: prospectiveY, vCenter: prospectiveY + draggedItemHeight / 2, bottom: prospectiveY + draggedItemHeight };

            if (!snappedToEdgeX || !snappedToEdgeY) {
                maquinasPontos.forEach(otherItem => {
                    if (otherItem === activeDraggedItem) return;
                    const otherItemLeft = parseFloat(otherItem.style.left); const otherItemTop = parseFloat(otherItem.style.top);
                    const otherItemWidth = otherItem.offsetWidth; const otherItemHeight = otherItem.offsetHeight;
                    const otherEdges = { left: otherItemLeft, hCenter: otherItemLeft + otherItemWidth / 2, right: otherItemLeft + otherItemWidth, top: otherItemTop, vCenter: otherItemTop + otherItemHeight / 2, bottom: otherItemTop + otherItemHeight };

                    if (!snappedToEdgeX && !snappedToSpacingX) {
                        if (Math.abs(draggedEdgesForSpacing.left - (otherEdges.right + DESIRED_SPACING)) < SNAP_THRESHOLD_SPACING) { prospectiveX = otherEdges.right + DESIRED_SPACING; snappedToSpacingX = true; }
                        else if (Math.abs(draggedEdgesForSpacing.right - (otherEdges.left - DESIRED_SPACING)) < SNAP_THRESHOLD_SPACING) { prospectiveX = otherEdges.left - DESIRED_SPACING - draggedItemWidth; snappedToSpacingX = true; }
                    }
                    if (!snappedToEdgeY && !snappedToSpacingY) {
                        if (Math.abs(draggedEdgesForSpacing.top - (otherEdges.bottom + DESIRED_SPACING)) < SNAP_THRESHOLD_SPACING) { prospectiveY = otherEdges.bottom + DESIRED_SPACING; snappedToSpacingY = true; }
                        else if (Math.abs(draggedEdgesForSpacing.bottom - (otherEdges.top - DESIRED_SPACING)) < SNAP_THRESHOLD_SPACING) { prospectiveY = otherEdges.top - DESIRED_SPACING - draggedItemHeight; snappedToSpacingY = true; }
                    }
                });
            }

            // 3. SE NÃO HOUVE SNAP À BORDA NEM ESPAÇAMENTO, tenta Snap à Grade
            if (isGridSnapActive) {
                if (!snappedToEdgeX && !snappedToSpacingX) prospectiveX = Math.round(prospectiveX / GRID_SIZE) * GRID_SIZE;
                if (!snappedToEdgeY && !snappedToSpacingY) prospectiveY = Math.round(prospectiveY / GRID_SIZE) * GRID_SIZE;
            }

            // 4. Detecção de Colisão
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

            // 5. Aplicar Movimento
            if (canMoveToProspective) {
                prospectiveX = Math.max(0, Math.min(prospectiveX, layoutArea.offsetWidth - draggedItemWidth));
                prospectiveY = Math.max(0, Math.min(prospectiveY, layoutArea.offsetHeight - draggedItemHeight));
                activeDraggedItem.style.left = `${prospectiveX}px`;
                activeDraggedItem.style.top = `${prospectiveY}px`;
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

    maquinasPontos.forEach(maquinaPonto => {
        let clickPreventedByDrag = false;
        maquinaPonto.addEventListener('mousedown', function(event) {
            clickPreventedByDrag = false;
            if (event.button !== 0 || isPanningLayout || !edicaoLayoutAtiva) {
                if (!edicaoLayoutAtiva && event.button === 0) clickPreventedByDrag = false;
                return;
            }
            activeDraggedItem = this; this.classList.add('dragging');
            initialMouseX = event.clientX; initialMouseY = event.clientY;
            initialItemX = parseFloat(this.style.left); initialItemY = parseFloat(this.style.top);
            document.body.style.userSelect = 'none'; event.preventDefault();
        });
        maquinaPonto.addEventListener('mousemove', function() { if (activeDraggedItem === this && edicaoLayoutAtiva) { clickPreventedByDrag = true; } });
        maquinaPonto.addEventListener('click', function (event) {
            if (clickPreventedByDrag && edicaoLayoutAtiva) { event.preventDefault(); clickPreventedByDrag = false; return; }
            currentMaquinaIdParaReporte = this.dataset.maquinaId;
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
                if(btnVerificarStatus) btnVerificarStatus.dataset.maquinaId = this.dataset.maquinaId;
                if(document.getElementById('modalStatusRede')) document.getElementById('modalStatusRede').textContent = "Clique em 'Verificar Agora'";
                if(document.getElementById('modalUltimaVerificacaoStatus')) document.getElementById('modalUltimaVerificacaoStatus').textContent = "Nunca";
                detalhesModal.style.display = 'block';
            }
        });
    });

    if(closeDetalhesModalButton && detalhesModal) { closeDetalhesModalButton.onclick = function () { detalhesModal.style.display = 'none'; }}
    fecharDetalhesModalBtns.forEach(btn => { if(btn && detalhesModal) btn.onclick = function() { detalhesModal.style.display = 'none'; }});

    if (btnReportarProblema && reportarProblemaModal && reportarMaquinaNomeSpan && reportarMaquinaIdInput && problemaTituloInput && problemaDescricaoTextarea) {
        btnReportarProblema.addEventListener('click', function() {
            if (currentMaquinaIdParaReporte) {
                const maquinaPonto = document.querySelector(`.maquina-ponto[data-maquina-id="${currentMaquinaIdParaReporte}"]`);
                reportarMaquinaNomeSpan.textContent = maquinaPonto ? maquinaPonto.dataset.nome : "Máquina";
                reportarMaquinaIdInput.value = currentMaquinaIdParaReporte;
                problemaTituloInput.value = ''; problemaDescricaoTextarea.value = '';
                if (detalhesModal) detalhesModal.style.display = 'none';
                reportarProblemaModal.style.display = 'block';
            } else { alert("Nenhuma máquina selecionada para reportar problema."); }
        });
    }

    if (closeReportarModalButton && reportarProblemaModal) { closeReportarModalButton.onclick = function() { reportarProblemaModal.style.display = 'none'; } }
    if (cancelReportarModalButton && reportarProblemaModal) { cancelReportarModalButton.onclick = function() { reportarProblemaModal.style.display = 'none'; } }

    if (formReportarProblema && reportarProblemaModal && typeof CRIAR_CHAMADO_URL !== 'undefined' && typeof CSRF_TOKEN !== 'undefined') {
        formReportarProblema.addEventListener('submit', function(event) {
            event.preventDefault();
            const maquinaId = reportarMaquinaIdInput.value; const titulo = problemaTituloInput.value; const descricao = problemaDescricaoTextarea.value;
            const submitBtn = this.querySelector('button[type="submit"]'); const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true; submitBtn.textContent = 'Enviando...';
            fetch(CRIAR_CHAMADO_URL, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' }, body: JSON.stringify({ maquina_id: maquinaId, titulo: titulo, descricao_problema: descricao }) })
            .then(response => response.json()).then(data => {
                if (data.status === 'success') {
                    alert('Problema reportado com sucesso!'); reportarProblemaModal.style.display = 'none';
                    const maquinaPonto = document.querySelector(`.maquina-ponto[data-maquina-id="${maquinaId}"]`);
                    if (maquinaPonto) {
                        maquinaPonto.classList.add('com-alerta');
                        if (!maquinaPonto.querySelector('.alerta-icone')) {
                            const icone = document.createElement('span'); icone.classList.add('alerta-icone'); icone.innerHTML = '⚠';
                            icone.title = "Esta máquina possui chamados abertos!"; maquinaPonto.appendChild(icone);
                        }
                    }
                } else { alert('Erro ao reportar problema: ' + (data.message || 'Erro desconhecido')); }
            })
            .catch(error => { console.error('Erro no fetch do chamado:', error); alert('Erro de comunicação ao reportar problema.'); })
            .finally(() => { submitBtn.disabled = false; submitBtn.textContent = originalBtnText; });
        });
    }

    if(window) {
        window.onclick = function (event) {
            if (event.target == detalhesModal && detalhesModal) { detalhesModal.style.display = 'none'; }
            if (event.target == reportarProblemaModal && reportarProblemaModal) { reportarProblemaModal.style.display = 'none'; }
        }
    }

    // Lógica para o botão Verificar Status (se existir)
    const btnVerificarStatus = document.getElementById('btn-verificar-status');
    if (btnVerificarStatus && typeof VERIFICAR_STATUS_URL_BASE !== 'undefined') {
        btnVerificarStatus.addEventListener('click', function() {
            const maquinaId = this.dataset.maquinaId;
            const modalStatusRedeSpan = document.getElementById('modalStatusRede');
            const modalUltimaVerificacaoSpan = document.getElementById('modalUltimaVerificacaoStatus');
            if (!maquinaId) { alert("ID da máquina não encontrado."); return; }
            if(modalStatusRedeSpan) modalStatusRedeSpan.textContent = "Verificando...";
            this.disabled = true; this.textContent = "Aguarde...";
            fetch(`${VERIFICAR_STATUS_URL_BASE}${maquinaId}/verificar-status/`, { method: 'GET', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => { if (!response.ok) { throw new Error(`Erro HTTP: ${response.status}`); } return response.json(); })
            .then(data => {
                if (modalStatusRedeSpan) modalStatusRedeSpan.textContent = data.online ? 'Online' : (data.online === false ? 'Offline' : 'Desconhecido');
                if (modalUltimaVerificacaoSpan) modalUltimaVerificacaoSpan.textContent = data.ultima_verificacao || "Erro";
                const maquinaPonto = document.querySelector(`.maquina-ponto[data-maquina-id="${data.maquina_id}"]`);
                if (maquinaPonto) {
                    maquinaPonto.classList.remove('status-online', 'status-offline', 'status-desconhecido');
                    if (data.online === true) maquinaPonto.classList.add('status-online');
                    else if (data.online === false) maquinaPonto.classList.add('status-offline');
                    else maquinaPonto.classList.add('status-desconhecido');
                }
            })
            .catch(error => {
                console.error('Erro ao verificar status:', error);
                if (modalStatusRedeSpan) modalStatusRedeSpan.textContent = "Erro";
                if (modalUltimaVerificacaoSpan) modalUltimaVerificacaoSpan.textContent = "Agora";
                alert('Erro ao verificar status: ' + error.message);
            })
            .finally(() => { this.disabled = false; this.textContent = "Verificar Agora"; });
        });
    }
});