from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash # Tambahkan import ini
import uuid
import datetime 

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_anda_yang_sangat_aman'# Ganti dengan kunci rahasia yang kuat

# ============== DATA DALAM MEMORI (Contoh) ==============

# Data Stok Material untuk Gudang

role_credentials = {
    "Production": {
        "password_hash": generate_password_hash("produksi456")
    },
    "Warehouse": {
        "password_hash": generate_password_hash("gudang789")
    },
    "Procurement": { 
        "password_hash": generate_password_hash("procurement123")
    },
    "Finance": { # BARU
        "password_hash": generate_password_hash("finance456")
    }
}

# ==== data warehouse
# --- Warehouse Inventory (menggantikan Material Stock) ---
warehouse_inventory_data = [
    {"id": 1, "material_id": "A01", "material_name": "Holder", "quantity": 5, "unit": "pcs", "notes": "-"},
    {"id": 2, "material_id": "B01", "material_name": "Main Machine", "quantity": 4, "unit": "pcs", "notes": "-"},
    {"id": 3, "material_id": "C01", "material_name": "Lower Arm", "quantity": 0, "unit": "pcs", "notes": "-"},
]
next_warehouse_inventory_id = 4

# --- Warehouse Procurement Data (sudah ada) ---
warehouse_procurement_data = [
    {"id": 1, "material_id": "A01", "material_name": "Holder", "quantity": 5, "unit": "pcs", "status": "Not Arrived"},
    {"id": 2, "material_id": "B01", "material_name": "Main Machine", "quantity": 4, "unit": "pcs", "status": "Arrived"},
]
next_warehouse_procurement_id = 3

# --- Warehouse Request Material Data (BARU) ---
warehouse_request_material_data = [
    {"id": 1, "material_id": "A01", "material_name": "Holder", "quantity": 1, "unit": "package", "status": "Requested"},
    {"id": 2, "material_id": "B01", "material_name": "Main Machine", "quantity": 1, "unit": "package", "status": "Requested"},
    {"id": 3, "material_id": "C01", "material_name": "Lower Arm", "quantity": 1, "unit": "package", "status": "Requested"},
    {"id": 4, "material_id": "D01", "material_name": "Portafilter", "quantity": 1, "unit": "package", "status": "Approved"},
]
next_warehouse_request_material_id = 5



# ==========================================================
#         DATA DALAM MEMORI (BAGIAN PRODUKSI DIPERBARUI)
# ==========================================================

# --- Production MPS (Master Production Schedule) Data ---
production_mps_data = [
    {"id": 1, "year": 2025, "month": "Jan", "beginning_inventory": 0, "product_type": "Green", "total_demand": 0, "balance": 0, "required_production": 0, "ending_inventory": 0},
    {"id": 2, "year": 2025, "month": "Jan", "beginning_inventory": 1, "product_type": "Black", "total_demand": 1, "balance": 1, "required_production": 1, "ending_inventory": 1},
    {"id": 3, "year": 2025, "month": "Feb", "beginning_inventory": 2, "product_type": "Green", "total_demand": 2, "balance": 2, "required_production": 2, "ending_inventory": 2},
]
next_production_mps_id = 4

# --- Production Request Material Data ---
production_request_material_data = [
    {"id": 1, "material_id": "B01", "material_name": "Main Machine", "quantity": 1, "unit": "package", "status": "Requested"},
    {"id": 2, "material_id": "A01", "material_name": "Holder", "quantity": 1, "unit": "package", "status": "Requested"},
    {"id": 3, "material_id": "D01", "material_name": "Portafilter", "quantity": 1, "unit": "package", "status": "Approved"},
]
next_production_request_material_id = 4

# --- Production WIP (Work in Progress) Detail Data ---
production_wip_detail_data = [
    {"id": 1, "wip_id": "GE1", "product_name": "Green Espresso Machine", "quantity": 1, "process": "paint", "status": "on progress", "estimated_time": "30'"},
    {"id": 2, "wip_id": "BE2", "product_name": "Black Espresso Machine", "quantity": 1, "process": "assembly", "status": "on hold", "estimated_time": "15'"},
]
next_production_wip_detail_id = 3

# --- Production Product Data ---
production_product_data = [
    {"id": 1, "product_id": "GE1", "product_name": "Green Espresso Machine", "quantity": 1, "inspection": "Accept", "notes": "-"},
    {"id": 2, "product_id": "BE2", "product_name": "Black Espresso Machine", "quantity": 1, "inspection": "Rejected", "notes": "There is defect on the lower arm"},
]
next_production_product_id = 3

# --- Production Daily Report Data ---
production_report_data = [
    {"id": 1, "time": "07.00-09.00", "target_qty": 100, "target_total": 100, "holder_qty": 12, "holder_total": 12, "main_machine_qty": 12, "main_machine_total": 12, "lower_arm_qty": 12, "lower_arm_total": 12, "portafilter_qty": 12, "portafilter_total": 12, "reject": 1, "output_qty": 12, "output_total": 12, "notes": "-"},
    {"id": 2, "time": "09.30-12.00", "target_qty": 125, "target_total": 225, "holder_qty": 15, "holder_total": 27, "main_machine_qty": 15, "main_machine_total": 27, "lower_arm_qty": 15, "lower_arm_total": 27, "portafilter_qty": 15, "portafilter_total": 27, "reject": 2, "output_qty": 15, "output_total": 27, "notes": "Assembly problem"},
]
next_production_report_id = 3


