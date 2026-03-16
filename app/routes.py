from flask import render_template, request, redirect, url_for
from .models import db, DailyLog, FuelType, Receipt
from datetime import datetime
import json

def register_routes(app):
    
    # --- 1. HP DASHBOARD (With Payment Analytics) ---
    @app.route('/')
    def home():
        fuels = FuelType.query.all()
        logs = DailyLog.query.all()

        # Calculate Total Cash vs Digital for the Doughnut Chart
        total_cash = sum(log.cash_sales for log in logs) if logs else 0
        total_digi = sum(log.digital_sales for log in logs) if logs else 0
        
        inventory = []
        for fuel in fuels:
            # Technical Logic: Current Stock = (Sum of Receipts) - (Sum of Sales)
            total_received = sum(r.quantity_received for r in fuel.receipts) if fuel.receipts else 0
            total_sold = sum((log.closing_reading - log.opening_reading) for log in fuel.daily_logs) if fuel.daily_logs else 0
            current_stock = total_received - total_sold
            
            # Inventory Percentage (Based on 20,000L tanks)
            percent = (current_stock / 20000) * 100
            color = "bg-success" if percent > 30 else "bg-danger"
            
            inventory.append({
                "name": fuel.name,
                "stock": current_stock,
                "percent": min(max(percent, 0), 100),
                "color": color
            })

        outlet_info = {
            "name": "Yalamanchili Fuels",
            "last_updated": datetime.now().strftime("%d %b %Y %H:%M")
        }

        return render_template('index.html', 
                               info=outlet_info, 
                               prices=fuels, 
                               inventory=inventory,
                               cash_val=total_cash,
                               digi_val=total_digi)

    # --- 2. DAILY METER ENTRY ---
    @app.route('/entry', methods=['GET', 'POST'])
    def daily_entry():
        if request.method == 'POST':
            def clean_float(val):
                return float(val) if val and val.strip() != '' else 0.0
            
            opening = clean_float(request.form.get('opening'))
            closing = clean_float(request.form.get('closing'))

            if closing < opening:
                fuels = FuelType.query.all()
                return render_template('entry.html', error="Error: Closing cannot be less than Opening.", fuels=fuels)

            try:
                new_log = DailyLog(
                    fuel_id=request.form.get('fuel_id'),
                    opening_reading=opening,
                    closing_reading=closing,
                    cash_sales=clean_float(request.form.get('cash')),
                    digital_sales=clean_float(request.form.get('digital')),
                    date=datetime.strptime(request.form.get('date'), '%Y-%m-%d')
                )
                db.session.add(new_log)
                db.session.commit()
                return redirect(url_for('view_records'))
            except Exception as e:
                db.session.rollback()
                return f"Database Error: {e}", 500
        
        fuels = FuelType.query.all()
        return render_template('entry.html', fuels=fuels)

    # --- 3. SALES LEDGER ---
    @app.route('/records')
    def view_records():
        logs_query = DailyLog.query.order_by(DailyLog.date.asc()).all()
        chart_dates = [log.date.strftime('%d %b') for log in logs_query]
        chart_sales = [int(log.closing_reading - log.opening_reading) for log in logs_query]
        total_vol = sum((log.closing_reading - log.opening_reading) for log in logs_query)
        total_rev = sum((log.cash_sales + log.digital_sales) for log in logs_query)

        return render_template('records.html', 
                               logs=reversed(logs_query), 
                               dates=json.dumps(chart_dates), 
                               sales=json.dumps(chart_sales),
                               total_vol=total_vol,
                               total_rev=total_rev)

    # --- 4. TANKER RECEIPTS ---
    @app.route('/receipt', methods=['GET', 'POST'])
    def tanker_receipt():
        if request.method == 'POST':
            try:
                new_receipt = Receipt(
                    fuel_id=request.form.get('fuel_id'),
                    quantity_received=float(request.form.get('quantity')),
                    invoice_number=request.form.get('invoice'),
                    density_observed=float(request.form.get('density')),
                    date=datetime.strptime(request.form.get('date'), '%Y-%m-%d')
                )
                db.session.add(new_receipt)
                db.session.commit()
                return redirect(url_for('home'))
            except Exception as e:
                db.session.rollback()
                return f"Error logging receipt: {e}", 500
        fuels = FuelType.query.all()
        return render_template('receipt.html', fuels=fuels)

    # --- 5. PRICE CONFIGURATION ---
    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        if request.method == 'POST':
            fuel = FuelType.query.get(request.form.get('fuel_id'))
            if fuel:
                fuel.base_price = float(request.form.get('new_price'))
                db.session.commit()
                return redirect(url_for('home'))
        fuels = FuelType.query.all()
        return render_template('settings.html', fuels=fuels)
