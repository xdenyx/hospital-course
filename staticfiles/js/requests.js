// Заявки
const RequestsModule = {
    async render() {
        const app = document.getElementById('app');
        const requests = await API.getRequests();
        
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Заявки</h2>
                <button class="btn btn-success" onclick="app.showRequestForm()">Додати</button>
            </div>
            
            <div id="requestsList"></div>
            <div id="requestForm"></div>
        `;
        
        this.renderList(requests);
    },
    
    renderList(requests) {
        const list = document.getElementById('requestsList');
        
        if (!requests || requests.length === 0) {
            list.innerHTML = '<p class="text-muted">Немає заявок</p>';
            return;
        }
        
        let html = '<table class="table table-striped">';
        html += '<thead><tr><th>Пацієнт</th><th>Дата/час</th><th>Лікар</th><th>Дії</th></tr></thead><tbody>';
        
        requests.forEach(r => {
            const doctorName = r.doctor?.full_name || 'Не призначен';
            html += `
                <tr>
                    <td>${r.patient.full_name}</td>
                    <td>${new Date(r.datetime).toLocaleString('uk-UA')}</td>
                    <td>${doctorName}</td>
                    <td>${r.reason}</td>
                    <td><span class="badge bg-info">${r.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="app.editRequest(${r.id})">Редагувати</button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteRequest(${r.id})">Видалити</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        list.innerHTML = html;
    },
    
    async showForm(requestId = null) {
        const formDiv = document.getElementById('requestForm');
        const request = requestId ? await API.getRequest(requestId) : null;
        const patients = await API.getPatients();
        
        let patientOptions = '<option value="">Виберіть пацієнта</option>';
        patients.forEach(p => {
            patientOptions += `<option value="${p.id}" ${request?.patient.id === p.id ? 'selected' : ''}>${p.full_name}</option>`;
        });
        
        const now = new Date().toISOString().slice(0, 16);
        
        let html = `
            <div class="card mt-4">
                <div class="card-header">
                    <h5>${requestId ? 'Редагувати' : 'Додати'} заявку</h5>
                </div>
                <div class="card-body">
                    <form id="requestFormElement">
                        <div class="mb-3">
                            <label class="form-label">Пацієнт</label>
                            <select class="form-control" name="patient_id" required>
                                ${patientOptions}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Дата/час</label>
                            <input type="datetime-local" class="form-control" name="datetime" value="${request?.datetime || now}" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Зберегти</button>
                        <button type="button" class="btn btn-secondary" onclick="app.hideForm()">Скасувати</button>
                    </form>
                </div>
            </div>
        `;
        
        formDiv.innerHTML = html;
        
        document.getElementById('requestFormElement').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveRequest(e.target, requestId);
        });
    },
    
    async saveRequest(form, requestId) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            if (requestId) {
                await API.updateRequest(requestId, data);
            } else {
                await API.createRequest(data);
            }
            
            this.render();
        } catch (error) {
            alert(`Помилка: ${error.message}`);
        }
    },
    
    async deleteRequest(id) {
        if (confirm('Ви впевнені?')) {
            try {
                await API.deleteRequest(id);
                this.render();
            } catch (error) {
                alert(`Помилка: ${error.message}`);
            }
        }
    }
};
