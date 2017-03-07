const STORAGE_KEY = "distributed.workers.state"

export function emptyState() {
    return {};
}

export function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    return state;
}

export function clearState() {
    localStorage.clear();
    return emptyState()
}

export function loadState() {
    if (window.bllyflapp) {
        return window.bllyflapp;
    }
    var raw = localStorage.getItem(STORAGE_KEY);
    if (typeof raw !== 'string') {
        return clearState();
    }
    try {
        return JSON.parse(raw);
    } catch (e) {
        return emptyState()
    }
}
