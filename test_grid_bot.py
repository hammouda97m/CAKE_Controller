"""
Unit tests for ATR Calculator and Grid Bot

Run with: python3 test_grid_bot.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atr_calculator import ATRCalculator
from grid_bot import GridOrder, VolatilityAdaptiveGridBot


class TestATRCalculator(unittest.TestCase):
    """Test cases for ATRCalculator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_router = Mock()
        self.mock_web3 = Mock()
        self.wbnb = "0xWBNB"
        self.usdt = "0xUSDT"
        
        self.calculator = ATRCalculator(
            self.mock_router,
            self.mock_web3,
            self.wbnb,
            self.usdt
        )
    
    def test_initialization(self):
        """Test ATRCalculator initialization"""
        self.assertEqual(self.calculator.atr_period, 14)
        self.assertEqual(len(self.calculator.price_history), 0)
        self.assertEqual(self.calculator.wbnb_address, self.wbnb)
        self.assertEqual(self.calculator.usdt_address, self.usdt)
    
    def test_get_current_bnb_price_success(self):
        """Test successful price fetching"""
        # Mock the router contract response
        self.mock_router.functions.getAmountsOut.return_value.call.return_value = [
            1000000000000000000,  # 1 BNB in wei
            600000000000000000000  # 600 USDT in wei
        ]
        
        price = self.calculator.get_current_bnb_price()
        
        self.assertIsNotNone(price)
        self.assertEqual(price, 600.0)
    
    def test_get_current_bnb_price_error(self):
        """Test price fetching with error"""
        # Mock an exception
        self.mock_router.functions.getAmountsOut.side_effect = Exception("Network error")
        
        price = self.calculator.get_current_bnb_price()
        
        self.assertIsNone(price)
    
    def test_volatility_level_low(self):
        """Test low volatility detection"""
        atr = 5.0  # $5 ATR
        price = 600.0  # $600 price
        # ATR% = (5/600) * 100 = 0.83% < 1% = LOW
        
        level = self.calculator.get_volatility_level(atr, price)
        
        self.assertEqual(level, 'low')
    
    def test_volatility_level_medium(self):
        """Test medium volatility detection"""
        atr = 10.0  # $10 ATR
        price = 600.0  # $600 price
        # ATR% = (10/600) * 100 = 1.67% (between 1% and 2.5%) = MEDIUM
        
        level = self.calculator.get_volatility_level(atr, price)
        
        self.assertEqual(level, 'medium')
    
    def test_volatility_level_high(self):
        """Test high volatility detection"""
        atr = 20.0  # $20 ATR
        price = 600.0  # $600 price
        # ATR% = (20/600) * 100 = 3.33% > 2.5% = HIGH
        
        level = self.calculator.get_volatility_level(atr, price)
        
        self.assertEqual(level, 'high')
    
    def test_grid_interval_low_volatility(self):
        """Test grid interval calculation for low volatility"""
        atr = 5.0
        price = 600.0
        base_interval = 5.0
        
        interval = self.calculator.get_grid_interval(atr, price, base_interval)
        
        # Low volatility: 60% of base = 3.0
        self.assertEqual(interval, 3.0)
    
    def test_grid_interval_medium_volatility(self):
        """Test grid interval calculation for medium volatility"""
        atr = 10.0
        price = 600.0
        base_interval = 5.0
        
        interval = self.calculator.get_grid_interval(atr, price, base_interval)
        
        # Medium volatility: 100% of base = 5.0
        self.assertEqual(interval, 5.0)
    
    def test_grid_interval_high_volatility(self):
        """Test grid interval calculation for high volatility"""
        atr = 20.0
        price = 600.0
        base_interval = 5.0
        
        interval = self.calculator.get_grid_interval(atr, price, base_interval)
        
        # High volatility: 160% of base = 8.0
        self.assertEqual(interval, 8.0)
    
    def test_update_price_history(self):
        """Test updating price history"""
        # Mock price fetching
        self.mock_router.functions.getAmountsOut.return_value.call.return_value = [
            1000000000000000000,
            600000000000000000000
        ]
        
        initial_length = len(self.calculator.price_history)
        self.calculator.update_price_history(num_samples=3)
        
        self.assertEqual(len(self.calculator.price_history), initial_length + 3)
    
    def test_calculate_atr_insufficient_data(self):
        """Test ATR calculation with insufficient data"""
        # Only 5 candles, need 14
        self.calculator.price_history = [
            {'high': 600, 'low': 598, 'close': 599} for _ in range(5)
        ]
        
        atr = self.calculator.calculate_atr()
        
        self.assertIsNone(atr)
    
    def test_calculate_atr_success(self):
        """Test successful ATR calculation"""
        # Create 20 candles with some variance
        self.calculator.price_history = [
            {'high': 600 + i, 'low': 598 + i, 'close': 599 + i} 
            for i in range(20)
        ]
        
        atr = self.calculator.calculate_atr()
        
        self.assertIsNotNone(atr)
        self.assertGreater(atr, 0)


