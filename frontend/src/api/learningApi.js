import api from "./api";

const unwrap = (promise) => promise.then((r) => r.data);

// ---- documents
export const listDocuments = () => unwrap(api.get("/documents"));
export const getSupported = () => unwrap(api.get("/documents/supported"));
export const previewDocument = (id) => unwrap(api.get(`/documents/${id}/preview`));
export const retryDocument = (id) => unwrap(api.post(`/documents/${id}/retry`));
export const deleteDocument = (id) => unwrap(api.delete(`/documents/${id}`));
export const uploadDocument = (file, onProgress, signal) => {
    const form = new FormData();
    form.append("file", file);
    return unwrap(
        api.post("/documents/upload", form, {
            signal,
            onUploadProgress: (e) => e.total && onProgress?.(Math.round((e.loaded / e.total) * 100)),
        })
    );
};

// ---- dashboard
export const getDashboard = () => unwrap(api.get("/dashboard"));

// ---- chat
export const sendChat = (payload) => unwrap(api.post("/chat/query", payload, { timeout: 300000 }));
export const listSessions = () => unwrap(api.get("/chat/sessions"));
export const getSession = (id) => unwrap(api.get(`/chat/sessions/${id}`));
export const deleteSession = (id) => unwrap(api.delete(`/chat/sessions/${id}`));

// ---- summary
export const generateSummary = (payload) => unwrap(api.post("/summary/", payload, { timeout: 600000 }));
export const summaryHistory = () => unwrap(api.get("/summary/history"));
export const getSummary = (id) => unwrap(api.get(`/summary/${id}`));

// ---- quiz
export const generateQuiz = (payload) => unwrap(api.post("/quiz/generate", payload, { timeout: 600000 }));
export const submitQuiz = (id, answers) => unwrap(api.post(`/quiz/attempts/${id}/submit`, { answers }));
export const retakeQuiz = (id) => unwrap(api.post(`/quiz/attempts/${id}/retake`));
export const quizHistory = () => unwrap(api.get("/quiz/attempts"));

// ---- flashcards
export const generateDeck = (payload) => unwrap(api.post("/flashcards/generate", payload, { timeout: 600000 }));
export const saveDeck = (title, cards) => unwrap(api.post("/flashcards/decks", { title, cards }));
export const listDecks = () => unwrap(api.get("/flashcards/decks"));
export const getDeck = (id) => unwrap(api.get(`/flashcards/decks/${id}`));
export const renameDeck = (id, title) => unwrap(api.patch(`/flashcards/decks/${id}`, { title }));
export const deleteDeck = (id) => unwrap(api.delete(`/flashcards/decks/${id}`));
export const resetDeck = (id) => unwrap(api.post(`/flashcards/decks/${id}/reset`));
export const markCard = (id, status) => unwrap(api.patch(`/flashcards/items/${id}`, { status }));
// legacy flows from the original Flashcards page
export const flashcardsFromText = (text) => unwrap(api.post("/flashcards", null, { params: { text }, timeout: 600000 }));
export const flashcardsFromPdf = (file) => {
    const form = new FormData();
    form.append("file", file);
    return unwrap(api.post("/upload/flashcards", form, { timeout: 600000 }));
};

// ---- study plans
export const generatePlan = (payload) => unwrap(api.post("/study-plan/generate", payload, { timeout: 600000 }));
export const listPlans = () => unwrap(api.get("/study-plan/plans"));
export const getPlan = (id) => unwrap(api.get(`/study-plan/plans/${id}`));
export const deletePlan = (id) => unwrap(api.delete(`/study-plan/plans/${id}`));
export const patchTask = (id, body) => unwrap(api.patch(`/study-plan/tasks/${id}`, body));
export const addTask = (planId, body) => unwrap(api.post(`/study-plan/plans/${planId}/tasks`, body));
export const deleteTask = (id) => unwrap(api.delete(`/study-plan/tasks/${id}`));

// ---- recommendations
export const getRecommendations = () => unwrap(api.get("/recommendation/"));
