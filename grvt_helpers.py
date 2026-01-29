"""
GRVT Helper Functions
ฟังก์ชันช่วยเหลือสำหรับ Jupyter Notebooks การสอน GRVT Trading

ใช้สำหรับลดความซับซ้อนของโค้ดใน notebooks เพื่อให้นักเรียนมองเห็นแนวคิดหลักได้ชัดเจน
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_typed_data

# Try to import pysdk (should be installed in env via pip)
try:
    from pysdk.grvt_ccxt import GrvtCcxt
    from pysdk.grvt_ccxt_env import GrvtEnv
    PYSDK_AVAILABLE = True
except ImportError:
    PYSDK_AVAILABLE = False
    print("⚠️ Warning: pysdk not found.")
    print("💡 แก้ไข:")
    print("   1. เปิดใช้งาน virtual environment: env\\Scripts\\activate")
    print("   2. ติดตั้ง pysdk: pip install git+https://github.com/gravity-technologies/grvt-pysdk.git")
    print("   3. เลือก Jupyter kernel ที่ถูกต้อง (.\env\Scripts\python.exe)")



# ============================================================================
# Configuration & Environment
# ============================================================================

def load_grvt_config(env_file: str = '.env') -> Dict[str, str]:
    """
    โหลด configuration จากไฟล์ .env
    
    Args:
        env_file: ชื่อไฟล์ .env (default: '.env')
    
    Returns:
        Dictionary ของ configuration values
    """
    load_dotenv(env_file)
    
    config = {
        'GRVT_ENV': os.getenv('GRVT_ENV', 'testnet'),
        'GRVT_API_KEY': os.getenv('GRVT_API_KEY', ''),
        # Note: GRVT ไม่ใช้ API_SECRET แบบ exchange ทั่วไป
        # ใช้ PRIVATE_KEY สำหรับ EIP-712 signing แทน
        'GRVT_PRIVATE_KEY': os.getenv('GRVT_PRIVATE_KEY', ''),
        'GRVT_TRADING_ACCOUNT_ID': os.getenv('GRVT_TRADING_ACCOUNT_ID', ''),
        'GRVT_SUB_ACCOUNT_ID': os.getenv('GRVT_SUB_ACCOUNT_ID', '0'),
    }
    
    return config


def validate_config(config: Dict[str, str]) -> tuple[bool, List[str]]:
    """
    ตรวจสอบว่า configuration ครบถ้วนหรือไม่
    
    Args:
        config: Configuration dictionary
    
    Returns:
        (is_valid, missing_fields)
    """
    required_fields = [
        'GRVT_API_KEY',
        'GRVT_PRIVATE_KEY',
        'GRVT_TRADING_ACCOUNT_ID',
    ]
    
    missing = []
    for field in required_fields:
        if not config.get(field) or config[field] == '':
            missing.append(field)
    
    return (len(missing) == 0, missing)


# ============================================================================
# GRVT Client Connection
# ============================================================================

def connect_to_grvt(config: Dict[str, str], logger: Optional[logging.Logger] = None) -> Optional[Any]:
    """
    สร้างการเชื่อมต่อกับ GRVT Exchange
    
    Args:
        config: Configuration dictionary
        logger: Logger instance (optional)
    
    Returns:
        GrvtCcxt client instance หรือ None ถ้าเชื่อมต่อไม่สำเร็จ
    """
    if not PYSDK_AVAILABLE:
        print("❌ Error: pysdk not available")
        return None
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        env = GrvtEnv(config['GRVT_ENV'])
        params = {
            "api_key": config['GRVT_API_KEY'],
            "trading_account_id": config['GRVT_TRADING_ACCOUNT_ID'],
            "private_key": config['GRVT_PRIVATE_KEY'],
        }
        
        client = GrvtCcxt(env, logger, parameters=params)
        print(f"✅ เชื่อมต่อกับ GRVT {config['GRVT_ENV']} สำเร็จ!")
        return client
        
    except Exception as e:
        print(f"❌ Error: ไม่สามารถเชื่อมต่อกับ GRVT: {e}")
        return None


# ============================================================================
# EIP-712 Signing
# ============================================================================

def create_eip712_domain(chain_id: int = 1) -> Dict:
    """
    สร้าง EIP-712 Domain สำหรับ GRVT
    
    Args:
        chain_id: Chain ID (default: 1 for mainnet)
    
    Returns:
        EIP-712 domain dictionary
    """
    return {
        'name': 'GRVT',
        'version': '1',
        'chainId': chain_id,
    }


def sign_order_eip712(private_key: str, order_data: Dict) -> Dict[str, str]:
    """
    ลงนามคำสั่ง order ด้วย EIP-712
    
    Args:
        private_key: Private key (ต้องขึ้นต้นด้วย 0x)
        order_data: ข้อมูล order ที่ต้องการลงนาม
    
    Returns:
        Dictionary ที่มี signature components (r, s, v)
    """
    # ตรวจสอบ private key format
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    # สร้าง account จาก private key
    account = Account.from_key(private_key)
    
    # สร้าง typed data structure
    typed_data = {
        'types': {
            'EIP712Domain': [
                {'name': 'name', 'type': 'string'},
                {'name': 'version', 'type': 'string'},
                {'name': 'chainId', 'type': 'uint256'},
            ],
            'Order': [
                {'name': 'symbol', 'type': 'string'},
                {'name': 'side', 'type': 'string'},
                {'name': 'amount', 'type': 'uint256'},
                {'name': 'price', 'type': 'uint256'},
                {'name': 'nonce', 'type': 'uint256'},
            ]
        },
        'primaryType': 'Order',
        'domain': create_eip712_domain(order_data.get('chain_id', 1)),
        'message': order_data
    }
    
    # Encode และ Sign
    encoded_data = encode_typed_data(typed_data)
    signature = account.sign_message(encoded_data)
    
    return {
        'r': hex(signature.r),
        's': hex(signature.s),
        'v': signature.v,
        'signature': signature.signature.hex(),
        'signer': account.address
    }


# ============================================================================
# Formatting & Display
# ============================================================================

def format_currency(value, decimals: int = 2, symbol: str = '$') -> str:
    """
    Format ตัวเลขเป็นรูปแบบสกุลเงิน
    
    Args:
        value: จำนวนเงิน (รับได้ทั้ง float, int, และ string)
        decimals: ทศนิยม (default: 2)
        symbol: สัญลักษณ์สกุลเงิน (default: '$')
    
    Returns:
        String ที่ format แล้ว เช่น "$1,234.56"
    """
    # Convert to float if string
    try:
        value = float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        value = 0.0
    
    if value >= 0:
        return f"{symbol}{value:,.{decimals}f}"
    else:
        return f"-{symbol}{abs(value):,.{decimals}f}"


def format_percentage(value, decimals: int = 2) -> str:
    """
    Format ตัวเลขเป็นเปอร์เซ็นต์
    
    Args:
        value: ค่าเปอร์เซ็นต์ (เช่น 5.67 = 5.67%, รับได้ทั้ง float และ string)
        decimals: ทศนิยม (default: 2)
    
    Returns:
        String ที่ format แล้ว เช่น "+5.67%" หรือ "-2.34%"
    """
    # Convert to float if string
    try:
        value = float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        value = 0.0
    
    sign = '+' if value >= 0 else ''
    return f"{sign}{value:.{decimals}f}%"


def create_account_table(account_data: Dict, positions: List[Dict] = None) -> pd.DataFrame:
    """
    สร้างตารางแสดงข้อมูล Account
    
    Args:
        account_data: ข้อมูล account จาก fetch_balance()
        positions: ข้อมูล positions (optional)
    
    Returns:
        pandas DataFrame
    """
    # Helper to safely get and convert to float
    def safe_get_float(d, *keys, default=0.0):
        val = d
        for key in keys:
            val = val.get(key, {}) if isinstance(val, dict) else default
        try:
            return float(val) if val not in (None, {}, '') else default
        except (ValueError, TypeError):
            return default
    
    # Extract balance info
    summary_data = {
        'Metric': ['Total Equity', 'Available Balance', 'Used Margin', 'Unrealized P&L'],
        'Value': [
            format_currency(safe_get_float(account_data, 'total', 'USDT')),
            format_currency(safe_get_float(account_data, 'free', 'USDT')),
            format_currency(safe_get_float(account_data, 'used', 'USDT')),
            format_currency(safe_get_float(account_data, 'info', 'unrealized_pnl'))
        ]
    }
    
    return pd.DataFrame(summary_data)


def create_positions_table(positions: List[Dict]) -> pd.DataFrame:
    """
    สร้างตารางแสดง Positions
    
    Args:
        positions: รายการ positions จาก fetch_positions()
    
    Returns:
        pandas DataFrame
    """
    if not positions:
        return pd.DataFrame(columns=['Symbol', 'Side', 'Size', 'Entry Price', 'Mark Price', 'Unrealized P&L'])
    
    # Helper to safely convert to float
    def safe_float(value, default=0.0):
        try:
            return float(value) if value not in (None, '', 'N/A') else default
        except (ValueError, TypeError):
            return default
    
    data = []
    for pos in positions:
        # GRVT uses 'size' instead of 'contracts'
        size = safe_float(pos.get('size', 0))
        if size != 0:  # แสดงเฉพาะที่มี position
            data.append({
                'Symbol': pos.get('instrument', 'N/A'),  # GRVT uses 'instrument'
                'Side': 'LONG' if size > 0 else 'SHORT',
                'Size': abs(size),
                'Entry Price': format_currency(safe_float(pos.get('entry_price', 0))),
                'Mark Price': format_currency(safe_float(pos.get('mark_price', 0))),
                'Unrealized P&L': format_currency(safe_float(pos.get('unrealized_pnl', 0)))
            })
    
    return pd.DataFrame(data)


def round_to_tick_size(price: float, tick_size: float = 0.5) -> float:
    """
    Round price ให้ตรงกับ tick size ของ GRVT
    
    Args:
        price: ราคาที่ต้องการ round
        tick_size: ขนาด tick (default: 0.5 สำหรับ BTC)
    
    Returns:
        ราคาที่ round แล้วตรงกับ tick size
    
    Examples:
        >>> round_to_tick_size(86486.17, 0.5)
        86486.0
        >>> round_to_tick_size(86486.37, 0.5)
        86486.5
        >>> round_to_tick_size(86486.17, 1.0)
        86486.0
    """
    return round(price / tick_size) * tick_size


def validate_tpsl_prices(
    side: str,
    last_price: float,
    take_profit_price: float = None,
    stop_loss_price: float = None
) -> tuple[bool, str]:
    """
    Validate TP/SL prices according to GRVT rules
    
    Rules:
    - For LONG (sell): TP > last_price, SL < last_price
    - For SHORT (buy): TP < last_price, SL > last_price
    
    Args:
        side: 'buy' or 'sell'
        last_price: Current market price
        take_profit_price: TP price (optional)
        stop_loss_price: SL price (optional)
    
    Returns:
        (is_valid, error_message)
    """
    if not take_profit_price and not stop_loss_price:
        return True, ""
    
    is_long = side.lower() == 'sell'  # Long position = sell to close
    
    # Validate TP
    if take_profit_price:
        if is_long:
            # Long: TP must be higher than current price
            if take_profit_price <= last_price:
                return False, f"TP for LONG must be > last price (${last_price:.2f})"
        else:
            # Short: TP must be lower than current price
            if take_profit_price >= last_price:
                return False, f"TP for SHORT must be < last price (${last_price:.2f})"
    
    # Validate SL
    if stop_loss_price:
        if is_long:
            # Long: SL must be lower than current price
            if stop_loss_price >= last_price:
                return False, f"SL for LONG must be < last price (${last_price:.2f})"
        else:
            # Short: SL must be higher than current price
            if stop_loss_price <= last_price:
                return False, f"SL for SHORT must be > last price (${last_price:.2f})"
    
    return True, ""


def create_tpsl_params(
    side: str,
    take_profit_price: float = None,
    stop_loss_price: float = None,
    trigger_by: str = 'LAST_PRICE',
    close_position: bool = True,
    tick_size: float = 0.5
) -> dict:
    """
    Create TP/SL params for GRVT order
    
    Args:
        side: 'buy' or 'sell' - direction of the CLOSING order
        take_profit_price: TP trigger price (optional)
        stop_loss_price: SL trigger price (optional)
        trigger_by: 'LAST_PRICE', 'INDEX_PRICE', or 'MARK_PRICE'
        close_position: Whether to close entire position
        tick_size: Price tick size for rounding
    
    Returns:
        dict with trigger params, or empty dict if no TP/SL
        
    Examples:
        >>> # Long position (will sell to close)
        >>> create_tpsl_params('sell', take_profit_price=95000)
        {'trigger': {'trigger_type': 'TAKE_PROFIT', 'tpsl': {...}}}
        
        >>> # Short position (will buy to close)
        >>> create_tpsl_params('buy', stop_loss_price=91000)
        {'trigger': {'trigger_type': 'STOP_LOSS', 'tpsl': {...}}}
    """
    params = {}
    
    # Round prices to tick size
    if take_profit_price:
        take_profit_price = round_to_tick_size(take_profit_price, tick_size)
    if stop_loss_price:
        stop_loss_price = round_to_tick_size(stop_loss_price, tick_size)
    
    # Create TP params
    if take_profit_price:
        params['take_profit'] = {
            'trigger': {
                'trigger_type': 'TAKE_PROFIT',
                'tpsl': {
                    'trigger_price': str(take_profit_price),
                    'trigger_by': trigger_by,
                    'close_position': close_position
                }
            }
        }
    
    # Create SL params
    if stop_loss_price:
        params['stop_loss'] = {
            'trigger': {
                'trigger_type': 'STOP_LOSS',
                'tpsl': {
                    'trigger_price': str(stop_loss_price),
                    'trigger_by': trigger_by,
                    'close_position': close_position
                }
            }
        }
    
    return params



# ============================================================================
# Emergency Functions
# ============================================================================

def emergency_cancel_all(client: Any) -> int:
    """
    🚨 ยกเลิก Orders ทั้งหมด
    
    Args:
        client: GRVT client instance
    
    Returns:
        จำนวน orders ที่ถูกยกเลิก
    """
    try:
        open_orders = client.fetch_open_orders()
        count = 0
        
        for order in open_orders:
            try:
                client.cancel_order(order['id'])
                count += 1
                print(f"✅ ยกเลิก Order: {order['id']}")
            except Exception as e:
                print(f"❌ ไม่สามารถยกเลิก Order {order['id']}: {e}")
        
        print(f"\n🟢 ยกเลิก {count} orders สำเร็จ")
        return count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


def emergency_close_all(client: Any, symbols: List[str] = None) -> int:
    """
    🚨 ปิด Positions ทั้งหมด
    
    Args:
        client: GRVT client instance
        symbols: รายการ symbols ที่ต้องการปิด (None = ทั้งหมด)
    
    Returns:
        จำนวน positions ที่ปิด
    """
    try:
        positions = client.fetch_positions(symbols)
        count = 0
        
        for pos in positions:
            contracts = pos.get('contracts', 0)
            if contracts != 0:
                symbol = pos['symbol']
                side = 'sell' if contracts > 0 else 'buy'
                amount = abs(contracts)
                
                try:
                    client.create_order(
                        symbol=symbol,
                        order_type='market',
                        side=side,
                        amount=amount
                    )
                    count += 1
                    print(f"✅ ปิด Position: {symbol} ({contracts} contracts)")
                except Exception as e:
                    print(f"❌ ไม่สามารถปิด Position {symbol}: {e}")
        
        print(f"\n🟢 ปิด {count} positions สำเร็จ")
        return count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """
    Rate Limiter สำหรับควบคุมความถี่ในการส่ง orders
    GRVT: 200 orders per 10 seconds
    """
    
    def __init__(self, max_requests: int = 200, time_window: int = 10):
        """
        Args:
            max_requests: จำนวน requests สูงสุด
            time_window: ช่วงเวลา (วินาที)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """ตรวจสอบว่าสามารถส่ง request ได้หรือไม่"""
        now = datetime.now()
        
        # ลบ requests ที่เก่าเกินกว่า time window
        self.requests = [
            req_time for req_time in self.requests
            if (now - req_time).total_seconds() < self.time_window
        ]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """บันทึก request ใหม่"""
        self.requests.append(datetime.now())
    
    def wait_if_needed(self):
        """รอถ้าเกิน rate limit"""
        if not self.can_make_request():
            # คำนวณเวลาที่ต้องรอ
            oldest_request = min(self.requests)
            wait_time = self.time_window - (datetime.now() - oldest_request).total_seconds()
            
            if wait_time > 0:
                print(f"⏳ Rate limit exceeded. รอ {wait_time:.2f} วินาที...")
                import time
                time.sleep(wait_time + 0.1)  # เผื่อเวลาเล็กน้อย


