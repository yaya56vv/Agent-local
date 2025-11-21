// Configuration
const API_BASE_URL = "http://127.0.0.1:8000";

// État de l'application
let sessionId = generateSessionId();
let autoScroll = true;
let backendStatus = 'unknown'; // 'connected', 'waiting', 'disconnected'
let recentLogs = []; // Store last 10 logs for the banner
const MAX_BANNER_LOGS = 10;
let sessionTimer = 0;
let timerInterval = null;

// État TODO List
let todoList = [];
let currentTodoId = 0;

// État agent temps réel
let agentState = 'inactive'; // 'active', 'idle', 'processing', 'error'
let currentTool = 'Aucun';
let currentAction = 'En attente';
let currentLocation = '';
let lastActivityTime = Date.now();
let activityLog = []; // Historique des activités avec durées
let activityTracker = null; // Timer pour le tracking continu
let idleTimer = null; // Timer pour détecter l'inactivité

// État du microphone et TTS
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let isTTSSpeaking = false;
let currentAudioElement = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('session-id').textContent = sessionId;
    
    // Démarrer le tracking temps réel en premier
    startRealTimeTracking();
    
    addLog('info', 'Interface chargée');
    
    // Vérifier la santé du backend au démarrage
    testHealth();
    startSessionTimer();

    // Enter pour envoyer message
    document.getElementById('user-message').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // CTRL+ENTER pour envoyer message
    document.getElementById('user-message').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // Enter pour interroger RAG
    const ragQuestion = document.getElementById('rag-question');
    if (ragQuestion) {
        ragQuestion.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                askRAG();
            }
        });
    }

    // Raccourcis clavier globaux
    setupKeyboardShortcuts();

    // Floating Interface: Enter pour envoyer
    const floatingInput = document.getElementById('floating-user-message');
    if (floatingInput) {
        floatingInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendFloatingMessage();
            }
        });
    }

    // Draggable Floating Interface
    setupDraggableInterface();

    // Initialiser l'explorateur de fichiers
    initFileExplorer();
    
    // Initialiser le drag & drop pour le contexte
    setupContextDragDrop();
    
    // Lier le bouton d'attachement au file input
    const attachButton = document.getElementById('attach-button');
    const fileInput = document.getElementById('context-file-input');
    if (attachButton && fileInput) {
        fileInput.addEventListener('change', handleContextFiles);
    }
});

// ============ CONTEXT FILE UPLOAD ============

function attachFileToContext() {
    const fileInput = document.getElementById('context-file-input');
    if (fileInput) {
        fileInput.click();
    }
}

async function handleContextFiles(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    addLog('info', `${files.length} fichier(s) sélectionné(s) pour le contexte`);
    
    for (const file of files) {
        await addFileToContext(file);
    }
    
    // Reset input
    event.target.value = '';
}

async function addFileToContext(file) {
    addLog('info', `Lecture du fichier: ${file.name}`);
    
    try {
        const text = await file.text();
        
        // Ajouter au contexte de la conversation
        const contextMessage = `📎 Fichier ajouté au contexte: ${file.name}\n\n${text.substring(0, 500)}${text.length > 500 ? '...' : ''}`;
        appendChat('system', contextMessage);
        
        // Optionnel: Ajouter au RAG pour persistance
        if (confirm(`Voulez-vous également ajouter "${file.name}" à la base de connaissances RAG ?`)) {
            await addToRAGFromFile(file.name, text);
        }
        
        addLog('success', `Fichier "${file.name}" ajouté au contexte`);
        
    } catch (error) {
        addLog('error', `Erreur lecture fichier "${file.name}": ${error.message}`);
        appendChat('error', `Impossible de lire le fichier: ${error.message}`);
    }
}

