"""支付和订阅服务."""

import stripe
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.config import settings
from app.core.logging import get_logger
from app.models.subscription import (
    Plan, PlanType, Subscription, SubscriptionStatus,
    Payment, PaymentStatus, UsageRecord
)
from app.utils.redis_client import redis_client

logger = get_logger(__name__)

# 初始化Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionService:
    """订阅管理服务."""
    
    async def get_plans(
        self,
        db: AsyncSession,
        active_only: bool = True
    ) -> List[Plan]:
        """获取套餐列表."""
        try:
            query = select(Plan)
            
            if active_only:
                query = query.where(Plan.is_active == True)
            
            query = query.order_by(Plan.monthly_price)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get plans: {e}")
            return []
    
    async def get_user_subscription(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[Subscription]:
        """获取用户当前订阅."""
        try:
            query = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status.in_([
                        SubscriptionStatus.TRIAL,
                        SubscriptionStatus.ACTIVE
                    ])
                )
            )
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get user subscription: {e}")
            return None
    
    async def create_subscription(
        self,
        db: AsyncSession,
        user_id: int,
        plan_id: int,
        payment_method_id: Optional[str] = None
    ) -> Optional[Subscription]:
        """创建订阅."""
        try:
            # 检查是否已有活跃订阅
            existing = await self.get_user_subscription(db, user_id)
            if existing:
                logger.warning(f"User {user_id} already has active subscription")
                return None
            
            # 获取套餐信息
            plan_query = select(Plan).where(Plan.id == plan_id)
            result = await db.execute(plan_query)
            plan = result.scalar_one_or_none()
            
            if not plan:
                logger.error(f"Plan {plan_id} not found")
                return None
            
            # 创建或获取Stripe客户
            stripe_customer = await self._get_or_create_stripe_customer(
                user_id,
                payment_method_id
            )
            
            if not stripe_customer:
                logger.error(f"Failed to create Stripe customer for user {user_id}")
                return None
            
            # 创建Stripe订阅
            stripe_subscription = None
            if plan.type != PlanType.FREE:
                stripe_subscription = await self._create_stripe_subscription(
                    stripe_customer.id,
                    plan.stripe_monthly_price_id
                )
                
                if not stripe_subscription:
                    logger.error(f"Failed to create Stripe subscription")
                    return None
            
            # 创建本地订阅记录
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.TRIAL if plan.type == PlanType.FREE else SubscriptionStatus.ACTIVE,
                billing_cycle="monthly",
                stripe_customer_id=stripe_customer.id,
                stripe_subscription_id=stripe_subscription.id if stripe_subscription else None,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                trial_ends_at=datetime.utcnow() + timedelta(days=14) if plan.type == PlanType.FREE else None
            )
            
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            logger.info(f"Subscription created for user {user_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            await db.rollback()
            return None
    
    async def cancel_subscription(
        self,
        db: AsyncSession,
        user_id: int,
        immediately: bool = False
    ) -> bool:
        """取消订阅."""
        try:
            subscription = await self.get_user_subscription(db, user_id)
            if not subscription:
                return False
            
            # 取消Stripe订阅
            if subscription.stripe_subscription_id:
                try:
                    if immediately:
                        stripe.Subscription.delete(subscription.stripe_subscription_id)
                    else:
                        stripe.Subscription.modify(
                            subscription.stripe_subscription_id,
                            cancel_at_period_end=True
                        )
                except stripe.error.StripeError as e:
                    logger.error(f"Failed to cancel Stripe subscription: {e}")
            
            # 更新本地记录
            subscription.canceled_at = datetime.utcnow()
            
            if immediately:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.ended_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Subscription canceled for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            await db.rollback()
            return False
    
    async def check_usage_limit(
        self,
        db: AsyncSession,
        user_id: int,
        usage_type: str,
        amount: int = 1
    ) -> bool:
        """检查使用限额."""
        try:
            subscription = await self.get_user_subscription(db, user_id)
            if not subscription:
                return False
            
            # 获取套餐信息
            plan = subscription.plan
            
            # 检查不同类型的限额
            if usage_type == "tokens":
                remaining = plan.monthly_tokens - subscription.tokens_used
                return remaining >= amount
            elif usage_type == "conversations":
                if plan.max_conversations:
                    return subscription.conversations_count < plan.max_conversations
            elif usage_type == "files":
                if plan.max_files_per_month:
                    return subscription.files_uploaded < plan.max_files_per_month
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check usage limit: {e}")
            return False
    
    async def record_usage(
        self,
        db: AsyncSession,
        user_id: int,
        usage_type: str,
        amount: int = 1
    ) -> bool:
        """记录使用量."""
        try:
            subscription = await self.get_user_subscription(db, user_id)
            if not subscription:
                return False
            
            # 更新订阅使用量
            if usage_type == "tokens":
                subscription.tokens_used += amount
            elif usage_type == "conversations":
                subscription.conversations_count += 1
            elif usage_type == "files":
                subscription.files_uploaded += 1
            
            # 创建使用记录
            usage_record = UsageRecord(
                user_id=user_id,
                subscription_id=subscription.id,
                usage_type=usage_type,
                tokens_used=amount if usage_type == "tokens" else 0,
                conversations_created=1 if usage_type == "conversations" else 0,
                files_uploaded=1 if usage_type == "files" else 0,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end
            )
            
            db.add(usage_record)
            await db.commit()
            
            # 缓存使用量
            await self._cache_usage(user_id, subscription)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            await db.rollback()
            return False
    
    async def _get_or_create_stripe_customer(
        self,
        user_id: int,
        payment_method_id: Optional[str] = None
    ) -> Optional[Any]:
        """获取或创建Stripe客户."""
        try:
            # 这里应该从用户表获取邮箱等信息
            # 简化实现
            customer = stripe.Customer.create(
                metadata={"user_id": str(user_id)},
                payment_method=payment_method_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                } if payment_method_id else None
            )
            
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    async def _create_stripe_subscription(
        self,
        customer_id: str,
        price_id: str
    ) -> Optional[Any]:
        """创建Stripe订阅."""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                expand=["latest_invoice.payment_intent"]
            )
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            return None
    
    async def _cache_usage(
        self,
        user_id: int,
        subscription: Subscription
    ) -> None:
        """缓存使用量."""
        try:
            key = f"subscription:usage:{user_id}"
            value = {
                "tokens_used": subscription.tokens_used,
                "conversations_count": subscription.conversations_count,
                "files_uploaded": subscription.files_uploaded,
                "plan_id": subscription.plan_id
            }
            
            await redis_client.setex(key, 3600, str(value))
            
        except Exception as e:
            logger.error(f"Failed to cache usage: {e}")


