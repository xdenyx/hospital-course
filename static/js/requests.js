// Заявки
const RequestsModule = {
    render() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Заявки</h2>
                <button class="btn btn-success" onclick="app.showRequestForm()">Додати</button>
            </div>
            
            <div id="requestsList"><p class="text-muted">Завантаження...</p></div>
            <div id="requestForm"></div>
        `;
        
        API.getRequests().then(requests => {
            this.renderList(requests);
        }).catch(err => {
            console.error('Error loading requests:', err);
            document.getElementById('requestsList').innerHTML = '<p class="text-danger">Помилка при завантаженні</p>';
        });
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
            const doctorName = r.doctor?.full_name || 'Не призначено';
            html += `
                <tr>
                    <td>${r.patient?.full_name || '-'}</td>
                    <td>${new Date(r.datetime).toLocaleString('uk-UA')}</td>
                    <td>${doctorName}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="app.editRequest(${r.id})">Редагувати</button>
                        </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        list.innerHTML = html;
    },
    
    showForm(requestId = null) {
        const formDiv = document.getElementById('requestForm');
        
        // ДОДАНО: Тепер ми також завантажуємо список лікарів через API.getDoctors()
        Promise.all([
            API.getPatients(), 
            API.getDoctors(), 
            requestId ? API.getRequest(requestId) : Promise.resolve(null)
        ])
            .then(([patients, doctors, request]) => {
                this.renderForm(patients, doctors, request, formDiv);
            })
            .catch(err => {
                console.error('Error loading data:', err);
                formDiv.innerHTML = '<p class="text-danger">Помилка при завантаженні</p>';
            });
    },
    
    // ДОДАНО: аргумент doctors
    renderForm(patients, doctors, request, formDiv) {
        let patientOptions = '<option value="">Виберіть пацієнта</option>';
        patients.forEach(p => {
            patientOptions += `<option value="${p.id}" ${request?.patient?.id === p.id ? 'selected' : ''}>${p.full_name}</option>`;
        });
        
        // ДОДАНО: Генеруємо список лікарів для селекта
        let doctorOptions = '<option value="">Виберіть лікаря</option>';
        doctors.forEach(d => {
            doctorOptions += `<option value="${d.id}" ${request?.doctor?.id === d.id ? 'selected' : ''}>${d.full_name} (${d.specialization})</option>`;
        });
        
        const now = new Date().toISOString().slice(0, 16);
        
        let html = `
            <div class="card mt-4">
                <div class="card-header">
                    <h5>${request ? 'Редагувати' : 'Додати'} заявку</h5>
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
                            <label class="form-label">Лікар</label>
                            <select class="form-control" name="doctor_id" required>
                                ${doctorOptions}
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
            const form = e.target;
            const data = {
                patient_id: parseInt(form.patient_id.value),
                doctor_id: parseInt(form.doctor_id.value), // ДОДАНО: відправляємо doctor_id на бекенд
                datetime: form.datetime.value
            };
            
            if (request) {
                API.updateRequest(request.id, data).then(() => {
                    this.render();
                    app.hideForm();
                }).catch(err => console.error('Error updating request:', err));
            } else {
                API.createRequest(data).then(() => {
                    this.render();
                    app.hideForm();
                }).catch(err => console.error('Error creating request:', err));
            }
        });
    }
};

console.log('RequestsModule завантажений');