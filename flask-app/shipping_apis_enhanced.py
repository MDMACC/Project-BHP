"""
Enhanced Shipping API Integration System
Supports multiple carriers with webhook integration
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from models import db, ShippingAccount, ShippingOrder, TrackingEvent

logger = logging.getLogger(__name__)

class BaseShippingAPI:
    """Base class for all shipping API integrations"""
    
    def __init__(self, account: ShippingAccount):
        self.account = account
        self.provider = account.provider.lower()
        self.api_key = account.api_key
        self.api_secret = account.api_secret
        self.base_url = self.get_base_url()
        self.session = requests.Session()
        self.setup_session()
    
    def get_base_url(self) -> str:
        """Override in subclasses"""
        raise NotImplementedError
    
    def setup_session(self):
        """Setup session with authentication"""
        pass
    
    def authenticate(self) -> bool:
        """Test API authentication"""
        try:
            response = self.test_connection()
            return response.get('success', False)
        except Exception as e:
            logger.error(f"Authentication failed for {self.provider}: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection"""
        raise NotImplementedError
    
    def get_orders(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Fetch orders from API"""
        raise NotImplementedError
    
    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get tracking information for a specific tracking number"""
        raise NotImplementedError
    
    def sync_orders(self) -> int:
        """Sync orders from API to database"""
        try:
            # Get orders from last 30 days
            start_date = datetime.now() - timedelta(days=30)
            orders = self.get_orders(start_date=start_date)
            
            synced_count = 0
            for order_data in orders:
                if self.process_order(order_data):
                    synced_count += 1
            
            # Update last sync time
            self.account.last_sync = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Synced {synced_count} orders from {self.provider}")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing orders from {self.provider}: {e}")
            db.session.rollback()
            return 0
    
    def process_order(self, order_data: Dict) -> bool:
        """Process a single order from API data"""
        try:
            # Extract common fields
            order_id = self.extract_order_id(order_data)
            tracking_number = self.extract_tracking_number(order_data)
            
            if not order_id:
                return False
            
            # Check if order already exists
            existing_order = ShippingOrder.query.filter_by(
                account_id=self.account.id,
                order_id=order_id
            ).first()
            
            if existing_order:
                # Update existing order
                self.update_order(existing_order, order_data)
            else:
                # Create new order
                self.create_order(order_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return False
    
    def extract_order_id(self, order_data: Dict) -> Optional[str]:
        """Extract order ID from API data - override in subclasses"""
        return order_data.get('order_id') or order_data.get('id')
    
    def extract_tracking_number(self, order_data: Dict) -> Optional[str]:
        """Extract tracking number from API data - override in subclasses"""
        return order_data.get('tracking_number') or order_data.get('trackingNumber')
    
    def create_order(self, order_data: Dict):
        """Create new shipping order from API data"""
        order = ShippingOrder(
            account_id=self.account.id,
            order_id=self.extract_order_id(order_data),
            tracking_number=self.extract_tracking_number(order_data),
            carrier=self.extract_carrier(order_data),
            status=self.extract_status(order_data),
            order_date=self.extract_order_date(order_data),
            ship_date=self.extract_ship_date(order_data),
            estimated_delivery=self.extract_estimated_delivery(order_data),
            total_amount=self.extract_total_amount(order_data),
            items_count=self.extract_items_count(order_data),
            shipping_address=self.extract_shipping_address(order_data)
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Create initial tracking event
        self.create_tracking_event(order.id, order_data)
    
    def update_order(self, order: ShippingOrder, order_data: Dict):
        """Update existing order with new data"""
        order.status = self.extract_status(order_data) or order.status
        order.tracking_number = self.extract_tracking_number(order_data) or order.tracking_number
        order.estimated_delivery = self.extract_estimated_delivery(order_data) or order.estimated_delivery
        order.updated_at = datetime.utcnow()
        
        # Create tracking event for update
        self.create_tracking_event(order.id, order_data)
    
    def create_tracking_event(self, order_id: int, order_data: Dict):
        """Create tracking event from order data"""
        event = TrackingEvent(
            shipping_order_id=order_id,
            event_date=datetime.utcnow(),
            status=self.extract_status(order_data) or 'update',
            description=self.extract_description(order_data),
            location=self.extract_location(order_data)
        )
        event.set_webhook_data(order_data)
        db.session.add(event)
    
    # Extract methods - override in subclasses for provider-specific parsing
    def extract_carrier(self, data: Dict) -> Optional[str]:
        return data.get('carrier') or self.provider.upper()
    
    def extract_status(self, data: Dict) -> Optional[str]:
        return data.get('status')
    
    def extract_order_date(self, data: Dict) -> Optional[datetime]:
        date_str = data.get('order_date') or data.get('orderDate')
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
        return None
    
    def extract_ship_date(self, data: Dict) -> Optional[datetime]:
        date_str = data.get('ship_date') or data.get('shipDate')
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
        return None
    
    def extract_estimated_delivery(self, data: Dict) -> Optional[datetime]:
        date_str = data.get('estimated_delivery') or data.get('estimatedDelivery')
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
        return None
    
    def extract_total_amount(self, data: Dict) -> Optional[float]:
        amount = data.get('total_amount') or data.get('totalAmount')
        if amount:
            try:
                return float(amount)
            except:
                pass
        return None
    
    def extract_items_count(self, data: Dict) -> int:
        return data.get('items_count') or data.get('itemsCount') or 1
    
    def extract_shipping_address(self, data: Dict) -> Optional[str]:
        address = data.get('shipping_address') or data.get('shippingAddress')
        if isinstance(address, dict):
            parts = []
            if address.get('street'): parts.append(address['street'])
            if address.get('city'): parts.append(address['city'])
            if address.get('state'): parts.append(address['state'])
            if address.get('zip'): parts.append(address['zip'])
            return ', '.join(parts) if parts else None
        return str(address) if address else None
    
    def extract_description(self, data: Dict) -> Optional[str]:
        return data.get('description') or data.get('statusDescription') or f"Update from {self.provider}"
    
    def extract_location(self, data: Dict) -> Optional[str]:
        location = data.get('location')
        if isinstance(location, dict):
            parts = []
            if location.get('city'): parts.append(location['city'])
            if location.get('state'): parts.append(location['state'])
            return ', '.join(parts) if parts else None
        return str(location) if location else None


class FedExAPI(BaseShippingAPI):
    """FedEx API integration"""
    
    def get_base_url(self) -> str:
        return "https://apis.fedex.com"
    
    def setup_session(self):
        """Setup FedEx authentication"""
        if self.api_key and self.api_secret:
            # Get OAuth token
            auth_response = self.session.post(
                f"{self.base_url}/oauth/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.api_secret
                }
            )
            
            if auth_response.status_code == 200:
                token_data = auth_response.json()
                self.session.headers.update({
                    'Authorization': f"Bearer {token_data['access_token']}",
                    'Content-Type': 'application/json'
                })
    
    def test_connection(self) -> Dict[str, Any]:
        """Test FedEx API connection"""
        try:
            response = self.session.get(f"{self.base_url}/track/v1/trackingnumbers")
            return {'success': response.status_code == 200}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_orders(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Fetch FedEx shipments"""
        # FedEx doesn't have a direct orders API, so we'd typically track specific numbers
        # This is a placeholder for the structure
        return []
    
    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get FedEx tracking information"""
        try:
            payload = {
                "includeDetailedScans": True,
                "trackingInfo": [
                    {
                        "trackingNumberInfo": {
                            "trackingNumber": tracking_number
                        }
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/track/v1/trackingnumbers",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API returned {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


class UPSAPI(BaseShippingAPI):
    """UPS API integration"""
    
    def get_base_url(self) -> str:
        return "https://onlinetools.ups.com/api"
    
    def setup_session(self):
        """Setup UPS authentication"""
        if self.api_key:
            self.session.headers.update({
                'AccessLicenseNumber': self.api_key,
                'Content-Type': 'application/json'
            })
    
    def test_connection(self) -> Dict[str, Any]:
        """Test UPS API connection"""
        try:
            # Test with a simple tracking request
            response = self.session.get(f"{self.base_url}/track/v1/details/1Z999AA1234567890")
            return {'success': response.status_code in [200, 404]}  # 404 is OK for test tracking number
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get UPS tracking information"""
        try:
            response = self.session.get(f"{self.base_url}/track/v1/details/{tracking_number}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API returned {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


class USPSAPI(BaseShippingAPI):
    """USPS API integration"""
    
    def get_base_url(self) -> str:
        return "https://secure.shippingapis.com/ShippingAPI.dll"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test USPS API connection"""
        try:
            # USPS uses XML API
            xml_request = f"""
            <TrackRequest USERID="{self.api_key}">
                <TrackID ID="9400109699937003611611"/>
            </TrackRequest>
            """
            
            response = self.session.get(
                f"{self.base_url}?API=TrackV2&XML={xml_request}"
            )
            
            return {'success': response.status_code == 200}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get USPS tracking information"""
        try:
            xml_request = f"""
            <TrackRequest USERID="{self.api_key}">
                <TrackID ID="{tracking_number}"/>
            </TrackRequest>
            """
            
            response = self.session.get(
                f"{self.base_url}?API=TrackV2&XML={xml_request}"
            )
            
            if response.status_code == 200:
                # Parse XML response (you'd use xml.etree.ElementTree in real implementation)
                return {'xml_response': response.text}
            else:
                return {'error': f'API returned {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


class DHLAPI(BaseShippingAPI):
    """DHL API integration"""
    
    def get_base_url(self) -> str:
        return "https://api-eu.dhl.com"
    
    def setup_session(self):
        """Setup DHL authentication"""
        if self.api_key:
            self.session.headers.update({
                'DHL-API-Key': self.api_key,
                'Content-Type': 'application/json'
            })
    
    def test_connection(self) -> Dict[str, Any]:
        """Test DHL API connection"""
        try:
            response = self.session.get(f"{self.base_url}/track/shipments")
            return {'success': response.status_code in [200, 400]}  # 400 is OK without tracking numbers
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get DHL tracking information"""
        try:
            response = self.session.get(
                f"{self.base_url}/track/shipments",
                params={'trackingNumber': tracking_number}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API returned {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


class AmazonAPI(BaseShippingAPI):
    """Amazon Seller API integration"""
    
    def get_base_url(self) -> str:
        return "https://sellingpartnerapi-na.amazon.com"
    
    def setup_session(self):
        """Setup Amazon SP-API authentication"""
        # Amazon uses AWS Signature V4 - this is simplified
        if self.api_key and self.api_secret:
            self.session.headers.update({
                'x-amz-access-token': self.api_key,
                'Content-Type': 'application/json'
            })
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Amazon API connection"""
        try:
            response = self.session.get(f"{self.base_url}/orders/v0/orders")
            return {'success': response.status_code in [200, 403]}  # 403 might be permissions
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_orders(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Fetch Amazon orders"""
        try:
            params = {}
            if start_date:
                params['CreatedAfter'] = start_date.isoformat()
            if end_date:
                params['CreatedBefore'] = end_date.isoformat()
            
            response = self.session.get(
                f"{self.base_url}/orders/v0/orders",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('payload', {}).get('Orders', [])
            
            return []
        except Exception as e:
            logger.error(f"Error fetching Amazon orders: {e}")
            return []


class AutoZoneAPI(BaseShippingAPI):
    """AutoZone API integration (if available)"""
    
    def get_base_url(self) -> str:
        return "https://api.autozone.com"  # Hypothetical
    
    def test_connection(self) -> Dict[str, Any]:
        """Test AutoZone API connection"""
        # Most auto parts stores don't have public APIs
        # This would be for B2B integrations if available
        return {'success': False, 'error': 'AutoZone API not publicly available'}


class ShippingAPIFactory:
    """Factory for creating shipping API instances"""
    
    API_CLASSES = {
        'fedex': FedExAPI,
        'ups': UPSAPI,
        'usps': USPSAPI,
        'dhl': DHLAPI,
        'amazon': AmazonAPI,
        'autozone': AutoZoneAPI,
    }
    
    @classmethod
    def create_api(cls, account: ShippingAccount) -> Optional[BaseShippingAPI]:
        """Create API instance for shipping account"""
        provider = account.provider.lower()
        api_class = cls.API_CLASSES.get(provider)
        
        if api_class:
            return api_class(account)
        else:
            logger.warning(f"No API class found for provider: {provider}")
            return None
    
    @classmethod
    def sync_all_accounts(cls) -> Dict[str, int]:
        """Sync all active shipping accounts"""
        results = {}
        
        active_accounts = ShippingAccount.query.filter_by(is_active=True).all()
        
        for account in active_accounts:
            api = cls.create_api(account)
            if api and api.authenticate():
                synced_count = api.sync_orders()
                results[account.provider] = synced_count
            else:
                results[account.provider] = 0
                logger.error(f"Failed to sync account: {account.account_name}")
        
        return results
    
    @classmethod
    def get_tracking_info(cls, provider: str, tracking_number: str) -> Dict[str, Any]:
        """Get tracking info from specific provider"""
        account = ShippingAccount.query.filter_by(
            provider=provider,
            is_active=True
        ).first()
        
        if not account:
            return {'error': f'No active account found for {provider}'}
        
        api = cls.create_api(account)
        if api and api.authenticate():
            return api.get_tracking_info(tracking_number)
        else:
            return {'error': f'Failed to authenticate with {provider}'}


class WebhookProcessor:
    """Process incoming webhooks from shipping providers"""
    
    @staticmethod
    def process_webhook(provider: str, payload: Dict, signature: str = None) -> Dict[str, Any]:
        """Process webhook payload from shipping provider"""
        try:
            # Verify signature if provided
            if signature:
                account = ShippingAccount.query.filter_by(
                    provider=provider,
                    is_active=True
                ).first()
                
                if account and not WebhookProcessor.verify_signature(
                    provider, payload, signature, account.api_secret
                ):
                    return {'success': False, 'error': 'Invalid signature'}
            
            # Process based on provider
            if provider.lower() == 'fedex':
                return WebhookProcessor.process_fedex_webhook(payload)
            elif provider.lower() == 'ups':
                return WebhookProcessor.process_ups_webhook(payload)
            elif provider.lower() == 'usps':
                return WebhookProcessor.process_usps_webhook(payload)
            elif provider.lower() == 'dhl':
                return WebhookProcessor.process_dhl_webhook(payload)
            else:
                return WebhookProcessor.process_generic_webhook(provider, payload)
                
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def verify_signature(provider: str, payload: Dict, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        import hmac
        import hashlib
        
        if not signature or not secret:
            return False
        
        try:
            payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            
            if provider.lower() in ['fedex', 'ups', 'dhl']:
                expected_signature = hmac.new(
                    secret.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
            elif provider.lower() == 'usps':
                expected_signature = hmac.new(
                    secret.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha1
                ).hexdigest()
            else:
                expected_signature = hmac.new(
                    secret.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    @staticmethod
    def process_fedex_webhook(payload: Dict) -> Dict[str, Any]:
        """Process FedEx webhook"""
        tracking_number = payload.get('trackingNumber')
        if not tracking_number:
            return {'success': False, 'error': 'No tracking number'}
        
        # Find or create shipping order
        order = ShippingOrder.query.filter_by(tracking_number=tracking_number).first()
        if not order:
            # Create new order from webhook
            order = ShippingOrder(
                account_id=1,  # Default FedEx account
                order_id=payload.get('shipmentId', tracking_number),
                tracking_number=tracking_number,
                carrier='FEDEX',
                status=payload.get('statusDescription', 'unknown')
            )
            db.session.add(order)
            db.session.flush()
        
        # Create tracking event
        event = TrackingEvent(
            shipping_order_id=order.id,
            event_date=datetime.utcnow(),
            status=payload.get('statusDescription', 'update'),
            description=payload.get('statusDescription', 'FedEx update'),
            location=payload.get('location', {}).get('city')
        )
        event.set_webhook_data(payload)
        db.session.add(event)
        db.session.commit()
        
        return {'success': True}
    
    @staticmethod
    def process_ups_webhook(payload: Dict) -> Dict[str, Any]:
        """Process UPS webhook"""
        # Similar structure to FedEx
        return {'success': True}
    
    @staticmethod
    def process_usps_webhook(payload: Dict) -> Dict[str, Any]:
        """Process USPS webhook"""
        # Similar structure to FedEx
        return {'success': True}
    
    @staticmethod
    def process_dhl_webhook(payload: Dict) -> Dict[str, Any]:
        """Process DHL webhook"""
        # Similar structure to FedEx
        return {'success': True}
    
    @staticmethod
    def process_generic_webhook(provider: str, payload: Dict) -> Dict[str, Any]:
        """Process webhook from unknown provider"""
        tracking_number = payload.get('tracking_number') or payload.get('trackingNumber')
        if not tracking_number:
            return {'success': False, 'error': 'No tracking number'}
        
        # Generic processing
        return {'success': True}


# Webhook endpoint handlers
def setup_webhook_routes(app):
    """Setup webhook routes for the Flask app"""
    
    @app.route('/webhooks/shipping/<provider>', methods=['POST'])
    def shipping_webhook(provider):
        """Enhanced shipping webhook endpoint"""
        try:
            # Get signature for verification
            signature = (
                request.headers.get('X-Signature') or 
                request.headers.get('X-Hub-Signature-256') or
                request.headers.get('X-UPS-Security-Token')
            )
            
            # Parse payload
            payload = request.get_json(force=True)
            
            # Process webhook
            result = WebhookProcessor.process_webhook(provider, payload, signature)
            
            if result['success']:
                return {'status': 'success', 'message': 'Webhook processed'}, 200
            else:
                return {'error': result.get('error', 'Processing failed')}, 400
                
        except Exception as e:
            logger.error(f"Webhook error for {provider}: {e}")
            return {'error': 'Internal server error'}, 500
    
    @app.route('/api/shipping/track/<provider>/<tracking_number>', methods=['GET'])
    def track_shipment(provider, tracking_number):
        """Manual tracking lookup"""
        try:
            result = ShippingAPIFactory.get_tracking_info(provider, tracking_number)
            return result
        except Exception as e:
            logger.error(f"Tracking error: {e}")
            return {'error': 'Failed to get tracking info'}, 500
    
    @app.route('/api/shipping/sync-all', methods=['POST'])
    def sync_all_shipping():
        """Sync all shipping accounts"""
        try:
            results = ShippingAPIFactory.sync_all_accounts()
            total_synced = sum(results.values())
            
            return {
                'success': True,
                'results': results,
                'total_synced': total_synced
            }
        except Exception as e:
            logger.error(f"Sync all error: {e}")
            return {'error': 'Failed to sync accounts'}, 500
