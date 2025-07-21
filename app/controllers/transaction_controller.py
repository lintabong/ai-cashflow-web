from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.cashflow import Cashflow
from app.models.wallet import Wallet
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/')
@login_required
def get_transactions():
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    flow_type = request.args.get('flow_type')
    wallet_id = request.args.get('wallet_id')
    
    # Build query
    query = Cashflow.query.filter_by(userId=current_user.id, isActive=True)
    
    # Apply filters
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Cashflow.transactionDate >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Add 1 day to include the end date
            end_date = end_date + timedelta(days=1)
            query = query.filter(Cashflow.transactionDate < end_date)
        except ValueError:
            pass
    
    if category:
        try:
            category_id = int(category)
            query = query.filter(Cashflow.categoryId == category_id)
        except ValueError:
            pass
    
    if flow_type and flow_type in ['income', 'expense', 'transfer']:
        query = query.filter(Cashflow.flowType == flow_type)
    
    if wallet_id:
        query = query.filter(Cashflow.walletId == wallet_id)
    
    transactions = query.order_by(Cashflow.transactionDate.desc()).all()
    
    # Get user wallets for filter dropdown
    wallets = Wallet.query.filter_by(userId=current_user.id, isActive=True).all()
    
    return render_template('transactions.html', transactions=transactions, wallets=wallets)

@transaction_bp.route('/api')
@login_required
def get_transactions_api():
    # Similar filtering logic as above
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    flow_type = request.args.get('flow_type')
    wallet_id = request.args.get('wallet_id')
    
    query = Cashflow.query.filter_by(userId=current_user.id, isActive=True)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Cashflow.transactionDate >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
            query = query.filter(Cashflow.transactionDate < end_date)
        except ValueError:
            pass
    
    if category:
        try:
            category_id = int(category)
            query = query.filter(Cashflow.categoryId == category_id)
        except ValueError:
            pass
    
    if flow_type and flow_type in ['income', 'expense', 'transfer']:
        query = query.filter(Cashflow.flowType == flow_type)
    
    if wallet_id:
        query = query.filter(Cashflow.walletId == wallet_id)
    
    transactions = query.order_by(Cashflow.transactionDate.desc()).all()
    
    transaction_data = []
    for transaction in transactions:
        transaction_data.append({
            'id': transaction.id,
            'activityName': transaction.activityName,
            'description': transaction.description,
            'transactionDate': transaction.transactionDate.isoformat(),
            'flowType': transaction.flowType,
            'total': float(transaction.total),
            'categoryId': transaction.categoryId,
            'walletId': transaction.walletId,
            'wallet_name': transaction.wallet.name
        })
    
    return jsonify(transaction_data)