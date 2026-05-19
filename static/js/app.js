// Главное приложение с маршрутизацией
class App {
    constructor() {
        this.currentModule = null;
        this.init();
    }
    
    init() {
        window.addEventListener('hashchange', () => this.route());
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
        this.route();
    }
    
    route() {
        const hash = window.location.hash.slice(1) || '/';
        const [path, ...params] = hash.split('/').filter(p => p);
        
        switch (path) {
            case '':
            case '/':
                this.showHome();
                break;
            case 'patients':
                if (params[0] === 'edit' && params[1]) {
                    this.editPatient(parseInt(params[1]));
                } else if (params[0] === 'detail' && params[1]) {
                    this.showPatientDetail(parseInt(params[1]));
                } else {
                    this.renderPatients();
                }
                break;
            case 'requests':
                if (params[0] === 'edit' && params[1]) {
                    this.editRequest(parseInt(params[1]));
                } else {
                    this.renderRequests();
                }
                break;
            case 'appointments':
                if (params[0] === 'edit' && params[1]) {
                    this.editAppointment(parseInt(params[1]));
                } else if (params[0] === 'detail' && params[1]) {
                    this.showAppointmentDetail(parseInt(params[1]));
                } else {
                    this.renderAppointments();
                }
                break;
            case 'reports':
                if (window.IS_ADMIN) {
                    if (params[0] === 'work-financial') {
                        ReportsModule.renderWorkFinancialReport();
                    } else {
                        this.renderReports();
                    }
                } else {
                    window.location.hash = '#/';
                }
                break;
            case 'dictionaries':
                this.renderDictionaries();
                break;
            default:
                this.showHome();
        }
    }
    
    showHome() {
        const app = document.getElementById('app');
        
        Promise.all([
            API.getPatients(),
            API.getRequests(),
            API.getAppointments(),
            API.getDoctors()
        ]).then(([patients, requests, appointments, doctors]) => {
            app.innerHTML = `
                <h1>Панель управління</h1>
                <div class="row mb-4 mt-4">
                    <div class="col-md-3"><p><strong>Пацієнтів:</strong> ${patients.length || 0}</p></div>
                    <div class="col-md-3"><p><strong>Заявок:</strong> ${requests.length || 0}</p></div>
                    <div class="col-md-3"><p><strong>Прийомів:</strong> ${appointments.length || 0}</p></div>
                    <div class="col-md-3"><p><strong>Лікарів:</strong> ${doctors.length || 0}</p></div>
                </div>
                
                <h3 class="mt-4">Швидкі дії</h3>
                <p>
                    <a href="#/patients" class="btn btn-primary btn-sm">Пацієнти</a>
                    <a href="#/requests" class="btn btn-primary btn-sm">Заявки</a>
                    <a href="#/appointments" class="btn btn-primary btn-sm">Прийоми</a>
                    ${window.IS_ADMIN ? '<a href="#/reports" class="btn btn-primary btn-sm">Звіти</a>' : ''}
                    <a href="#/dictionaries" class="btn btn-primary btn-sm">Довідники</a>
                </p>
            `;
        }).catch(err => {
            console.error('Error loading home:', err);
            app.innerHTML = '<p class="text-danger">Помилка при завантаженні даних</p>';
        });
    }
    
    renderPatients() {
        PatientsModule.render();
        this.currentModule = PatientsModule;
    }
    
    showPatientForm() {
        PatientsModule.showForm();
    }
    
    editPatient(id) {
        PatientsModule.showForm(id);
    }
    
    deletePatient(id) {
        PatientsModule.deletePatient(id);
    }
    
    showPatientDetail(id) {
        PatientsModule.showDetail(id);
    }
    
    renderRequests() {
        RequestsModule.render();
        this.currentModule = RequestsModule;
    }
    
    showRequestForm() {
        RequestsModule.showForm();
    }
    
    editRequest(id) {
        RequestsModule.showForm(id);
    }
    
    deleteRequest(id) {
        RequestsModule.deleteRequest(id);
    }
    
    renderAppointments() {
        AppointmentsModule.render();
        this.currentModule = AppointmentsModule;
    }
    
    showAppointmentForm() {
        AppointmentsModule.showForm();
    }
    
    editAppointment(id) {
        AppointmentsModule.showForm(id);
    }
    
    deleteAppointment(id) {
        AppointmentsModule.deleteAppointment(id);
    }
    
    showAppointmentDetail(id) {
        AppointmentsModule.showDetail(id);
    }
    
    renderReports() {
        ReportsModule.render();
        this.currentModule = ReportsModule;
    }
    
    showFinancialReport() {
        ReportsModule.showFinancialReport();
    }
    
    showWorkFinancialReport() {
        ReportsModule.showWorkFinancialReport();
    }
    
    renderDictionaries() {
        DictionariesModule.render();
        this.currentModule = DictionariesModule;
    }
    
    showWorkCategories() {
        DictionariesModule.showWorkCategories();
    }
    
    showMaterialCategories() {
        DictionariesModule.showMaterialCategories();
    }
    
    showMedicineCategories() {
        DictionariesModule.showMedicineCategories();
    }
    
    showProcedureCategories() {
        DictionariesModule.showProcedureCategories();
    }
    
    showWorkCategoryForm() {
        DictionariesModule.showCategoryForm('work');
    }
    
    showMaterialCategoryForm() {
        DictionariesModule.showCategoryForm('material');
    }
    
    showMedicineCategoryForm() {
        DictionariesModule.showCategoryForm('medicine');
    }
    
    showProcedureCategoryForm() {
        DictionariesModule.showCategoryForm('procedure');
    }
    
    deleteCategory(id, type) {
        DictionariesModule.deleteCategory(id, type);
    }
    
    hideForm() {
        const pf = document.getElementById('patientForm');
        const rf = document.getElementById('requestForm');
        const af = document.getElementById('appointmentForm');
        if (pf) pf.innerHTML = '';
        if (rf) rf.innerHTML = '';
        if (af) af.innerHTML = '';
    }
    
    logout() {
        window.location.href = '/logout/';
    }
}

console.log('App клас завантажений');

// Инициализация приложения
const app = new App();
