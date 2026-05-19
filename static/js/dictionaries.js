// Довідники
const DictionariesModule = {
    render() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <h2>Довідники</h2>
            <p>
                <button class="btn btn-primary" onclick="app.showWorkCategories()">Категорії робіт</button>
                <button class="btn btn-primary" onclick="app.showMaterialCategories()">Категорії матеріалів</button>
                <button class="btn btn-primary" onclick="app.showMedicineCategories()">Категорії ліків</button>
                <button class="btn btn-primary" onclick="app.showProcedureCategories()">Категорії процедур</button>
            </p>
        `;
    },
    
    showWorkCategories() {
        const app = document.getElementById('app');
        app.innerHTML = '<p class="text-muted">Завантаження...</p>';
        
        API.getWorkCategories().then(categories => {
            this.renderCategoriesList(categories, 'work');
        }).catch(err => {
            console.error('Error:', err);
            app.innerHTML = '<p class="text-danger">Помилка</p>';
        });
    },
    
    showMaterialCategories() {
        const app = document.getElementById('app');
        app.innerHTML = '<p class="text-muted">Завантаження...</p>';
        
        API.getMaterialCategories().then(categories => {
            this.renderCategoriesList(categories, 'material');
        }).catch(err => {
            console.error('Error:', err);
            app.innerHTML = '<p class="text-danger">Помилка</p>';
        });
    },
    
    showMedicineCategories() {
        const app = document.getElementById('app');
        app.innerHTML = '<p class="text-muted">Завантаження...</p>';
        
        API.getMedicineCategories().then(categories => {
            this.renderCategoriesList(categories, 'medicine');
        }).catch(err => {
            console.error('Error:', err);
            app.innerHTML = '<p class="text-danger">Помилка</p>';
        });
    },
    
    showProcedureCategories() {
        const app = document.getElementById('app');
        app.innerHTML = '<p class="text-muted">Завантаження...</p>';
        
        API.getProcedureCategories().then(categories => {
            this.renderCategoriesList(categories, 'procedure');
        }).catch(err => {
            console.error('Error:', err);
            app.innerHTML = '<p class="text-danger">Помилка</p>';
        });
    },
    
    renderCategoriesList(categories, type) {
        const app = document.getElementById('app');
        const typeLabel = {
            'work': 'Категорії робіт',
            'material': 'Категорії матеріалів',
            'medicine': 'Категорії ліків',
            'procedure': 'Категорії процедур'
        }[type] || type;
        
        let html = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3>${typeLabel}</h3>
                <button class="btn btn-secondary btn-sm" onclick="app.renderDictionaries()">← Назад до довідників</button>
            </div>
            <table class="table table-striped">
                <thead><tr><th>Назва</th></tr></thead>
                <tbody>
        `;
        
        categories.forEach(c => {
            html += `<tr><td>${c.name}</td></tr>`;
        });
        
        html += '</tbody></table>';
        app.innerHTML = html;
    },
    
    showCategoryForm(type) {
        // Placeholder
        console.log('Show form for', type);
    }
};

console.log('DictionariesModule завантажений');
