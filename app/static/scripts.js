document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const queryInput = document.getElementById('query-input');
    const chatArea = document.getElementById('chat-area');
    const clearHistoryBtn = document.getElementById('clear-history');
    const saveApiKeyBtn = document.getElementById('save-api-key');
    const uploadPdfBtn = document.getElementById('upload-pdf');
    const apiKeyInput = document.getElementById('api-key-input');
    const pdfUploadInput = document.getElementById('pdf-upload');

    function addMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);
        messageDiv.textContent = text;
        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    async function sendMessage() {
        const message = queryInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: message })
            });

            const data = await response.json();
            
            if (response.ok) {
                addMessage('bot', data.answer);
            } else {
                addMessage('bot', data.error || 'An error occurred');
            }
        } catch (error) {
            addMessage('bot', 'Network error. Please try again.');
            console.error('Error:', error);
        }

        queryInput.value = '';
    }

    async function uploadPDF() {
        const file = pdfUploadInput.files[0];
        if (!file) {
            alert('Please select a PDF file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                alert(data.message);
            } else {
                alert(data.error || 'PDF upload failed');
            }
        } catch (error) {
            alert('Network error during PDF upload');
            console.error('Error:', error);
        }
    }

    async function saveAPIKey() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            alert('Please enter an API key');
            return;
        }

        try {
            const response = await fetch('/set-api-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `api_key=${encodeURIComponent(apiKey)}`
            });

            const data = await response.json();
            
            if (response.ok) {
                alert(data.message);
                apiKeyInput.value = '';
            } else {
                alert(data.error || 'API key setting failed');
            }
        } catch (error) {
            alert('Network error during API key setting');
            console.error('Error:', error);
        }
    }

    function clearHistory() {
        chatArea.innerHTML = '';
    }

    sendBtn.addEventListener('click', sendMessage);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    clearHistoryBtn.addEventListener('click', clearHistory);
    uploadPdfBtn.addEventListener('click', uploadPDF);
    saveApiKeyBtn.addEventListener('click', saveAPIKey);
});