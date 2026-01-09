"""
ATR (Average True Range) Calculator for Volatility Measurement

This module fetches market data and calculates ATR to measure market volatility.
The ATR is used by the Grid Bot to dynamically adjust trading intervals.
"""

import time
from typing import List, Dict, Optional
import pandas as pd
from ta.volatility import AverageTrueRange


class ATRCalculator:
    """Calculate Average True Range (ATR) for volatility measurement"""
    
    def __init__(self, router_contract, web3, wbnb_address: str, usdt_address: str):
        """
        Initialize ATR Calculator
        
        Args:
            router_contract: PancakeSwap router contract instance
            web3: Web3 instance
            wbnb_address: WBNB token address
            usdt_address: USDT token address
        """
        self.router_contract = router_contract
        self.web3 = web3
        self.wbnb_address = wbnb_address
        self.usdt_address = usdt_address
        self.price_history = []
        self.atr_period = 14  # Standard ATR period
        
    def get_current_bnb_price(self) -> Optional[float]:
        """
        Get current BNB/USDT price from PancakeSwap
        
        Returns:
            Current BNB price in USDT, or None if error
        """
        try:
            # Get price for 1 BNB in USDT
            one_bnb = int(1e18)  # 1 BNB in wei
            path = [self.wbnb_address, self.usdt_address]
            amounts = self.router_contract.functions.getAmountsOut(one_bnb, path).call()
            usdt_amount = amounts[1] / 1e18
            return usdt_amount
        except Exception as e:
            print(f"⚠️ Error getting BNB price: {e}")
            return None
    
    def fetch_price_data(self, interval_seconds: int = 60, num_candles: int = 20) -> List[Dict]:
        """
        Fetch historical price data by sampling current prices
        
        Args:
            interval_seconds: Time between price samples in seconds
            num_candles: Number of price candles to collect
            
        Returns:
            List of price candles with high, low, close
        """
        print(f"📊 Collecting {num_candles} price samples (interval: {interval_seconds}s)...")
        candles = []
        
        for i in range(num_candles):
            price = self.get_current_bnb_price()
            if price is None:
                print(f"⚠️ Failed to get price at sample {i+1}")
                continue
                
            # For simplicity, use the same price for high, low, close
            # In a real implementation, you'd track actual high/low during the interval
            candle = {
                'timestamp': int(time.time()),
                'high': price,
                'low': price,
                'close': price
            }
            candles.append(candle)
            
            print(f"  Sample {i+1}/{num_candles}: ${price:.2f}")
            
            if i < num_candles - 1:  # Don't sleep after last sample
                time.sleep(interval_seconds)
        
        return candles
    
    def update_price_history(self, num_samples: int = 1) -> None:
        """
        Update price history with new samples
        
        Args:
            num_samples: Number of new samples to add
        """
        for _ in range(num_samples):
            price = self.get_current_bnb_price()
            if price is not None:
                candle = {
                    'timestamp': int(time.time()),
                    'high': price,
                    'low': price,
                    'close': price
                }
                self.price_history.append(candle)
                
                # Keep only the last 100 candles to avoid memory issues
                if len(self.price_history) > 100:
                    self.price_history = self.price_history[-100:]
    
    def calculate_atr(self, candles: Optional[List[Dict]] = None) -> Optional[float]:
        """
        Calculate Average True Range (ATR) from price candles
        
        Args:
            candles: List of price candles, or None to use stored history
            
        Returns:
            ATR value, or None if insufficient data
        """
        if candles is None:
            candles = self.price_history
            
        if len(candles) < self.atr_period:
            print(f"⚠️ Insufficient data for ATR calculation. Need {self.atr_period}, have {len(candles)}")
            return None
        
        try:
            # Convert to DataFrame for ta library
            df = pd.DataFrame(candles)
            
            # ta library requires high, low, close columns
            atr_indicator = AverageTrueRange(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=self.atr_period
            )
            
            atr_values = atr_indicator.average_true_range()
            current_atr = atr_values.iloc[-1]
            
            return float(current_atr)
            
        except Exception as e:
            print(f"❌ Error calculating ATR: {e}")
            return None
    
    def get_volatility_level(self, atr: float, current_price: float) -> str:
        """
        Determine volatility level based on ATR
        
        Args:
            atr: Average True Range value
            current_price: Current asset price
            
        Returns:
            Volatility level: 'low', 'medium', or 'high'
        """
        # Calculate ATR as percentage of price
        atr_percentage = (atr / current_price) * 100
        
        # Define thresholds
        # Low volatility: < 1% ATR
        # Medium volatility: 1% - 2.5% ATR
        # High volatility: > 2.5% ATR
        
        if atr_percentage < 1.0:
            return 'low'
        elif atr_percentage < 2.5:
            return 'medium'
        else:
            return 'high'
    
    def get_grid_interval(self, atr: float, current_price: float, 
                         base_interval: float = 5.0) -> float:
        """
        Calculate dynamic grid interval based on ATR
        
        Args:
            atr: Average True Range value
            current_price: Current asset price
            base_interval: Base interval in dollars (default $5)
            
        Returns:
            Adjusted grid interval in dollars
        """
        volatility = self.get_volatility_level(atr, current_price)
        
        if volatility == 'low':
            # Calm market: tighter intervals (60% of base)
            interval = base_interval * 0.6
        elif volatility == 'medium':
            # Normal market: use base interval
            interval = base_interval
        else:
            # Volatile market: wider intervals (160% of base)
            interval = base_interval * 1.6
        
        return round(interval, 2)
    
    def initialize_history(self, quick_start: bool = False) -> bool:
        """
        Initialize price history for ATR calculation
        
        Args:
            quick_start: If True, use faster sampling for testing (5s intervals)
            
        Returns:
            True if successful, False otherwise
        """
        print("\n🔧 Initializing ATR Calculator...")
        
        if quick_start:
            # Quick start for testing: 5 second intervals, 14 samples
            interval = 5
            num_samples = self.atr_period
            print(f"⚡ Quick start mode: {interval}s intervals")
        else:
            # Production mode: 60 second intervals, 20 samples
            interval = 60
            num_samples = 20
            print(f"📊 Production mode: {interval}s intervals")
        
        candles = self.fetch_price_data(interval, num_samples)
        
        if len(candles) < self.atr_period:
            print(f"❌ Failed to collect enough price data")
            return False
        
        self.price_history = candles
        print(f"✅ Initialized with {len(candles)} price samples")
        return True
    
    def get_atr_summary(self) -> Dict:
        """
        Get current ATR summary with all relevant metrics
        
        Returns:
            Dictionary with ATR metrics
        """
        current_price = self.get_current_bnb_price()
        if current_price is None:
            return {'error': 'Failed to get current price'}
        
        atr = self.calculate_atr()
        if atr is None:
            return {'error': 'Insufficient data for ATR calculation'}
        
        volatility = self.get_volatility_level(atr, current_price)
        grid_interval = self.get_grid_interval(atr, current_price)
        atr_percentage = (atr / current_price) * 100
        
        return {
            'current_price': current_price,
            'atr': atr,
            'atr_percentage': atr_percentage,
            'volatility_level': volatility,
            'recommended_grid_interval': grid_interval,
            'samples': len(self.price_history)
        }
