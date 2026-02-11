from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.database import get_user_by_id, db
from app.config import settings
from app.models import SubscriptionTier
import stripe
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


async def get_current_user():
    """Get current user (placeholder)"""
    return {
        "id": "test-user-123",
        "email": "test@example.com"
    }


@router.post("/payments/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session for subscription
    
    Args:
        price_id: Stripe price ID (creator or agency plan)
    
    Returns:
        checkout_url: URL to redirect user to Stripe checkout
    """
    
    try:
        # Create or get Stripe customer
        user = await get_user_by_id(current_user["id"])
        
        if user.get("stripe_customer_id"):
            customer_id = user["stripe_customer_id"]
        else:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=current_user["email"],
                metadata={"user_id": current_user["id"]}
            )
            customer_id = customer.id
            
            # Save customer ID to database
            client = db.get_client()
            client.table("users").update({
                "stripe_customer_id": customer_id
            }).eq("id", current_user["id"]).execute()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
            metadata={
                "user_id": current_user["id"]
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    
    Events:
        - checkout.session.completed: New subscription
        - customer.subscription.updated: Subscription changed
        - customer.subscription.deleted: Subscription canceled
        - invoice.payment_succeeded: Monthly payment successful
        - invoice.payment_failed: Payment failed
    """
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Received Stripe event: {event_type}")
    
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data)
    
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data)
    
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data)
    
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(data)
    
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data)
    
    return JSONResponse(content={"status": "success"})


async def handle_checkout_completed(session):
    """Handle successful checkout"""
    try:
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        
        # Get subscription details
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription["items"]["data"][0]["price"]["id"]
        
        # Determine tier based on price ID
        if price_id == settings.STRIPE_PRICE_ID_CREATOR:
            tier = "creator"
            credits = settings.CREATOR_CREDITS_PER_MONTH
        elif price_id == settings.STRIPE_PRICE_ID_AGENCY:
            tier = "agency"
            credits = settings.AGENCY_CREDITS_PER_MONTH
        else:
            tier = "free"
            credits = settings.FREE_CREDITS_PER_MONTH
        
        # Update user in database
        client = db.get_client()
        result = client.table("users").update({
            "subscription_tier": tier,
            "stripe_subscription_id": subscription_id,
            "credits_remaining": credits,
            "credits_reset_date": stripe.util.convert_to_stripe_object(
                subscription["current_period_end"]
            )
        }).eq("stripe_customer_id", customer_id).execute()
        
        logger.info(f"Updated user subscription to {tier}")
        
    except Exception as e:
        logger.error(f"Error handling checkout: {e}")


async def handle_subscription_updated(subscription):
    """Handle subscription update"""
    try:
        customer_id = subscription.get("customer")
        price_id = subscription["items"]["data"][0]["price"]["id"]
        status = subscription.get("status")
        
        # Only update if subscription is active
        if status != "active":
            return
        
        # Determine tier
        if price_id == settings.STRIPE_PRICE_ID_CREATOR:
            tier = "creator"
            credits = settings.CREATOR_CREDITS_PER_MONTH
        elif price_id == settings.STRIPE_PRICE_ID_AGENCY:
            tier = "agency"
            credits = settings.AGENCY_CREDITS_PER_MONTH
        else:
            tier = "free"
            credits = settings.FREE_CREDITS_PER_MONTH
        
        # Update user
        client = db.get_client()
        client.table("users").update({
            "subscription_tier": tier,
            "credits_remaining": credits
        }).eq("stripe_customer_id", customer_id).execute()
        
        logger.info(f"Subscription updated to {tier}")
        
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")


async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription.get("customer")
        
        # Downgrade to free tier
        client = db.get_client()
        client.table("users").update({
            "subscription_tier": "free",
            "stripe_subscription_id": None,
            "credits_remaining": settings.FREE_CREDITS_PER_MONTH
        }).eq("stripe_customer_id", customer_id).execute()
        
        logger.info("Subscription canceled, downgraded to free")
        
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")


async def handle_payment_succeeded(invoice):
    """Handle successful monthly payment"""
    try:
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        
        if not subscription_id:
            return
        
        # Get subscription to determine tier
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription["items"]["data"][0]["price"]["id"]
        
        # Reset credits for the new billing period
        if price_id == settings.STRIPE_PRICE_ID_CREATOR:
            credits = settings.CREATOR_CREDITS_PER_MONTH
        elif price_id == settings.STRIPE_PRICE_ID_AGENCY:
            credits = settings.AGENCY_CREDITS_PER_MONTH
        else:
            credits = settings.FREE_CREDITS_PER_MONTH
        
        # Update credits
        client = db.get_client()
        client.table("users").update({
            "credits_remaining": credits
        }).eq("stripe_customer_id", customer_id).execute()
        
        logger.info(f"Credits reset to {credits} after payment")
        
    except Exception as e:
        logger.error(f"Error handling payment: {e}")


async def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        customer_id = invoice.get("customer")
        
        # Optionally: send email notification, downgrade account, etc.
        logger.warning(f"Payment failed for customer {customer_id}")
        
        # You could downgrade to free tier or send notifications here
        
    except Exception as e:
        logger.error(f"Error handling failed payment: {e}")


@router.post("/payments/cancel-subscription")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """
    Cancel user's subscription
    
    Cancels at end of billing period (doesn't refund)
    """
    try:
        user = await get_user_by_id(current_user["id"])
        subscription_id = user.get("stripe_subscription_id")
        
        if not subscription_id:
            raise HTTPException(
                status_code=400,
                detail="No active subscription"
            )
        
        # Cancel subscription at period end
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        return {
            "message": "Subscription will be canceled at end of billing period",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/payments/portal")
async def customer_portal(current_user: dict = Depends(get_current_user)):
    """
    Create Stripe customer portal session
    
    Allows users to manage their subscription, payment methods, invoices
    """
    try:
        user = await get_user_by_id(current_user["id"])
        customer_id = user.get("stripe_customer_id")
        
        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No Stripe customer found"
            )
        
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        return {
            "portal_url": portal_session.url
        }
        
    except Exception as e:
        logger.error(f"Portal creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create portal session: {str(e)}"
        )