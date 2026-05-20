// Пацієнти та Протоколи
const PatientsModule = {
    render() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-primary">Пацієнти</h2>
                <button class="btn btn-success shadow-sm" onclick="app.showPatientForm()">
                    <i class="bi bi-person-plus-fill me-1"></i> Додати пацієнта
                </button>
            </div>
            
            <div id="patientsList"><p class="text-muted text-center py-5">Завантаження...</p></div>
            <div id="patientForm"></div>
        `;
        
        API.getPatients().then(patients => {
            this.renderList(patients);
        }).catch(err => {
            console.error('Error loading patients:', err);
            document.getElementById('patientsList').innerHTML = '<div class="alert alert-danger">Помилка при завантаженні даних</div>';
        });
    },
    
    renderList(patients) {
        const list = document.getElementById('patientsList');
        
        if (!patients || patients.length === 0) {
            list.innerHTML = '<div class="text-center py-5 border rounded bg-white"><p class="text-muted mb-0">Немає пацієнтів у базі</p></div>';
            return;
        }
        
        let html = '<div class="card shadow-sm"><table class="table table-hover table-striped mb-0">';
        html += '<thead class="table-primary text-primary-emphasis"><tr><th>ПІБ</th><th>Дата народження</th><th>Вік</th><th class="text-end">Дії</th></tr></thead><tbody>';
        
        patients.forEach(p => {
            html += `
                <tr class="align-middle">
                    <td class="fw-bold text-dark">${p.full_name}</td>
                    <td>${p.date_of_birth}</td>
                    <td><span class="badge bg-light text-dark border">${p.age || '-'} років</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info me-1" onclick="app.editPatient(${p.id})">Редагувати</button>
                        <button class="btn btn-sm btn-primary shadow-sm" onclick="PatientsModule.showDetail(${p.id})">
                            <i class="bi bi-file-earmark-medical-fill me-1"></i>Протокол
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        list.innerHTML = html;
    },
    
    showForm(patientId = null) {
        const formDiv = document.getElementById('patientForm');
        
        if (patientId) {
            API.getPatient(patientId).then(patient => {
                this.renderForm(patient, formDiv);
            }).catch(err => {
                console.error('Error loading patient:', err);
                formDiv.innerHTML = '<div class="alert alert-danger mt-3">Помилка при завантаженні даних пацієнта</div>';
            });
        } else {
            this.renderForm(null, formDiv);
        }
    },
    
    renderForm(patient, formDiv) {
        let html = `
            <div class="card mt-4 shadow border-success">
                <div class="card-header bg-success bg-opacity-10 text-success">
                    <h5 class="mb-0 fw-bold">${patient ? 'Редагувати картку' : 'Створити нову картку'} пацієнта</h5>
                </div>
                <div class="card-body bg-white">
                    <form id="patientFormElement">
                        <div class="mb-3">
                            <label class="form-label fw-bold text-success">ПІБ</label>
                            <input type="text" class="form-control form-control-lg border-success-subtle" name="full_name" value="${patient?.full_name || ''}" required placeholder="Іванов Іван Іванович">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold text-success">Дата народження</label>
                            <input type="date" class="form-control" name="date_of_birth" value="${patient?.date_of_birth || ''}" required>
                        </div>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-success btn-lg">Зберегти</button>
                            <button type="button" class="btn btn-outline-secondary btn-lg" onclick="app.hideForm()">Скасувати</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        formDiv.innerHTML = html;
        
        document.getElementById('patientFormElement').addEventListener('submit', (e) => {
            e.preventDefault();
            const form = e.target;
            const data = {
                full_name: form.full_name.value,
                date_of_birth: form.date_of_birth.value
            };
            
            if (patient) {
                API.updatePatient(patient.id, data).then(() => {
                    this.render();
                    app.hideForm();
                }).catch(err => console.error('Error updating patient:', err));
            } else {
                API.createPatient(data).then(() => {
                    this.render();
                    app.hideForm();
                }).catch(err => console.error('Error creating patient:', err));
            }
        });
    },

    // Реалізація детального медичного протоколу пацієнта
    showDetail(id) {
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="text-muted mt-2">Формування протоколу лікування...</p></div>';

        Promise.all([API.getPatient(id), API.getPatientProtocol(id)])
            .then(([patient, protocol]) => {
                
                let protocolHtml = '';
                
                if (!protocol || protocol.length === 0) {
                    protocolHtml = `
                        <div class="text-center py-5 border rounded bg-white mt-3">
                            <i class="bi bi-slash-circle text-warning fs-1"></i>
                            <p class="text-muted mt-3 mb-0">Історія прийомів та виконаних процедур для цього пацієнта відсутня.</p>
                        </div>
                    `;
                } else {
                    protocol.forEach(appt => {
                        let worksHtml = '';
                        
                        if (appt.works && appt.works.length > 0) {
                            appt.works.forEach(w => {
                                let materialsLi = '';
                                if (w.materials && w.materials.length > 0) {
                                    w.materials.forEach(m => {
                                        materialsLi += `
                                            <li class="d-flex justify-content-between align-items-center mb-1">
                                                <span class="text-dark-emphasis">${m.category_name || 'Невідомий матеріал'}</span>
                                                <span class="badge bg-light text-secondary border ms-2">${m.quantity} шт.</span>
                                            </li>
                                        `;
                                    });
                                }
                                
                                let medicinesLi = '';
                                if (w.medicines && w.medicines.length > 0) {
                                    w.medicines.forEach(med => {
                                        medicinesLi += `
                                            <li class="d-flex justify-content-between align-items-center mb-1">
                                                <span class="text-dark-emphasis">${med.category_name || 'Невідомі ліки'}</span>
                                                <span class="badge bg-light text-secondary border ms-2">${med.quantity} шт.</span>
                                            </li>
                                        `;
                                    });
                                }
                                
                                let proceduresLi = '';
                                if (w.procedures && w.procedures.length > 0) {
                                    w.procedures.forEach(proc => {
                                        proceduresLi += `
                                            <li class="d-flex justify-content-between align-items-center mb-1">
                                                <span class="text-dark-emphasis">${proc.category_name || 'Невідома процедура'}</span>
                                                <span class="badge bg-light text-secondary border ms-2">${parseFloat(proc.cost).toFixed(2)} грн</span>
                                            </li>
                                        `;
                                    });
                                }

                                worksHtml += `
                                    <div class="border border-info-subtle rounded p-3 mb-3 bg-white shadow-sm">
                                        <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-info-subtle">
                                            <h6 class="text-info fw-bold mb-0">
                                                <i class="bi bi-wrench-adjustable me-1"></i>
                                                ${w.category_name || 'Маніпуляція / Робота'}
                                            </h6>
                                            <span class="text-muted small">ID: ${w.work_category}</span>
                                        </div>
                                        <div class="p-2 bg-light rounded mb-3 d-flex gap-2 flex-wrap">
                                            <span class="badge bg-success bg-opacity-75">Ціна для пацієнта: ${parseFloat(w.price).toFixed(2)} грн</span>
                                            <span class="badge bg-danger bg-opacity-75">Витрати: ${parseFloat(w.cost).toFixed(2)} грн</span>
                                            <span class="badge bg-primary">Чистий дохід: ${parseFloat(w.profit).toFixed(2)} грн</span>
                                        </div>
                                        <div class="row g-2 style="font-size: 0.85rem;">
                                            <div class="col-md-4">
                                                <div class="p-2 border rounded h-100 bg-white">
                                                    <small class="text-muted d-block font-weight-bold mb-1 pb-1 border-bottom">Списані матеріали:</small>
                                                    <ul class="ps-0 mb-0 list-unstyled" style="min-height: 20px;">
                                                        ${materialsLi || '<li class="text-muted italic small">Не використовувались</li>'}
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="p-2 border rounded h-100 bg-white">
                                                    <small class="text-muted d-block font-weight-bold mb-1 pb-1 border-bottom">Використані ліки:</small>
                                                    <ul class="ps-0 mb-0 list-unstyled" style="min-height: 20px;">
                                                        ${medicinesLi || '<li class="text-muted italic small">Не використовувались</li>'}
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="p-2 border rounded h-100 bg-white">
                                                    <small class="text-muted d-block font-weight-bold mb-1 pb-1 border-bottom">Супутні процедури:</small>
                                                    <ul class="ps-0 mb-0 list-unstyled" style="min-height: 20px;">
                                                        ${proceduresLi || '<li class="text-muted italic small">Не проводились</li>'}
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            });
                        } else {
                            worksHtml = '<div class="alert alert-light border text-muted italic small">Роботи під час цього прийому не фіксувалися.</div>';
                        }

                        protocolHtml += `
                            <div class="card mb-4 border-primary-subtle shadow-sm overflow-hidden">
                                <div class="card-header bg-primary-subtle text-primary-emphasis border-bottom border-primary-subtle d-flex justify-content-between align-items-center">
                                    <h5 class="mb-0 fw-bold">Прийом #${appt.id} від ${new Date(appt.request?.datetime).toLocaleString('uk-UA')}</h5>
                                    <div class="text-end">
                                        <i class="bi bi-person-fill-gear me-1"></i><strong>Лікар:</strong> 
                                        ${appt.request?.doctor?.full_name || 'Не вказано'} 
                                        <span class="badge bg-primary ms-1">${appt.request?.doctor?.specialization || 'Н/Д'}</span>
                                    </div>
                                </div>
                                <div class="card-body bg-light bg-opacity-25">
                                    <div class="p-3 bg-white border rounded mb-3">
                                        <strong>Нотатки лікаря:</strong> 
                                        <p class="mb-0 text-dark-emphasis">${appt.notes || '<span class="text-muted italic small">відсутні</span>'}</p>
                                    </div>
                                    <h6 class="text-primary mt-3 mb-3 pb-1 border-bottom border-primary-subtle">
                                        <i class="bi bi-clipboard2-pulse me-1"></i>Деталізація медичних послуг та розрахунок витрат:
                                    </h6>
                                    ${worksHtml}
                                </div>
                            </div>
                        `;
                    });
                }

                appContainer.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2 class="text-primary fw-bold">Медичний протокол лікування</h2>
                        <button class="btn btn-outline-secondary" onclick="PatientsModule.render()">
                            <i class="bi bi-arrow-left me-1"></i> Назад до списку
                        </button>
                    </div>
                    
                    <div class="card card-body bg-primary text-white mb-4 shadow border-0">
                        <div class="row align-items-center">
                            <div class="col-md-7">
                                <h1 class="display-6 mb-1 text-white">${patient.full_name}</h1>
                                <p class="lead mb-0 opacity-75">ID картки: ${patient.id}</p>
                            </div>
                            <div class="col-md-5 text-md-end mt-3 mt-md-0">
                                <p class="mb-1"><strong><i class="bi bi-calendar-event me-1"></i>Дата народження:</strong> ${patient.date_of_birth}</p>
                                <h2 class="mb-0 fw-bold"><span class="badge bg-white text-primary">${patient.age} років</span></h2>
                            </div>
                        </div>
                    </div>
                    
                    <h4 class="mb-3 text-dark fw-bold">Картка призначень та виконаних маніпуляцій:</h4>
                    ${protocolHtml}
                    
                    <div class="mt-5 mb-5 pb-5 border-top pt-3 text-center">
                        <button class="btn btn-lg btn-outline-secondary px-5 shadow-sm" onclick="PatientsModule.render()">
                            <i class="bi bi-arrow-left-circle-fill me-2"></i> Повернутися до списку пацієнтів
                        </button>
                    </div>
                `;
            })
            .catch(err => {
                console.error(err);
                appContainer.innerHTML = '<div class="alert alert-danger mt-3">Помилка завантаження медичного протоколу.</div>';
            });
    }
};

console.log('PatientsModule завантажений');