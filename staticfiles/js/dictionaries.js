// Довідники
const DictionariesModule = {
    async render() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <h2>Довідники</h2>
            <div class="row mt-4">
                <div class="col-md-3 mb-3">
                    <button class="btn btn-outline-primary w-100" onclick="app.showWorkCategories()">Категорії робіт</button>
                </div>
                <div class="col-md-3 mb-3">
                    <button class="btn btn-outline-primary w-100" onclick="app.showMaterialCategories()">Матеріали</button>
                </div>
                <div class="col-md-3 mb-3">
                    <button class="btn btn-outline-primary w-100" onclick="app.showMedicineCategories()">Ліки</button>
                </div>
                <div class="col-md-3 mb-3">
                    <button class="btn btn-outline-primary w-100" onclick="app.showProcedureCategories()">Процедури</button>
                </div>
            </div>
            <div id="dictContent"></div>
        `;
    },
    
    async showWorkCategories() {
        const content = document.getElementById('dictContent');
        const categories = await API.getWorkCategories();
        
        let html = `
            <div class="mt-4">
                <h5>Категорії робіт</h5>
                <button class="btn btn-success mb-3" onclick="app.showWorkCategoryForm()">Додати</button>
                <div id="workCategoriesList"></div>
                <div id="workCategoryForm"></div>
            </div>
        `;
        content.innerHTML = html;
        this.renderCategoriesList(categories, 'workCategoriesList', 'work');
    },
    
    async showMaterialCategories() {
        const content = document.getElementById('dictContent');
        const categories = await API.getMaterialCategories();
        
        let html = `
            <div class="mt-4">
                <h5>Матеріали</h5>
                <button class="btn btn-success mb-3" onclick="app.showMaterialCategoryForm()">Додати</button>
                <div id="materialCategoriesList"></div>
                <div id="materialCategoryForm"></div>
            </div>
        `;
        content.innerHTML = html;
        this.renderCategoriesList(categories, 'materialCategoriesList', 'material');
    },
    
    async showMedicineCategories() {
        const content = document.getElementById('dictContent');
        const categories = await API.getMedicineCategories();
        
        let html = `
            <div class="mt-4">
                <h5>Ліки</h5>
                <button class="btn btn-success mb-3" onclick="app.showMedicineCategoryForm()">Додати</button>
                <div id="medicineCategoriesList"></div>
                <div id="medicineCategoryForm"></div>
            </div>
        `;
        content.innerHTML = html;
        this.renderCategoriesList(categories, 'medicineCategoriesList', 'medicine');
    },
    
    async showProcedureCategories() {
        const content = document.getElementById('dictContent');
        const categories = await API.getProcedureCategories();
        
        let html = `
            <div class="mt-4">
                <h5>Процедури</h5>
                <button class="btn btn-success mb-3" onclick="app.showProcedureCategoryForm()">Додати</button>
                <div id="procedureCategoriesList"></div>
                <div id="procedureCategoryForm"></div>
            </div>
        `;
        content.innerHTML = html;
        this.renderCategoriesList(categories, 'procedureCategoriesList', 'procedure');
    },
    
    renderCategoriesList(categories, elementId, type) {
        const list = document.getElementById(elementId);
        
        if (!categories || categories.length === 0) {
            list.innerHTML = '<p class="text-muted">Немає категорій</p>';
            return;
        }
        
        let html = '<table class="table table-striped"><thead><tr><th>Назва</th><th>Дії</th></tr></thead><tbody>';
        
        categories.forEach(c => {
            html += `
                <tr>
                    <td>${c.name}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteCategory(${c.id}, '${type}')">Видалити</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        list.innerHTML = html;
    },
    
    async showCategoryForm(type) {
        const formDivId = `${type}CategoryForm`;
        const formDiv = document.getElementById(formDivId);
        
        let html = `
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Додати категорію</h5>
                </div>
                <div class="card-body">
                    <form id="${type}CategoryFormElement">
                        <div class="mb-3">
                            <label class="form-label">Назва</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Зберегти</button>
                        <button type="button" class="btn btn-secondary" onclick="app.hideForm()">Скасувати</button>
                    </form>
                </div>
            </div>
        `;
        
        formDiv.innerHTML = html;
        
        document.getElementById(`${type}CategoryFormElement`).addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCategory(e.target, type);
        });
    },
    
    async saveCategory(form, type) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            if (type === 'work') {
                await API.createWorkCategory(data);
                this.showWorkCategories();
            } else if (type === 'material') {
                await API.createMaterialCategory(data);
                this.showMaterialCategories();
            } else if (type === 'medicine') {
                await API.createMedicineCategory(data);
                this.showMedicineCategories();
            } else if (type === 'procedure') {
                await API.createProcedureCategory(data);
                this.showProcedureCategories();
            }
        } catch (error) {
            alert(`Помилка: ${error.message}`);
        }
    },
    
    async deleteCategory(id, type) {
        if (confirm('Ви впевнені?')) {
            // API не має DELETE для категорій, тому просто оновлюємо список
            alert('Видалення доступне через адмін панель');
        }
    }
};