# ============================================================================
# Utilities
# ============================================================================

def print_section_header(title: str):
    """พิมพ์หัวข้อแบบสวยงาม"""
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def check_pysdk_availability() -> bool:
    """ตรวจสอบว่า pysdk พร้อมใช้งานหรือไม่"""
    if PYSDK_AVAILABLE:
        print("✅ pysdk พร้อมใช้งาน")
        return True
    else:
        print("❌ pysdk ไม่พร้อมใช้งาน")
        print(f"💡 ตรวจสอบว่า path {PYSDK_PATH} มีอยู่หรือไม่")
        return False


def get_account_public_address(private_key: str) -> str:
    """
    ดึง public address จาก private key
    
    Args:
        private_key: Private key (ต้องขึ้นต้นด้วย 0x)
    
    Returns:
        Public address (Ethereum format)
    """
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    account = Account.from_key(private_key)
    return account.address


# ============================================================================
# Test & Verification
# ============================================================================

def run_preflight_checks(config: Dict[str, str]) -> Dict[str, bool]:
    """
    รัน pre-flight checks ก่อนใช้งานบอท
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Dictionary ของผลการตรวจสอบ
    """
    results = {}
    
    print_section_header("🔍 Pre-flight Checks")
    
    # Check 1: pysdk availability
    results['pysdk'] = check_pysdk_availability()
    
    # Check 2: Configuration validity
    is_valid, missing = validate_config(config)
    results['config'] = is_valid
    if not is_valid:
        print(f"❌ Configuration ไม่ครบ: {', '.join(missing)}")
    else:
        print("✅ Configuration ครบถ้วน")
    
    # Check 3: Private key format
    private_key = config.get('GRVT_PRIVATE_KEY', '')
    if private_key and private_key.startswith('0x') and len(private_key) == 66:
        results['private_key_format'] = True
        print("✅ Private key format ถูกต้อง")
        print(f"   Public Address: {get_account_public_address(private_key)}")
    else:
        results['private_key_format'] = False
        print("❌ Private key format ไม่ถูกต้อง")
    
    # Summary
    print_section_header("📊 Summary")
    all_passed = all(results.values())
    if all_passed:
        print("🟢 All checks passed! พร้อมใช้งาน")
    else:
        print("🔴 Some checks failed. กรุณาแก้ไขปัญหาก่อนใช้งาน")
    
    return results