# =====data Finance ====
finance_history_data = [
    {"id": 1, "date": "2025-07-06", "material_name": "Chain and Link", "vendor": "Raka", "quantity": 5, "price": 123456, "total": 617280},
    {"id": 2, "date": "2025-07-06", "material_name": "Sprocket", "vendor": "PT Antam", "quantity": 4, "price": 123456, "total": 493824},
    {"id": 3, "date": "2025-07-06", "material_name": "Top Cover", "vendor": "PT A", "quantity": 0, "price": 123456, "total": 0},
]

# --- Finance Financial Report Data (CRUD) ---
finance_financial_report_data = [
    {"id": 1, "date": "2025-07-08", "category": "Income", "items": "sales", "amount": 456789, "balance": 456789},
    {"id": 2, "date": "2025-07-09", "category": "Expense", "items": "procurement", "amount": 456789, "balance": 456789},
    {"id": 3, "date": "2025-07-10", "category": "Expense", "items": "procurement", "amount": 456789, "balance": 456789},
]
next_finance_report_id = 4


# ====== DATA PROCUREMENT ====
procurement_request_warehouse_data = [
    {"id": 1, "material_id": "A01", "material_name": "Holder", "quantity": 5, "unit": "pcs", "status": "Not Arrived"},
    {"id": 2, "material_id": "B01", "material_name": "Main Machine", "quantity": 4, "unit": "pcs", "status": "Arrived"},
    {"id": 3, "material_id": "C01", "material_name": "Lower Arm", "quantity": 0, "unit": "pcs", "status": "Not Arrived"},
]

# --- Procurement Purchase Order Data (CRUD) ---
procurement_po_data = [
    {"id": 1, "date": "2025-07-06", "material_name": "Holder", "vendor": "Mecha Nova", "quantity": 5, "price": 123456, "total": 617280},
    {"id": 2, "date": "2025-07-06", "material_name": "Main Machine", "vendor": "Gear Fusion", "quantity": 4, "price": 123456, "total": 493824},
]
next_procurement_po_id = 3

# --- Procurement History Data (CRUD) ---
procurement_history_data = [
    {"id": 1, "no": 1, "date": "2025-07-08", "vendor": "Mecha Nova", "material_name": "Holder", "quantity": 5, "status": "on shipping"},
    {"id": 2, "no": 2, "date": "2025-07-10", "vendor": "Gear Fusion", "material_name": "Main Machine", "quantity": 4, "status": "arrived"},
]
next_procurement_history_id = 3


# ============== FUNGSI BANTU ==============
def get_warehouse_inventory_by_id(item_id):
    return next((item for item in warehouse_inventory_data if item["id"] == item_id), None)

def get_warehouse_procurement_by_id(item_id):
    return next((item for item in warehouse_procurement_data if item["id"] == item_id), None)

def get_warehouse_request_material_by_id(item_id):
    return next((item for item in warehouse_request_material_data if item["id"] == item_id), None)


# ========= Production ==========
def get_production_mps_by_id(item_id):
    return next((item for item in production_mps_data if item["id"] == item_id), None)

def get_production_request_material_by_id(item_id):
    return next((item for item in production_request_material_data if item["id"] == item_id), None)

def get_production_wip_detail_by_id(item_id):
    return next((item for item in production_wip_detail_data if item["id"] == item_id), None)

def get_production_product_by_id(item_id):
    return next((item for item in production_product_data if item["id"] == item_id), None)

def get_production_report_by_id(item_id):
    return next((item for item in production_report_data if item["id"] == item_id), None)

#========= FINANCE =====
def get_financial_report_by_id(item_id):
    return next((item for item in finance_financial_report_data if item["id"] == item_id), None)


# ===== PROCUREMENT ====
def get_procurement_request_warehouse_by_id(item_id):
    return next((item for item in procurement_request_warehouse_data if item["id"] == item_id), None)

def get_procurement_po_by_id(item_id):
    return next((item for item in procurement_po_data if item["id"] == item_id), None)

def get_procurement_history_by_id(item_id):
    return next((item for item in procurement_history_data if item["id"] == item_id), None)
    
# ==========================================================
#                           ROUTES
# ==========================================================

