const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
export const MEDIA_BASE_URL = 'http://127.0.0.1:8000/media/';

export const api = {
    async fetcher(endpoint, options = {}, isBlob = false) {
        const token = document.cookie.split('; ').find(row => row.startsWith('auth_token='))?.split('=')[1];
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (!response.ok) {
            const errorInfo = await response.json();
            throw new Error(errorInfo.detail || 'Erro na API');
        }
        if (isBlob) {
            return response.blob(); // Retorna o ficheiro como um blob
        }
        return response.status === 204 ? null : response.json();
    },
    login: (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        return fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        }).then(res => res.ok ? res.json() : Promise.reject(res.json()));
    },
    signup: (firstname, lastname, username, email, password) => 
        api.fetcher('/users/', { 
            method: 'POST', 
            body: JSON.stringify({ first_name: firstname, last_name: lastname, username, email, password }) 
        }),
    getCurrentUser: () => api.fetcher('/users/me'),
    getDecks: () => api.fetcher('/decks/'),
    getDeckById: (id) => api.fetcher(`/decks/${id}`),
    createDeck: (name, wordLanguageId, explanationLanguageId, isPublic = false) => 
        api.fetcher('/decks/', { 
            method: 'POST', 
            body: JSON.stringify({ name, word_language_id: wordLanguageId, explanation_language_id: explanationLanguageId, is_public: isPublic }) 
        }),
    addWordToDeck: (deckId, word) => api.fetcher(`/decks/${deckId}/cards`, { method: 'POST', body: JSON.stringify({ word }) }),
    getLanguages: () => api.fetcher('/languages/'),
    deleteDeck: (deckId) => api.fetcher(`/decks/${deckId}`, { method: 'DELETE' }),
    updateCard: (deckId, cardId, data) => api.fetcher(`/decks/${deckId}/cards/${cardId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    updateUserProfile: (userData) => api.fetcher('/users/me', {
        method: 'PUT',
        body: JSON.stringify(userData)
    }),
    deleteCardFromDeck: (deckId, cardId) => api.fetcher(`/decks/${deckId}/cards/${cardId}`, { method: 'DELETE' }),
    
    // --- NOVA FUNÇÃO ---
    exportAnkiDeck: (deckId) => api.fetcher(`/anki/export/${deckId}`, {}, true),
};
