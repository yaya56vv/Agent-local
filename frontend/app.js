// Configuration
const API_BASE_URL = "http://127.0.0.1:8000";

// État de l'application
let sessionId = generateSessionId();
let autoScroll = true;
let backendStatus = 'unknown'; // 'connected', 'waiting', 'disconnected'

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('session-id').textContent = sessionId;
    addLog('info', 'Interface chargée');
    
    // Vérifier la santé du backend au démarrage
    testHealth();

    // Enter pour envoyer message
    document.getElementById('user-message').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
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
});

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

    // Ajouter log
    addLog('info', `Message envoyé: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);

    // Mettre à jour le statut
    updateBackendStatus('waiting');

    try {
        const response = await fetch(`${API_BASE_URL}/orchestrate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message,
                session_id: sessionId
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

    } catch (error) {
        const errorMsg = `Erreur: ${error.message}`;
        appendChat('error', errorMsg);
        addLog('error', `Échec de l'envoi: ${error.message}`);
        updateBackendStatus('disconnected');
    }
}

function appendChat(type, text) {
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

    // Auto-scroll
    if (autoScroll) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
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
    const logsWindow = document.getElementById('logs-window');
    const logEntry = document.createElement('div');

    logEntry.className = 'log-entry';

    const timestamp = new Date().toLocaleTimeString('fr-FR');

    // Coloration selon le niveau
    let levelClass = level;
    let levelIcon = '';
    
    switch(level) {
        case 'success':
            levelIcon = '✓';
            break;
        case 'error':
            levelIcon = '✗';
            break;
        case 'warning':
            levelIcon = '⚠';
            break;
        case 'info':
            levelIcon = 'ℹ';
            break;
    }

    logEntry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-level ${levelClass}">${levelIcon} ${level.toUpperCase()}</span>
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

function clearLogs() {
    const logsWindow = document.getElementById('logs-window');
    logsWindow.innerHTML = '';
    addLog('info', 'Logs effacés');
}

function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const statusSpan = document.getElementById('autoscroll-status');
    if (statusSpan) {
        statusSpan.textContent = autoScroll ? 'ON' : 'OFF';
    }
    addLog('info', `Auto-scroll: ${autoScroll ? 'activé' : 'désactivé'}`);
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
