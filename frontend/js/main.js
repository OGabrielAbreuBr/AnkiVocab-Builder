import { api, MEDIA_BASE_URL } from './api.js';
import { ui } from './ui.js';

const state = {
    user: null,
    decks: [],
    currentDeck: null,
    languages: [],
};

const audioPlayer = new Audio();

const router = {
    async handleRouteChange() {
        const hash = window.location.hash || '#';
        const token = document.cookie.split('; ').find(row => row.startsWith('auth_token='))?.split('=')[1];

        if (!token) {
            ui.showView(hash === '#signup' ? 'signup-view' : 'login-view');
            document.getElementById('app-shell').classList.remove('active');
            if (hash.startsWith('#login') && window.location.search.includes('status=success')) {
                document.getElementById('login-success-message').textContent = 'Registo efetuado com sucesso! Faça o login.';
                document.getElementById('login-success-message').classList.remove('hidden');
            }
            return;
        }
        
        ui.showView('app-shell');

        if (!state.user) {
            try {
                state.user = await api.getCurrentUser();
            } catch (e) {
                auth.logout();
                return;
            }
        }
        
        if (hash.startsWith('#deck/')) {
            const deckId = parseInt(hash.split('/')[1], 10);
            document.getElementById('content-area').innerHTML = '<p class="text-center text-slate-500">A carregar deck...</p>';
            state.currentDeck = await api.getDeckById(deckId);
            ui.renderDeckView(state);
        } else if (hash === '#profile') {
            document.getElementById('content-area').innerHTML = '<p class="text-center text-slate-500">A carregar perfil...</p>';
            ui.renderProfileView(state);
        } else {
            state.decks = await api.getDecks();
            ui.renderHeader(state);
            ui.renderDashboard(state);
        }
    }
};

const auth = {
    logout() {
        document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
        state.user = null;
        window.location.hash = '#login';
        router.handleRouteChange();
    }
};

