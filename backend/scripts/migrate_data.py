"""
数据迁移工具
用于从旧系统导入历史客户数据和资料文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from app.models.document import CustomerDocument, DocumentType
from app.core.security import get_password_hash
from app.models.user import User
import pandas as pd
import shutil
from datetime import datetime


def create_admin_user(db: Session):
    """创建管理员账户"""
    print("Creating admin user...")
    
    # 检查是否已存在
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("Admin user already exists")
        return existing
    
    admin = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        full_name="系统管理员",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✅ Admin user created: username=admin, password=admin123")
    return admin


def create_sample_products(db: Session):
    """创建示例产品"""
    print("\nCreating sample products...")
    
    products_data = [
        {
            "code": "personal_loan",
            "name": "个人信用贷",
            "description": "无抵押个人信用贷款",
            "is_active": True
        },
        {
            "code": "car_loan",
            "name": "汽车贷款",
            "description": "购车分期贷款",
            "is_active": True
        },
        {
            "code": "house_loan",
            "name": "房屋贷款",
            "description": "购房按揭贷款",
            "is_active": True
        }
    ]
    
    created_products = []
    for data in products_data:
        existing = db.query(LoanProduct).filter(LoanProduct.code == data["code"]).first()
        if existing:
            print(f"Product {data['code']} already exists")
            created_products.append(existing)
            continue
        
        product = LoanProduct(**data)
        db.add(product)
        created_products.append(product)
        print(f"✅ Created product: {data['name']}")
    
    db.commit()
    return created_products


def create_document_types(db: Session):
    """创建资料类型"""
    print("\nCreating document types...")
    
    doc_types_data = [
        {"code": "id_card", "name": "身份证", "category": "identity", "description": "身份证正反面"},
        {"code": "income_proof", "name": "收入证明", "category": "financial", "description": "工资流水或收入证明"},
        {"code": "bank_statement", "name": "银行流水", "category": "financial", "description": "近6个月银行流水"},
        {"code": "work_proof", "name": "工作证明", "category": "employment", "description": "在职证明或劳动合同"},
        {"code": "house_proof", "name": "房产证明", "category": "asset", "description": "房产证或购房合同"},
        {"code": "car_proof", "name": "车辆证明", "category": "asset", "description": "行驶证或购车发票"},
    ]
    
    created_types = []
    for data in doc_types_data:
        existing = db.query(DocumentType).filter(DocumentType.code == data["code"]).first()
        if existing:
            print(f"Document type {data['code']} already exists")
            created_types.append(existing)
            continue
        
        doc_type = DocumentType(**data)
        db.add(doc_type)
        created_types.append(doc_type)
        print(f"✅ Created document type: {data['name']}")
    
    db.commit()
    return created_types


def import_customers_from_excel(db: Session, excel_file: str):
    """从Excel导入客户数据"""
    print(f"\nImporting customers from {excel_file}...")
    
    if not os.path.exists(excel_file):
        print(f"❌ File not found: {excel_file}")
        return
    
    df = pd.read_excel(excel_file)
    
    # 获取产品映射
    products = db.query(LoanProduct).all()
    product_map = {p.code: p.id for p in products}
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            product_code = str(row.get('产品代码', '')).strip()
            if product_code not in product_map:
                print(f"❌ Row {index+2}: Invalid product code '{product_code}'")
                error_count += 1
                continue
            
            customer = Customer(
                customer_no=str(row.get('客户编号', '')).strip(),
                name=str(row.get('客户姓名', '')).strip(),
                phone=str(row.get('手机号', '')).strip() if pd.notna(row.get('手机号')) else None,
                id_card=str(row.get('身份证号', '')).strip() if pd.notna(row.get('身份证号')) else None,
                product_id=product_map[product_code],
                note=str(row.get('备注', '')).strip() if pd.notna(row.get('备注')) else None,
                status='pending'
            )
            
            db.add(customer)
            success_count += 1
            
        except Exception as e:
            print(f"❌ Row {index+2}: {str(e)}")
            error_count += 1
    
    db.commit()
    print(f"✅ Imported {success_count} customers, {error_count} errors")


def import_documents_from_folder(db: Session, folder_path: str, upload_dir: str):
    """从文件夹导入资料文件"""
    print(f"\nImporting documents from {folder_path}...")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    # 获取所有客户
    customers = db.query(Customer).all()
    customer_map = {c.customer_no: c.id for c in customers}
    
    # 获取所有资料类型
    doc_types = db.query(DocumentType).all()
    doc_type_map = {dt.code: dt.id for dt in doc_types}
    
    success_count = 0
    error_count = 0
    
    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                # 文件命名规则: {customer_no}_{doc_type_code}_{序号}.{ext}
                # 例如: C001_id_card_1.jpg
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file)
                
                # 解析文件名
                parts = file_name.split('_')
                if len(parts) < 3:
                    print(f"❌ Invalid file name format: {file_name}")
                    error_count += 1
                    continue
                
                customer_no = parts[0]
                doc_type_code = parts[1]
                
                if customer_no not in customer_map:
                    print(f"❌ Customer not found: {customer_no}")
                    error_count += 1
                    continue
                
                if doc_type_code not in doc_type_map:
                    print(f"❌ Document type not found: {doc_type_code}")
                    error_count += 1
                    continue
                
                # 复制文件到上传目录
                customer_id = customer_map[customer_no]
                dest_dir = os.path.join(upload_dir, str(customer_id))
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_path = os.path.join(dest_dir, file_name)
                shutil.copy2(file_path, dest_path)
                
                # 创建数据库记录
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(file_name)[1]
                
                document = CustomerDocument(
                    customer_id=customer_id,
                    document_type_id=doc_type_map[doc_type_code],
                    file_name=file_name,
                    file_path=dest_path,
                    file_size=file_size,
                    file_type=f"image/{file_ext[1:]}" if file_ext in ['.jpg', '.jpeg', '.png'] else "application/octet-stream",
                    status='pending'
                )
                
                db.add(document)
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error processing {file}: {str(e)}")
                error_count += 1
    
    db.commit()
    print(f"✅ Imported {success_count} documents, {error_count} errors")


def main():
    """主函数"""
    print("=" * 60)
    print("数据迁移工具")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 创建管理员用户
        create_admin_user(db)
        
        # 2. 创建示例产品
        create_sample_products(db)
        
        # 3. 创建资料类型
        create_document_types(db)
        
        # 4. 导入客户数据（如果有Excel文件）
        excel_file = "data/customers.xlsx"
        if os.path.exists(excel_file):
            import_customers_from_excel(db, excel_file)
        else:
            print(f"\n⚠️  Customer data file not found: {excel_file}")
            print("   Skipping customer import")
        
        # 5. 导入资料文件（如果有文件夹）
        documents_folder = "data/documents"
        upload_dir = "uploads"
        if os.path.exists(documents_folder):
            import_documents_from_folder(db, documents_folder, upload_dir)
        else:
            print(f"\n⚠️  Documents folder not found: {documents_folder}")
            print("   Skipping document import")
        
        print("\n" + "=" * 60)
        print("✅ Data migration completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