def emergency_cancel_all(client):
    """
    ฟังก์ชันฉุกเฉิน: ยกเลิก orders ทั้งหมด
    
    Args:
        client: GRVT client instance
    
    Returns:
        int: จำนวน orders ที่ยกเลิกสำเร็จ
    """
    try:
        open_orders = client.fetch_open_orders()
        count = 0
        
        if not open_orders:
            print("ℹ️ ไม่มี open orders")
            return 0
        
        print(f"📋 พบ {len(open_orders)} open order(s)")
        
        for order in open_orders:
            try:
                # ใช้ 'order_id' ตาม GRVT structure
                order_id = order.get('order_id', order.get('id'))
                
                if not order_id:
                    print(f"⚠️ ข้าม order ที่ไม่มี order_id: {order}")
                    continue
                
                # Get symbol for logging
                legs = order.get('legs', [])
                if legs:
                    symbol = legs[0].get('instrument', 'N/A')
                    is_buying = legs[0].get('is_buying_asset', True)
                    side = 'BUY' if is_buying else 'SELL'
                else:
                    symbol = order.get('symbol', 'N/A')
                    side = order.get('side', 'N/A').upper()
                
                emoji = "🟢" if side == "BUY" else "🔴"
                
                print(f"  ❌ Cancelling: {emoji} {symbol} - {side} (Order ID: {str(order_id)[:20]}...)")
                
                result = client.cancel_order(order_id)
                
                # เช็คว่าสำเร็จหรือไม่
                if result is False or result is None or (isinstance(result, dict) and not result):
                    print(f"     ⚠️ Failed to cancel")
                else:
                    count += 1
                    print(f"     ✅ Cancelled")
                    
            except Exception as e:
                print(f"  ⚠️ Error cancelling order: {e}")
                continue
        
        return count
        
    except Exception as e:
        print(f"❌ Error in emergency_cancel_all: {e}")
        import traceback
        traceback.print_exc()
        return 0