function setupEventListeners() {
    window.addEventListener('hashchange', router.handleRouteChange);
    
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const errorDiv = document.getElementById('login-error');
        errorDiv.classList.add('hidden');
        try {
            const data = await api.login(form.email.value, form.password.value);
            document.cookie = `auth_token=${data.access_token}; path=/; max-age=3600`;
            window.location.hash = '#';
            await router.handleRouteChange();
        } catch (err) {
            errorDiv.textContent = 'Falha no login. Verifique as credenciais.';
            errorDiv.classList.remove('hidden');
        }
    });

    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const errorDiv = document.getElementById('signup-error');
        errorDiv.classList.add('hidden');
        try {
            await api.signup(
                form.firstname.value,
                form.lastname.value,
                form.username.value,
                form.email.value,
                form.password.value
            );
            window.location.href = '/?status=success#login';
        } catch (err) {
            errorDiv.textContent = err.message || 'Erro ao registar.';
            errorDiv.classList.remove('hidden');
        }
    });

    document.getElementById('logout-btn').addEventListener('click', auth.logout);

    document.getElementById('new-deck-btn').addEventListener('click', async () => {
        if (state.languages.length === 0) {
            state.languages = await api.getLanguages();
            const options = state.languages.map(l => `<option value="${l.id}">${l.name}</option>`).join('');
            document.getElementById('deck-word-lang').innerHTML = options;
            document.getElementById('deck-expl-lang').innerHTML = options;
        }
        document.getElementById('new-deck-modal').classList.remove('hidden');
    });

    document.getElementById('cancel-deck-btn').addEventListener('click', () => {
        document.getElementById('new-deck-modal').classList.add('hidden');
    });

    document.getElementById('new-deck-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const errorDiv = document.getElementById('modal-error');
        errorDiv.classList.add('hidden');
        try {
            await api.createDeck(form['deck-name'].value, form['deck-word-lang'].value, form['deck-expl-lang'].value);
            document.getElementById('new-deck-modal').classList.add('hidden');
            form.reset();
            await router.handleRouteChange();
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    });

    // --- OUVINTE DE EVENTOS GLOBAL CORRIGIDO ---
    document.body.addEventListener('click', async (e) => {
        const target = e.target;

        // Lógica para tocar áudio (com a sua sugestão de normalização)
        const playBtn = target.closest('[data-audio-src]');
        if (playBtn) {
            const rawSrc = playBtn.dataset.audioSrc;
            console.log('🔊 Play:', rawSrc);

            const base = MEDIA_BASE_URL.replace(/\/$/, ''); // Tira a barra do fim
            const path = rawSrc.replace(/^\//, '');      // Tira a barra do início
            const url = `${base}/${path}`;
            
            console.log('URL do Áudio →', url);
            audioPlayer.src = url;
            audioPlayer.play().catch(err => console.error('Erro ao tocar áudio:', err));
            return;
        }

        // Lógica para apagar deck
        const deleteDeckBtn = target.closest('[data-delete-deck-id]');
        if (deleteDeckBtn) {
            const deckId = deleteDeckBtn.dataset.deleteDeckId;
            const deckName = deleteDeckBtn.dataset.deleteDeckName;
            document.getElementById('deck-to-delete-name').textContent = deckName;
            const modal = document.getElementById('confirm-delete-deck-modal');
            modal.dataset.deckId = deckId;
            modal.classList.remove('hidden');
            return;
        }

        // Lógica para editar card
        const editCardBtn = target.closest('[data-edit-card]');
        if (editCardBtn) {
            const card = JSON.parse(editCardBtn.dataset.editCard);
            document.getElementById('edit-card-id').value = card.id;
            document.getElementById('edit-card-word').value = card.word.text;
            document.getElementById('edit-card-meaning').value = card.word.meaning;
            document.getElementById('edit-card-example').value = card.word.example;
            document.getElementById('edit-card-modal').classList.remove('hidden');
            return;
        }

        // Lógica para apagar card
        const deleteCardBtn = target.closest('[data-delete-card]');
        if (deleteCardBtn) {
            const cardId = parseInt(deleteCardBtn.dataset.deleteCard, 10);
            await api.deleteCardFromDeck(state.currentDeck.id, cardId);
            state.currentDeck.cards = state.currentDeck.cards.filter(c => c.id !== cardId);
            ui.renderDeckView(state);
            return;
        }
    });

    // Listeners para os modais
    document.getElementById('cancel-delete-deck-btn').addEventListener('click', () => document.getElementById('confirm-delete-deck-modal').classList.add('hidden'));
    document.getElementById('confirm-delete-deck-btn').addEventListener('click', async () => {
        const modal = document.getElementById('confirm-delete-deck-modal');
        const deckId = modal.dataset.deckId;
        await api.deleteDeck(deckId);
        modal.classList.add('hidden');
        window.location.hash = '#';
        await router.handleRouteChange();
    });
    document.getElementById('cancel-edit-card-btn').addEventListener('click', () => document.getElementById('edit-card-modal').classList.add('hidden'));
    document.getElementById('edit-card-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const cardId = form['edit-card-id'].value;
        const data = {
            meaning: form['edit-card-meaning'].value,
            example: form['edit-card-example'].value
        };
        await api.updateCard(state.currentDeck.id, cardId, data);
        document.getElementById('edit-card-modal').classList.add('hidden');
        await router.handleRouteChange();
    });
    
    // Listener para os formulários
    document.body.addEventListener('submit', async (e) => {
        if (e.target.id === 'profile-form') {
            e.preventDefault();
            const form = e.target;
            const userData = {
                first_name: form['profile-firstname'].value,
                last_name: form['profile-lastname'].value
            };
            const updatedUser = await api.updateUserProfile(userData);
            state.user = updatedUser;
            ui.renderHeader(state);
            alert('Perfil atualizado com sucesso!');
        } else if (e.target.id === 'add-word-form') {
            e.preventDefault();
            const form = e.target;
            const wordInput = form.word;
            const errorDiv = document.getElementById('add-word-error');
            errorDiv.classList.add('hidden');
            try {
                const newCard = await api.addWordToDeck(state.currentDeck.id, wordInput.value);
                state.currentDeck.cards.push(newCard);
                ui.renderDeckView(state);
                form.reset();
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.classList.remove('hidden');
            }
        }
    });
}

async function init() {
    setupEventListeners();
    await router.handleRouteChange();
}

init();
