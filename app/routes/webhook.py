from sanic import Blueprint, Request
from sanic_ext import openapi
from sanic.response import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
import hashlib
from app.models import User, Account, Payment
from app.config import SECRET_KEY
from app.schemas_webhook import WebhookRequest, WebhookResponse

webhook_bp = Blueprint('webhook')

def compute_signature(account_id: int, amount: Decimal, transaction_id: str, user_id: int, secret_key: str) -> str:
    keys = ['account_id', 'amount', 'transaction_id', 'user_id']
    sorted_vals = [str(account_id), str(amount), transaction_id, str(user_id)]
    concatenated = ''.join(sorted_vals) + secret_key
    return hashlib.sha256(concatenated.encode()).hexdigest()

@webhook_bp.route('/api/webhook/payment', methods=['POST'])
@openapi.schema('Webhook', 'Process Payment')
async def process_payment(request: Request):
    db = request.ctx.db
    data = request.json
    
    try:
        webhook_data = WebhookRequest(**data)
    except Exception as e:
        return json({'success': False, 'message': 'Invalid request data'}, status=400)
    
    expected_signature = compute_signature(
        webhook_data.account_id,
        webhook_data.amount,
        webhook_data.transaction_id,
        webhook_data.user_id,
        SECRET_KEY
    )
    
    if webhook_data.signature != expected_signature:
        return json({'success': False, 'message': 'Invalid signature'}, status=400)
    
    result = await db.execute(select(User).where(User.id == webhook_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        return json({'success': False, 'message': 'User not found'}, status=404)
    
    result = await db.execute(select(Account).where(
        Account.id == webhook_data.account_id,
        Account.user_id == webhook_data.user_id
    ))
    account = result.scalar_one_or_none()
    
    if not account:
        account = Account(user_id=webhook_data.user_id, balance=0)
        db.add(account)
        await db.flush()
        await db.refresh(account)
    
    result = await db.execute(select(Payment).where(
        Payment.transaction_id == webhook_data.transaction_id
    ))
    existing_payment = result.scalar_one_or_none()
    
    if existing_payment:
        return json({
            'success': False,
            'message': 'Transaction already processed',
            'account_id': account.id,
            'new_balance': float(account.balance)
        })
    
    payment = Payment(
        transaction_id=webhook_data.transaction_id,
        account_id=account.id,
        user_id=webhook_data.user_id,
        amount=webhook_data.amount
    )
    db.add(payment)
    
    account.balance += webhook_data.amount
    await db.commit()
    await db.refresh(account)
    await db.refresh(payment)
    
    return json({
        'success': True,
        'message': 'Payment processed successfully',
        'account_id': account.id,
        'new_balance': float(account.balance)
    })