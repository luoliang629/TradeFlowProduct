"""业务功能服务（产品、买家、供应商）."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.core.logging import get_logger
from app.models.product import Product, ProductStatus, Buyer, Supplier
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class ProductService:
    """产品管理服务."""
    
    async def create_product(
        self,
        db: AsyncSession,
        user_id: int,
        product_data: Dict[str, Any]
    ) -> Optional[Product]:
        """创建产品."""
        try:
            product = Product(
                user_id=user_id,
                **product_data
            )
            
            db.add(product)
            await db.commit()
            await db.refresh(product)
            
            logger.info(f"Product created: {product.id}")
            return product
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            await db.rollback()
            return None
    
    async def get_product(
        self,
        db: AsyncSession,
        product_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Product]:
        """获取产品."""
        try:
            query = select(Product).where(Product.id == product_id)
            
            if user_id:
                query = query.where(Product.user_id == user_id)
            
            result = await db.execute(query)
            product = result.scalar_one_or_none()
            
            # 增加浏览次数
            if product:
                product.view_count += 1
                await db.commit()
            
            return product
            
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            return None
    
    async def update_product(
        self,
        db: AsyncSession,
        product_id: int,
        user_id: int,
        product_data: Dict[str, Any]
    ) -> Optional[Product]:
        """更新产品."""
        try:
            product = await self.get_product(db, product_id, user_id)
            if not product:
                return None
            
            for key, value in product_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            await db.commit()
            await db.refresh(product)
            
            return product
            
        except Exception as e:
            logger.error(f"Failed to update product: {e}")
            await db.rollback()
            return None
    
    async def delete_product(
        self,
        db: AsyncSession,
        product_id: int,
        user_id: int
    ) -> bool:
        """删除产品（软删除）."""
        try:
            product = await self.get_product(db, product_id, user_id)
            if not product:
                return False
            
            product.status = ProductStatus.ARCHIVED
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete product: {e}")
            await db.rollback()
            return False
    
    async def search_products(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """搜索产品."""
        try:
            stmt = select(Product)
            
            # 构建查询条件
            conditions = []
            
            if query:
                conditions.append(
                    or_(
                        Product.name.ilike(f"%{query}%"),
                        Product.description.ilike(f"%{query}%"),
                        Product.sku.ilike(f"%{query}%")
                    )
                )
            
            if category:
                conditions.append(Product.category == category)
            
            if user_id:
                conditions.append(Product.user_id == user_id)
            
            if status:
                conditions.append(Product.status == status)
            else:
                conditions.append(Product.status != ProductStatus.ARCHIVED)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(Product.created_at.desc())
            stmt = stmt.offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []


class BuyerService:
    """买家推荐服务."""
    
    async def get_buyer_recommendations(
        self,
        db: AsyncSession,
        product_categories: List[str],
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[Buyer]:
        """获取买家推荐."""
        try:
            stmt = select(Buyer)
            
            # 基于产品类别匹配
            if product_categories:
                # 使用JSON字段查询
                category_conditions = []
                for category in product_categories:
                    category_conditions.append(
                        func.json_contains(
                            Buyer.purchase_categories,
                            f'"{category}"'
                        )
                    )
                
                if category_conditions:
                    stmt = stmt.where(or_(*category_conditions))
            
            # 国家过滤
            if country:
                stmt = stmt.where(Buyer.country == country)
            
            # 只推荐已验证的买家
            stmt = stmt.where(Buyer.verified == True)
            
            # 按评分排序
            stmt = stmt.order_by(
                (Buyer.quality_score + Buyer.reliability_score).desc()
            )
            
            stmt = stmt.limit(limit)
            
            result = await db.execute(stmt)
            buyers = result.scalars().all()
            
            # 缓存推荐结果
            await self._cache_recommendations(buyers)
            
            return buyers
            
        except Exception as e:
            logger.error(f"Failed to get buyer recommendations: {e}")
            return []
    
    async def create_buyer(
        self,
        db: AsyncSession,
        buyer_data: Dict[str, Any],
        created_by: int
    ) -> Optional[Buyer]:
        """创建买家信息."""
        try:
            buyer = Buyer(
                created_by=created_by,
                **buyer_data
            )
            
            db.add(buyer)
            await db.commit()
            await db.refresh(buyer)
            
            return buyer
            
        except Exception as e:
            logger.error(f"Failed to create buyer: {e}")
            await db.rollback()
            return None
    
    async def search_buyers(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        country: Optional[str] = None,
        verified_only: bool = False,
        skip: int = 0,
        limit: int = 20
    ) -> List[Buyer]:
        """搜索买家."""
        try:
            stmt = select(Buyer)
            
            if query:
                stmt = stmt.where(
                    or_(
                        Buyer.company_name.ilike(f"%{query}%"),
                        Buyer.contact_name.ilike(f"%{query}%"),
                        Buyer.email.ilike(f"%{query}%")
                    )
                )
            
            if country:
                stmt = stmt.where(Buyer.country == country)
            
            if verified_only:
                stmt = stmt.where(Buyer.verified == True)
            
            stmt = stmt.order_by(Buyer.created_at.desc())
            stmt = stmt.offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to search buyers: {e}")
            return []
    
    async def _cache_recommendations(self, buyers: List[Buyer]) -> None:
        """缓存推荐结果."""
        try:
            # 简单的缓存实现
            for buyer in buyers[:5]:  # 缓存前5个推荐
                key = f"buyer_recommendation:{buyer.id}"
                value = {
                    "id": buyer.id,
                    "company_name": buyer.company_name,
                    "country": buyer.country,
                    "quality_score": buyer.quality_score
                }
                await redis_client.setex(key, 3600, str(value))
                
        except Exception as e:
            logger.error(f"Failed to cache recommendations: {e}")


class SupplierService:
    """供应商搜索服务."""
    
    async def search_suppliers(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        product_category: Optional[str] = None,
        country: Optional[str] = None,
        verified_only: bool = False,
        min_score: Optional[float] = None,
        sort_by: str = "overall_score",
        skip: int = 0,
        limit: int = 20
    ) -> List[Supplier]:
        """搜索供应商."""
        try:
            stmt = select(Supplier)
            
            # 搜索条件
            if query:
                stmt = stmt.where(
                    or_(
                        Supplier.company_name.ilike(f"%{query}%"),
                        func.json_contains(
                            Supplier.main_products,
                            f'"{query}"'
                        )
                    )
                )
            
            # 产品类别过滤
            if product_category:
                stmt = stmt.where(
                    func.json_contains(
                        Supplier.main_products,
                        f'"{product_category}"'
                    )
                )
            
            # 国家过滤
            if country:
                stmt = stmt.where(Supplier.country == country)
            
            # 验证状态过滤
            if verified_only:
                stmt = stmt.where(Supplier.verified == True)
            
            # 最低评分过滤
            if min_score:
                stmt = stmt.where(Supplier.overall_score >= min_score)
            
            # 排序
            if sort_by == "quality_score":
                stmt = stmt.order_by(Supplier.quality_score.desc())
            elif sort_by == "price_score":
                stmt = stmt.order_by(Supplier.price_score.desc())
            elif sort_by == "delivery_score":
                stmt = stmt.order_by(Supplier.delivery_score.desc())
            else:
                stmt = stmt.order_by(Supplier.overall_score.desc())
            
            stmt = stmt.offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to search suppliers: {e}")
            return []
    
    async def create_supplier(
        self,
        db: AsyncSession,
        supplier_data: Dict[str, Any],
        created_by: int
    ) -> Optional[Supplier]:
        """创建供应商信息."""
        try:
            # 计算综合评分
            scores = [
                supplier_data.get("quality_score", 0),
                supplier_data.get("service_score", 0),
                supplier_data.get("delivery_score", 0),
                supplier_data.get("price_score", 0)
            ]
            
            valid_scores = [s for s in scores if s > 0]
            if valid_scores:
                supplier_data["overall_score"] = sum(valid_scores) / len(valid_scores)
            
            supplier = Supplier(
                created_by=created_by,
                **supplier_data
            )
            
            db.add(supplier)
            await db.commit()
            await db.refresh(supplier)
            
            return supplier
            
        except Exception as e:
            logger.error(f"Failed to create supplier: {e}")
            await db.rollback()
            return None
    
    async def compare_suppliers(
        self,
        db: AsyncSession,
        supplier_ids: List[int]
    ) -> Dict[str, Any]:
        """比较供应商."""
        try:
            stmt = select(Supplier).where(Supplier.id.in_(supplier_ids))
            result = await db.execute(stmt)
            suppliers = result.scalars().all()
            
            if not suppliers:
                return {}
            
            # 构建比较结果
            comparison = {
                "suppliers": [],
                "best_quality": None,
                "best_price": None,
                "best_delivery": None,
                "best_overall": None
            }
            
            best_quality_score = 0
            best_price_score = 0
            best_delivery_score = 0
            best_overall_score = 0
            
            for supplier in suppliers:
                supplier_info = {
                    "id": supplier.id,
                    "company_name": supplier.company_name,
                    "country": supplier.country,
                    "quality_score": supplier.quality_score,
                    "price_score": supplier.price_score,
                    "delivery_score": supplier.delivery_score,
                    "overall_score": supplier.overall_score,
                    "verified": supplier.verified
                }
                
                comparison["suppliers"].append(supplier_info)
                
                # 找出各项最佳
                if supplier.quality_score and supplier.quality_score > best_quality_score:
                    best_quality_score = supplier.quality_score
                    comparison["best_quality"] = supplier_info
                
                if supplier.price_score and supplier.price_score > best_price_score:
                    best_price_score = supplier.price_score
                    comparison["best_price"] = supplier_info
                
                if supplier.delivery_score and supplier.delivery_score > best_delivery_score:
                    best_delivery_score = supplier.delivery_score
                    comparison["best_delivery"] = supplier_info
                
                if supplier.overall_score and supplier.overall_score > best_overall_score:
                    best_overall_score = supplier.overall_score
                    comparison["best_overall"] = supplier_info
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare suppliers: {e}")
            return {}


# 全局服务实例
product_service = ProductService()
buyer_service = BuyerService()
supplier_service = SupplierService()