from sanic import Blueprint, Request
from sanic_ext import openapi
from sanic.response import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Account, Payment
from app.auth import verify_password, get_password_hash
from app.jwt_utils import create_access_token, decode_token
from app.schemas import (
    UserCreate, UserUpdate, UserResponse, AccountResponse, 
    PaymentResponse, LoginRequest, TokenResponse
)
from datetime import datetime

user_bp = Blueprint('user')

async def get_current_user(request: Request):
    db = request.ctx.db
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
        user_type = payload.get('type')
        if user_type != 'user' or user_id is None:
            return None
        result = await db.execute(select(User).where(User.id == int(user_id)))
        return result.scalar_one_or_none()
    except:
        return None

@user_bp.route('/api/user/register', methods=['POST'])
@openapi.schema('User', 'Register')
async def register(request: Request):
    db = request.ctx.db
    data = request.json
    user_create = UserCreate(**data)
    
    result = await db.execute(select(User).where(User.email == user_create.email))
    if result.scalar_one_or_none():
        return json({'error': 'Email already registered'}, status=400)
    
    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    account = Account(user_id=user.id, balance=0)
    db.add(account)
    await db.commit()
    
    return json({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name
    }, status=201)

@user_bp.route('/api/user/login', methods=['POST'])
@openapi.schema('User', 'Login')
async def login(request: Request):
    db = request.ctx.db
    data = request.json
    login_request = LoginRequest(**data)
    
    result = await db.execute(select(User).where(User.email == login_request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_request.password, user.hashed_password):
        return json({'error': 'Invalid credentials'}, status=401)
    
    token = create_access_token({'sub': str(user.id), 'type': 'user'})
    
    return json({
        'access_token': token,
        'token_type': 'bearer'
    })

@user_bp.route('/api/user/me', methods=['GET'])
@openapi.schema('User', 'Get Profile')
async def get_me(request: Request):
    user = await get_current_user(request)
    if not user:
        return json({'error': 'Not authenticated'}, status=401)
    
    return json({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name
    })

@user_bp.route('/api/user/accounts', methods=['GET'])
@openapi.schema('User', 'Get Accounts')
async def get_accounts(request: Request):
    db = request.ctx.db
    user = await get_current_user(request)
    if not user:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(select(Account).where(Account.user_id == user.id))
    accounts = result.scalars().all()
    
    return json([
        {
            'id': acc.id,
            'user_id': acc.user_id,
            'balance': float(acc.balance)
        }
        for acc in accounts
    ])

@user_bp.route('/api/user/payments', methods=['GET'])
@openapi.schema('User', 'Get Payments')
async def get_payments(request: Request):
    db = request.ctx.db
    user = await get_current_user(request)
    if not user:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(
        select(Payment).where(Payment.user_id == user.id).order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    
    return json([
        {
            'id': p.id,
            'transaction_id': p.transaction_id,
            'account_id': p.account_id,
            'user_id': p.user_id,
            'amount': float(p.amount),
            'created_at': p.created_at.isoformat()
        }
        for p in payments
    ])