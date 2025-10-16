"""add indexes for performance

Revision ID: 001
Revises: 
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """添加性能优化索引"""
    
    # customers表索引
    op.create_index('idx_customer_no', 'customers', ['customer_no'], unique=False)
    op.create_index('idx_customer_phone', 'customers', ['phone'], unique=False)
    op.create_index('idx_customer_id_card', 'customers', ['id_card'], unique=False)
    op.create_index('idx_customer_status', 'customers', ['status'], unique=False)
    op.create_index('idx_customer_product_id', 'customers', ['product_id'], unique=False)
    op.create_index('idx_customer_created_at', 'customers', ['created_at'], unique=False)
    
    # customer_documents表索引
    op.create_index('idx_document_customer_id', 'customer_documents', ['customer_id'], unique=False)
    op.create_index('idx_document_type_id', 'customer_documents', ['document_type_id'], unique=False)
    op.create_index('idx_document_status', 'customer_documents', ['status'], unique=False)
    op.create_index('idx_document_created_at', 'customer_documents', ['created_at'], unique=False)
    
    # customer_assignments表索引
    op.create_index('idx_assignment_customer_id', 'customer_assignments', ['customer_id'], unique=False)
    op.create_index('idx_assignment_user_id', 'customer_assignments', ['user_id'], unique=False)
    op.create_index('idx_assignment_assigned_at', 'customer_assignments', ['assigned_at'], unique=False)
    
    # users表索引
    op.create_index('idx_user_username', 'users', ['username'], unique=True)
    op.create_index('idx_user_role', 'users', ['role'], unique=False)
    
    # audit_logs表索引
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_action', 'audit_logs', ['action'], unique=False)
    op.create_index('idx_audit_created_at', 'audit_logs', ['created_at'], unique=False)
    
    # loan_products表索引
    op.create_index('idx_product_code', 'loan_products', ['code'], unique=True)
    op.create_index('idx_product_is_active', 'loan_products', ['is_active'], unique=False)
    
    # document_types表索引
    op.create_index('idx_doctype_code', 'document_types', ['code'], unique=True)
    op.create_index('idx_doctype_category', 'document_types', ['category'], unique=False)


def downgrade() -> None:
    """移除索引"""
    
    # customers表索引
    op.drop_index('idx_customer_no', table_name='customers')
    op.drop_index('idx_customer_phone', table_name='customers')
    op.drop_index('idx_customer_id_card', table_name='customers')
    op.drop_index('idx_customer_status', table_name='customers')
    op.drop_index('idx_customer_product_id', table_name='customers')
    op.drop_index('idx_customer_created_at', table_name='customers')
    
    # customer_documents表索引
    op.drop_index('idx_document_customer_id', table_name='customer_documents')
    op.drop_index('idx_document_type_id', table_name='customer_documents')
    op.drop_index('idx_document_status', table_name='customer_documents')
    op.drop_index('idx_document_created_at', table_name='customer_documents')
    
    # customer_assignments表索引
    op.drop_index('idx_assignment_customer_id', table_name='customer_assignments')
    op.drop_index('idx_assignment_user_id', table_name='customer_assignments')
    op.drop_index('idx_assignment_assigned_at', table_name='customer_assignments')
    
    # users表索引
    op.drop_index('idx_user_username', table_name='users')
    op.drop_index('idx_user_role', table_name='users')
    
    # audit_logs表索引
    op.drop_index('idx_audit_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_created_at', table_name='audit_logs')
    
    # loan_products表索引
    op.drop_index('idx_product_code', table_name='loan_products')
    op.drop_index('idx_product_is_active', table_name='loan_products')
    
    # document_types表索引
    op.drop_index('idx_doctype_code', table_name='document_types')
    op.drop_index('idx_doctype_category', table_name='document_types')

