#!/usr/bin/env python3
"""
Grid Bot Demo Script

This script demonstrates the Grid Bot functionality without requiring
a live blockchain connection. It uses mocked price data to show how
the bot adapts to different market conditions.
"""

import time
from unittest.mock import Mock
from atr_calculator import ATRCalculator
from grid_bot import VolatilityAdaptiveGridBot


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_atr_calculation():
    """Demo: ATR calculation with different volatility scenarios"""
    print_section("DEMO 1: ATR Calculation & Volatility Detection")
    
    # Create mock objects
    mock_router = Mock()
    mock_web3 = Mock()
    
    calculator = ATRCalculator(mock_router, mock_web3, "0xWBNB", "0xUSDT")
    
    # Scenario 1: Low Volatility
    print("\n📊 Scenario 1: Low Volatility Market")
    print("   Simulating: Stable price around $600, small fluctuations")
    
    low_vol_price = 600.0
    low_vol_atr = 4.0  # $4 ATR = 0.67% of price
    
    volatility = calculator.get_volatility_level(low_vol_atr, low_vol_price)
    interval = calculator.get_grid_interval(low_vol_atr, low_vol_price)
    
    print(f"   Price: ${low_vol_price:.2f}")
    print(f"   ATR: ${low_vol_atr:.2f} ({(low_vol_atr/low_vol_price)*100:.2f}%)")
    print(f"   Volatility Level: {volatility.upper()}")
    print(f"   Grid Interval: ${interval:.2f} (60% of base)")
    print(f"   ✅ Tighter intervals for more frequent trades")
    
    # Scenario 2: Medium Volatility
    print("\n📊 Scenario 2: Medium Volatility Market")
    print("   Simulating: Normal market conditions")
    
    med_vol_price = 600.0
    med_vol_atr = 10.0  # $10 ATR = 1.67% of price
    
    volatility = calculator.get_volatility_level(med_vol_atr, med_vol_price)
    interval = calculator.get_grid_interval(med_vol_atr, med_vol_price)
    
    print(f"   Price: ${med_vol_price:.2f}")
    print(f"   ATR: ${med_vol_atr:.2f} ({(med_vol_atr/med_vol_price)*100:.2f}%)")
    print(f"   Volatility Level: {volatility.upper()}")
    print(f"   Grid Interval: ${interval:.2f} (100% of base)")
    print(f"   ✅ Standard intervals for balanced trading")
    
    # Scenario 3: High Volatility
    print("\n📊 Scenario 3: High Volatility Market")
    print("   Simulating: Volatile market with large price swings")
    
    high_vol_price = 600.0
    high_vol_atr = 20.0  # $20 ATR = 3.33% of price
    
    volatility = calculator.get_volatility_level(high_vol_atr, high_vol_price)
    interval = calculator.get_grid_interval(high_vol_atr, high_vol_price)
    
    print(f"   Price: ${high_vol_price:.2f}")
    print(f"   ATR: ${high_vol_atr:.2f} ({(high_vol_atr/high_vol_price)*100:.2f}%)")
    print(f"   Volatility Level: {volatility.upper()}")
    print(f"   Grid Interval: ${interval:.2f} (160% of base)")
    print(f"   ✅ Wider intervals to avoid whipsaw losses")


def demo_grid_repositioning():
    """Demo: Grid order placement and repositioning"""
    print_section("DEMO 2: Grid Order Placement & Repositioning")
    
    # Create mocked components
    mock_atr_calc = Mock()
    mock_swap_mgr = Mock()
    mock_wallet_mgr = Mock()
    
    # Initialize bot
    bot = VolatilityAdaptiveGridBot(
        mock_atr_calc,
        mock_swap_mgr,
        mock_wallet_mgr,
        "0xMainWallet",
        base_interval=5.0
    )
    
    # Mock ATR responses
    mock_atr_calc.initialize_history.return_value = True
    mock_atr_calc.get_atr_summary.return_value = {
        'current_price': 600.0,
        'atr': 10.0,
        'atr_percentage': 1.67,
        'volatility_level': 'medium',
        'recommended_grid_interval': 5.0,
        'samples': 20
    }
    
    # Initialize bot
    print("\n🔧 Initializing Grid Bot...")
    bot.initialize(quick_start=True)
    
    print("\n📊 Initial Grid Configuration:")
    status = bot.get_status()
    print(f"   Active Orders: {status['active_orders']}")
    print(f"   Position BNB: {status['position_bnb']:.6f}")
    print(f"   Position USDT: ${status['position_usdt']:.2f}")
    
    print("\n🎯 Initial Orders:")
    for order in bot.orders:
        print(f"   {order}")
    
    # Simulate price increase - sell order triggered
    print("\n📈 SIMULATION: Price increases to $605")
    print("   Triggering SELL order...")
    
    mock_atr_calc.get_atr_summary.return_value['current_price'] = 605.0
    sell_order = [o for o in bot.orders if o.order_type == 'sell'][0]
    bot._execute_sell_order(sell_order, 605.0)
    
    print("\n📊 Updated Position:")
    status = bot.get_status()
    print(f"   Position BNB: {status['position_bnb']:.6f} (sold BNB)")
    print(f"   Position USDT: ${status['position_usdt']:.2f} (received USDT)")
    print(f"   Total Trades: {status['total_trades']}")
    
    print("\n🎯 New Orders (Grid Repositioned):")
    active_orders = [o for o in bot.orders if not o.filled]
    for order in active_orders[:2]:  # Show first 2
        print(f"   {order}")
    
    # Simulate price decrease - buy order triggered
    print("\n📉 SIMULATION: Price decreases to $595")
    print("   Triggering BUY order...")
    
    mock_atr_calc.get_atr_summary.return_value['current_price'] = 595.0
    buy_order = [o for o in bot.orders if o.order_type == 'buy' and not o.filled][0]
    bot._execute_buy_order(buy_order, 595.0)
    
    print("\n📊 Updated Position:")
    status = bot.get_status()
    print(f"   Position BNB: {status['position_bnb']:.6f} (bought BNB)")
    print(f"   Position USDT: ${status['position_usdt']:.2f} (spent USDT)")
    print(f"   Total Trades: {status['total_trades']}")
    
    print("\n✅ Grid successfully adapts to price movements!")


