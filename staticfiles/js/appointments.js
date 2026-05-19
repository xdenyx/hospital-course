// Прийоми
const AppointmentsModule = {
    async render() {
        const app = document.getElementById('app');
        const appointments = await API.getAppointments();
        
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Прийоми</h2>
                <button class="btn btn-success" onclick="app.showAppointmentForm()">Додати</button>
            </div>
            
            <div id="appointmentsList"></div>
            <div id="appointmentForm"></div>
        `;
        
        this.renderList(appointments);
    },
    
    renderList(appointments) {
        const list = document.getElementById('appointmentsList');
        
        if (!appointments || appointments.length === 0) {
            list.innerHTML = '<p class="text-muted">Немає прийомів</p>';
            return;
        }
        
        let html = '<table class="table table-striped">';
        html += '<thead><tr><th>Заявка</th><th>Пацієнт</th><th>Лікар</th><th>Примітки</th><th>Дії</th></tr></thead><tbody>';
        
        appointments.forEach(a => {
            const doctorName = a.request?.doctor?.full_name || '-';
            const patientName = a.request?.patient?.full_name || '-';
            html += `
                <tr>
                    <td>#${a.request}</td>
                    <td>${patientName}</td>
                    <td>${doctorName}</td>
                    <td>${a.notes || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="app.editAppointment(${a.id})">Редагувати</button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteAppointment(${a.id})">Видалити</button>
                        <button class="btn btn-sm btn-primary" onclick="app.showAppointmentDetail(${a.id})">Деталі</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        list.innerHTML = html;
    },
    
    async showForm(appointmentId = null) {
        const formDiv = document.getElementById('appointmentForm');
        const appointment = appointmentId ? await API.getAppointment(appointmentId) : null;
        const requests = await API.getRequests();
        
        let requestOptions = '<option value="">Виберіть заявку</option>';
        requests.forEach(r => {
            const doctorName = r.doctor?.full_name || 'Не призначен';
            const patientName = r.patient?.full_name || '-';
            const selected = appointment?.request === r.id ? 'selected' : '';
            requestOptions += `<option value="${r.id}" ${selected}>#${r.id} - ${patientName} (Лікар: ${doctorName})</option>`;
        });
        
        let html = `
            <div class="card mt-4">
                <div class="card-header">
                    <h5>${appointmentId ? 'Редагувати' : 'Додати'} прийом</h5>
                </div>
                <div class="card-body">
                    <form id="appointmentFormElement">
                        <div class="mb-3">
                            <label class="form-label">Заявка</label>
                            <select class="form-control" name="request" required>
                                ${requestOptions}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Примітки</label>
                            <textarea class="form-control" name="notes" rows="4">${appointment?.notes || ''}</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Зберегти</button>
                        <button type="button" class="btn btn-secondary" onclick="app.hideForm()">Скасувати</button>
                    </form>
                </div>
            </div>
        `;
        
        formDiv.innerHTML = html;
        
        document.getElementById('appointmentFormElement').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAppointment(e.target, appointmentId);
        });
    },
    
    async saveAppointment(form, appointmentId) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            if (appointmentId) {
                await API.updateAppointment(appointmentId, data);
            } else {
                await API.createAppointment(data);
            }
            
            this.render();
        } catch (error) {
            alert(`Помилка: ${error.message}`);
        }
    },
    
    async deleteAppointment(id) {
        if (confirm('Ви впевнені?')) {
            try {
                await API.deleteAppointment(id);
                this.render();
            } catch (error) {
                alert(`Помилка: ${error.message}`);
            }
        }
    },
    
    async showDetail(id) {
        const app = document.getElementById('app');
        const appointment = await API.getAppointment(id);
        
        const doctorName = appointment.request?.doctor?.full_name || 'Не призначен';
        const patientName = appointment.request?.patient?.full_name || '-';
        
        app.innerHTML = `
            <div>
                <button class="btn btn-secondary mb-3" onclick="app.renderAppointments()">Назад</button>
                <div class="card">
                    <div class="card-body">
                        <h5>Прийом #${appointment.id}</h5>
                        <p><strong>Пацієнт:</strong> ${patientName}</p>
                        <p><strong>Лікар:</strong> ${doctorName}</p>
                        <p><strong>Примітки:</strong> ${appointment.notes || '-'}</p>
                    </div>
                </div>
            </div>
        `;
    }
};