@app.route('/', methods=['GET', 'POST'])
def login():
    """Menampilkan halaman login dan memproses login."""
    if 'role' in session:
        # Logika redirect jika sudah login
        if session['role'] == 'Procurement':
            return redirect(url_for('dashboard_procurement'))
        elif session['role'] == 'Production':
            return redirect(url_for('dashboard_production'))
        elif session['role'] == 'Warehouse':
            return redirect(url_for('dashboard_warehouse'))
        elif session['role'] == 'Finance':
            return redirect(url_for('dashboard_finance'))

    if request.method == 'POST':
        role = request.form.get('role')
        password_candidate = request.form.get('password')

        if not role or not password_candidate:
            flash('Peran dan Password harus diisi.', 'danger')
            return redirect(url_for('login'))

        if role in role_credentials:
            user_creds = role_credentials[role]
            # Cek password
            if check_password_hash(user_creds["password_hash"], password_candidate):
                session['role'] = role
                session['username'] = role 
                flash(f'Login sebagai {role} berhasil!', 'success')
                
                # Redirect ke dashboard yang sesuai SETELAH login berhasil
                if role == 'Procurement':
                    return redirect(url_for('dashboard_procurement'))
                elif role == 'Production':
                    return redirect(url_for('dashboard_production'))
                elif role == 'Warehouse':
                    return redirect(url_for('dashboard_warehouse'))
                elif role == 'Finance':
                    return redirect(url_for('dashboard_finance'))
            else:
                flash('Password salah.', 'danger')
        else:
            flash('Peran tidak valid atau tidak ditemukan.', 'danger')
        
        return redirect(url_for('login'))

    return render_template('login.html', title="Login")

