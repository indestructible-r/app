from sanic import Blueprint, Request
from sanic_ext import openapi
from sanic.response import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Admin, Account
from app.auth import verify_password, get_password_hash
from app.jwt_utils import create_access_token, decode_token
from app.schemas import (
    UserCreate, UserUpdate, AdminCreate, AdminResponse
)
from datetime import datetime

admin_bp = Blueprint('admin')

async def get_current_admin(request: Request):
    db = request.ctx.db
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = decode_token(token)
        admin_id = payload.get('sub')
        user_type = payload.get('type')
        if user_type != 'admin' or admin_id is None:
            return None
        result = await db.execute(select(Admin).where(Admin.id == int(admin_id)))
        return result.scalar_one_or_none()
    except:
        return None

@admin_bp.route('/api/admin/register', methods=['POST'])
@openapi.schema('Admin', 'Register')
async def register(request: Request):
    db = request.ctx.db
    data = request.json
    admin_create = AdminCreate(**data)
    
    result = await db.execute(select(Admin).where(Admin.email == admin_create.email))
    if result.scalar_one_or_none():
        return json({'error': 'Email already registered'}, status=400)
    
    admin = Admin(
        email=admin_create.email,
        full_name=admin_create.full_name,
        hashed_password=get_password_hash(admin_create.password)
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    return json({
        'id': admin.id,
        'email': admin.email,
        'full_name': admin.full_name
    }, status=201)

@admin_bp.route('/api/admin/login', methods=['POST'])
@openapi.schema('Admin', 'Login')
async def login(request: Request):
    db = request.ctx.db
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    result = await db.execute(select(Admin).where(Admin.email == email))
    admin = result.scalar_one_or_none()
    
    if not admin or not verify_password(password, admin.hashed_password):
        return json({'error': 'Invalid credentials'}, status=401)
    
    token = create_access_token({'sub': str(admin.id), 'type': 'admin'})
    
    return json({
        'access_token': token,
        'token_type': 'bearer'
    })

@admin_bp.route('/api/admin/me', methods=['GET'])
@openapi.schema('Admin', 'Get Profile')
async def get_me(request: Request):
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    return json({
        'id': admin.id,
        'email': admin.email,
        'full_name': admin.full_name
    })

@admin_bp.route('/api/admin/users', methods=['GET'])
@openapi.schema('Admin', 'List Users')
async def list_users(request: Request):
    db = request.ctx.db
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return json([
        {
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name,
            'created_at': u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ])

@admin_bp.route('/api/admin/users', methods=['POST'])
@openapi.schema('Admin', 'Create User')
async def create_user(request: Request):
    db = request.ctx.db
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    data = request.json
    user_create = UserCreate(**data)
    
    result = await db.execute(select(User).where(User.email == user_create.email))
    if result.scalar_one_or_none():
        return json({'error': 'Email already exists'}, status=400)
    
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

@admin_bp.route('/api/admin/users/<user_id:int>', methods=['PUT'])
@openapi.schema('Admin', 'Update User')
async def update_user(request: Request, user_id: int):
    db = request.ctx.db
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return json({'error': 'User not found'}, status=404)
    
    data = request.json
    if 'email' in data and data['email']:
        result = await db.execute(select(User).where(User.email == data['email']))
        existing = result.scalar_one_or_none()
        if existing and existing.id != user_id:
            return json({'error': 'Email already exists'}, status=400)
        user.email = data['email']
    
    if 'full_name' in data and data['full_name']:
        user.full_name = data['full_name']
    
    if 'password' in data and data['password']:
        user.hashed_password = get_password_hash(data['password'])
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    return json({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name
    })

@admin_bp.route('/api/admin/users/<user_id:int>', methods=['DELETE'])
@openapi.schema('Admin', 'Delete User')
async def delete_user(request: Request, user_id: int):
    db = request.ctx.db
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return json({'error': 'User not found'}, status=404)
    
    await db.delete(user)
    await db.commit()
    
    return json({'message': 'User deleted'})

@admin_bp.route('/api/admin/users/<user_id:int>/accounts', methods=['GET'])
@openapi.schema('Admin', 'Get User Accounts')
async def get_user_accounts(request: Request, user_id: int):
    db = request.ctx.db
    admin = await get_current_admin(request)
    if not admin:
        return json({'error': 'Not authenticated'}, status=401)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return json({'error': 'User not found'}, status=404)
    
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    accounts = result.scalars().all()
    
    return json([
        {
            'id': acc.id,
            'user_id': acc.user_id,
            'balance': float(acc.balance),
            'created_at': acc.created_at.isoformat() if acc.created_at else None
        }
        for acc in accounts
    ])