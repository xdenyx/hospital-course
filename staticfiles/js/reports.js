// Звіти
const ReportsModule = {
    async render() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <h2>Звіти</h2>
            <div class="row mt-4">
                <div class="col-md-6 mb-3">
                    <button class="btn btn-info w-100" onclick="app.showFinancialReport()">Фінансовий звіт (Процедури)</button>
                </div>
                <div class="col-md-6 mb-3">
                    <button class="btn btn-info w-100" onclick="app.showWorkFinancialReport()">Фінансовий звіт (Роботи)</button>
                </div>
            </div>
            <div id="reportContent"></div>
        `;
    },
    
    async showFinancialReport() {
        const reportDiv = document.getElementById('reportContent');
        
        try {
            const response = await fetch('/api/schema/');
            const data = await response.json();
            
            reportDiv.innerHTML = `
                <div class="alert alert-info">
                    <h5>Фінансовий звіт за класами процедур</h5>
                    <p>Переглядіть звіт: <a href="/reports/financial/" target="_blank">Перейти</a></p>
                </div>
            `;
        } catch (error) {
            reportDiv.innerHTML = `<div class="alert alert-danger">Помилка: ${error.message}</div>`;
        }
    },
    
    async showWorkFinancialReport() {
        const reportDiv = document.getElementById('reportContent');
        
        try {
            reportDiv.innerHTML = `
                <div class="alert alert-info">
                    <h5>Фінансовий звіт за категоріями робіт</h5>
                    <p>Переглядіть звіт: <a href="/reports/work-financial/" target="_blank">Перейти</a></p>
                </div>
            `;
        } catch (error) {
            reportDiv.innerHTML = `<div class="alert alert-danger">Помилка: ${error.message}</div>`;
        }
    }
};