class PaymentService:
    """支付服务."""
    
    async def process_payment(
        self,
        db: AsyncSession,
        user_id: int,
        amount: float,
        currency: str = "USD",
        payment_method_id: Optional[str] = None
    ) -> Optional[Payment]:
        """处理支付."""
        try:
            # 创建Stripe支付意图
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe使用分为单位
                currency=currency,
                payment_method=payment_method_id,
                confirm=True if payment_method_id else False,
                metadata={"user_id": str(user_id)}
            )
            
            # 创建支付记录
            payment = Payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PROCESSING,
                stripe_payment_intent_id=payment_intent.id
            )
            
            db.add(payment)
            await db.commit()
            
            # 等待支付确认（实际应该通过Webhook处理）
            if payment_intent.status == "succeeded":
                payment.status = PaymentStatus.SUCCEEDED
                payment.paid_at = datetime.utcnow()
                await db.commit()
            
            return payment
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            await db.rollback()
            return None
    
    async def handle_webhook(
        self,
        db: AsyncSession,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """处理Stripe Webhook."""
        try:
            if event_type == "payment_intent.succeeded":
                await self._handle_payment_success(db, event_data)
            elif event_type == "payment_intent.payment_failed":
                await self._handle_payment_failure(db, event_data)
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_update(db, event_data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deletion(db, event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False
    
    async def _handle_payment_success(
        self,
        db: AsyncSession,
        event_data: Dict[str, Any]
    ) -> None:
        """处理支付成功."""
        payment_intent_id = event_data.get("id")
        
        query = select(Payment).where(
            Payment.stripe_payment_intent_id == payment_intent_id
        )
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.SUCCEEDED
            payment.paid_at = datetime.utcnow()
            await db.commit()
    
    async def _handle_payment_failure(
        self,
        db: AsyncSession,
        event_data: Dict[str, Any]
    ) -> None:
        """处理支付失败."""
        payment_intent_id = event_data.get("id")
        
        query = select(Payment).where(
            Payment.stripe_payment_intent_id == payment_intent_id
        )
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.FAILED
            await db.commit()
    
    async def _handle_subscription_update(
        self,
        db: AsyncSession,
        event_data: Dict[str, Any]
    ) -> None:
        """处理订阅更新."""
        stripe_subscription_id = event_data.get("id")
        
        query = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # 更新订阅状态
            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "past_due": SubscriptionStatus.PAST_DUE,
                "canceled": SubscriptionStatus.CANCELED
            }
            
            stripe_status = event_data.get("status")
            if stripe_status in status_map:
                subscription.status = status_map[stripe_status]
            
            # 更新周期信息
            current_period = event_data.get("current_period")
            if current_period:
                subscription.current_period_start = datetime.fromtimestamp(
                    current_period.get("start")
                )
                subscription.current_period_end = datetime.fromtimestamp(
                    current_period.get("end")
                )
            
            await db.commit()
    
    async def _handle_subscription_deletion(
        self,
        db: AsyncSession,
        event_data: Dict[str, Any]
    ) -> None:
        """处理订阅删除."""
        stripe_subscription_id = event_data.get("id")
        
        query = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.ended_at = datetime.utcnow()
            await db.commit()


# 全局服务实例
subscription_service = SubscriptionService()
payment_service = PaymentService()