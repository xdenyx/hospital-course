// API utilities for REST endpoints
class API {
    static request(endpoint, options = {}) {
        const url = `/api${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': API.getCSRFToken()
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options }).then(res => {
            if (!res.ok) {
                return res.json().then(error => {
                    throw new Error(error.detail || `HTTP ${res.status}`);
                }).catch(() => {
                    throw new Error(`HTTP ${res.status}`);
                });
            }
            return res.json();
        });
    }
    
    static getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue || '';
    }
    
    // Пацієнти
    static getPatients() {
        return API.request('/patients/');
    }
    
    static getPatient(id) {
        return API.request(`/patients/${id}/`);
    }
    
    static getPatientProtocol(id) {
        return API.request(`/patients/${id}/protocol/`);
    }

    static createPatient(data) {
        return API.request('/patients/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static updatePatient(id, data) {
        return API.request(`/patients/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static deletePatient(id) {
        return API.request(`/patients/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Заявки
    static getRequests() {
        return API.request('/requests/');
    }
    
    static getRequest(id) {
        return API.request(`/requests/${id}/`);
    }
    
    static createRequest(data) {
        return API.request('/requests/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static updateRequest(id, data) {
        return API.request(`/requests/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static deleteRequest(id) {
        return API.request(`/requests/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Прийоми
    static getAppointments() {
        return API.request('/appointments/');
    }
    
    static getAppointment(id) {
        return API.request(`/appointments/${id}/`);
    }
    
    static createAppointment(data) {
        return API.request('/appointments/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static updateAppointment(id, data) {
        return API.request(`/appointments/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static deleteAppointment(id) {
        return API.request(`/appointments/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Лікарі
    static getDoctors() {
        return API.request('/doctors/');
    }
    
    // Категорії робіт
    static getWorkCategories() {
        return API.request('/work-categories/');
    }
    
    static createWorkCategory(data) {
        return API.request('/work-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії матеріалів
    static getMaterialCategories() {
        return API.request('/material-categories/');
    }
    
    static createMaterialCategory(data) {
        return API.request('/material-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії ліків
    static getMedicineCategories() {
        return API.request('/medicine-categories/');
    }
    
    static createMedicineCategory(data) {
        return API.request('/medicine-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії процедур
    static getProcedureCategories() {
        return API.request('/procedure-categories/');
    }
    
    static createProcedureCategory(data) {
        return API.request('/procedure-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Роботи в прийомах
    static getAppointmentWorks() {
        return API.request('/appointment-works/');
    }
    
    static createAppointmentWork(data) {
        return API.request('/appointment-works/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // --- УПРАВЛІННЯ ВИТРАТАМИ ТА РОБОТАМИ ---
    
    // Часткове оновлення роботи (щоб оновлювати ціну/прибуток)
    static patchAppointmentWork(id, data) {
        return API.request(`/appointment-works/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    static createWorkMaterial(data) {
        return API.request('/work-materials/', { method: 'POST', body: JSON.stringify(data) });
    }
    
    static deleteWorkMaterial(id) {
        return API.request(`/work-materials/${id}/`, { method: 'DELETE' });
    }

    static createWorkMedicine(data) {
        return API.request('/work-medicines/', { method: 'POST', body: JSON.stringify(data) });
    }
    
    static deleteWorkMedicine(id) {
        return API.request(`/work-medicines/${id}/`, { method: 'DELETE' });
    }

    static createWorkProcedure(data) {
        return API.request('/work-procedures/', { method: 'POST', body: JSON.stringify(data) });
    }
    
    static deleteWorkProcedure(id) {
        return API.request(`/work-procedures/${id}/`, { method: 'DELETE' });
    }
    
}

console.log('API класс завантажений');
