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

// État du microphone et TTS
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let isTTSSpeaking = false;
let currentAudioElement = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('session-id').textContent = sessionId;
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
});

// ============ EXPLORATEUR DE FICHIERS ============

async function initFileExplorer() {
    // Charger la racine par défaut
    await loadDirectory('.');
}

async function loadDirectory(path) {
    const explorerList = document.getElementById('file-explorer');
    if (!explorerList) return;

    // Afficher loading
    explorerList.innerHTML = '<li class="loading"><i class="fas fa-spinner fa-spin"></i> Chargement...</li>';

    try {
        const response = await fetch(`${API_BASE_URL}/files/list`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dir_path: path })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (data.status === 'error') throw new Error(data.error);

        renderFileTree(data.items, path);

    } catch (error) {
        explorerList.innerHTML = `<li class="error"><i class="fas fa-exclamation-triangle"></i> Erreur: ${error.message}</li>`;
        addLog('error', `Explorateur: ${error.message}`);
    }
}

function renderFileTree(items, currentPath) {
    const explorerList = document.getElementById('file-explorer');
    explorerList.innerHTML = '';

    // Bouton retour si pas à la racine
    if (currentPath !== '.' && currentPath !== './') {
        const parentPath = currentPath.split('/').slice(0, -1).join('/') || '.';
        const backItem = document.createElement('li');
        backItem.innerHTML = '<i class="fas fa-level-up-alt"></i> ..';
        backItem.onclick = () => loadDirectory(parentPath);
        explorerList.appendChild(backItem);
    }

    // Trier: Dossiers d'abord, puis fichiers
    items.sort((a, b) => {
        if (a.is_dir === b.is_dir) return a.name.localeCompare(b.name);
        return a.is_dir ? -1 : 1;
    });

    items.forEach(item => {
        const li = document.createElement('li');
        const iconClass = item.is_dir ? 'fa-folder' : getFileIcon(item.name);
        
        li.innerHTML = `<i class="fas ${iconClass}"></i> ${item.name}`;
        
        if (item.is_dir) {
            li.onclick = () => loadDirectory(item.path);
        } else {
            li.onclick = () => openFile(item.path);
        }
        
        explorerList.appendChild(li);
    });
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

    // 1. Update Timeline (New Feature)
    updateTimeline(level, message, timestamp);

    // 2. Update Status Card (New Feature)
    updateStatusCard(level, message);

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

// ============ DASHBOARD FEATURES ============

function updateTimeline(level, message, timestamp) {
    const track = document.getElementById('timeline-track');
    if (!track) return;

    const node = document.createElement('div');
    node.className = `timeline-node ${level === 'error' ? 'error' : ''}`;
    
    // Determine icon based on message content (simple heuristic)
    let icon = '⚡';
    if (message.includes('RAG')) icon = '📚';
    if (message.includes('Message')) icon = '💬';
    if (message.includes('Enregistrement')) icon = '🎤';
    if (message.includes('TTS')) icon = '🔊';
    if (message.includes('Arrêt')) icon = '🛑';

    node.innerHTML = `
        <span class="time">${timestamp}</span>
        <span class="icon">${icon}</span>
        <span class="label">${message.substring(0, 20)}${message.length > 20 ? '...' : ''}</span>
    `;

    // Add to start
    track.insertBefore(node, track.firstChild);

    // Highlight first one
    const nodes = track.querySelectorAll('.timeline-node');
    nodes.forEach(n => n.classList.remove('active'));
    node.classList.add('active');

    // Limit nodes
    if (nodes.length > 20) {
        track.removeChild(track.lastChild);
    }
}

function updateStatusCard(level, message) {
    const statusText = document.getElementById('agent-status-text');
    const detailText = document.getElementById('current-action-detail');
    
    if (statusText && detailText) {
        if (level === 'error') {
            statusText.innerHTML = '<span class="status-dot" style="background:red; box-shadow:0 0 8px red;"></span> Erreur';
            statusText.style.color = '#ef4444';
        } else if (level === 'waiting') {
             statusText.innerHTML = '<span class="status-dot" style="background:orange; box-shadow:0 0 8px orange;"></span> Occupé';
             statusText.style.color = '#f59e0b';
        } else {
            statusText.innerHTML = '<span class="status-dot"></span> Prêt';
            statusText.style.color = '#10b981';
        }
        
        detailText.textContent = message;
    }
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
