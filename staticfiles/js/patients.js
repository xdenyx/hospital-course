// Пацієнти
const PatientsModule = {
    async render() {
        const app = document.getElementById('app');
        const patients = await API.getPatients();
        
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Пацієнти</h2>
                <button class="btn btn-success" onclick="app.showPatientForm()">Додати</button>
            </div>
            
            <div id="patientsList"></div>
            <div id="patientForm"></div>
        `;
        
        this.renderList(patients);
    },
    
    renderList(patients) {
        const list = document.getElementById('patientsList');
        
        if (!patients || patients.length === 0) {
            list.innerHTML = '<p class="text-muted">Немає пацієнтів</p>';
            return;
        }
        
        let html = '<table class="table table-striped">';
        html += '<thead><tr><th>ПІБ</th><th>Дата народження</th><th>Вік</th><th>Дії</th></tr></thead><tbody>';
        
        patients.forEach(p => {
            html += `
                <tr>
                    <td>${p.full_name}</td>
                    <td>${p.date_of_birth}</td>
                    <td>${p.age || '-'} років</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="app.editPatient(${p.id})">Редагувати</button>
                        <button class="btn btn-sm btn-danger" onclick="app.deletePatient(${p.id})">Видалити</button>
                        <button class="btn btn-sm btn-primary" onclick="app.showPatientDetail(${p.id})">Деталі</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        list.innerHTML = html;
    },
    
    async showForm(patientId = null) {
        const formDiv = document.getElementById('patientForm');
        const patient = patientId ? await API.getPatient(patientId) : null;
        
        let html = `
            <div class="card mt-4">
                <div class="card-header">
                    <h5>${patientId ? 'Редагувати' : 'Додати'} пацієнта</h5>
                </div>
                <div class="card-body">
                    <form id="patientFormElement">
                        <div class="mb-3">
                            <label class="form-label">ПІБ</label>
                            <input type="text" class="form-control" name="full_name" value="${patient?.full_name || ''}" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Дата народження</label>
                            <input type="date" class="form-control" name="date_of_birth" value="${patient?.date_of_birth || ''}" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Зберегти</button>
                        <button type="button" class="btn btn-secondary" onclick="app.hideForm()">Скасувати</button>
                    </form>
                </div>
            </div>
        `;
        
        formDiv.innerHTML = html;
        
        document.getElementById('patientFormElement').addEventListener('submit', (e) => {
            e.preventDefault();
            this.savePatient(e.target, patientId);
        });
    },
    
    async savePatient(form, patientId) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            if (patientId) {
                await API.updatePatient(patientId, data);
            } else {
                await API.createPatient(data);
            }
            
            this.render();
        } catch (error) {
            alert(`Помилка: ${error.message}`);
        }
    },
    
    async deletePatient(id) {
        if (confirm('Ви впевнені?')) {
            try {
                await API.deletePatient(id);
                this.render();
            } catch (error) {
                alert(`Помилка: ${error.message}`);
            }
        }
    },
    
    async showDetail(id) {
        const app = document.getElementById('app');
        const patient = await API.getPatient(id);
        
        app.innerHTML = `
            <div>
                <button class="btn btn-secondary mb-3" onclick="app.renderPatients()">Назад</button>
                <div class="card">
                    <div class="card-body">
                        <h5>{{ patient.full_name }}</h5>
                        <p><strong>Дата народження:</strong> {{ patient.date_of_birth }}</p>
                        <p><strong>Контакт:</strong> {{ patient.contact }}</p>
                        <p><strong>Адреса:</strong> {{ patient.address }}</p>
                    </div>
                </div>
            </div>
        `;
    }
};
