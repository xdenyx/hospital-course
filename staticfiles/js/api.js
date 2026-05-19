// API utilities for REST endpoints
class API {
    static BASE_URL = '/api';
    
    static async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        
        return response.json();
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
    static async getPatients() {
        return this.request('/patients/');
    }
    
    static async getPatient(id) {
        return this.request(`/patients/${id}/`);
    }
    
    static async createPatient(data) {
        return this.request('/patients/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async updatePatient(id, data) {
        return this.request(`/patients/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async deletePatient(id) {
        return this.request(`/patients/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Заявки
    static async getRequests() {
        return this.request('/requests/');
    }
    
    static async getRequest(id) {
        return this.request(`/requests/${id}/`);
    }
    
    static async createRequest(data) {
        return this.request('/requests/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async updateRequest(id, data) {
        return this.request(`/requests/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async deleteRequest(id) {
        return this.request(`/requests/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Прийоми
    static async getAppointments() {
        return this.request('/appointments/');
    }
    
    static async getAppointment(id) {
        return this.request(`/appointments/${id}/`);
    }
    
    static async createAppointment(data) {
        return this.request('/appointments/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async updateAppointment(id, data) {
        return this.request(`/appointments/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async deleteAppointment(id) {
        return this.request(`/appointments/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Лікарі
    static async getDoctors() {
        return this.request('/doctors/');
    }
    
    // Категорії робіт
    static async getWorkCategories() {
        return this.request('/work-categories/');
    }
    
    static async createWorkCategory(data) {
        return this.request('/work-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії матеріалів
    static async getMaterialCategories() {
        return this.request('/material-categories/');
    }
    
    static async createMaterialCategory(data) {
        return this.request('/material-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії ліків
    static async getMedicineCategories() {
        return this.request('/medicine-categories/');
    }
    
    static async createMedicineCategory(data) {
        return this.request('/medicine-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Категорії процедур
    static async getProcedureCategories() {
        return this.request('/procedure-categories/');
    }
    
    static async createProcedureCategory(data) {
        return this.request('/procedure-categories/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // Роботи в прийомах
    static async getAppointmentWorks() {
        return this.request('/appointment-works/');
    }
    
    static async createAppointmentWork(data) {
        return this.request('/appointment-works/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}
