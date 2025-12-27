"""add_customers_table

Revision ID: 368b63fcfacf
Revises: 0b33d5224e29
Create Date: 2025-12-23 13:33:52.512323+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '368b63fcfacf'
down_revision: Union[str, None] = '0b33d5224e29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建客户表
    op.create_table(
        'erp_customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(30), nullable=False, comment='客户编码'),
        sa.Column('customer_name', sa.String(100), nullable=False, comment='客户名称'),
        sa.Column('short_name', sa.String(50), nullable=True, comment='简称'),
        sa.Column('contact_person', sa.String(50), nullable=True, comment='联系人'),
        sa.Column('contact_phone', sa.String(20), nullable=True, comment='联系电话'),
        sa.Column('contact_email', sa.String(100), nullable=True, comment='邮箱'),
        sa.Column('address', sa.Text(), nullable=True, comment='地址'),
        sa.Column('customer_level', sa.Enum('A', 'B', 'C', 'D', name='customer_level_enum'),
                  nullable=False, server_default='C', comment='客户等级'),
        sa.Column('credit_limit', sa.DECIMAL(12, 2), nullable=False, server_default='0.00', comment='信用额度'),
        sa.Column('balance', sa.DECIMAL(12, 2), nullable=False, server_default='0.00', comment='账户余额'),
        sa.Column('tax_number', sa.String(50), nullable=True, comment='税号'),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='customer_status_enum'),
                  nullable=False, server_default='ACTIVE', comment='状态'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_code'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # 创建索引
    op.create_index('idx_customer_name', 'erp_customers', ['customer_name'])
    op.create_index('idx_contact_phone', 'erp_customers', ['contact_phone'])
    op.create_index('idx_status', 'erp_customers', ['status'])

    # 为订单表添加customer_id字段（向后兼容，保留customer_name）
    op.add_column('erp_orders', sa.Column('customer_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_orders_customer', 'erp_orders', 'erp_customers', ['customer_id'], ['id'])
    op.create_index('idx_customer_id', 'erp_orders', ['customer_id'])


def downgrade() -> None:
    # 删除订单表的customer_id字段
    op.drop_constraint('fk_orders_customer', 'erp_orders', type_='foreignkey')
    op.drop_index('idx_customer_id', 'erp_orders')
    op.drop_column('erp_orders', 'customer_id')

    # 删除客户表索引
    op.drop_index('idx_status', 'erp_customers')
    op.drop_index('idx_contact_phone', 'erp_customers')
    op.drop_index('idx_customer_name', 'erp_customers')

    # 删除客户表
    op.drop_table('erp_customers')

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS customer_level_enum')
    op.execute('DROP TYPE IF EXISTS customer_status_enum')