def emergency_close_all(client):
    """
    ฟังก์ชันฉุกเฉิน: ปิด positions ทั้งหมดด้วย market orders
    
    Args:
        client: GRVT client instance
    
    Returns:
        int: จำนวน positions ที่ปิดสำเร็จ
    """
    try:
        positions = client.fetch_positions()
        count = 0
        
        # Filter non-zero positions
        active_positions = [p for p in positions if safe_float(p.get('size', 0)) != 0]
        
        if not active_positions:
            print("ℹ️ ไม่มี open positions")
            return 0
        
        print(f"📊 พบ {len(active_positions)} open position(s)")
        
        for pos in active_positions:
            try:
                # Parse GRVT position structure
                legs = pos.get('legs', [])
                if legs:
                    leg = legs[0]
                    symbol = leg.get('instrument', 'N/A')
                    size = safe_float(leg.get('size', 0))
                else:
                    symbol = pos.get('symbol', pos.get('instrument', 'N/A'))
                    size = safe_float(pos.get('size', 0))
                
                if size == 0:
                    continue
                
                # กำหนด side ตรงข้าม
                is_long = size > 0
                side = 'sell' if is_long else 'buy'
                amount = abs(size)
                
                emoji = "🟢" if is_long else "🔴"
                position_type = "LONG" if is_long else "SHORT"
                
                print(f"  🚪 Closing: {emoji} {symbol} - {position_type} ({amount:.4f})")
                
                # ส่ง market order เพื่อปิด position
                order = client.create_order(
                    symbol=symbol,
                    order_type='market',
                    side=side,
                    amount=amount,
                    params={
                        'sub_account_id': client.config.get('GRVT_SUB_ACCOUNT_ID'),
                        'reduce_only': True  # ปิด position เท่านั้น
                    }
                )
                
                if order is None or (isinstance(order, dict) and not order):
                    print(f"     ⚠️ Failed to close")
                else:
                    count += 1
                    print(f"     ✅ Closed")
                    
            except Exception as e:
                print(f"  ⚠️ Error closing position: {e}")
                continue
        
        return count
        
    except Exception as e:
        print(f"❌ Error in emergency_close_all: {e}")
        import traceback
        traceback.print_exc()
        return 0



    # ทดสอบ helper functions
    print("🧪 Testing GRVT Helper Functions...")
    
    config = load_grvt_config()
    results = run_preflight_checks(config)
    
    print("\n✅ Helper functions module loaded successfully!")
