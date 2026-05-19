// Главное приложение с маршрутизацией
class App {
    constructor() {
        this.currentModule = null;
        this.init();
    }
    
    init() {
        window.addEventListener('hashchange', () => this.route());
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());
        this.route();
    }
    
    route() {
        const hash = window.location.hash.slice(1) || '/';
        const [path, ...params] = hash.split('/');
        
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
                this.renderReports();
                break;
            case 'dictionaries':
                this.renderDictionaries();
                break;
            default:
                this.showHome();
        }
    }
    
    async showHome() {
        const app = document.getElementById('app');
        
        try {
            const patients = await API.getPatients();
            const requests = await API.getRequests();
            const appointments = await API.getAppointments();
            const doctors = await API.getDoctors();
            
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
                    <a href="#/reports" class="btn btn-info btn-sm">Звіти</a>
                    <a href="#/dictionaries" class="btn btn-outline-primary btn-sm">Довідники</a>
                </p>
            `;
        } catch (error) {
            app.innerHTML = `<div class="alert alert-danger">Помилка: ${error.message}</div>`;
        }
    }
    
    async renderPatients() {
        await PatientsModule.render();
        this.currentModule = PatientsModule;
    }
    
    async showPatientForm() {
        await PatientsModule.showForm();
    }
    
    async editPatient(id) {
        await PatientsModule.showForm(id);
    }
    
    async deletePatient(id) {
        await PatientsModule.deletePatient(id);
    }
    
    async showPatientDetail(id) {
        await PatientsModule.showDetail(id);
    }
    
    async renderRequests() {
        await RequestsModule.render();
        this.currentModule = RequestsModule;
    }
    
    async showRequestForm() {
        await RequestsModule.showForm();
    }
    
    async editRequest(id) {
        await RequestsModule.showForm(id);
    }
    
    async deleteRequest(id) {
        await RequestsModule.deleteRequest(id);
    }
    
    async renderAppointments() {
        await AppointmentsModule.render();
        this.currentModule = AppointmentsModule;
    }
    
    async showAppointmentForm() {
        await AppointmentsModule.showForm();
    }
    
    async editAppointment(id) {
        await AppointmentsModule.showForm(id);
    }
    
    async deleteAppointment(id) {
        await AppointmentsModule.deleteAppointment(id);
    }
    
    async showAppointmentDetail(id) {
        await AppointmentsModule.showDetail(id);
    }
    
    async renderReports() {
        await ReportsModule.render();
        this.currentModule = ReportsModule;
    }
    
    async showFinancialReport() {
        await ReportsModule.showFinancialReport();
    }
    
    async showWorkFinancialReport() {
        await ReportsModule.showWorkFinancialReport();
    }
    
    async renderDictionaries() {
        await DictionariesModule.render();
        this.currentModule = DictionariesModule;
    }
    
    async showWorkCategories() {
        await DictionariesModule.showWorkCategories();
    }
    
    async showMaterialCategories() {
        await DictionariesModule.showMaterialCategories();
    }
    
    async showMedicineCategories() {
        await DictionariesModule.showMedicineCategories();
    }
    
    async showProcedureCategories() {
        await DictionariesModule.showProcedureCategories();
    }
    
    async showWorkCategoryForm() {
        await DictionariesModule.showCategoryForm('work');
    }
    
    async showMaterialCategoryForm() {
        await DictionariesModule.showCategoryForm('material');
    }
    
    async showMedicineCategoryForm() {
        await DictionariesModule.showCategoryForm('medicine');
    }
    
    async showProcedureCategoryForm() {
        await DictionariesModule.showCategoryForm('procedure');
    }
    
    async deleteCategory(id, type) {
        await DictionariesModule.deleteCategory(id, type);
    }
    
    hideForm() {
        document.getElementById('patientForm')?.remove();
        document.getElementById('requestForm')?.remove();
        document.getElementById('appointmentForm')?.remove();
    }
    
    logout() {
        // Редирект на старую страницу входа
        window.location.href = '/logout/';
    }
}

// Инициализация приложения
const app = new App();
