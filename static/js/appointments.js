// Прийоми та Управління Роботами (Без ручного введення цін)
const AppointmentsModule = {
    render() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-primary fw-bold">Прийоми</h2>
                <button class="btn btn-success shadow-sm" onclick="app.showAppointmentForm()">Створити прийом</button>
            </div>
            <div id="appointmentsList"><p class="text-muted text-center py-4">Завантаження...</p></div>
            <div id="appointmentForm"></div>
        `;
        API.getAppointments().then(appointments => this.renderList(appointments))
           .catch(err => document.getElementById('appointmentsList').innerHTML = '<div class="alert alert-danger">Помилка при завантаженні</div>');
    },
    
    renderList(appointments) {
        const list = document.getElementById('appointmentsList');
        if (!appointments || appointments.length === 0) {
            list.innerHTML = '<div class="alert alert-light text-center border">Немає прийомів</div>';
            return;
        }
        
        let html = '<div class="card shadow-sm border-0"><table class="table table-hover mb-0">';
        html += '<thead class="table-light"><tr><th>ID</th><th>Пацієнт</th><th>Лікар</th><th>Примітки</th><th class="text-end">Дії</th></tr></thead><tbody>';
        
        appointments.forEach(a => {
            html += `
                <tr class="align-middle">
                    <td>#${a.id}</td>
                    <td class="fw-bold">${a.request?.patient?.full_name || '-'}</td>
                    <td>${a.request?.doctor?.full_name || '-'}</td>
                    <td class="text-muted small">${a.notes || '-'}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info me-2" onclick="app.editAppointment(${a.id})">Редагувати</button>
                        <button class="btn btn-sm btn-primary shadow-sm" onclick="AppointmentsModule.showDetail(${a.id})">Керувати прийомом</button>
                    </td>
                </tr>
            `;
        });
        html += '</tbody></table></div>';
        list.innerHTML = html;
    },
    
    showForm(appointmentId = null) {
        const formDiv = document.getElementById('appointmentForm');
        Promise.all([API.getRequests(), appointmentId ? API.getAppointment(appointmentId) : Promise.resolve(null)])
            .then(([requests, appointment]) => {
                let requestOptions = '<option value="">Виберіть заявку</option>';
                requests.forEach(r => { requestOptions += `<option value="${r.id}" ${appointment?.request?.id === r.id ? 'selected' : ''}>Заявка #${r.id} - ${r.patient?.full_name}</option>`; });
                
                formDiv.innerHTML = `
                    <div class="card mt-4 shadow-sm border-0">
                        <div class="card-header bg-light"><h5 class="mb-0 text-primary">${appointment ? 'Редагувати' : 'Створити'} прийом</h5></div>
                        <div class="card-body">
                            <form id="appointmentFormElement">
                                <div class="mb-3">
                                    <label class="form-label">Заявка (Пацієнт)</label>
                                    <select class="form-select" name="request_id" required>${requestOptions}</select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Примітки лікаря</label>
                                    <textarea class="form-control" name="notes" rows="3">${appointment?.notes || ''}</textarea>
                                </div>
                                <button type="submit" class="btn btn-primary px-4">Зберегти</button>
                                <button type="button" class="btn btn-light ms-2 px-4" onclick="app.hideForm()">Скасувати</button>
                            </form>
                        </div>
                    </div>
                `;
                
                document.getElementById('appointmentFormElement').addEventListener('submit', (e) => {
                    e.preventDefault();
                    const data = { request_id: parseInt(e.target.request_id.value), notes: e.target.notes.value };
                    const requestPromise = appointment ? API.updateAppointment(appointment.id, data) : API.createAppointment(data);
                    requestPromise.then(() => { this.render(); app.hideForm(); }).catch(err => console.error(err));
                });
            }).catch(err => formDiv.innerHTML = '<div class="alert alert-danger">Помилка завантаження</div>');
    },

    showDetail(id) {
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>';

        Promise.all([
            API.getAppointment(id),
            API.getWorkCategories(),
            API.getMaterialCategories(),
            API.getMedicineCategories(),
            API.getProcedureCategories()
        ]).then(([appt, works, materials, medicines, procedures]) => {
            
            const workOpts = works.map(w => `<option value="${w.id}">${w.name}</option>`).join('');
            const matOpts = materials.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            const medOpts = medicines.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            const procOpts = procedures.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

            let worksHtml = '';
            
            if (appt.works && appt.works.length > 0) {
                appt.works.forEach(w => {
                    const renderList = (items) => items.map(i => `
                        <li class="list-group-item d-flex justify-content-between align-items-center bg-white border rounded py-1 px-2 mb-1">
                            <span class="small">${i.category_name} ${i.quantity ? `(<b>${i.quantity} шт.</b>)` : ''}</span>
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-10">${i.cost} грн</span>
                        </li>
                    `).join('');

                    worksHtml += `
                        <div class="card mb-4 border-info shadow-sm bg-light bg-opacity-50">
                            <div class="card-header bg-white d-flex justify-content-between align-items-center py-3 border-bottom border-info border-opacity-25">
                                <h6 class="mb-0 fw-bold text-primary">${w.category_name}</h6>
                                <div class="d-flex gap-2">
                                    <span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25">Ціна: ${w.price} ₴</span>
                                    <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25">Витрати: ${w.cost} ₴</span>
                                    <span class="badge bg-primary">Прибуток: ${w.profit} ₴</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row g-3">
                                    <div class="col-md-4">
                                        <div class="p-2 bg-white rounded border shadow-sm h-100">
                                            <h6 class="text-muted small text-uppercase fw-bold border-bottom pb-1 mb-2">Матеріали</h6>
                                            <ul class="list-group list-group-flush mb-2">${w.materials.length ? renderList(w.materials) : '<p class="small text-muted mb-2 fst-italic">Немає матеріалів</p>'}</ul>
                                            <form onsubmit="AppointmentsModule.addConsumable(event, 'mat', ${w.id}, ${appt.id})" class="mt-2 border-top pt-2">
                                                <select class="form-select form-select-sm mb-1" name="cat" required><option value="">+ Обрати матеріал</option>${matOpts}</select>
                                                <input type="number" class="form-control form-control-sm mb-1" name="qty" placeholder="Кількість" required min="1" value="1">
                                                <button type="submit" class="btn btn-sm btn-outline-success w-100">Додати</button>
                                            </form>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="p-2 bg-white rounded border shadow-sm h-100">
                                            <h6 class="text-muted small text-uppercase fw-bold border-bottom pb-1 mb-2">Ліки</h6>
                                            <ul class="list-group list-group-flush mb-2">${w.medicines.length ? renderList(w.medicines) : '<p class="small text-muted mb-2 fst-italic">Немає ліків</p>'}</ul>
                                            <form onsubmit="AppointmentsModule.addConsumable(event, 'med', ${w.id}, ${appt.id})" class="mt-2 border-top pt-2">
                                                <select class="form-select form-select-sm mb-1" name="cat" required><option value="">+ Обрати ліки</option>${medOpts}</select>
                                                <input type="number" class="form-control form-control-sm mb-1" name="qty" placeholder="Кількість" required min="1" value="1">
                                                <button type="submit" class="btn btn-sm btn-outline-success w-100">Додати</button>
                                            </form>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="p-2 bg-white rounded border shadow-sm h-100">
                                            <h6 class="text-muted small text-uppercase fw-bold border-bottom pb-1 mb-2">Супутні процедури</h6>
                                            <ul class="list-group list-group-flush mb-2">${w.procedures.length ? renderList(w.procedures) : '<p class="small text-muted mb-2 fst-italic">Немає процедур</p>'}</ul>
                                            <form onsubmit="AppointmentsModule.addConsumable(event, 'proc', ${w.id}, ${appt.id})" class="mt-2 border-top pt-2">
                                                <select class="form-select form-select-sm mb-1" name="cat" required><option value="">+ Обрати процедуру</option>${procOpts}</select>
                                                <button type="submit" class="btn btn-sm btn-outline-success w-100 mt-1">Додати</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
            } else {
                worksHtml = '<div class="alert alert-light text-center py-4 border text-muted">У цьому прийомі ще не виконано жодної роботи.</div>';
            }

            appContainer.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2 class="text-primary fw-bold">Керування прийомом #${appt.id}</h2>
                    <button class="btn btn-outline-secondary" onclick="AppointmentsModule.render()">← Назад до списку</button>
                </div>
                
                <div class="card mb-4 bg-light border-0 shadow-sm">
                    <div class="card-body p-4">
                        <h4 class="mb-1 text-dark">Пацієнт: <strong>${appt.request?.patient?.full_name}</strong></h4>
                        <p class="mb-0 text-muted">Лікар: ${appt.request?.doctor?.full_name} | Дата: ${new Date(appt.request?.datetime).toLocaleString('uk-UA')}</p>
                        ${appt.notes ? `<p class="mt-2 mb-0 border-top pt-2 text-dark"><strong>Нотатки лікаря:</strong> ${appt.notes}</p>` : ''}
                    </div>
                </div>

                <div class="mb-4">
                    <h5 class="text-dark fw-bold mb-3">Виконані роботи та витрати:</h5>
                    ${worksHtml}
                </div>

                <div class="card border-0 shadow-sm bg-light mb-5">
                    <div class="card-body p-4">
                        <h5 class="text-primary fw-bold mb-3">Додати роботу</h5>
                        <form onsubmit="AppointmentsModule.addWork(event, ${appt.id})" class="row g-2 align-items-center">
                            <div class="col-md-9">
                                <select class="form-select" name="work_category" required>
                                    <option value="">Оберіть роботу зі списку...</option>
                                    ${workOpts}
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button type="submit" class="btn btn-success w-100 shadow-sm">Зберегти роботу</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
        }).catch(err => {
            console.error(err);
            appContainer.innerHTML = '<div class="alert alert-danger">Помилка завантаження даних прийому.</div>';
        });
    },

    addWork(event, appointmentId) {
        event.preventDefault();
        const data = {
            appointment: appointmentId,
            work_category: parseInt(event.target.work_category.value)
        };
        
        API.createAppointmentWork(data)
            .then(() => this.showDetail(appointmentId))
            .catch(err => alert('Помилка при додаванні роботи!'));
    },

    addConsumable(event, type, workId, appointmentId) {
        event.preventDefault();
        const form = event.target;
        const categoryId = parseInt(form.cat.value);
        
        let apiCall;
        
        if (type === 'mat') {
            apiCall = API.createWorkMaterial({ appointment_work: workId, category: categoryId, quantity: parseInt(form.qty.value) });
        } else if (type === 'med') {
            apiCall = API.createWorkMedicine({ appointment_work: workId, category: categoryId, quantity: parseInt(form.qty.value) });
        } else if (type === 'proc') {
            apiCall = API.createWorkProcedure({ appointment_work: workId, category: categoryId });
        }

        apiCall.then(() => this.showDetail(appointmentId))
        .catch(err => {
            console.error(err);
            alert('Помилка при збереженні витрат!');
        });
    }
};

console.log('AppointmentsModule завантажений');