def demo_volatility_adaptation():
    """Demo: How grid adapts to changing volatility"""
    print_section("DEMO 3: Volatility Adaptation")
    
    mock_atr_calc = Mock()
    calculator = ATRCalculator(Mock(), Mock(), "0xWBNB", "0xUSDT")
    
    scenarios = [
        ("Morning", 600.0, 5.0, "Calm overnight trading"),
        ("News Event", 610.0, 18.0, "Breaking news causes volatility spike"),
        ("Afternoon", 605.0, 8.0, "Market settles after news"),
        ("Evening", 602.0, 4.5, "Low volume trading"),
    ]
    
    print("\n📅 Simulating a full day of trading:")
    
    for time_period, price, atr, description in scenarios:
        volatility = calculator.get_volatility_level(atr, price)
        interval = calculator.get_grid_interval(atr, price)
        atr_pct = (atr / price) * 100
        
        print(f"\n⏰ {time_period} - {description}")
        print(f"   Price: ${price:.2f}")
        print(f"   ATR: ${atr:.2f} ({atr_pct:.2f}%)")
        print(f"   Volatility: {volatility.upper()}")
        print(f"   Grid Interval: ${interval:.2f}")
        
        if volatility == 'low':
            print(f"   📊 Strategy: Tight grid for frequent small profits")
        elif volatility == 'medium':
            print(f"   📊 Strategy: Standard grid for balanced trading")
        else:
            print(f"   📊 Strategy: Wide grid to avoid false signals")
    
    print("\n✅ Grid automatically adapts throughout the day!")


def demo_profit_calculation():
    """Demo: Simple profit calculation example"""
    print_section("DEMO 4: Profit Calculation Example")
    
    print("\n💰 Example Trading Scenario:")
    print("   Grid Interval: $5")
    print("   Trade Size: 0.01 BNB per order")
    
    trades = [
        ("BUY", 595.0, 0.01),
        ("SELL", 600.0, 0.01),
        ("BUY", 595.0, 0.01),
        ("SELL", 605.0, 0.01),
        ("BUY", 600.0, 0.01),
        ("SELL", 608.0, 0.01),
    ]
    
    total_profit = 0.0
    print("\n📊 Trade History:")
    
    for i, (action, price, amount) in enumerate(trades, 1):
        if action == "BUY":
            cost = price * amount
            print(f"   {i}. {action} {amount} BNB @ ${price:.2f} = -${cost:.2f}")
        else:  # SELL
            revenue = price * amount
            # Find corresponding buy
            buy_price = trades[i-2][1] if i > 1 else price - 5
            profit = (price - buy_price) * amount
            total_profit += profit
            print(f"   {i}. {action} {amount} BNB @ ${price:.2f} = +${revenue:.2f} (profit: ${profit:.2f})")
    
    print(f"\n💵 Total Profit: ${total_profit:.2f}")
    print(f"   Average per trade: ${total_profit/len([t for t in trades if t[0]=='SELL']):.2f}")
    print("\n✅ Small profits add up over many trades!")


def main():
    """Run all demos"""
    print("\n" + "🔷" * 40)
    print("  VOLATILITY-ADAPTIVE GRID BOT DEMONSTRATION")
    print("🔷" * 40)
    
    print("\nThis demo shows how the Grid Bot works without a live connection.")
    print("It uses simulated price data to demonstrate key features.")
    
    input("\nPress Enter to start Demo 1 (ATR Calculation)...")
    demo_atr_calculation()
    
    input("\n\nPress Enter to start Demo 2 (Grid Repositioning)...")
    demo_grid_repositioning()
    
    input("\n\nPress Enter to start Demo 3 (Volatility Adaptation)...")
    demo_volatility_adaptation()
    
    input("\n\nPress Enter to start Demo 4 (Profit Calculation)...")
    demo_profit_calculation()
    
    print("\n" + "🔷" * 40)
    print("  DEMONSTRATION COMPLETE")
    print("🔷" * 40)
    
    print("\n📚 Key Takeaways:")
    print("   ✅ Grid Bot automatically adjusts to market volatility")
    print("   ✅ Tighter intervals in calm markets for frequent trades")
    print("   ✅ Wider intervals in volatile markets to avoid losses")
    print("   ✅ Orders automatically reposition after fills")
    print("   ✅ Designed for consistent small profits over time")
    
    print("\n🚀 Ready to try with real data? Run: python3 manager_Version4.py")
    print("   Then select option 13 to initialize the Grid Bot!\n")


if __name__ == '__main__':
    main()
