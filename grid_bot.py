"""
Volatility-Adaptive Grid Bot

This module implements a grid trading bot that dynamically adjusts its trading
intervals based on market volatility using ATR (Average True Range).
"""

import time
import threading
from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal


class GridOrder:
    """Represents a grid order (buy or sell)"""
    
    def __init__(self, order_type: str, price: float, amount: float):
        """
        Initialize a grid order
        
        Args:
            order_type: 'buy' or 'sell'
            price: Target price for the order
            amount: Amount to trade
        """
        self.order_type = order_type
        self.price = price
        self.amount = amount
        self.filled = False
        self.created_at = datetime.now()
        
    def __repr__(self):
        status = "FILLED" if self.filled else "OPEN"
        return f"GridOrder({self.order_type.upper()}, ${self.price:.2f}, {self.amount:.6f} BNB, {status})"


class VolatilityAdaptiveGridBot:
    """Grid bot that adapts trading intervals based on market volatility"""
    
    def __init__(self, atr_calculator, swap_manager, wallet_manager, 
                 main_wallet_address: str, base_interval: float = 5.0):
        """
        Initialize the Volatility-Adaptive Grid Bot
        
        Args:
            atr_calculator: ATRCalculator instance
            swap_manager: SwapManager instance for executing trades
            wallet_manager: WalletManager instance
            main_wallet_address: Address of the main wallet for trading
            base_interval: Base grid interval in dollars (default $5)
        """
        self.atr_calculator = atr_calculator
        self.swap_manager = swap_manager
        self.wallet_manager = wallet_manager
        self.main_wallet_address = main_wallet_address
        self.base_interval = base_interval
        
        self.active = False
        self.orders: List[GridOrder] = []
        self.position_bnb = 0.0  # Current BNB position
        self.position_usdt = 0.0  # Current USDT position
        self.trades_executed = 0
        self.total_profit = 0.0
        
        self.monitor_thread = None
        self.update_interval = 10  # Check orders every 10 seconds
        self.atr_update_frequency = 5  # Update ATR every 5 trades
        
    def initialize(self, quick_start: bool = False) -> bool:
        """
        Initialize the grid bot
        
        Args:
            quick_start: If True, use faster initialization for testing
            
        Returns:
            True if successful, False otherwise
        """
        print("\n🤖 Initializing Volatility-Adaptive Grid Bot...")
        
        # Initialize ATR calculator
        if not self.atr_calculator.initialize_history(quick_start):
            print("❌ Failed to initialize ATR calculator")
            return False
        
        # Get initial ATR summary
        summary = self.atr_calculator.get_atr_summary()
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return False
        
        print("\n📊 Initial Market Analysis:")
        print(f"   Current Price: ${summary['current_price']:.2f}")
        print(f"   ATR: ${summary['atr']:.2f} ({summary['atr_percentage']:.2f}%)")
        print(f"   Volatility: {summary['volatility_level'].upper()}")
        print(f"   Grid Interval: ${summary['recommended_grid_interval']:.2f}")
        
        # Set up initial grid
        current_price = summary['current_price']
        grid_interval = summary['recommended_grid_interval']
        
        # Create initial orders
        sell_price = current_price + grid_interval
        buy_price = current_price - grid_interval
        
        # Use small amounts for initial orders (can be configured)
        order_amount_bnb = 0.01  # 0.01 BNB per order
        
        self.orders = [
            GridOrder('sell', sell_price, order_amount_bnb),
            GridOrder('buy', buy_price, order_amount_bnb)
        ]
        
        print("\n🎯 Initial Grid Setup:")
        for order in self.orders:
            print(f"   {order}")
        
        print("\n✅ Grid Bot initialized successfully!")
        return True
    
    def start(self) -> bool:
        """
        Start the grid bot
        
        Returns:
            True if started successfully
        """
        if self.active:
            print("⚠️ Grid bot is already running")
            return False
        
        if not self.orders:
            print("❌ No orders configured. Initialize the bot first.")
            return False
        
        self.active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("🚀 Grid Bot started!")
        return True
    
    def stop(self) -> None:
        """Stop the grid bot"""
        if not self.active:
            print("⚠️ Grid bot is not running")
            return
        
        self.active = False
        print("⏹️ Grid Bot stopped!")
        
    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in separate thread)"""
        print("👀 Grid Bot monitoring active...")
        
        while self.active:
            try:
                self._check_orders()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"⚠️ Error in monitor loop: {e}")
                time.sleep(self.update_interval)
    
    def _check_orders(self) -> None:
        """Check if any orders should be filled"""
        current_price = self.atr_calculator.get_current_bnb_price()
        if current_price is None:
            return
        
        for order in self.orders:
            if order.filled:
                continue
            
            # Check if order should be filled
            if order.order_type == 'sell' and current_price >= order.price:
                self._execute_sell_order(order, current_price)
            elif order.order_type == 'buy' and current_price <= order.price:
                self._execute_buy_order(order, current_price)
    
    def _execute_sell_order(self, order: GridOrder, current_price: float) -> None:
        """
        Execute a sell order (BNB -> USDT)
        
        Args:
            order: The sell order to execute
            current_price: Current market price
        """
        print(f"\n💰 SELL ORDER TRIGGERED!")
        print(f"   Order: {order}")
        print(f"   Current Price: ${current_price:.2f}")
        
        # Mark order as filled
        order.filled = True
        self.trades_executed += 1
        
        # In a real implementation, this would execute the swap
        # For now, we'll simulate it
        usdt_received = order.amount * current_price
        self.position_bnb -= order.amount
        self.position_usdt += usdt_received
        
        print(f"   ✅ Sold {order.amount:.6f} BNB for ~${usdt_received:.2f} USDT")
        
        # Update ATR if needed
        if self.trades_executed % self.atr_update_frequency == 0:
            self._update_atr()
        
        # Reposition grid
        self._reposition_grid_after_sell(current_price)
    
    def _execute_buy_order(self, order: GridOrder, current_price: float) -> None:
        """
        Execute a buy order (USDT -> BNB)
        
        Args:
            order: The buy order to execute
            current_price: Current market price
        """
        print(f"\n💰 BUY ORDER TRIGGERED!")
        print(f"   Order: {order}")
        print(f"   Current Price: ${current_price:.2f}")
        
        # Mark order as filled
        order.filled = True
        self.trades_executed += 1
        
        # In a real implementation, this would execute the swap
        # For now, we'll simulate it
        usdt_spent = order.amount * current_price
        self.position_bnb += order.amount
        self.position_usdt -= usdt_spent
        
        print(f"   ✅ Bought {order.amount:.6f} BNB for ~${usdt_spent:.2f} USDT")
        
        # Update ATR if needed
        if self.trades_executed % self.atr_update_frequency == 0:
            self._update_atr()
        
        # Reposition grid
        self._reposition_grid_after_buy(current_price)
    
    def _update_atr(self) -> None:
        """Update ATR and display current metrics"""
        print("\n📊 Updating ATR...")
        self.atr_calculator.update_price_history(num_samples=1)
        
        summary = self.atr_calculator.get_atr_summary()
        if 'error' not in summary:
            print(f"   Current Price: ${summary['current_price']:.2f}")
            print(f"   ATR: ${summary['atr']:.2f} ({summary['atr_percentage']:.2f}%)")
            print(f"   Volatility: {summary['volatility_level'].upper()}")
            print(f"   Grid Interval: ${summary['recommended_grid_interval']:.2f}")
    
    def _reposition_grid_after_sell(self, current_price: float) -> None:
        """
        Reposition grid after a sell order is filled
        
        Args:
            current_price: Current market price
        """
        # Get updated grid interval based on current ATR
        summary = self.atr_calculator.get_atr_summary()
        if 'error' in summary:
            grid_interval = self.base_interval
        else:
            grid_interval = summary['recommended_grid_interval']
        
        # Place new sell order higher
        new_sell_price = current_price + grid_interval
        new_sell_order = GridOrder('sell', new_sell_price, 0.01)
        
        # Place new buy order below current price
        new_buy_price = current_price - grid_interval
        new_buy_order = GridOrder('buy', new_buy_price, 0.01)
        
        # Remove filled orders and add new ones
        self.orders = [o for o in self.orders if not o.filled]
        self.orders.extend([new_sell_order, new_buy_order])
        
        print(f"\n🔄 Grid Repositioned (after SELL):")
        print(f"   New Sell Order: ${new_sell_price:.2f}")
        print(f"   New Buy Order: ${new_buy_price:.2f}")
        print(f"   Grid Interval: ${grid_interval:.2f}")
    
    def _reposition_grid_after_buy(self, current_price: float) -> None:
        """
        Reposition grid after a buy order is filled
        
        Args:
            current_price: Current market price
        """
        # Get updated grid interval based on current ATR
        summary = self.atr_calculator.get_atr_summary()
        if 'error' in summary:
            grid_interval = self.base_interval
        else:
            grid_interval = summary['recommended_grid_interval']
        
        # Place new sell order above current price
        new_sell_price = current_price + grid_interval
        new_sell_order = GridOrder('sell', new_sell_price, 0.01)
        
        # Place new buy order lower
        new_buy_price = current_price - grid_interval
        new_buy_order = GridOrder('buy', new_buy_price, 0.01)
        
        # Remove filled orders and add new ones
        self.orders = [o for o in self.orders if not o.filled]
        self.orders.extend([new_sell_order, new_buy_order])
        
        print(f"\n🔄 Grid Repositioned (after BUY):")
        print(f"   New Sell Order: ${new_sell_price:.2f}")
        print(f"   New Buy Order: ${new_buy_price:.2f}")
        print(f"   Grid Interval: ${grid_interval:.2f}")
    
    def get_status(self) -> Dict:
        """
        Get current grid bot status
        
        Returns:
            Dictionary with bot status
        """
        active_orders = [o for o in self.orders if not o.filled]
        
        return {
            'active': self.active,
            'total_trades': self.trades_executed,
            'position_bnb': self.position_bnb,
            'position_usdt': self.position_usdt,
            'active_orders': len(active_orders),
            'total_orders': len(self.orders)
        }
    
    def display_status(self) -> None:
        """Display detailed grid bot status"""
        status = self.get_status()
        
        print("\n" + "=" * 80)
        print("📊 GRID BOT STATUS")
        print("=" * 80)
        print(f"Status: {'🟢 ACTIVE' if status['active'] else '🔴 STOPPED'}")
        print(f"Total Trades: {status['total_trades']}")
        print(f"Position BNB: {status['position_bnb']:.6f}")
        print(f"Position USDT: ${status['position_usdt']:.2f}")
        print(f"Active Orders: {status['active_orders']}/{status['total_orders']}")
        
        # Display current ATR info
        summary = self.atr_calculator.get_atr_summary()
        if 'error' not in summary:
            print(f"\n📈 Market Conditions:")
            print(f"   Price: ${summary['current_price']:.2f}")
            print(f"   ATR: ${summary['atr']:.2f} ({summary['atr_percentage']:.2f}%)")
            print(f"   Volatility: {summary['volatility_level'].upper()}")
            print(f"   Grid Interval: ${summary['recommended_grid_interval']:.2f}")
        
        # Display active orders
        active_orders = [o for o in self.orders if not o.filled]
        if active_orders:
            print(f"\n🎯 Active Orders:")
            for order in active_orders:
                print(f"   {order}")
        
        print("=" * 80)