@app.route('/logout')
def logout():
    """Memproses logout."""
    session.pop('role', None)
    session.pop('username', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD UTAMA ---
@app.route('/dashboard/production')
def dashboard_production():
    if 'role' not in session or session['role'] != 'Production':
        flash('Akses ditolak. Silakan login sebagai Production.', 'warning')
        return redirect(url_for('login'))

    # Data untuk KPI cards
    active_mps_count = len(production_mps_data)
    total_products_count = len(production_product_data)
    material_requests_count = len(production_request_material_data)
    reports_count = len(production_report_data)

    return render_template('dashboard_production.html', 
                           title="Dashboard Produksi", 
                           active_page="home",
                           active_mps_count=active_mps_count,
                           total_products_count=total_products_count,
                           material_requests_count=material_requests_count,
                           reports_count=reports_count)

@app.route('/dashboard/warehouse')
def dashboard_warehouse():
    """Menampilkan dashboard untuk Warehouse."""
    if 'role' not in session or session['role'] != 'Warehouse':
        flash('Akses ditolak. Silakan login sebagai Warehouse.', 'warning')
        return redirect(url_for('login'))

    # Data untuk KPI cards
    inventory_count = len(warehouse_inventory_data)
    procurement_count = len(warehouse_procurement_data)
    request_material_count = len(warehouse_request_material_data)

    return render_template('dashboard_warehouse.html',
                           title="Dashboard Warehouse", 
                           active_page="home",
                           inventory_count=inventory_count,
                           procurement_count=procurement_count,
                           request_material_count=request_material_count)

# --- WAREHOUSE ROUTE ---
@app.route('/warehouse/inventory')
def view_warehouse_inventory():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    return render_template('warehouse/inventory/inventory_warehouse.html', title="Inventory", items=warehouse_inventory_data, active_page="inventory_warehouse")

@app.route('/warehouse/inventory/add', methods=['GET', 'POST'])
def add_warehouse_inventory():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_warehouse_inventory_id
        try:
            new_item = { "id": next_warehouse_inventory_id, "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "notes": request.form.get('notes') }
            warehouse_inventory_data.append(new_item)
            next_warehouse_inventory_id += 1
            flash('Stok berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_warehouse_inventory'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/inventory/add_inventory_warehouse.html', title="Add Stock", active_page="inventory_warehouse", item=request.form)
    return render_template('warehouse/inventory/add_inventory_warehouse.html', title="Add Stock", active_page="inventory_warehouse")

@app.route('/warehouse/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_warehouse_inventory(item_id):
    item = get_warehouse_inventory_by_id(item_id)
    if not item: return redirect(url_for('view_warehouse_inventory'))
    if request.method == 'POST':
        try:
            item.update({ "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "notes": request.form.get('notes') })
            flash('Stok berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_warehouse_inventory'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/inventory/edit_inventory_warehouse.html', title="Edit Stock", active_page="inventory_warehouse", item=item)
    return render_template('warehouse/inventory/edit_inventory_warehouse.html', title="Edit Stock", active_page="inventory_warehouse", item=item)

@app.route('/warehouse/inventory/delete/<int:item_id>', methods=['POST'])
def delete_warehouse_inventory(item_id):
    global warehouse_inventory_data
    warehouse_inventory_data = [i for i in warehouse_inventory_data if i['id'] != item_id]
    flash('Stok telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_warehouse_inventory'))


@app.route('/warehouse/procurement')
def view_warehouse_procurement():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    return render_template('warehouse/procurement/procurement_warehouse.html', title="Procurement", items=warehouse_procurement_data, active_page="procurement_warehouse")

@app.route('/warehouse/procurement/add', methods=['GET', 'POST'])
def add_warehouse_procurement():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_warehouse_procurement_id
        try:
            new_item = {
                "id": next_warehouse_procurement_id,
                "material_id": request.form.get('material_id'),
                "material_name": request.form.get('material_name'),
                "quantity": int(request.form.get('quantity')),
                "unit": request.form.get('unit'),
                "status": request.form.get('status')
            }
            warehouse_procurement_data.append(new_item)
            next_warehouse_procurement_id += 1
            flash('Request berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_warehouse_procurement'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/procurement/add_procurement_warehouse.html', title="Add Request", active_page="procurement_warehouse", item=request.form)
    return render_template('warehouse/procurement/add_procurement_warehouse.html', title="Add Request", active_page="procurement_warehouse")

@app.route('/warehouse/procurement/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_warehouse_procurement(item_id):
    item = get_warehouse_procurement_by_id(item_id)
    if not item: return redirect(url_for('view_warehouse_procurement'))
    if request.method == 'POST':
        try:
            item.update({
                "material_id": request.form.get('material_id'),
                "material_name": request.form.get('material_name'),
                "quantity": int(request.form.get('quantity')),
                "unit": request.form.get('unit'),
                "status": request.form.get('status')
            })
            flash('Request berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_warehouse_procurement'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/procurement/edit_procurement_warehouse.html', title="Edit Request", active_page="procurement_warehouse", item=item)
    return render_template('warehouse/procurement/edit_procurement_warehouse.html', title="Edit Request", active_page="procurement_warehouse", item=item)


@app.route('/warehouse/procurement/delete/<int:item_id>', methods=['POST'])
def delete_warehouse_procurement(item_id):
    global warehouse_procurement_data
    warehouse_procurement_data = [i for i in warehouse_procurement_data if i['id'] != item_id]
    flash('Request telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_warehouse_procurement'))

@app.route('/warehouse/request_material')
def view_warehouse_request_material():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    return render_template('warehouse/reqmaterial/request_material_warehouse.html', title="Request Material", items=warehouse_request_material_data, active_page="request_material_warehouse")

@app.route('/warehouse/request_material/add', methods=['GET', 'POST'])
def add_warehouse_request_material():
    if 'role' not in session or session['role'] != 'Warehouse': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_warehouse_request_material_id
        try:
            new_item = { "id": next_warehouse_request_material_id, "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "status": request.form.get('status') }
            warehouse_request_material_data.append(new_item)
            next_warehouse_request_material_id += 1
            flash('Request berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_warehouse_request_material'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/reqmaterial/add_request_material_warehouse.html', title="Add Request", active_page="request_material_warehouse", item=request.form)
    return render_template('warehouse/reqmaterial/add_request_material_warehouse.html', title="Add Request", active_page="request_material_warehouse")

@app.route('/warehouse/request_material/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_warehouse_request_material(item_id):
    item = get_warehouse_request_material_by_id(item_id)
    if not item: return redirect(url_for('view_warehouse_request_material'))
    if request.method == 'POST':
        try:
            item.update({ "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "status": request.form.get('status') })
            flash('Request berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_warehouse_request_material'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('warehouse/reqmaterial/edit_request_material_warehouse.html', title="Edit Request", active_page="request_material_warehouse", item=item)
    return render_template('warehouse/reqmaterial/edit_request_material_warehouse.html', title="Edit Request", active_page="request_material_warehouse", item=item)

@app.route('/warehouse/request_material/delete/<int:item_id>', methods=['POST'])
def delete_warehouse_request_material(item_id):
    global warehouse_request_material_data
    warehouse_request_material_data = [i for i in warehouse_request_material_data if i['id'] != item_id]
    flash('Request telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_warehouse_request_material'))

# ======= FINANCE ROUTE ======
@app.route('/dashboard/finance')
def dashboard_finance():
    if 'role' not in session or session['role'] != 'Finance': return redirect(url_for('login'))
    
    # Data untuk KPI cards
    total_income = sum(item['amount'] for item in finance_financial_report_data if item['category'] == 'Income')
    total_expense = sum(item['amount'] for item in finance_financial_report_data if item['category'] == 'Expense')
    
    return render_template('dashboard_finance.html', 
                           title="Dashboard Finance", 
                           active_page="home",
                           total_income=total_income,
                           total_expense=total_expense,
                           history_count=len(finance_history_data))

@app.route('/finance/history')
def view_finance_history():
    if 'role' not in session or session['role'] != 'Finance': return redirect(url_for('login'))
    return render_template('finance/history_finance.html', title="History", items=finance_history_data, active_page="history_finance")

@app.route('/finance/production_report')
def view_finance_production_report():
    if 'role' not in session or session['role'] != 'Finance': return redirect(url_for('login'))
    # Menampilkan data WIP dari modul produksi
    return render_template('finance/production_report_finance.html', title="Production Report", items=production_wip_detail_data, active_page="production_report_finance")

# --- Financial Report CRUD ---
@app.route('/finance/financial_report')
def view_financial_report():
    if 'role' not in session or session['role'] != 'Finance': return redirect(url_for('login'))
    return render_template('finance/report/financial_report_finance.html', title="Financial Report", items=finance_financial_report_data, active_page="financial_report_finance")

@app.route('/finance/financial_report/add', methods=['GET', 'POST'])
def add_financial_report():
    if 'role' not in session or session['role'] != 'Finance': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_finance_report_id
        try:
            new_item = {
                "id": next_finance_report_id,
                "date": request.form.get('date'),
                "category": request.form.get('category'),
                "items": request.form.get('items'),
                "amount": int(request.form.get('amount')),
                "balance": int(request.form.get('balance'))
            }
            finance_financial_report_data.append(new_item)
            next_finance_report_id += 1
            flash('Item laporan keuangan berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_financial_report'))
        except (ValueError, TypeError):
            flash('Pastikan Amount dan Balance diisi dengan angka.', 'danger')
            return render_template('finance/report/add_financial_report.html', title="Add Item", active_page="financial_report_finance", item=request.form)
    return render_template('finance/report/add_financial_report.html', title="Add Item", active_page="financial_report_finance")

@app.route('/finance/financial_report/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_financial_report(item_id):
    item = get_financial_report_by_id(item_id)
    if not item: return redirect(url_for('view_financial_report'))
    if request.method == 'POST':
        try:
            item.update({
                "date": request.form.get('date'),
                "category": request.form.get('category'),
                "items": request.form.get('items'),
                "amount": int(request.form.get('amount')),
                "balance": int(request.form.get('balance'))
            })
            flash('Item laporan keuangan berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_financial_report'))
        except (ValueError, TypeError):
            flash('Pastikan Amount dan Balance diisi dengan angka.', 'danger')
            return render_template('finance/report/edit_financial_report.html', title="Edit Item", active_page="financial_report_finance", item=item)
    return render_template('finance/report/edit_financial_report.html', title="Edit Item", active_page="financial_report_finance", item=item)

@app.route('/finance/financial_report/delete/<int:item_id>', methods=['POST'])
def delete_financial_report(item_id):
    global finance_financial_report_data
    finance_financial_report_data = [i for i in finance_financial_report_data if i['id'] != item_id]
    flash('Item laporan keuangan telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_financial_report'))


# ======== Production Routes =========
# --- MPS (Master Production Schedule) CRUD ---
@app.route('/production/mps')
def view_production_mps():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    return render_template('production/mps/mps_production.html', title="Master Production Schedule", items=production_mps_data, active_page="mps_production")

@app.route('/production/mps/add', methods=['GET', 'POST'])
def add_production_mps():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_production_mps_id
        try:
            new_item = { "id": next_production_mps_id, "year": int(request.form.get('year')), "month": request.form.get('month'), "beginning_inventory": int(request.form.get('beginning_inventory')), "product_type": request.form.get('product_type'), "total_demand": int(request.form.get('total_demand')), "balance": int(request.form.get('balance')), "required_production": int(request.form.get('required_production')), "ending_inventory": int(request.form.get('ending_inventory')) }
            production_mps_data.append(new_item)
            next_production_mps_id += 1
            flash('Data MPS berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_production_mps'))
        except (ValueError, TypeError):
            flash('Pastikan semua field angka diisi dengan benar.', 'danger')
            return render_template('production/mps/add_mps_production.html', title="Add MPS", active_page="mps_production", item=request.form)
    return render_template('production/mps/add_mps_production.html', title="Add MPS", active_page="mps_production")

@app.route('/production/mps/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_production_mps(item_id):
    item = get_production_mps_by_id(item_id)
    if not item: return redirect(url_for('view_production_mps'))
    if request.method == 'POST':
        try:
            item.update({ "year": int(request.form.get('year')), "month": request.form.get('month'), "beginning_inventory": int(request.form.get('beginning_inventory')), "product_type": request.form.get('product_type'), "total_demand": int(request.form.get('total_demand')), "balance": int(request.form.get('balance')), "required_production": int(request.form.get('required_production')), "ending_inventory": int(request.form.get('ending_inventory')) })
            flash('Data MPS berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_production_mps'))
        except (ValueError, TypeError):
            flash('Pastikan semua field angka diisi dengan benar.', 'danger')
            return render_template('production/mps/edit_mps_production.html', title="Edit MPS", active_page="mps_production", item=item)
    return render_template('production/mps/edit_mps_production.html', title="Edit MPS", active_page="mps_production", item=item)

@app.route('/production/mps/delete/<int:item_id>', methods=['POST'])
def delete_production_mps(item_id):
    global production_mps_data
    production_mps_data = [i for i in production_mps_data if i['id'] != item_id]
    flash('Data MPS berhasil dihapus!', 'modal_success_delete')
    return redirect(url_for('view_production_mps'))

# --- Request Material CRUD ---
@app.route('/production/request_material')
def view_request_material():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    return render_template('production/reqmaterial/request_material_production.html', title="Request Material", items=production_request_material_data, active_page="request_material_production")

@app.route('/production/request_material/add', methods=['GET', 'POST'])
def add_request_material():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_production_request_material_id
        try:
            new_item = { "id": next_production_request_material_id, "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "status": request.form.get('status') }
            production_request_material_data.append(new_item)
            next_production_request_material_id += 1
            flash('Request material berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_request_material'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/add_request_material_production.html', title="Add Request", active_page="request_material_production", item=request.form)
    return render_template('production/reqmaterial/add_request_material_production.html', title="Add Request", active_page="request_material_production")

@app.route('/production/request_material/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_request_material(item_id):
    item = get_production_request_material_by_id(item_id)
    if not item: return redirect(url_for('view_request_material'))
    if request.method == 'POST':
        try:
            item.update({ "material_id": request.form.get('material_id'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "unit": request.form.get('unit'), "status": request.form.get('status') })
            flash('Request material berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_request_material'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/edit_request_material_production.html', title="Edit Request", active_page="request_material_production", item=item)
    return render_template('production/reqmaterial/edit_request_material_production.html', title="Edit Request", active_page="request_material_production", item=item)

@app.route('/production/request_material/delete/<int:item_id>', methods=['POST'])
def delete_request_material(item_id):
    global production_request_material_data
    production_request_material_data = [i for i in production_request_material_data if i['id'] != item_id]
    flash('Request material berhasil dihapus!', 'modal_success_delete')
    return redirect(url_for('view_request_material'))


# --- WIP Detail CRUD ---
@app.route('/production/wip_detail')
def view_wip_detail():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    return render_template('production/wip/wip_detail_production.html', title="Work in Progress", items=production_wip_detail_data, active_page="wip_detail_production")

@app.route('/production/wip_detail/add', methods=['GET', 'POST'])
def add_wip_detail():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_production_wip_detail_id
        try:
            new_item = { "id": next_production_wip_detail_id, "wip_id": request.form.get('wip_id'), "product_name": request.form.get('product_name'), "quantity": int(request.form.get('quantity')), "process": request.form.get('process'), "status": request.form.get('status'), "estimated_time": request.form.get('estimated_time') }
            production_wip_detail_data.append(new_item)
            next_production_wip_detail_id += 1
            flash('Data WIP berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_wip_detail'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/wip/add_wip_detail_production.html', title="Add WIP", active_page="wip_detail_production", item=request.form)
    return render_template('production/wip/add_wip_detail_production.html', title="Add WIP", active_page="wip_detail_production")

@app.route('/production/wip_detail/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_wip_detail(item_id):
    item = get_production_wip_detail_by_id(item_id)
    if not item: return redirect(url_for('view_wip_detail'))
    if request.method == 'POST':
        try:
            item.update({ "wip_id": request.form.get('wip_id'), "product_name": request.form.get('product_name'), "quantity": int(request.form.get('quantity')), "process": request.form.get('process'), "status": request.form.get('status'), "estimated_time": request.form.get('estimated_time') })
            flash('Data WIP berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_wip_detail'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/wip/edit_wip_detail_production.html', title="Edit WIP", active_page="wip_detail_production", item=item)
    return render_template('production/wip/edit_wip_detail_production.html', title="Edit WIP", active_page="wip_detail_production", item=item)

@app.route('/production/wip_detail/delete/<int:item_id>', methods=['POST'])
def delete_wip_detail(item_id):
    global production_wip_detail_data
    production_wip_detail_data = [i for i in production_wip_detail_data if i['id'] != item_id]
    flash('Data WIP berhasil dihapus!', 'modal_success_delete')
    return redirect(url_for('view_wip_detail'))


# --- Product CRUD ---
@app.route('/production/product')
def view_production_product():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    return render_template('production/product/product_production.html', title="Product", items=production_product_data, active_page="product_production")

@app.route('/production/product/add', methods=['GET', 'POST'])
def add_production_product():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_production_product_id
        try:
            new_item = { "id": next_production_product_id, "product_id": request.form.get('product_id'), "product_name": request.form.get('product_name'), "quantity": int(request.form.get('quantity')), "inspection": request.form.get('inspection'), "notes": request.form.get('notes') }
            production_product_data.append(new_item)
            next_production_product_id += 1
            flash('Data produk berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_production_product'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/add_product_production.html', title="Add Product", active_page="product_production", item=request.form)
    return render_template('production/product/add_product_production.html', title="Add Product", active_page="product_production")

@app.route('/production/product/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_production_product(item_id):
    item = get_production_product_by_id(item_id)
    if not item: return redirect(url_for('view_production_product'))
    if request.method == 'POST':
        try:
            item.update({ "product_id": request.form.get('product_id'), "product_name": request.form.get('product_name'), "quantity": int(request.form.get('quantity')), "inspection": request.form.get('inspection'), "notes": request.form.get('notes') })
            flash('Data produk berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_production_product'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('production/edit_product_production.html', title="Edit Product", active_page="product_production", item=item)
    return render_template('production/product/edit_product_production.html', title="Edit Product", active_page="product_production", item=item)

@app.route('/production/product/delete/<int:item_id>', methods=['POST'])
def delete_production_product(item_id):
    global production_product_data
    production_product_data = [i for i in production_product_data if i['id'] != item_id]
    flash('Data produk berhasil dihapus!', 'modal_success_delete')
    return redirect(url_for('view_production_product'))


# --- Report CRUD ---
@app.route('/production/report')
def view_production_report():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    return render_template('production/report/report_production.html', title="Production Daily Report", items=production_report_data, active_page="report_production")

@app.route('/production/report/add', methods=['GET', 'POST'])
def add_production_report():
    if 'role' not in session or session['role'] != 'Production': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_production_report_id
        try:
            new_item = { "id": next_production_report_id, "time": request.form.get('time'), "target_qty": int(request.form.get('target_qty')), "target_total": int(request.form.get('target_total')), "holder_qty": int(request.form.get('holder_qty')), "holder_total": int(request.form.get('holder_total')), "main_machine_qty": int(request.form.get('main_machine_qty')), "main_machine_total": int(request.form.get('main_machine_total')), "lower_arm_qty": int(request.form.get('lower_arm_qty')), "lower_arm_total": int(request.form.get('lower_arm_total')), "portafilter_qty": int(request.form.get('portafilter_qty')), "portafilter_total": int(request.form.get('portafilter_total')), "reject": int(request.form.get('reject')), "output_qty": int(request.form.get('output_qty')), "output_total": int(request.form.get('output_total')), "notes": request.form.get('notes') }
            production_report_data.append(new_item)
            next_production_report_id += 1
            flash('Data laporan berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_production_report'))
        except (ValueError, TypeError):
            flash('Pastikan semua field angka diisi dengan benar.', 'danger')
            return render_template('production/add_report_production.html', title="Add Records", active_page="report_production", item=request.form)
    return render_template('production/report/add_report_production.html', title="Add Records", active_page="report_production")

@app.route('/production/report/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_production_report(item_id):
    item = get_production_report_by_id(item_id)
    if not item: return redirect(url_for('view_production_report'))
    if request.method == 'POST':
        try:
            item.update({ "time": request.form.get('time'), "target_qty": int(request.form.get('target_qty')), "target_total": int(request.form.get('target_total')), "holder_qty": int(request.form.get('holder_qty')), "holder_total": int(request.form.get('holder_total')), "main_machine_qty": int(request.form.get('main_machine_qty')), "main_machine_total": int(request.form.get('main_machine_total')), "lower_arm_qty": int(request.form.get('lower_arm_qty')), "lower_arm_total": int(request.form.get('lower_arm_total')), "portafilter_qty": int(request.form.get('portafilter_qty')), "portafilter_total": int(request.form.get('portafilter_total')), "reject": int(request.form.get('reject')), "output_qty": int(request.form.get('output_qty')), "output_total": int(request.form.get('output_total')), "notes": request.form.get('notes') })
            flash('Data laporan berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_production_report'))
        except (ValueError, TypeError):
            flash('Pastikan semua field angka diisi dengan benar.', 'danger')
            return render_template('production/edit_report_production.html', title="Edit Records", active_page="report_production", item=item)
    return render_template('production/report/edit_report_production.html', title="Edit Records", active_page="report_production", item=item)

@app.route('/production/report/delete/<int:item_id>', methods=['POST'])
def delete_production_report(item_id):
    global production_report_data
    production_report_data = [i for i in production_report_data if i['id'] != item_id]
    flash('Data laporan berhasil dihapus!', 'modal_success_delete')
    return redirect(url_for('view_production_report'))



# ====== PROCUREMENT ROUTES =====
@app.route('/dashboard/procurement')
def dashboard_procurement():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    
    # Data untuk KPI cards
    request_warehouse_count = len(procurement_request_warehouse_data)
    purchase_order_count = len(procurement_po_data)
    history_count = len(procurement_history_data)

    return render_template('dashboard_procurement.html', 
                           title="Dashboard Procurement", 
                           active_page="home",
                           request_warehouse_count=request_warehouse_count,
                           purchase_order_count=purchase_order_count,
                           history_count=history_count)


# --- Request Warehouse (View & Edit) ---
@app.route('/procurement/request_warehouse')
def view_procurement_request_warehouse():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    return render_template('procurement/request/request_warehouse_procurement.html', title="Request Warehouse", items=procurement_request_warehouse_data, active_page="request_warehouse_procurement")

@app.route('/procurement/request_warehouse/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_procurement_request_warehouse(item_id):
    item = get_procurement_request_warehouse_by_id(item_id)
    if not item: return redirect(url_for('view_procurement_request_warehouse'))
    if request.method == 'POST':
        try:
            item.update({
                "material_id": request.form.get('material_id'),
                "material_name": request.form.get('material_name'),
                "quantity": int(request.form.get('quantity')),
                "unit": request.form.get('unit'),
                "status": request.form.get('status')
            })
            flash('Request Warehouse berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_procurement_request_warehouse'))
        except (ValueError, TypeError):
            flash('Pastikan quantity diisi dengan angka.', 'danger')
            return render_template('procurement/request/edit_request_warehouse_procurement.html', title="Edit Request", active_page="request_warehouse_procurement", item=item)
    return render_template('procurement/request/edit_request_warehouse_procurement.html', title="Edit Request", active_page="request_warehouse_procurement", item=item)


# --- Purchase Order CRUD ---
@app.route('/procurement/purchase_order')
def view_procurement_po():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    return render_template('procurement/purchase/po_procurement.html', title="Purchase Order", items=procurement_po_data, active_page="po_procurement")

@app.route('/procurement/purchase_order/add', methods=['GET', 'POST'])
def add_procurement_po():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_procurement_po_id
        try:
            price = int(request.form.get('price').replace('.', ''))
            quantity = int(request.form.get('quantity'))
            new_item = { "id": next_procurement_po_id, "date": request.form.get('date'), "material_name": request.form.get('material_name'), "vendor": request.form.get('vendor'), "quantity": quantity, "price": price, "total": price * quantity }
            procurement_po_data.append(new_item)
            next_procurement_po_id += 1
            flash('Purchase Order berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_procurement_po'))
        except (ValueError, TypeError):
            flash('Pastikan Quantity dan Price diisi dengan angka.', 'danger')
            return render_template('procurement/purchase/add_po_procurement.html', title="Add PO", active_page="po_procurement", item=request.form)
    return render_template('procurement/purchase/add_po_procurement.html', title="Add PO", active_page="po_procurement")

@app.route('/procurement/purchase_order/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_procurement_po(item_id):
    item = get_procurement_po_by_id(item_id)
    if not item: return redirect(url_for('view_procurement_po'))
    if request.method == 'POST':
        try:
            price = int(request.form.get('price').replace('.', ''))
            quantity = int(request.form.get('quantity'))
            item.update({ "date": request.form.get('date'), "material_name": request.form.get('material_name'), "vendor": request.form.get('vendor'), "quantity": quantity, "price": price, "total": price * quantity })
            flash('Purchase Order berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_procurement_po'))
        except (ValueError, TypeError):
            flash('Pastikan Quantity dan Price diisi dengan angka.', 'danger')
            return render_template('procurement/purchase/edit_po_procurement.html', title="Edit PO", active_page="po_procurement", item=item)
    return render_template('procurement/purchase/edit_po_procurement.html', title="Edit PO", active_page="po_procurement", item=item)

@app.route('/procurement/purchase_order/delete/<int:item_id>', methods=['POST'])
def delete_procurement_po(item_id):
    global procurement_po_data
    procurement_po_data = [i for i in procurement_po_data if i['id'] != item_id]
    flash('Purchase Order telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_procurement_po'))

# --- History CRUD ---
@app.route('/procurement/history')
def view_procurement_history():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    return render_template('procurement/history/history_procurement.html', title="History", items=procurement_history_data, active_page="history_procurement")

@app.route('/procurement/history/add', methods=['GET', 'POST'])
def add_procurement_history():
    if 'role' not in session or session['role'] != 'Procurement': return redirect(url_for('login'))
    if request.method == 'POST':
        global next_procurement_history_id
        try:
            new_item = { "id": next_procurement_history_id, "no": next_procurement_history_id, "date": request.form.get('date'), "vendor": request.form.get('vendor'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "status": request.form.get('status') }
            procurement_history_data.append(new_item)
            next_procurement_history_id += 1
            flash('Data histori berhasil ditambahkan!', 'modal_success_add')
            return redirect(url_for('view_procurement_history'))
        except (ValueError, TypeError):
            flash('Pastikan Quantity diisi dengan angka.', 'danger')
            return render_template('procurement/history/add_history_procurement.html', title="Add History", active_page="history_procurement", item=request.form)
    return render_template('procurement/history/add_history_procurement.html', title="Add History", active_page="history_procurement")

@app.route('/procurement/history/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_procurement_history(item_id):
    item = get_procurement_history_by_id(item_id)
    if not item: return redirect(url_for('view_procurement_history'))
    if request.method == 'POST':
        try:
            item.update({ "date": request.form.get('date'), "vendor": request.form.get('vendor'), "material_name": request.form.get('material_name'), "quantity": int(request.form.get('quantity')), "status": request.form.get('status') })
            flash('Data histori berhasil diperbarui!', 'modal_success_edit')
            return redirect(url_for('view_procurement_history'))
        except (ValueError, TypeError):
            flash('Pastikan Quantity diisi dengan angka.', 'danger')
            return render_template('procurement/history/edit_history_procurement.html', title="Edit History", active_page="history_procurement", item=item)
    return render_template('procurement/history/edit_history_procurement.html', title="Edit History", active_page="history_procurement", item=item)

@app.route('/procurement/history/delete/<int:item_id>', methods=['POST'])
def delete_procurement_history(item_id):
    global procurement_history_data
    procurement_history_data = [i for i in procurement_history_data if i['id'] != item_id]
    flash('Data histori telah dihapus.', 'modal_success_delete')
    return redirect(url_for('view_procurement_history'))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

































