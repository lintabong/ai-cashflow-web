from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.wallet import Wallet

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/')
@login_required
def get_wallets():
    wallets = Wallet.query.filter_by(userId=current_user.id, isActive=True).all()
    return render_template('wallets.html', wallets=wallets)

@wallet_bp.route('/api')
@login_required
def get_wallets_api():
    wallets = Wallet.query.filter_by(userId=current_user.id, isActive=True).all()
    wallet_data = []
    for wallet in wallets:
        wallet_data.append({
            'id': wallet.id,
            'name': wallet.name,
            'description': wallet.description,
            'balance': float(wallet.balance),
            'createdAt': wallet.createdAt.isoformat()
        })
    return jsonify(wallet_data)