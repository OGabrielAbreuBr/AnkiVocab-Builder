import { MEDIA_BASE_URL } from './api.js';

const langToFlag = {
    en: 'gb', pt: 'br', es: 'es', fr: 'fr', de: 'de', it: 'it', jp: 'jp'
};

export const ui = {
    renderHeader(state) {
        if (!state.user) return;
        document.getElementById('user-name').textContent = `${state.user.first_name} ${state.user.last_name}`;
        const totalWords = state.decks.reduce((sum, deck) => sum + (deck.cards?.length || 0), 0);
        document.getElementById('user-stats').textContent = `{ ${state.decks.length} DECKS } { ${totalWords} PALAVRAS }`;
    },
    
    renderDashboard(state) {
        const contentArea = document.getElementById('content-area');
        const decksGrid = state.decks.map(deck => {
            const flagCode = langToFlag[deck.word_language.code] || 'un';
            return `
            <div class="group relative bg-white border border-slate-200 rounded-xl shadow-md hover:shadow-xl transition-all duration-300">
                <a href="#deck/${deck.id}" class="block p-6">
                    <div class="flex justify-between items-start">
                        <h3 class="font-bold text-xl text-slate-900 pr-4">${deck.name}</h3>
                        <img src="https://flagcdn.com/w40/${flagCode}.png" alt="${deck.word_language.name}" class="h-6 rounded-sm shadow">
                    </div>
                    <p class="mt-4 text-slate-500 font-medium">${deck.cards?.length || 0} palavras</p>
                </a>
                <button data-delete-deck-id="${deck.id}" data-delete-deck-name="${deck.name}" class="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-red-600 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" title="Apagar Deck">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </div>
        `}).join('');
        
        contentArea.innerHTML = `
            <h1 class="text-4xl font-bold text-slate-900 tracking-tight mb-8">Meus Decks</h1>
            ${state.decks.length > 0 ? `<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">${decksGrid}</div>` : 
            `<div class="text-center py-16 px-6 border-2 border-dashed border-slate-300 rounded-xl">
                <h3 class="mt-2 text-lg font-medium text-slate-800">Nenhum deck encontrado</h3>
                <p class="mt-1 text-slate-500">Clique em "Novo Deck" para criar o seu primeiro!</p>
            </div>`
            }
        `;
    },

    renderDeckView(state) {
        const deck = state.currentDeck;
        if (!deck) {
            document.getElementById('content-area').innerHTML = `<p>Deck não encontrado.</p>`;
            return;
        }
        
        const playIcon = `<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20"><path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.841z"></path></svg>`;
        const editIcon = `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>`;
        const deleteIcon = `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>`;

        const cardsHtml = deck.cards.map(card => {
            const findAudio = (type) => card.word.audio.find(a => a.audio_type === type);
            const audioWord = findAudio('word');
            const audioMeaning = findAudio('meaning');
            const audioExample = findAudio('example');

            return `
            <div class="flex flex-col md:flex-row gap-6 bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div class="flex-1">
                    <div class="flex items-start justify-between">
                        <div class="flex items-center gap-3">
                            <h3 class="text-3xl font-bold text-slate-900">${card.word.text}</h3>
                            ${audioWord ? `<button data-audio-src="${audioWord.path}" class="p-1 text-slate-400 hover:text-blue-600" title="Ouvir palavra">${playIcon}</button>` : ''}
                        </div>
                        <div class="flex items-center gap-3">
                            ${card.word.cefr ? `<span class="px-2 py-0.5 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">${card.word.cefr}</span>` : ''}
                            <button data-edit-card='${JSON.stringify(card)}' class="p-2 text-slate-500 hover:bg-yellow-100 hover:text-yellow-600 rounded-full" title="Editar Palavra">${editIcon}</button>
                            <button data-delete-card="${card.id}" class="p-2 text-slate-500 hover:bg-red-100 hover:text-red-600 rounded-full" title="Remover Palavra">${deleteIcon}</button>
                        </div>
                    </div>
                    ${card.word.phonetic ? `<p class="mt-1 text-slate-500 font-mono">/${card.word.phonetic}/</p>` : ''}
                    <div class="mt-4 space-y-3 text-slate-700">
                        <div class="flex items-center justify-between gap-3">
                            <p class="flex-1">${card.word.meaning}</p>
                            ${audioMeaning ? `<button data-audio-src="${audioMeaning.path}" class="p-1 text-slate-400 hover:text-blue-600" title="Ouvir significado">${playIcon}</button>` : ''}
                        </div>
                        <div class="flex items-center justify-between gap-3">
                            <p class="flex-1 italic">"${card.word.example}"</p>
                            ${audioExample ? `<button data-audio-src="${audioExample.path}" class="p-1 text-slate-400 hover:text-blue-600" title="Ouvir exemplo">${playIcon}</button>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `}).join('');

        document.getElementById('content-area').innerHTML = `
            <div class="flex justify-between items-center mb-6">
                <a href="#" class="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900">&larr; Voltar para todos os decks</a>
                <!-- BOTÃO DE EXPORTAR -->
                <button id="export-anki-btn" class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Exportar para Anki
                </button>
            </div>
            <h1 class="text-4xl font-bold text-slate-900 tracking-tight mb-8">${deck.name}</h1>
            <div class="mb-10 p-6 bg-white rounded-xl shadow-md border border-slate-200">
                <h2 class="text-xl font-semibold mb-2">Adicionar Nova Palavra</h2>
                <form id="add-word-form" class="flex items-center gap-4">
                    <input type="text" name="word" placeholder="Digite uma palavra..." class="w-full px-4 py-2 border border-slate-300 rounded-lg" required>
                    <button type="submit" class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700">Adicionar</button>
                </form>
                <div id="add-word-error" class="hidden text-sm text-red-600 mt-2"></div>
            </div>
            <h2 class="text-2xl font-semibold mb-4">Palavras no Deck</h2>
            <div class="space-y-4">${cardsHtml.length > 0 ? cardsHtml : '<p class="text-slate-500">Ainda não há palavras neste deck.</p>'}</div>
        `;
    },
    
    renderProfileView(state) {
        const contentArea = document.getElementById('content-area');
        if (!state.user || !state.languages) {
            contentArea.innerHTML = `<p>A carregar dados do perfil...</p>`;
            return;
        }

        // Cria um conjunto com os IDs dos idiomas que o utilizador já tem
        const userLangIds = new Set(state.user.languages.map(lang => lang.language_id));

        // Gera o HTML para cada checkbox de idioma
        const languagesHtml = state.languages.map(lang => `
            <div class="flex items-center">
                <input 
                    id="lang-${lang.id}" 
                    name="languages" 
                    type="checkbox" 
                    value="${lang.id}"
                    ${userLangIds.has(lang.id) ? 'checked' : ''}
                    class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                >
                <label for="lang-${lang.id}" class="ml-3 block text-sm text-gray-900">
                    ${lang.name}
                </label>
            </div>
        `).join('');

        contentArea.innerHTML = `
            <a href="#" class="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6">&larr; Voltar para os decks</a>
            <h1 class="text-4xl font-bold text-slate-900 mb-8">Meu Perfil</h1>
            
            <form id="profile-form" class="space-y-8 bg-white p-8 rounded-xl shadow-md">
                <!-- Secção de Dados Pessoais -->
                <div class="space-y-6">
                    <h2 class="text-xl font-semibold text-slate-800 border-b pb-2">Dados Pessoais</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label for="profile-firstname" class="block text-sm font-medium text-slate-600">Nome</label>
                            <input id="profile-firstname" type="text" value="${state.user.first_name}" class="w-full mt-1 p-2 border rounded-md">
                        </div>
                        <div>
                            <label for="profile-lastname" class="block text-sm font-medium text-slate-600">Apelido</label>
                            <input id="profile-lastname" type="text" value="${state.user.last_name}" class="w-full mt-1 p-2 border rounded-md">
                        </div>
                    </div>
                </div>

                <!-- Secção de Idiomas -->
                <div class="space-y-4">
                    <h2 class="text-xl font-semibold text-slate-800 border-b pb-2">Meus Idiomas</h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                        ${languagesHtml}
                    </div>
                </div>

                <div class="pt-4 text-right">
                    <button type="submit" class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-lg">Salvar Alterações</button>
                </div>
            </form>
        `;
    },

    showView(viewId) {
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
    }
};