class TestGridOrder(unittest.TestCase):
    """Test cases for GridOrder"""
    
    def test_initialization_buy_order(self):
        """Test buy order initialization"""
        order = GridOrder('buy', 590.0, 0.01)
        
        self.assertEqual(order.order_type, 'buy')
        self.assertEqual(order.price, 590.0)
        self.assertEqual(order.amount, 0.01)
        self.assertFalse(order.filled)
        self.assertIsNotNone(order.created_at)
    
    def test_initialization_sell_order(self):
        """Test sell order initialization"""
        order = GridOrder('sell', 610.0, 0.01)
        
        self.assertEqual(order.order_type, 'sell')
        self.assertEqual(order.price, 610.0)
        self.assertEqual(order.amount, 0.01)
        self.assertFalse(order.filled)
    
    def test_order_repr(self):
        """Test order string representation"""
        order = GridOrder('buy', 590.0, 0.01)
        
        repr_str = repr(order)
        
        self.assertIn('BUY', repr_str)
        self.assertIn('590.00', repr_str)
        self.assertIn('OPEN', repr_str)
        
        order.filled = True
        repr_str = repr(order)
        self.assertIn('FILLED', repr_str)


class TestVolatilityAdaptiveGridBot(unittest.TestCase):
    """Test cases for VolatilityAdaptiveGridBot"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_atr_calc = Mock(spec=ATRCalculator)
        self.mock_swap_mgr = Mock()
        self.mock_wallet_mgr = Mock()
        self.main_wallet = "0xMainWallet"
        
        self.bot = VolatilityAdaptiveGridBot(
            self.mock_atr_calc,
            self.mock_swap_mgr,
            self.mock_wallet_mgr,
            self.main_wallet,
            base_interval=5.0
        )
    
    def test_initialization(self):
        """Test GridBot initialization"""
        self.assertEqual(self.bot.base_interval, 5.0)
        self.assertFalse(self.bot.active)
        self.assertEqual(len(self.bot.orders), 0)
        self.assertEqual(self.bot.trades_executed, 0)
        self.assertEqual(self.bot.position_bnb, 0.0)
        self.assertEqual(self.bot.position_usdt, 0.0)
    
    def test_get_status_inactive(self):
        """Test getting status when bot is inactive"""
        status = self.bot.get_status()
        
        self.assertFalse(status['active'])
        self.assertEqual(status['total_trades'], 0)
        self.assertEqual(status['active_orders'], 0)
    
    def test_get_status_with_orders(self):
        """Test getting status with active orders"""
        self.bot.orders = [
            GridOrder('buy', 590.0, 0.01),
            GridOrder('sell', 610.0, 0.01)
        ]
        
        status = self.bot.get_status()
        
        self.assertEqual(status['active_orders'], 2)
        self.assertEqual(status['total_orders'], 2)
    
    def test_get_status_with_filled_orders(self):
        """Test getting status with some filled orders"""
        order1 = GridOrder('buy', 590.0, 0.01)
        order1.filled = True
        order2 = GridOrder('sell', 610.0, 0.01)
        
        self.bot.orders = [order1, order2]
        
        status = self.bot.get_status()
        
        self.assertEqual(status['active_orders'], 1)
        self.assertEqual(status['total_orders'], 2)
    
    def test_initialize_success(self):
        """Test successful bot initialization"""
        # Mock ATR calculator responses
        self.mock_atr_calc.initialize_history.return_value = True
        self.mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 600.0,
            'atr': 10.0,
            'atr_percentage': 1.67,
            'volatility_level': 'medium',
            'recommended_grid_interval': 5.0,
            'samples': 20
        }
        
        result = self.bot.initialize(quick_start=True)
        
        self.assertTrue(result)
        self.assertEqual(len(self.bot.orders), 2)
        self.assertTrue(any(o.order_type == 'buy' for o in self.bot.orders))
        self.assertTrue(any(o.order_type == 'sell' for o in self.bot.orders))
    
    def test_initialize_atr_failure(self):
        """Test bot initialization with ATR failure"""
        self.mock_atr_calc.initialize_history.return_value = False
        
        result = self.bot.initialize(quick_start=True)
        
        self.assertFalse(result)
        self.assertEqual(len(self.bot.orders), 0)
    
    def test_start_without_initialization(self):
        """Test starting bot without initialization"""
        result = self.bot.start()
        
        self.assertFalse(result)
        self.assertFalse(self.bot.active)
    
    def test_start_when_already_running(self):
        """Test starting bot when already running"""
        self.bot.active = True
        
        result = self.bot.start()
        
        self.assertFalse(result)
    
    def test_stop_when_not_running(self):
        """Test stopping bot when not running"""
        # Should not raise an exception
        self.bot.stop()
        self.assertFalse(self.bot.active)
    
    def test_execute_sell_order(self):
        """Test executing a sell order"""
        order = GridOrder('sell', 605.0, 0.01)
        self.bot.orders = [order]
        
        # Mock swap manager to return success
        self.mock_swap_mgr.swap_bnb_to_usdt.return_value = True
        
        # Mock ATR summary
        self.mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 605.0,
            'recommended_grid_interval': 5.0
        }
        
        self.bot._execute_sell_order(order, 605.0)
        
        self.assertTrue(order.filled)
        self.assertEqual(self.bot.trades_executed, 1)
        self.assertLess(self.bot.position_bnb, 0)  # Sold BNB
        self.assertGreater(self.bot.position_usdt, 0)  # Received USDT
        # Verify swap was called with correct parameters
        self.mock_swap_mgr.swap_bnb_to_usdt.assert_called_once()
    
    def test_execute_buy_order(self):
        """Test executing a buy order"""
        order = GridOrder('buy', 595.0, 0.01)
        self.bot.orders = [order]
        
        # Mock swap manager to return success
        self.mock_swap_mgr.swap_usdt_to_bnb.return_value = True
        
        # Mock ATR summary
        self.mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 595.0,
            'recommended_grid_interval': 5.0
        }
        
        self.bot._execute_buy_order(order, 595.0)
        
        self.assertTrue(order.filled)
        self.assertEqual(self.bot.trades_executed, 1)
        self.assertGreater(self.bot.position_bnb, 0)  # Bought BNB
        self.assertLess(self.bot.position_usdt, 0)  # Spent USDT
        # Verify swap was called with correct parameters
        self.mock_swap_mgr.swap_usdt_to_bnb.assert_called_once()
    
    def test_execute_sell_order_swap_failure(self):
        """Test executing a sell order when swap fails"""
        order = GridOrder('sell', 605.0, 0.01)
        self.bot.orders = [order]
        
        # Mock swap manager to return failure
        self.mock_swap_mgr.swap_bnb_to_usdt.return_value = False
        
        # Mock ATR summary
        self.mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 605.0,
            'recommended_grid_interval': 5.0
        }
        
        self.bot._execute_sell_order(order, 605.0)
        
        # Order should not be filled if swap fails
        self.assertFalse(order.filled)
        self.assertEqual(self.bot.trades_executed, 0)
        self.assertEqual(self.bot.position_bnb, 0)  # No change in position
        self.assertEqual(self.bot.position_usdt, 0)  # No change in position
    
    def test_execute_buy_order_swap_failure(self):
        """Test executing a buy order when swap fails"""
        order = GridOrder('buy', 595.0, 0.01)
        self.bot.orders = [order]
        
        # Mock swap manager to return failure
        self.mock_swap_mgr.swap_usdt_to_bnb.return_value = False
        
        # Mock ATR summary
        self.mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 595.0,
            'recommended_grid_interval': 5.0
        }
        
        self.bot._execute_buy_order(order, 595.0)
        
        # Order should not be filled if swap fails
        self.assertFalse(order.filled)
        self.assertEqual(self.bot.trades_executed, 0)
        self.assertEqual(self.bot.position_bnb, 0)  # No change in position
        self.assertEqual(self.bot.position_usdt, 0)  # No change in position


class TestIntegration(unittest.TestCase):
    """Integration tests for Grid Bot system"""
    
    def test_end_to_end_grid_repositioning(self):
        """Test full cycle of order fill and repositioning"""
        mock_atr_calc = Mock(spec=ATRCalculator)
        mock_swap_mgr = Mock()
        mock_wallet_mgr = Mock()
        
        # Mock swap methods to return success
        mock_swap_mgr.swap_bnb_to_usdt.return_value = True
        mock_swap_mgr.swap_usdt_to_bnb.return_value = True
        
        bot = VolatilityAdaptiveGridBot(
            mock_atr_calc,
            mock_swap_mgr,
            mock_wallet_mgr,
            "0xMain"
        )
        
        # Setup initial orders
        bot.orders = [
            GridOrder('buy', 590.0, 0.01),
            GridOrder('sell', 610.0, 0.01)
        ]
        
        # Mock ATR responses
        mock_atr_calc.get_atr_summary.return_value = {
            'current_price': 610.0,
            'recommended_grid_interval': 5.0
        }
        
        # Execute sell order
        sell_order = bot.orders[1]
        bot._execute_sell_order(sell_order, 610.0)
        
        # After repositioning, filled orders are removed and new orders added
        # So we should have the original unfilled buy order + 2 new orders = 3 total
        # But only 2 of them are active (not filled)
        active_orders = [o for o in bot.orders if not o.filled]
        self.assertGreaterEqual(len(active_orders), 2)
        
        # Should have at least one buy and one sell order
        buy_orders = [o for o in active_orders if o.order_type == 'buy']
        sell_orders = [o for o in active_orders if o.order_type == 'sell']
        
        self.assertGreaterEqual(len(buy_orders), 1)
        self.assertGreaterEqual(len(sell_orders), 1)
        
        # Newest sell order should be higher than current price
        new_sell_orders = [o for o in sell_orders if o != sell_order]
        if new_sell_orders:
            self.assertGreater(new_sell_orders[0].price, 610.0)
        
        # There should be a buy order lower than current price
        low_buy_orders = [o for o in buy_orders if o.price < 610.0]
        self.assertGreater(len(low_buy_orders), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestATRCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestGridOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestVolatilityAdaptiveGridBot))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
