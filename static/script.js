document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const clearBtn = document.getElementById('clear-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const commandInput = document.getElementById('command-input');
    
    const loadingEl = document.getElementById('loading');
    const resultPanel = document.getElementById('result-panel');
    const errorPanel = document.getElementById('error-panel');
    const errorMsg = document.getElementById('error-msg');
    
    let currentFile = null;

    // Drag and Drop Events
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
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    clearBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = "";
        previewContainer.classList.add('hidden');
        dropZone.classList.remove('hidden');
        hideResults();
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            showError("Please upload an image file.");
            return;
        }
        
        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            hideError();
        };
        reader.readAsDataURL(file);
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) {
            showError("Please upload an image first.");
            return;
        }
        
        const command = commandInput.value.trim() || 'Analyze this screen';
        
        const formData = new FormData();
        formData.append('image', currentFile);
        formData.append('command', command);
        
        loadingEl.classList.remove('hidden');
        resultPanel.classList.add('hidden');
        errorPanel.classList.add('hidden');
        analyzeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                const message = data.error || data.detail || "Server error occurred";
                throw new Error(message);
            }
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            renderSuccess(data);
            
        } catch (err) {
            console.error("Analysis failed:", err);
            showError(err.message);
        } finally {
            loadingEl.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function renderSuccess(data) {
        document.getElementById('screen-type-badge').textContent = data.screen_type || "UNKNOWN";
        
        renderList('res-summary', data.summary);
        renderList('res-key-info', data.key_information);
        renderList('res-action-items', data.action_items);
        renderList('res-suggestions', data.suggestions);
        
        // Render Executable Actions
        const actionsContainer = document.getElementById('res-actions');
        actionsContainer.innerHTML = '';
        if (data.actions && data.actions.length > 0) {
            data.actions.forEach(act => {
                const card = document.createElement('div');
                card.className = 'action-card';
                
                const info = document.createElement('div');
                info.className = 'action-info';
                info.innerHTML = `<strong>${act.action}</strong><span>${act.input.length > 50 ? act.input.substring(0, 50) + '...' : act.input}</span>`;
                
                const btn = document.createElement('button');
                btn.className = 'execute-btn';
                btn.textContent = 'Execute';
                btn.onclick = async () => {
                    btn.textContent = 'Running...';
                    btn.style.opacity = '0.7';
                    try {
                        const res = await fetch('/api/execute', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ action: act.action, input: act.input })
                        });
                        const jData = await res.json();
                        btn.textContent = 'Success!';
                        btn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
                    } catch (e) {
                        btn.textContent = 'Failed';
                        btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                    }
                };
                
                card.appendChild(info);
                card.appendChild(btn);
                actionsContainer.appendChild(card);
            });
        } else {
            actionsContainer.innerHTML = '<p style="color:var(--text-secondary)">No executable actions detected.</p>';
        }

        // Render Quick Actions
        const quickContainer = document.getElementById('res-quick-actions');
        quickContainer.innerHTML = '';
        if (data.quick_actions && data.quick_actions.length > 0) {
            data.quick_actions.forEach(qa => {
                const pill = document.createElement('button');
                pill.className = 'quick-action-pill';
                pill.textContent = qa;
                pill.onclick = () => {
                    const chatInput = document.getElementById('chat-input');
                    chatInput.value = pill.textContent;
                    document.getElementById('chat-btn').click();
                };
                quickContainer.appendChild(pill);
            });
        }
        
        resultPanel.classList.remove('hidden');
    }

    function renderList(elementId, items) {
        const ul = document.getElementById(elementId);
        ul.innerHTML = '';
        if (items && items.length > 0) {
            items.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                ul.appendChild(li);
            });
        } else {
            ul.innerHTML = '<li style="color:var(--text-secondary); list-style:none">None</li>';
        }
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorPanel.classList.remove('hidden');
    }
    
    function hideError() {
        errorPanel.classList.add('hidden');
    }
    
    function hideResults() {
        resultPanel.classList.add('hidden');
        document.getElementById('chat-panel').classList.add('hidden');
    }

    const clearHistoryBtn = document.getElementById('clear-history-btn');
    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm("Clear conversation history and memory?")) return;
        
        try {
            const resp = await fetch('/api/clear_context', { method: 'POST' });
            const data = await resp.json();
            if (resp.ok) {
                alert("History cleared!");
                chatLog.innerHTML = '';
            } else {
                showError(data.detail || "Failed to clear history");
            }
        } catch (err) {
            showError("Request failed: " + err.message);
        }
    });

    // Chat functionality
    const chatBtn = document.getElementById('chat-btn');
    const chatInput = document.getElementById('chat-input');
    const chatLog = document.getElementById('chat-log');
    
    function appendChatMessage(msg, type='user') {
        const bubble = document.createElement('div');
        bubble.className = `chat-message chat-${type}`;
        if (type === 'ai' && typeof marked !== 'undefined') {
            bubble.innerHTML = marked.parse(msg);
        } else {
            bubble.textContent = msg;
        }
        chatLog.appendChild(bubble);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    chatBtn.addEventListener('click', async () => {
        const text = chatInput.value.trim();
        if (!text) return;
        
        appendChatMessage(text, 'user');
        chatInput.value = '';
        chatBtn.disabled = true;
        
        // Add a temporary loading bot bubble
        const typingId = 'typing-' + Date.now();
        const bubble = document.createElement('div');
        bubble.id = typingId;
        bubble.className = 'chat-message chat-ai';
        bubble.innerHTML = '<i>Jarvis is thinking...</i>';
        chatLog.appendChild(bubble);
        chatLog.scrollTop = chatLog.scrollHeight;

        try {
            const resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await resp.json();
            
            document.getElementById(typingId).remove();
            
            if (!resp.ok) throw new Error(data.detail || "Chat error");
            appendChatMessage(data.response, 'ai');
            
        } catch (err) {
            document.getElementById(typingId).remove();
            appendChatMessage("Error: " + err.message, 'ai');
        } finally {
            chatBtn.disabled = false;
            chatInput.focus();
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') chatBtn.click();
    });
    
    // Show chat panel alongside results when analysis succeeds
    const oldRenderSuccess = renderSuccess;
    renderSuccess = function(data) {
        oldRenderSuccess(data);
        document.getElementById('chat-panel').classList.remove('hidden');
        chatLog.innerHTML = '';
        appendChatMessage("I've analyzed the image. What else would you like to know?", 'ai');
    };
});
