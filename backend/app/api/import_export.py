from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from uuid import UUID

from app.database import get_db
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from app.core.dependencies import get_current_active_user, require_permission
from app.models.user import User

router = APIRouter()


@router.post("/customers/import")
async def import_customers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.create"))
):
    """
    批量导入客户数据
    支持Excel (.xlsx, .xls) 和 CSV (.csv) 格式
    """
    # 检查文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['xlsx', 'xls', 'csv']:
        raise HTTPException(status_code=400, detail="不支持的文件格式，请上传Excel或CSV文件")
    
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型读取数据
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 验证必需列
        required_columns = ['客户编号', '客户姓名', '产品代码']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必需列: {', '.join(missing_columns)}"
            )
        
        # 导入结果
        success_count = 0
        error_count = 0
        errors = []
        
        # 获取所有产品代码映射
        products = db.query(LoanProduct).all()
        product_map = {p.code: p.id for p in products}
        
        # 逐行处理
        for index, row in df.iterrows():
            try:
                # 验证产品代码
                product_code = str(row.get('产品代码', '')).strip()
                if not product_code:
                    errors.append(f"第{index+2}行: 产品代码不能为空")
                    error_count += 1
                    continue
                
                if product_code not in product_map:
                    errors.append(f"第{index+2}行: 产品代码 '{product_code}' 不存在")
                    error_count += 1
                    continue
                
                # 验证客户编号
                customer_no = str(row.get('客户编号', '')).strip()
                if not customer_no:
                    errors.append(f"第{index+2}行: 客户编号不能为空")
                    error_count += 1
                    continue
                
                # 检查客户编号是否已存在
                existing = db.query(Customer).filter(Customer.customer_no == customer_no).first()
                if existing:
                    errors.append(f"第{index+2}行: 客户编号 '{customer_no}' 已存在")
                    error_count += 1
                    continue
                
                # 创建客户
                customer = Customer(
                    customer_no=customer_no,
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
                errors.append(f"第{index+2}行: {str(e)}")
                error_count += 1
        
        # 提交事务
        if success_count > 0:
            db.commit()
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "total": len(df),
            "errors": errors[:100]  # 最多返回100条错误
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="文件为空")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/customers/export")
async def export_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.view"))
):
    """
    导出客户数据为Excel
    """
    from fastapi.responses import StreamingResponse
    
    # 查询客户数据
    customers = db.query(Customer).all()
    
    # 构建数据
    data = []
    for customer in customers:
        data.append({
            '客户编号': customer.customer_no,
            '客户姓名': customer.name,
            '手机号': customer.phone or '',
            '身份证号': customer.id_card or '',
            '产品代码': customer.product.code if customer.product else '',
            '产品名称': customer.product.name if customer.product else '',
            '状态': customer.status,
            '备注': customer.note or '',
            '创建时间': customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else ''
        })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 写入Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='客户数据')
    
    output.seek(0)
    
    # 返回文件
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename=customers.xlsx'
        }
    )


@router.get("/customers/template")
async def download_template():
    """
    下载客户导入模板
    """
    from fastapi.responses import StreamingResponse
    
    # 创建模板数据
    template_data = {
        '客户编号': ['C001', 'C002'],
        '客户姓名': ['张三', '李四'],
        '手机号': ['13800138000', '13900139000'],
        '身份证号': ['110101199001011234', '110101199002021234'],
        '产品代码': ['personal_loan', 'car_loan'],
        '备注': ['示例客户', '']
    }
    
    df = pd.DataFrame(template_data)
    
    # 写入Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='客户导入模板')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename=customer_import_template.xlsx'
        }
    )