async function addToRAGFromFile(filename, content) {
    try {
        const response = await fetch(`${API_BASE_URL}/rag/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset: 'scratchpad',
                filename: filename,
                content: content
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        addLog('success', `Fichier "${filename}" ajouté au RAG`);
        
        // Rafraîchir l'explorateur RAG
        await loadRAGDocuments();
        
    } catch (error) {
        addLog('error', `Erreur ajout RAG: ${error.message}`);
    }
}

function setupContextDragDrop() {
    const chatWindow = document.getElementById('chat-window');
    const overlay = document.getElementById('context-drop-overlay');
    
    if (!chatWindow || !overlay) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        chatWindow.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        chatWindow.addEventListener(eventName, () => {
            overlay.classList.remove('hidden');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        chatWindow.addEventListener(eventName, () => {
            overlay.classList.add('hidden');
        }, false);
    });
    
    // Handle dropped files
    chatWindow.addEventListener('drop', async (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            addLog('info', `${files.length} fichier(s) déposé(s)`);
            for (const file of files) {
                await addFileToContext(file);
            }
        }
    }, false);
}

// ============ EXPLORATEUR DE FICHIERS ============

async function initFileExplorer() {
    // Charger les datasets disponibles
    await loadRAGDatasets();

    // Charger les documents RAG
    await loadRAGDocuments();
    
    // Gérer le changement de dataset
    const select = document.getElementById('rag-dataset-select');
    const newInput = document.getElementById('rag-new-dataset-input');
    
    if (select && newInput) {
        select.onchange = () => {
            if (select.value === 'new') {
                newInput.classList.remove('hidden');
                newInput.focus();
            } else {
                newInput.classList.add('hidden');
            }
        };
    }

    // Ajouter le gestionnaire de clic sur la drop zone
    const dropZone = document.getElementById('rag-drop-zone');
    if (dropZone) {
        dropZone.onclick = () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.txt,.md,.pdf,.docx,.py,.js,.html,.css,.json';
            input.multiple = true;
            input.onchange = async (e) => {
                const files = e.target.files;
                if (files && files.length > 0) {
                    for (const file of files) {
                        await uploadFileToRAG(file);
                    }
                }
            };
            input.click();
        };
    }
}

async function loadRAGDatasets() {
    const select = document.getElementById('rag-dataset-select');
    if (!select) return;

    try {
        const response = await fetch(`${API_BASE_URL}/rag/datasets`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const datasets = await response.json();

        // Sauvegarder la sélection actuelle
        const currentSelection = select.value;

        // Reconstruire le select
        select.innerHTML = '<option value="new">+ Nouveau dataset...</option>';
        
        // Ajouter les datasets existants
        datasets.forEach(ds => {
            const option = document.createElement('option');
            option.value = ds;
            option.textContent = `Dataset: ${ds}`;
            select.appendChild(option);
        });
        
        // Restaurer la sélection ou mettre par défaut
        if (datasets.includes(currentSelection)) {
            select.value = currentSelection;
        } else if (datasets.includes('default')) {
            select.value = 'default';
        } else if (datasets.length > 0) {
            select.value = datasets[0];
        }

    } catch (error) {
        addLog('error', `Erreur chargement datasets: ${error.message}`);
    }
}

async function uploadFileToRAG(file) {
    addLog('info', `Upload vers RAG: ${file.name}`);
    
    // Déterminer le dataset cible
    const select = document.getElementById('rag-dataset-select');
    const newInput = document.getElementById('rag-new-dataset-input');
    let dataset = 'default';
    
    if (select) {
        if (select.value === 'new' && newInput) {
            dataset = newInput.value.trim() || 'default';
        } else {
            dataset = select.value;
        }
    }

    try {
        const text = await file.text();
        
        const response = await fetch(`${API_BASE_URL}/rag/documents/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content: text,
                metadata: {
                    filename: file.name,
                    dataset: dataset,
                    uploaded_at: new Date().toISOString()
                }
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        addLog('success', `Fichier "${file.name}" ajouté au dataset "${dataset}"`);
        
        // Rafraîchir l'interface
        await loadRAGDatasets();
        await loadRAGDocuments();
        
        // Reset input si nouveau dataset créé
        if (select.value === 'new' && newInput) {
            newInput.value = '';
            // Sélectionner le nouveau dataset
            select.value = dataset;
            newInput.classList.add('hidden');
        }
        
    } catch (error) {
        addLog('error', `Erreur upload RAG: ${error.message}`);
    }
}

async function loadRAGDocuments() {
    const explorerList = document.getElementById('file-explorer');
    if (!explorerList) return;

    // Afficher loading
    explorerList.innerHTML = '<li class="loading"><i class="fas fa-spinner fa-spin"></i> Chargement RAG...</li>';

    try {
        const response = await fetch(`${API_BASE_URL}/rag/documents`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const documents = await response.json();

        renderRAGTree(documents);

    } catch (error) {
        explorerList.innerHTML = `<li class="error"><i class="fas fa-exclamation-triangle"></i> Erreur: ${error.message}</li>`;
        addLog('error', `Explorateur RAG: ${error.message}`);
    }
}

function renderRAGTree(documents) {
    const explorerList = document.getElementById('file-explorer');
    explorerList.innerHTML = '';

    if (documents.length === 0) {
        explorerList.innerHTML = '<li class="empty">Aucun document indexé</li>';
        return;
    }

    // Organiser les documents par dataset
    const datasetMap = {};
    documents.forEach(doc => {
        const dataset = doc.metadata?.dataset || 'default';
        if (!datasetMap[dataset]) {
            datasetMap[dataset] = [];
        }
        datasetMap[dataset].push(doc);
    });

    // Créer l'arborescence
    Object.keys(datasetMap).sort().forEach(dataset => {
        // Créer le dossier dataset
        const folderLi = document.createElement('li');
        folderLi.className = 'folder-item';
        
        const folderHeader = document.createElement('div');
        folderHeader.className = 'folder-header';
        folderHeader.innerHTML = `
            <i class="fas fa-folder folder-icon"></i>
            <span class="folder-name">${dataset}</span>
            <span class="folder-count">(${datasetMap[dataset].length})</span>
        `;
        
        // Toggle pour déplier/replier
        folderHeader.onclick = (e) => {
            e.stopPropagation();
            folderLi.classList.toggle('expanded');
            const icon = folderHeader.querySelector('.folder-icon');
            if (folderLi.classList.contains('expanded')) {
                icon.classList.remove('fa-folder');
                icon.classList.add('fa-folder-open');
            } else {
                icon.classList.remove('fa-folder-open');
                icon.classList.add('fa-folder');
            }
        };
        
        folderLi.appendChild(folderHeader);
        
        // Créer la liste des fichiers
        const filesList = document.createElement('ul');
        filesList.className = 'files-list';
        
        datasetMap[dataset].forEach(doc => {
            const fileLi = document.createElement('li');
            fileLi.className = 'file-item';
            
            const filename = doc.metadata?.filename || doc.id.substring(0, 20) + '...';
            const iconClass = getFileIcon(filename);
            
            fileLi.innerHTML = `
                <i class="fas ${iconClass} file-icon"></i>
                <span class="file-name">${filename}</span>
            `;
            
            fileLi.title = `Double-clic pour voir les détails\nID: ${doc.id}`;
            
            // Simple clic : sélection
            fileLi.onclick = (e) => {
                e.stopPropagation();
                document.querySelectorAll('.file-item').forEach(f => f.classList.remove('selected'));
                fileLi.classList.add('selected');
            };
            
            // Double-clic : afficher les détails
            fileLi.ondblclick = (e) => {
                e.stopPropagation();
                showDocumentDetails(doc);
            };
            
            filesList.appendChild(fileLi);
        });
        
        folderLi.appendChild(filesList);
        explorerList.appendChild(folderLi);
    });
    
    addLog('success', `${documents.length} document(s) chargé(s) dans ${Object.keys(datasetMap).length} dataset(s)`);
}

function showDocumentDetails(doc) {
    addLog('info', `Détails document: ${doc.id}`);
    
    // Basculer vers la vue fichier
    const chatContainer = document.querySelector('.chat-container');
    
    // Créer ou récupérer le conteneur de fichier
    let fileViewer = document.getElementById('file-viewer');
    if (!fileViewer) {
        fileViewer = document.createElement('div');
        fileViewer.id = 'file-viewer';
        fileViewer.className = 'file-viewer hidden';
        
        // Header du viewer
        const header = document.createElement('div');
        header.className = 'file-viewer-header';
        header.innerHTML = `
            <span id="file-viewer-filename">filename.txt</span>
            <button class="btn-close-file" onclick="closeFileViewer()">
                <i class="fas fa-times"></i> Fermer
            </button>
        `;
        
        // Contenu du viewer
        const content = document.createElement('pre');
        content.id = 'file-viewer-content';
        
        fileViewer.appendChild(header);
        fileViewer.appendChild(content);
        
        // Insérer après le chat
        chatContainer.parentNode.insertBefore(fileViewer, chatContainer.nextSibling);
    }

    // Afficher le contenu
    const filename = doc.metadata && doc.metadata.filename ? doc.metadata.filename : doc.id;
    document.getElementById('file-viewer-filename').textContent = filename;
    document.getElementById('file-viewer-content').textContent = doc.content;
    
    // Masquer chat, afficher viewer
    chatContainer.classList.add('hidden');
    fileViewer.classList.remove('hidden');
}

function getFileIcon(filename) {
    if (filename.endsWith('.py')) return 'fa-python';
    if (filename.endsWith('.js')) return 'fa-js';
    if (filename.endsWith('.html')) return 'fa-html5';
    if (filename.endsWith('.css')) return 'fa-css3';
    if (filename.endsWith('.md')) return 'fa-markdown';
    if (filename.endsWith('.json')) return 'fa-code';
    if (filename.endsWith('.txt')) return 'fa-file-alt';
    return 'fa-file';
}

async function openFile(path) {
    addLog('info', `Ouverture du fichier: ${path}`);
    
    // Basculer vers la vue fichier
    const chatContainer = document.querySelector('.chat-container');
    
    // Créer ou récupérer le conteneur de fichier
    let fileViewer = document.getElementById('file-viewer');
    if (!fileViewer) {
        fileViewer = document.createElement('div');
        fileViewer.id = 'file-viewer';
        fileViewer.className = 'file-viewer hidden';
        
        // Header du viewer
        const header = document.createElement('div');
        header.className = 'file-viewer-header';
        header.innerHTML = `
            <span id="file-viewer-filename">filename.txt</span>
            <button class="btn-close-file" onclick="closeFileViewer()">
                <i class="fas fa-times"></i> Fermer
            </button>
        `;
        
        // Contenu du viewer
        const content = document.createElement('pre');
        content.id = 'file-viewer-content';
        
        fileViewer.appendChild(header);
        fileViewer.appendChild(content);
        
        // Insérer après le chat
        chatContainer.parentNode.insertBefore(fileViewer, chatContainer.nextSibling);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/files/read`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (data.status === 'error') throw new Error(data.error);

        // Afficher le contenu
        document.getElementById('file-viewer-filename').textContent = path;
        document.getElementById('file-viewer-content').textContent = data.content;
        
        // Masquer chat, afficher viewer
        chatContainer.classList.add('hidden');
        fileViewer.classList.remove('hidden');
        
        addLog('success', `Fichier chargé: ${path}`);

    } catch (error) {
        addLog('error', `Erreur lecture fichier: ${error.message}`);
        alert(`Impossible d'ouvrir le fichier: ${error.message}`);
    }
}

function closeFileViewer() {
    const chatContainer = document.querySelector('.chat-container');
    const fileViewer = document.getElementById('file-viewer');
    
    if (chatContainer && fileViewer) {
        fileViewer.classList.add('hidden');
        chatContainer.classList.remove('hidden');
    }
}

// ============ RACCOURCIS CLAVIER ============

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ignorer si on est dans un champ de saisie (sauf pour CTRL+ENTER)
        const isInputField = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';
        
        // F1 : Toggle Micro UNIQUE (Désactivé temporairement)
        if (e.key === 'F1') {
            e.preventDefault();
            // toggleMicrophone();
            addLog('info', 'Audio désactivé temporairement');
            return;
        }
        
        // F5 : Réinitialiser chat
        if (e.key === 'F5') {
            e.preventDefault();
            resetChat();
            return;
        }
        
        // F12 : Ouvrir/fermer logs
        if (e.key === 'F12') {
            e.preventDefault();
            toggleFullLogs();
            return;
        }
        
        // CTRL+ENTER : Envoyer message (géré dans l'input mais aussi globalement)
        if (e.ctrlKey && e.key === 'Enter' && !isInputField) {
            e.preventDefault();
            document.getElementById('user-message').focus();
            return;
        }
    });
    
    addLog('success', '⌨️ Raccourcis clavier activés (F1=Micro, F5=Reset, F12=Logs)');
}

