// Звіти та вибірки
const ReportsModule = {
    render() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <h2>Звіти та вибірки</h2>
            <div class="mb-4">
                <a href="#/reports/work-financial" class="btn btn-primary me-2">Звіт по класам робіт</a>
                <button class="btn btn-info" onclick="ReportsModule.showPatientFilter()">Вибірка пацієнтів за роботами</button>
            </div>
            <div id="reportContent"></div>
        `;
    },
    
    renderWorkFinancialReport() {
        this.render();
        
        setTimeout(() => {
            const contentDiv = document.getElementById('reportContent');
            contentDiv.innerHTML = '<p class="text-muted">Завантаження звіту...</p>';
            
            Promise.all([API.getWorkCategories(), API.getAppointmentWorks()])
                .then(([categories, works]) => {
                    const reportData = {};
                    categories.forEach(c => {
                        reportData[c.id] = { name: c.name, income: 0, expenses: 0, profit: 0 };
                    });
                    
                    works.forEach(w => {
                        if (reportData[w.work_category]) {
                            reportData[w.work_category].income += parseFloat(w.price || 0);
                            reportData[w.work_category].expenses += parseFloat(w.cost || 0);
                            reportData[w.work_category].profit += parseFloat(w.profit || 0);
                        }
                    });
                    
                    let html = `
                        <div class="d-flex justify-content-between align-items-center mt-4 mb-2">
                            <h5>Фінансовий звіт за класами робіт</h5>
                            <button class="btn btn-sm btn-secondary" onclick="ReportsModule.render()">← Назад</button>
                        </div>
                        <div class="card p-0 shadow-sm">
                            <table class="table table-striped table-bordered mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>Клас роботи</th>
                                        <th>Дохід (грн)</th>
                                        <th>Витрати (матеріали, ліки, процедури)</th>
                                        <th>Чистий дохід (грн)</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    let totalInc = 0, totalExp = 0, totalProf = 0;
                    Object.values(reportData).forEach(row => {
                        html += `
                            <tr>
                                <td><strong>${row.name}</strong></td>
                                <td class="text-success">${row.income.toFixed(2)}</td>
                                <td class="text-danger">${row.expenses.toFixed(2)}</td>
                                <td class="text-primary fw-bold">${row.profit.toFixed(2)}</td>
                            </tr>
                        `;
                        totalInc += row.income;
                        totalExp += row.expenses;
                        totalProf += row.profit;
                    });
                    
                    html += `
                                </tbody>
                                <tfoot class="table-dark">
                                    <tr>
                                        <th>Всього:</th>
                                        <th>${totalInc.toFixed(2)}</th>
                                        <th>${totalExp.toFixed(2)}</th>
                                        <th>${totalProf.toFixed(2)}</th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                    contentDiv.innerHTML = html;
                })
                .catch(err => {
                    contentDiv.innerHTML = '<p class="text-danger">Помилка завантаження даних</p>';
                });
        }, 50);
    },
    
    showPatientFilter() {
        this.render();
        
        setTimeout(() => {
            const contentDiv = document.getElementById('reportContent');
            
            API.getWorkCategories().then(works => {
                let workOptions = '<option value="">Оберіть роботу</option>';
                works.forEach(w => {
                    workOptions += `<option value="${w.id}">${w.name}</option>`;
                });

                contentDiv.innerHTML = `
                    <div class="card mt-4 bg-light shadow-sm">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="mb-0">Вибірка пацієнтів за виконаними роботами</h5>
                                <button class="btn btn-sm btn-secondary" onclick="ReportsModule.render()">← Назад</button>
                            </div>
                            <form id="filterPatientsForm" class="row g-3">
                                <div class="col-md-4">
                                    <label class="form-label">Робота</label>
                                    <select class="form-select" id="filterWorkId" required>
                                        ${workOptions}
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">З дати</label>
                                    <input type="date" class="form-control" id="filterStartDate" required>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">По дату</label>
                                    <input type="date" class="form-control" id="filterEndDate" required>
                                </div>
                                <div class="col-md-2 d-flex align-items-end">
                                    <button type="submit" class="btn btn-primary w-100">Шукати</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div id="filteredResults" class="mt-4"></div>
                `;

                document.getElementById('filterPatientsForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    const workId = document.getElementById('filterWorkId').value;
                    const startDate = document.getElementById('filterStartDate').value;
                    const endDate = document.getElementById('filterEndDate').value;
                    
                    document.getElementById('filteredResults').innerHTML = '<p>Обробка...</p>';
                    
                    API.request(`/patients/by-work/?work_id=${workId}&start_date=${startDate}&end_date=${endDate}`)
                        .then(patients => {
                            if (patients.length === 0) {
                                document.getElementById('filteredResults').innerHTML = '<div class="alert alert-warning">За вказаний період пацієнтів не знайдено.</div>';
                                return;
                            }
                            
                            let html = '<h5 class="mt-3">Результат вибірки:</h5><table class="table table-bordered table-hover mt-2">';
                            html += '<thead class="table-dark"><tr><th>ПІБ</th><th>Дата народження</th><th>Вік</th></tr></thead><tbody>';
                            patients.forEach(p => {
                                html += `<tr><td>${p.full_name}</td><td>${p.date_of_birth}</td><td>${p.age || '-'}</td></tr>`;
                            });
                            html += '</tbody></table>';
                            document.getElementById('filteredResults').innerHTML = html;
                        })
                        .catch(err => {
                            document.getElementById('filteredResults').innerHTML = '<div class="alert alert-danger">Помилка завантаження даних</div>';
                        });
                });
            });
        }, 50);
    }
};

console.log('ReportsModule завантажений');