async function activateMicrophone() {
    if (isRecording) {
        return; // Déjà actif
    }

    // Si TTS parle, on l'arrête pour écouter (optionnel, mais logique pour un toggle)
    if (isTTSSpeaking && currentAudioElement) {
        currentAudioElement.pause();
        currentAudioElement = null;
        isTTSSpeaking = false;
        updateTTSIndicator(false);
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendVoiceMessage(audioBlob);
            
            // Arrêter le stream
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        
        addLog('success', '🎤 Micro ON (F1)');
        appendChat('system', '🎤 Micro ON...');
        
        // Mettre à jour le bouton micro si présent
        updateMicButton();

    } catch (error) {
        addLog('error', `❌ Erreur microphone: ${error.message}`);
        appendChat('error', `Impossible d'accéder au microphone: ${error.message}`);
    }
}

function stopMicrophone() {
    if (isRecording && mediaRecorder) {
        mediaRecorder.stop();
        isRecording = false;
        
        addLog('info', '🎤 Micro OFF (F1)');
        
        // Mettre à jour le bouton micro si présent
        updateMicButton();
    }
}

async function sendVoiceMessage(audioBlob) {
    addLog('info', '📤 Envoi de l\'audio au serveur...');
    updateBackendStatus('waiting');

    try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'speech.webm');
        // On passe le session_id
        const url = `${API_BASE_URL}/voice/listen?session_id=${sessionId}`;

        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Afficher le texte transcrit
        if (data.user_text) {
            appendChat('user', `🎤 ${data.user_text}`);
            addLog('success', `Transcription: "${data.user_text}"`);
        }

        // Afficher la réponse de l'agent et la lire à voix haute
        if (data.reply_text) {
            appendChat('agent', data.reply_text);
            addLog('success', 'Réponse vocale reçue');
            
            // Lire la réponse à voix haute
            await speakText(data.reply_text);
        }

        updateBackendStatus('connected');

    } catch (error) {
        const errorMsg = `Erreur vocale: ${error.message}`;
        appendChat('error', errorMsg);
        addLog('error', errorMsg);
        updateBackendStatus('disconnected');
    }
}

function updateMicButton() {
    const micButton = document.getElementById('mic-button');
    if (micButton) {
        if (isRecording) {
            micButton.classList.add('recording');
            micButton.title = 'Micro ON (F1)';
            micButton.innerHTML = '🎤 ON'; // Visuel clair
        } else {
            micButton.classList.remove('recording');
            micButton.title = 'Micro OFF (F1)';
            micButton.innerHTML = '🎤 OFF';
        }
    }
}

async function speakText(text) {
    /**
     * Fait parler l'agent à voix haute via TTS.
     */
    if (!text || text.trim().length === 0) {
        return;
    }

    // Si le micro est actif, on le coupe (Règle 2: Micro OFF pendant TTS)
    if (isRecording) {
        stopMicrophone();
    }

    addLog('info', '🔊 Génération de la voix...');
    
    try {
        // Marquer TTS comme actif
        isTTSSpeaking = true;
        updateTTSIndicator(true);

        // Demander l'audio au serveur
        const response = await fetch(`${API_BASE_URL}/voice/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Créer un élément audio et le jouer
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        currentAudioElement = new Audio(audioUrl);
        
        // Gérer la fin de la lecture
        currentAudioElement.onended = async () => {
            addLog('success', '🔊 TTS terminé');
            isTTSSpeaking = false;
            updateTTSIndicator(false);
            
            // Libérer la mémoire
            URL.revokeObjectURL(audioUrl);
            currentAudioElement = null;
            
            // PAS de reprise automatique du micro (Règle 1 & 2)
        };

        currentAudioElement.onerror = (error) => {
            addLog('error', `Erreur lecture audio: ${error}`);
            isTTSSpeaking = false;
            updateTTSIndicator(false);
        };

        // Lancer la lecture
        await currentAudioElement.play();
        addLog('success', '🔊 Lecture TTS démarrée');

    } catch (error) {
        addLog('error', `Erreur TTS: ${error.message}`);
        isTTSSpeaking = false;
        updateTTSIndicator(false);
    }
}

function updateTTSIndicator(speaking) {
    /**
     * Met à jour l'indicateur visuel du TTS.
     */
    const micButton = document.getElementById('mic-button');
    if (micButton) {
        if (speaking) {
            micButton.classList.add('tts-speaking');
            micButton.title = 'Agent parle...';
        } else {
            micButton.classList.remove('tts-speaking');
            // updateMicButton se chargera de remettre le bon état
            updateMicButton();
        }
    }
}

function toggleMicrophone() {
    /**
     * Toggle microphone ON/OFF (F1).
     * Simple : ON → OFF, OFF → ON
     */
    if (isRecording) {
        stopMicrophone();
    } else {
        activateMicrophone();
    }
}

function resetChat() {
    // Effacer le chat et réinitialiser la session
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = '';

    // Effacer aussi le chat flottant
    const floatingChat = document.getElementById('floating-chat-window');
    if (floatingChat) floatingChat.innerHTML = '';
    
    // Générer une nouvelle session
    sessionId = generateSessionId();
    document.getElementById('session-id').textContent = sessionId;
    
    addLog('success', '🔄 Chat réinitialisé (F5) - Nouvelle session créée');
    appendChat('system', '🔄 Chat réinitialisé - Nouvelle session démarrée');
    
    // Vérifier la santé du backend
    testHealth();
}

// ============ CONVERSATION ============

async function sendMessage() {
    const input = document.getElementById('user-message');
    const message = input.value.trim();

    // Protection : vérifier que le message n'est pas vide
    if (!message) {
        addLog('warning', 'Message vide - envoi annulé');
        return;
    }

    // Mettre à jour l'état pour l'envoi
    updateAgentState('Chat', 'Envoi message', 'conversation', 'processing');

    // Afficher message utilisateur
    appendChat('user', message);
    input.value = '';
    
    // Clear floating input too if it matches
    const floatingInput = document.getElementById('floating-user-message');
    if (floatingInput) floatingInput.value = '';

    // Ajouter log
    addLog('info', `Message envoyé: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);

    // Mettre à jour le statut
    updateBackendStatus('waiting');

    try {
        const response = await fetch(`${API_BASE_URL}/orchestrate/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message,
                session_id: sessionId,
                execution_mode: "auto"
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Afficher réponse
        const reply = data.response || JSON.stringify(data);
        appendChat('agent', reply);

        // Mettre à jour l'état pour la réponse reçue
        updateAgentState('Agent', 'Réponse générée', 'orchestrator', 'active');
        addLog('success', 'Réponse reçue de l\'agent');
        updateBackendStatus('connected');
        
        // Lire la réponse à voix haute automatiquement (Désactivé)
        // await speakText(reply);

    } catch (error) {
        const errorMsg = `Erreur: ${error.message}`;
        appendChat('error', errorMsg);
        addLog('error', `Échec de l'envoi: ${error.message}`);
        updateBackendStatus('disconnected');
    }
}

function appendChat(type, text) {
    // 1. Main Chat Window
    const chatWindow = document.getElementById('chat-window');
    const messageDiv = document.createElement('div');

    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;

    // Ajouter timestamp
    const timeSpan = document.createElement('div');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString('fr-FR');
    messageDiv.appendChild(timeSpan);

    chatWindow.appendChild(messageDiv);

    // Auto-scroll Main
    if (autoScroll) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // 2. Floating Chat Window (Sync)
    const floatingChat = document.getElementById('floating-chat-window');
    if (floatingChat) {
        const floatMsg = messageDiv.cloneNode(true);
        floatingChat.appendChild(floatMsg);
        floatingChat.scrollTop = floatingChat.scrollHeight;
    }
}

// ============ RAG ============

async function addToRAG() {
    const dataset = document.getElementById('dataset').value.trim();
    const text = document.getElementById('rag-text').value.trim();

    // Protection : vérifier que les champs ne sont pas vides
    if (!dataset) {
        alert('⚠️ Le nom du dataset est obligatoire');
        addLog('warning', 'RAG: Dataset manquant');
        return;
    }

    if (!text) {
        alert('⚠️ Le contenu à ajouter est obligatoire');
        addLog('warning', 'RAG: Contenu manquant');
        return;
    }

    addLog('info', `RAG: Ajout au dataset "${dataset}" (${text.length} caractères)`);
    updateBackendStatus('waiting');

    try {
        const response = await fetch(`${API_BASE_URL}/rag/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset: dataset,
                filename: `note_${Date.now()}.txt`,
                content: text
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        alert(`✅ Contenu ajouté au dataset "${dataset}"`);
        document.getElementById('rag-text').value = '';

        addLog('success', `RAG: Contenu ajouté avec succès`);
        updateBackendStatus('connected');

    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
        addLog('error', `RAG: Échec de l'ajout - ${error.message}`);
        updateBackendStatus('disconnected');
    }
}

async function askRAG() {
    const dataset = document.getElementById('dataset').value.trim();
    const question = document.getElementById('rag-question').value.trim();

    // Protection : vérifier que les champs ne sont pas vides
    if (!dataset) {
        alert('⚠️ Le nom du dataset est obligatoire');
        addLog('warning', 'RAG: Dataset manquant');
        return;
    }

    if (!question) {
        alert('⚠️ La question est obligatoire');
        addLog('warning', 'RAG: Question manquante');
        return;
    }

    // Mettre à jour l'état pour la requête RAG
    updateAgentState('RAG', 'Requête base de connaissances', dataset, 'processing');
    addLog('info', `RAG: Question sur "${dataset}"`);

    // Afficher loading
    const answerDiv = document.getElementById('rag-answer');
    answerDiv.textContent = '⏳ Recherche en cours...';
    answerDiv.classList.add('loading');

    updateBackendStatus('waiting');

    try {
        const response = await fetch(`${API_BASE_URL}/rag/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset: dataset,
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Formater la réponse
        let output = `📝 Réponse:\n${data.answer}\n\n`;

        if (data.chunks && data.chunks.length > 0) {
            output += `📚 Passages utilisés (${data.chunks.length}):\n`;
            data.chunks.forEach((chunk, i) => {
                output += `\n[${i + 1}] ${chunk.substring(0, 150)}...\n`;
            });
        }

        answerDiv.textContent = output;
        addLog('success', `RAG: Réponse obtenue (${data.chunks?.length || 0} chunks)`);
        updateBackendStatus('connected');

    } catch (error) {
        answerDiv.textContent = `❌ Erreur: ${error.message}`;
        addLog('error', `RAG: Échec de la requête - ${error.message}`);
        updateBackendStatus('disconnected');
    } finally {
        answerDiv.classList.remove('loading');
    }
}

// ============ FONCTIONS UTILITAIRES ============

async function testHealth() {
    addLog('info', 'Test de santé du backend...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === 'ok') {
            addLog('success', '✅ Backend opérationnel');
            updateBackendStatus('connected');
        } else {
            addLog('warning', `⚠️ Backend répond mais statut: ${data.status}`);
            updateBackendStatus('waiting');
        }

    } catch (error) {
        addLog('error', `❌ Backend indisponible: ${error.message}`);
        updateBackendStatus('disconnected');
    }
}

async function showMemory() {
    addLog('info', `Récupération de la mémoire pour session: ${sessionId}`);
    updateBackendStatus('waiting');

    try {
        const response = await fetch(`${API_BASE_URL}/memory/${sessionId}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            addLog('success', `📚 Mémoire: ${data.history.length} messages trouvés`);
            
            // Afficher un résumé dans les logs
            data.history.slice(0, 3).forEach((msg, i) => {
                const preview = msg.content ? msg.content.substring(0, 50) : 'N/A';
                addLog('info', `  [${i + 1}] ${msg.role}: ${preview}...`);
            });
            
            if (data.history.length > 3) {
                addLog('info', `  ... et ${data.history.length - 3} autres messages`);
            }
        } else {
            addLog('info', '📭 Aucun message en mémoire pour cette session');
        }

        updateBackendStatus('connected');

    } catch (error) {
        addLog('error', `❌ Échec récupération mémoire: ${error.message}`);
        updateBackendStatus('disconnected');
    }
}

function clearChat() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = '';
    
    const floatingChat = document.getElementById('floating-chat-window');
    if (floatingChat) floatingChat.innerHTML = '';

    addLog('info', '🗑️ Chat effacé (mémoire backend conservée)');
}

function openRAG() {
    addLog('info', 'Ouverture de l\'interface RAG...');
    
    try {
        // Ouvrir l'interface RAG dans un nouvel onglet
        const ragUrl = `${API_BASE_URL}/ui/rag`;
        window.open(ragUrl, '_blank');
        addLog('success', 'Interface RAG ouverte dans un nouvel onglet');
    } catch (error) {
        addLog('error', `Échec ouverture RAG: ${error.message}`);
    }
}

async function stopAgent() {
    // Demander confirmation
    const confirmed = confirm(
        '⚠️ Êtes-vous sûr de vouloir arrêter l\'agent?\n\n' +
        'Cela fermera le serveur backend et vous devrez le redémarrer manuellement.'
    );
    
    if (!confirmed) {
        addLog('info', 'Arrêt annulé par l\'utilisateur');
        return;
    }
    
    addLog('warning', '🛑 Arrêt de l\'agent en cours...');
    updateBackendStatus('waiting');
    
    try {
        const response = await fetch(`${API_BASE_URL}/shutdown`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        addLog('success', '✅ ' + data.message);
        appendChat('system', '🛑 L\'agent s\'arrête. Vous pouvez fermer cette fenêtre.');
        
        // Mettre à jour le statut après un court délai
        setTimeout(() => {
            updateBackendStatus('disconnected');
            addLog('info', 'Backend arrêté. Rechargez la page après redémarrage.');
        }, 1000);
        
    } catch (error) {
        // Si l'erreur est une déconnexion réseau, c'est normal (le serveur s'est arrêté)
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            addLog('success', '✅ Agent arrêté avec succès');
            appendChat('system', '🛑 L\'agent est arrêté. Vous pouvez fermer cette fenêtre.');
            updateBackendStatus('disconnected');
        } else {
            addLog('error', `❌ Erreur lors de l'arrêt: ${error.message}`);
            updateBackendStatus('disconnected');
        }
    }
}

async function checkActiveSessions() {
    addLog('info', '🔍 Vérification des sessions actives...');
    
    try {
        // Tenter de se connecter au backend
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            addLog('success', '✅ Une session est active sur le port 8000');
            appendChat('system', '✅ Session active détectée - Backend opérationnel');
            
            // Vérifier les processus Python (optionnel, nécessite un endpoint dédié)
            addLog('info', 'Session ID actuelle: ' + sessionId);
        } else {
            addLog('warning', '⚠️ Backend répond mais avec un statut inhabituel');
        }
        
    } catch (error) {
        addLog('info', '❌ Aucune session active détectée sur le port 8000');
        appendChat('system', '❌ Aucune session active - Le backend est arrêté');
    }
}

function ensureSession() {
    // Vérifier que la session existe et est valide
    if (!sessionId || sessionId.length < 10) {
        sessionId = generateSessionId();
        document.getElementById('session-id').textContent = sessionId;
        addLog('warning', 'Session régénérée');
    }
    return sessionId;
}

// ============ LOGS ============

function addLog(level, message) {
    const timestamp = new Date().toLocaleTimeString('fr-FR');
    
    // Coloration selon le niveau
    let levelIcon = '';
    
    switch(level) {
        case 'success': levelIcon = '✓'; break;
        case 'error': levelIcon = '✗'; break;
        case 'warning': levelIcon = '⚠'; break;
        case 'info': levelIcon = 'ℹ'; break;
    }

    // 1. Détecter l'état de l'agent à partir du log
    detectStateFromLog(message, level);

    // 2. Update Timeline (Nouvelle implémentation temps réel)
    renderTimeline();

    // 3. Update Status Card (Enhanced)
    updateStatusCardEnhanced(level, message);

    // Add to recent logs array for banner
    const logData = {
        timestamp,
        level,
        levelIcon,
        message,
        time: Date.now()
    };
    
    recentLogs.push(logData);
    
    // Keep only last 10 logs
    if (recentLogs.length > MAX_BANNER_LOGS) {
        recentLogs.shift();
    }
    
    // Update banner
    updateLogBanner();
    
    // Also update old logs window if it exists (for backward compatibility)
    const logsWindow = document.getElementById('logs-window');
    if (logsWindow) {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';

        logEntry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-level ${level}">${levelIcon} ${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;

        logsWindow.appendChild(logEntry);

        // Auto-scroll si activé
        if (autoScroll) {
            logsWindow.scrollTop = logsWindow.scrollHeight;
        }

        // Limiter à 100 logs
        while (logsWindow.children.length > 100) {
            logsWindow.removeChild(logsWindow.firstChild);
        }
    }
}

function updateLogBanner() {
    const banner = document.getElementById('status-log-banner');
    if (!banner) return;
    
    const logsContainer = banner.querySelector('.banner-logs');
    if (!logsContainer) return;
    
    // Clear current logs
    logsContainer.innerHTML = '';
    
    // Display logs in chronological order (oldest first)
    recentLogs.forEach(log => {
        const logItem = document.createElement('div');
        logItem.className = `banner-log-item banner-log-${log.level}`;
        
        logItem.innerHTML = `
            <span class="banner-log-time">${log.timestamp}</span>
            <span class="banner-log-level">${log.levelIcon} ${log.level.toUpperCase()}</span>
            <span class="banner-log-message">${log.message}</span>
        `;
        
        logsContainer.appendChild(logItem);
    });
    
    // Auto-scroll to show latest logs
    logsContainer.scrollLeft = logsContainer.scrollWidth;
}

// ============ TIMELINE TEMPS RÉEL AVANCÉE ============

function startRealTimeTracking() {
    // Démarrer le tracking continu de l'agent
    if (activityTracker) clearInterval(activityTracker);
    
    activityTracker = setInterval(() => {
        updateAgentState();
        renderTimeline();
    }, 1000); // Mise à jour chaque seconde

    // Démarrer la détection d'inactivité
    startIdleDetection();
    
    // État initial
    updateAgentState('initialisation', 'Interface', 'frontend', 'Chargement initial');
}

function updateAgentState(tool = null, location = null, action = null, status = null) {
    const now = Date.now();
    
    // Si des paramètres sont fournis, mettre à jour l'état
    if (tool) {
        currentTool = tool;
        currentLocation = location || '';
        currentAction = action || 'Activité en cours';
        agentState = status || 'active';
        lastActivityTime = now;
        
        // Ajouter à l'historique
        addToActivityLog(tool, currentAction, currentLocation, now);
    }
    
    // Détecter l'inactivité (pas d'activité depuis 30 secondes)
    const idleTime = now - lastActivityTime;
    if (idleTime > 30000 && agentState !== 'idle') {
        agentState = 'idle';
        currentTool = 'Aucun';
        currentAction = 'En attente';
        currentLocation = 'aucun';
    }
    
    // Détecter un bug prolongé (plus de 2 minutes sans activité utile)
    if (idleTime > 120000) {
        agentState = 'error';
        currentAction = 'Possiblement bloqué';
    }
}

function addToActivityLog(tool, action, location, timestamp) {
    // Éviter les doublons consécutifs
    const lastEntry = activityLog[activityLog.length - 1];
    if (lastEntry && lastEntry.tool === tool && lastEntry.action === action && lastEntry.location === location) {
        return;
    }
    
    // Calculer la durée de l'activité précédente
    if (lastEntry) {
        lastEntry.duration = timestamp - lastEntry.startTime;
    }
    
    // Ajouter la nouvelle entrée
    activityLog.push({
        tool,
        action,
        location,
        startTime: timestamp,
        duration: 0 // Sera calculé à la prochaine entrée
    });
    
    // Limiter l'historique à 20 entrées
    if (activityLog.length > 20) {
        activityLog.shift();
    }
}

function startIdleDetection() {
    if (idleTimer) clearTimeout(idleTimer);
    
    idleTimer = setTimeout(() => {
        if (agentState === 'active' && Date.now() - lastActivityTime > 45000) {
            updateAgentState('Système', 'temps réel', 'Surveillance inactive', 'idle');
            renderTimeline();
        }
    }, 50000); // Vérification toutes les 50 secondes
}

function renderTimeline() {
    const track = document.getElementById('timeline-track');
    if (!track) return;

    track.innerHTML = ''; // Vider complètement
    
    const now = Date.now();
    const recentActivities = getRecentActivities(now);
    
    // Créer la timeline continue
    recentActivities.forEach((activity, index) => {
        const node = createTimelineNode(activity, index === recentActivities.length - 1, now);
        track.appendChild(node);
    });
    
    // Auto-scroll pour montrer les derniers éléments
    track.scrollLeft = track.scrollWidth;
}

function getRecentActivities(now) {
    const activities = [];
    const lookbackTime = 60000; // 1 minute de lookback
    
    // Ajouter l'activité actuelle
    const currentActivity = {
        tool: currentTool,
        action: currentAction,
        location: currentLocation,
        startTime: Math.max(lastActivityTime, now - 5000), // Au moins 5 secondes
        duration: 0,
        isActive: true
    };
    activities.push(currentActivity);
    
    // Ajouter les activités récentes de l'historique
    const recentHistory = activityLog.filter(activity => 
        now - activity.startTime < lookbackTime && activity.duration > 2000 // Au moins 2 secondes
    );
    
    // Fusionner et trier par temps
    activities.push(...recentHistory);
    activities.sort((a, b) => b.startTime - a.startTime);
    
    // Limiter à 10 activités max
    return activities.slice(0, 10);
}

function createTimelineNode(activity, isActive, now) {
    const node = document.createElement('div');
    const isIdle = activity.tool === 'Aucun';
    const hasError = agentState === 'error' && isActive;
    const duration = activity.duration || (now - activity.startTime);
    
    node.className = `timeline-node ${isActive ? 'active' : ''} ${hasError ? 'error' : ''}`;
    
    // Icône selon l'outil
    const icon = getToolIcon(activity.tool);
    const timeDisplay = formatDuration(duration);
    
    node.innerHTML = `
        <div class="timeline-node-header">
            <div class="timeline-node-icon ${isIdle ? 'idle' : ''}">${icon}</div>
            <div class="timeline-node-tool">${activity.tool}</div>
        </div>
        <div class="timeline-node-action">${activity.action}</div>
        <div class="timeline-node-location">${activity.location}</div>
        <div class="timeline-node-footer">
            <div class="timeline-node-duration">${timeDisplay}</div>
            <div class="timeline-node-time">${new Date(activity.startTime).toLocaleTimeString('fr-FR', { hour12: false })}</div>
        </div>
    `;
    
    return node;
}

function getToolIcon(tool) {
    const icons = {
        'Chat': '💬',
        'Web Search': '🌐',
        'RAG': '📚',
        'Fichiers': '📁',
        'Audio': '🎤',
        'TTS': '🔊',
        'Agent': '🤖',
        'Backend': '💚',
        'Interface': '🖥️',
        'Système': '⚙️',
        'Aucun': '⏳',
        'Erreur': '❌',
        'Vision': '👁️',
        'Contrôle PC': '🖱️',
        'MouseController': '🖱️'
    };
    return icons[tool] || '⚡';
}

function formatDuration(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    
    if (minutes > 0) {
        return `${minutes}m${seconds % 60}s`;
    } else {
        return `${seconds}s`;
    }
}

// Fonction pour détecter les changements d'état à partir des logs
function detectStateFromLog(message, level) {
    let tool = currentTool;
    let action = currentAction;
    let location = currentLocation;
    let status = agentState;
    
    // Détection intelligente basée sur le message
    if (message.includes('Backend opérationnel') || message.includes('Interface chargée')) {
        tool = 'Système';
        action = 'Initialisation';
        location = 'système';
        status = 'active';
    }
    else if (message.includes('search') || message.includes('recherche')) {
        tool = 'Web Search';
        action = 'Recherche';
        const match = message.match(/["'](.+?)["']/);
        location = match ? match[1] : 'web';
        status = 'processing';
    }
    else if (message.includes('RAG')) {
        tool = 'RAG';
        if (message.includes('Ajout') || message.includes('ajouté')) {
            action = 'Ajout document';
        } else if (message.includes('Question') || message.includes('query')) {
            action = 'Requête';
        }
        location = 'base de connaissances';
        status = 'processing';
    }
    else if (message.includes('fichier') || message.includes('Ouverture')) {
        tool = 'Fichiers';
        action = 'Lecture fichier';
        const match = message.match(/:\s*(.+?)$/);
        location = match ? match[1] : 'système';
        status = 'processing';
    }
    else if (message.includes('Message envoyé')) {
        tool = 'Chat';
        action = 'Envoi message';
        location = 'conversation';
        status = 'processing';
    }
    else if (message.includes('Réponse reçue')) {
        tool = 'Agent';
        action = 'Génération réponse';
        location = 'orchestrator';
        status = 'active';
    }
    else if (message.includes('Micro') || message.includes('🎤')) {
        tool = 'Audio';
        action = message.includes('ON') ? 'Écoute vocale' : 'Audio inactif';
        location = 'microphone';
        status = 'active';
    }
    else if (level === 'error') {
        tool = 'Erreur';
        action = message.substring(0, 30);
        location = 'système';
        status = 'error';
    }
    
    updateAgentState(tool, location, action, status);
}

function updateStatusCardEnhanced(level, message) {
    const statusText = document.getElementById('agent-status-text');
    const detailText = document.getElementById('current-action-detail');
    
    if (!statusText || !detailText) return;

    // Utiliser l'état intelligent de l'agent
    let statusDisplay = '';
    let statusColor = '';
    let statusIcon = '';
    
    switch (agentState) {
        case 'active':
            statusDisplay = 'Actif';
            statusColor = '#10b981';
            statusIcon = '🟢';
            break;
        case 'processing':
            statusDisplay = 'Traitement';
            statusColor = '#f59e0b';
            statusIcon = '🟡';
            break;
        case 'idle':
            statusDisplay = 'En attente';
            statusColor = '#6b7280';
            statusIcon = '⏳';
            break;
        case 'error':
            statusDisplay = 'Erreur';
            statusColor = '#ef4444';
            statusIcon = '🔴';
            break;
        default:
            statusDisplay = 'Inconnu';
            statusColor = '#9ca3af';
            statusIcon = '⚫';
    }
    
    statusText.innerHTML = `
        <span class="status-dot" style="background:${statusColor}; box-shadow:0 0 8px ${statusColor};"></span> 
        ${statusDisplay}
    `;
    statusText.style.color = statusColor;
    
    // Afficher l'outil actuel et l'action
    let enhancedMessage = `${currentTool}: ${currentAction}`;
    if (currentLocation && currentLocation !== 'aucun') {
        enhancedMessage += ` (${currentLocation})`;
    }
    
    // Ajouter le message original pour le contexte
    if (message && !message.includes(currentAction)) {
        enhancedMessage += ` - ${message}`;
    }
    
    detailText.textContent = enhancedMessage;
}

function startSessionTimer() {
    if (timerInterval) clearInterval(timerInterval);
    sessionTimer = 0;
    const display = document.getElementById('timer-display');
    
    timerInterval = setInterval(() => {
        sessionTimer++;
        const hours = Math.floor(sessionTimer / 3600);
        const minutes = Math.floor((sessionTimer % 3600) / 60);
        const seconds = sessionTimer % 60;
        
        if (display) {
            display.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

// ============ STATUT BACKEND ============

function updateBackendStatus(status) {
    backendStatus = status;
    
    // Si un élément status-bar existe, le mettre à jour
    const statusBar = document.getElementById('status-bar');
    if (statusBar) {
        let statusText = '';
        let statusClass = '';
        
        switch(status) {
            case 'connected':
                statusText = '🟢 Connecté';
                statusClass = 'status-connected';
                break;
            case 'waiting':
                statusText = '🟡 En attente';
                statusClass = 'status-waiting';
                break;
            case 'disconnected':
                statusText = '🔴 Backend indisponible';
                statusClass = 'status-disconnected';
                break;
            default:
                statusText = '⚪ Statut inconnu';
                statusClass = 'status-unknown';
        }
        
        statusBar.textContent = statusText;
        statusBar.className = `status-bar ${statusClass}`;
    }
}

// ============ UTILS ============

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
}

// Log les erreurs globales
window.addEventListener('error', (e) => {
    addLog('error', `Erreur JS: ${e.message}`);
});

window.addEventListener('unhandledrejection', (e) => {
    addLog('error', `Promise rejetée: ${e.reason}`);
});

// Vérifier périodiquement la santé du backend (toutes les 30 secondes)
setInterval(() => {
    if (backendStatus === 'disconnected') {
        testHealth();
    }
}, 30000);

// ============ FLOATING INTERFACE ============

function toggleFloatingInterface() {
    const floatingInterface = document.getElementById('floating-interface');
    if (floatingInterface) {
        floatingInterface.classList.toggle('hidden');
        const isHidden = floatingInterface.classList.contains('hidden');
        addLog('info', `Interface flottante ${isHidden ? 'masquée' : 'affichée'} (F2)`);
        
        if (!isHidden) {
            setTimeout(() => document.getElementById('floating-user-message').focus(), 100);
        }
    }
}

async function sendFloatingMessage() {
    const input = document.getElementById('floating-user-message');
    const message = input.value.trim();

    if (!message) return;

    // Utiliser la logique existante
    // On met le message dans l'input principal pour simuler
    const mainInput = document.getElementById('user-message');
    mainInput.value = message;
    
    // On appelle sendMessage qui va gérer l'affichage et l'envoi
    await sendMessage();
    
    // On vide l'input flottant (sendMessage le fait déjà mais par sécurité)
    input.value = '';
}

function setupDraggableInterface() {
    const elmnt = document.getElementById('floating-interface');
    const header = document.getElementById('floating-header');
    
    if (!elmnt || !header) return;

    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    header.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // Get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // Call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // Calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // Set the element's new position:
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
        
        // Reset bottom/right to auto to allow top/left positioning
        elmnt.style.bottom = 'auto';
        elmnt.style.right = 'auto';
    }

    function closeDragElement() {
        // Stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

// ============ TODO LIST / SÉQUENCES D'ACTIONS ============

function validateTodoSequence() {
    /**
     * Valide et crée une séquence TODO à partir du message utilisateur
     */
    const input = document.getElementById('user-message');
    const message = input.value.trim();
    
    if (!message) {
        addLog('warning', 'Aucun message à valider comme TODO');
        return;
    }
    
    // Détecter si le message contient plusieurs étapes
    const steps = detectStepsInMessage(message);
    
    if (steps.length === 0) {
        // Message simple, créer un seul TODO
        addTodo(message, 'Action unique');
    } else {
        // Message avec plusieurs étapes
        steps.forEach((step, index) => {
            addTodo(step.title, step.description, index === 0 ? 'in-progress' : 'pending');
        });
    }
    
    // Vider l'input
    input.value = '';
    
    addLog('success', `Séquence TODO créée avec ${steps.length || 1} étape(s)`);
    appendChat('system', `✅ Séquence d'actions créée avec ${steps.length || 1} étape(s)`);
}

function detectStepsInMessage(message) {
    /**
     * Détecte les étapes dans un message
     * Cherche des patterns comme:
     * - Numéros: 1. 2. 3.
     * - Tirets: - étape 1 - étape 2
     * - Mots-clés: "puis", "ensuite", "après"
     */
    const steps = [];
    
    // Pattern 1: Numéros (1. 2. 3. ou 1) 2) 3))
    const numberedPattern = /(?:^|\n)\s*(\d+)[.)]\s*(.+?)(?=\n\s*\d+[.)]|\n\n|$)/gs;
    let match;
    
    while ((match = numberedPattern.exec(message)) !== null) {
        steps.push({
            title: match[2].trim().substring(0, 100),
            description: match[2].trim().length > 100 ? '...' : ''
        });
    }
    
    // Pattern 2: Tirets ou puces
    if (steps.length === 0) {
        const bulletPattern = /(?:^|\n)\s*[-•*]\s*(.+?)(?=\n\s*[-•*]|\n\n|$)/gs;
        while ((match = bulletPattern.exec(message)) !== null) {
            steps.push({
                title: match[1].trim().substring(0, 100),
                description: match[1].trim().length > 100 ? '...' : ''
            });
        }
    }
    
    // Pattern 3: Mots-clés de séquence
    if (steps.length === 0) {
        const sequenceWords = ['puis', 'ensuite', 'après', 'enfin', 'finalement'];
        const parts = message.split(new RegExp(`\\b(${sequenceWords.join('|')})\\b`, 'gi'));
        
        if (parts.length > 2) {
            for (let i = 0; i < parts.length; i += 2) {
                const part = parts[i].trim();
                if (part && part.length > 5) {
                    steps.push({
                        title: part.substring(0, 100),
                        description: part.length > 100 ? '...' : ''
                    });
                }
            }
        }
    }
    
    return steps;
}

function addTodo(title, description = '', status = 'pending') {
    /**
     * Ajoute un TODO à la liste
     * @param {string} title - Titre du TODO
     * @param {string} description - Description optionnelle
     * @param {string} status - 'pending', 'in-progress', 'completed'
     */
    const todo = {
        id: currentTodoId++,
        title: title,
        description: description,
        status: status,
        createdAt: Date.now()
    };
    
    todoList.push(todo);
    renderTodoList();
    
    addLog('info', `TODO ajouté: ${title.substring(0, 50)}`);
}

function updateTodoStatus(todoId, newStatus) {
    /**
     * Met à jour le statut d'un TODO
     */
    const todo = todoList.find(t => t.id === todoId);
    if (!todo) return;
    
    const oldStatus = todo.status;
    todo.status = newStatus;
    
    renderTodoList();
    
    addLog('success', `TODO ${todoId} : ${oldStatus} → ${newStatus}`);
    
    // Si terminé, passer au suivant automatiquement
    if (newStatus === 'completed') {
        const nextTodo = todoList.find(t => t.status === 'pending');
        if (nextTodo) {
            setTimeout(() => {
                updateTodoStatus(nextTodo.id, 'in-progress');
            }, 500);
        }
    }
}

function removeTodo(todoId) {
    /**
     * Supprime un TODO de la liste
     */
    const index = todoList.findIndex(t => t.id === todoId);
    if (index !== -1) {
        todoList.splice(index, 1);
        renderTodoList();
        addLog('info', `TODO ${todoId} supprimé`);
    }
}

function clearCompletedTodos() {
    /**
     * Supprime tous les TODO terminés
     */
    const completedCount = todoList.filter(t => t.status === 'completed').length;
    todoList = todoList.filter(t => t.status !== 'completed');
    renderTodoList();
    addLog('success', `${completedCount} TODO(s) terminé(s) supprimé(s)`);
}

function renderTodoList() {
    /**
     * Affiche la liste des TODO dans l'interface
     */
    const container = document.getElementById('todo-list');
    if (!container) return;
    
    // Vider le conteneur
    container.innerHTML = '';
    
    if (todoList.length === 0) {
        container.innerHTML = '<div class="empty-state">Aucune séquence en cours</div>';
        return;
    }
    
    // Créer les éléments TODO
    todoList.forEach(todo => {
        const todoElement = createTodoElement(todo);
        container.appendChild(todoElement);
    });
}

function createTodoElement(todo) {
    /**
     * Crée l'élément HTML pour un TODO
     */
    const div = document.createElement('div');
    div.className = `todo-item ${todo.status}`;
    div.dataset.todoId = todo.id;
    
    // Icône selon le statut
    let icon = '⏳';
    let statusText = 'En attente';
    
    if (todo.status === 'in-progress') {
        icon = '⚙️';
        statusText = 'En cours';
    } else if (todo.status === 'completed') {
        icon = '✅';
        statusText = 'Terminé';
    }
    
    div.innerHTML = `
        <div class="todo-icon">${icon}</div>
        <div class="todo-content">
            <div class="todo-title">${todo.title}</div>
            ${todo.description ? `<div class="todo-description">${todo.description}</div>` : ''}
            <div class="todo-status">${statusText}</div>
        </div>
    `;
    
    // Ajouter les événements de clic
    div.onclick = () => {
        if (todo.status === 'pending') {
            updateTodoStatus(todo.id, 'in-progress');
        } else if (todo.status === 'in-progress') {
            updateTodoStatus(todo.id, 'completed');
        }
    };
    
    // Double-clic pour supprimer
    div.ondblclick = (e) => {
        e.stopPropagation();
        if (confirm(`Supprimer ce TODO ?\n"${todo.title}"`)) {
            removeTodo(todo.id);
        }
    };
    
    return div;
}

// Fonction pour marquer un TODO comme terminé depuis l'agent
function markTodoCompleted(todoId) {
    updateTodoStatus(todoId, 'completed');
}

// Fonction pour démarrer un TODO depuis l'agent
function startTodo(todoId) {
    updateTodoStatus(todoId, 'in-progress');
}

// Export des fonctions pour utilisation globale
window.validateTodoSequence = validateTodoSequence;
window.addTodo = addTodo;
window.updateTodoStatus = updateTodoStatus;
window.removeTodo = removeTodo;
window.clearCompletedTodos = clearCompletedTodos;
window.markTodoCompleted = markTodoCompleted;
window.startTodo = startTodo;
