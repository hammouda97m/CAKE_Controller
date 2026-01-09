# Multi-Wallet Prediction Bot with Volatility-Adaptive Grid Trading

This is a **comprehensive wallet management and betting system** for PancakeSwap predictions with instant Telegram betting capabilities and an advanced **Volatility-Adaptive Grid Bot** for automated trading.

## Core Purpose
Manage multiple betting wallets, swap between BNB/USDT, place bets, claim rewards, execute instant bets via Telegram commands, and automate trading with the Volatility-Adaptive Grid Bot that dynamically adjusts to market conditions.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- BSC (Binance Smart Chain) RPC endpoint
- Main wallet with private key (for swaps and distributions)
- (Optional) Telegram Bot Token for notifications

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/hammouda97m/CAKE_Controller.git
cd CAKE_Controller
```

2. **Install required dependencies:**
```bash
pip3 install -r requirements.txt
```

Required packages:
- `web3>=6.0.0` - BSC blockchain interaction
- `python-dotenv>=0.19.0` - Environment variable management
- `eth-account>=0.8.0` - Ethereum account utilities
- `requests>=2.28.0` - HTTP requests for APIs
- `ta>=0.11.0` - Technical analysis library for ATR
- `pandas>=1.5.0` - Data manipulation for price analysis

3. **Configure environment variables:**

Create a `.env` file in the project root:
```bash
MAIN_PRIVATE_KEY=your_private_key_here
MAIN_WALLET_ADDRESS=your_wallet_address_here
TELEGRAM_TOKEN=your_telegram_bot_token  # Optional
TELEGRAM_CHAT_ID=your_chat_id  # Optional
```

4. **Run the bot:**
```bash
python3 manager_Version4.py
```

### Quick Start with Grid Bot

**For Testing (Quick Mode):**
```
1. Run: python3 manager_Version4.py
2. Select: 13 (Grid Bot: Initialize)
3. Choose: 1 (Quick Start - 5s intervals, ~70 seconds)
4. Wait for initialization to complete
5. Select: 14 (Grid Bot: Start/Stop)
6. Confirm: y (Start)
7. Select: 15 (Grid Bot: Status) - Monitor performance
```

**For Live Trading (Production Mode):**
```
1. Run: python3 manager_Version4.py
2. Select: 13 (Grid Bot: Initialize)
3. Choose: 2 (Production Mode - 60s intervals, ~20 minutes)
4. Wait for initialization to complete (~20 minutes)
5. Select: 14 (Grid Bot: Start/Stop)
6. Confirm: y (Start)
7. Select: 15 (Grid Bot: Status) - Monitor performance
```

### Running Tests

To verify the Grid Bot implementation:
```bash
python3 test_grid_bot.py
```

All 27 tests should pass, confirming:
- ATR calculation accuracy
- Volatility level detection
- Grid interval adjustments
- Order placement and execution
- Grid repositioning logic

## Key Components

### 1. **Wallet Management System (`WalletManager`)**

**Creates & Manages Sub-Wallets:**
- Generates new wallets with cryptographically secure random keys
- Stores wallet data in `created_wallets.json`
- Tracks balances (BNB and USDT) for each wallet
- Auto-names wallets or accepts custom names

**Key Operations:**
- **Create**: Generate new wallet with private key
- **List**: Display all wallets with current balances
- **Delete**: Permanently remove wallet from system
- **Empty**: Send all BNB from wallet back to main wallet
- **Get Balances**: Real-time BNB and USDT balance updates

### 2. **Swap Management System (`SwapManager`)**

**PancakeSwap Integration:**
- Swaps USDT → BNB using PancakeSwap Router
- Swaps BNB → USDT (0.1% slippage tolerance)
- Gets real-time exchange rates
- Automatic approval handling for USDT spending

**How Swaps Work:**
```
USDT (Main Wallet) → Approve Router → Swap on PancakeSwap → BNB (Target Wallet)
```

**Safety Features:**
- Checks balance before swapping
- 0.1% slippage protection (99.9% minimum output)
- Automatic approval management
- Transaction confirmation tracking

### 3. **Betting Management System (`BettingManager`)**

**Places Bets via Smart Contract:**
- Supports UP (Bull) and DOWN (Bear) bets
- Validates round is still open (not locked)
- Checks wallet has sufficient balance
- Uses 95% of wallet balance for betting (reserves 5% for gas)

**Transaction Flow:**
```
Check Round Status → Validate Balance → Build TX → Sign with Wallet → Send to Contract
```

### 4. **Reward Management System (`RewardManager`)**

**Automatic Reward Claiming:**
- Scans last 100 rounds for claimable wins
- Calculates estimated rewards
- Claims multiple epochs in one session
- Shows detailed breakdown of claimable amounts

**Features:**
- **Show Claimable**: Lists all unclaimed winning rounds
- **Claim All**: Batch claims all available rewards
- **Estimate Rewards**: Calculates expected payout before claiming

**Reward Calculation:**
```
User's Bet Amount × Total Reward Pool ÷ Winning Side Total = User's Reward
```

### 5. **⚡ INSTANT Telegram Betting System** (NEW!)

**Revolutionary Zero-Delay Betting:**

**Command Format:**
```
/bet [wallet_number]/[usdt_amount]/[up|down]

Example: /bet 1/50/up
```

This means:
- Wallet #1
- Swap 50 USDT to BNB
- Bet UP (Bull)

**How It Works:**
1. **Instant Monitoring**: Runs in background thread with NO sleep delays
2. **Command Detection**: Parses `/bet` commands from Telegram
3. **Auto-Execution**: Automatically swaps USDT → BNB → Places bet
4. **Real-time Updates**: Sends status messages throughout process

**Execution Flow:**
```
Telegram Message → Parse Command → Validate → Swap USDT → Wait 0.5s → Place Bet → Confirm
```

**Key Innovation:**
- **No polling delay** - checks for messages continuously
- **Instant execution** - processes commands immediately upon receipt
- **Automated workflow** - no manual steps required

### 6. **Advanced Wallet Operations**

#### **Drain All Wallets**
Sends ALL BNB from every sub-wallet back to main wallet:
- Useful for consolidating funds
- Leaves only enough for gas fees
- Processes each wallet sequentially
- Sends Telegram notification when complete

#### **Distribute Wealth**
Opposite of drain - spreads main wallet funds:
- Takes 95% of main wallet BNB
- Divides equally among all sub-wallets
- Reserves gas fees automatically
- Confirms before execution

**Use Case**: Fund multiple wallets for simultaneous betting

#### **Total Balance Check**
Shows combined BNB across all sub-wallets (excluding main):
- Quick overview of deployed capital
- Helps decide when to drain or redistribute

### 7. **Telegram Integration**

**Instant Command System:**
```python
def telegram_monitor():
    while True:
        check_telegram_commands()
        # NO SLEEP = INSTANT ⚡
```

**Benefits:**
- Remote betting from anywhere
- No need to access bot directly
- Mobile-friendly betting
- Real-time status updates

**Notification Types:**
1. **Bet Confirmations**: When bets are placed
2. **Swap Confirmations**: When swaps complete
3. **Reward Claims**: When rewards are collected
4. **Wallet Operations**: Drain/empty notifications
5. **Distribution Complete**: When wealth is distributed
6. **Grid Bot Updates**: When grid bot is started/stopped

### 8. **🔷 Volatility-Adaptive Grid Bot** (NEW!)

**Revolutionary Automated Trading System:**

The Volatility-Adaptive Grid Bot is an intelligent trading system that automatically executes buy and sell orders based on market volatility. It dynamically adjusts its trading intervals using ATR (Average True Range) to adapt to changing market conditions.

#### **Key Features:**

**Dynamic Grid Intervals:**
- **Low Volatility** (ATR < 1%): Tighter intervals (60% of base = $3)
- **Medium Volatility** (ATR 1-2.5%): Normal intervals (100% of base = $5)
- **High Volatility** (ATR > 2.5%): Wider intervals (160% of base = $8)

**Automatic Order Placement:**
```
Initial Setup:
- Sell Order: Current Price + Grid Interval
- Buy Order: Current Price - Grid Interval

On Sell Fill (Price Increase):
- New Sell Order: New Price + Updated Interval
- New Buy Order: New Price - Updated Interval

On Buy Fill (Price Decrease):
- New Sell Order: New Price + Updated Interval
- New Buy Order: New Price - Updated Interval
```

**ATR-Based Volatility Measurement:**
- Continuously monitors market price movements
- Calculates ATR using 14-period moving average
- Updates grid intervals based on real-time volatility
- Recalculates ATR after every 5 trades

#### **How It Works:**

1. **Initialization Phase:**
   - Collects historical price data (14+ samples)
   - Calculates initial ATR
   - Sets up initial buy/sell orders
   - Determines optimal grid interval

2. **Trading Phase:**
   - Monitors price movements every 10 seconds
   - Triggers orders when price crosses thresholds
   - Automatically repositions grid after fills
   - Updates ATR periodically for dynamic adjustment

3. **Risk Management:**
   - Wider intervals during high volatility prevent whipsaw losses
   - Tighter intervals during calm markets maximize profit opportunities
   - Configurable base interval (default $5)
   - Automatic position tracking (BNB and USDT)

#### **Usage:**

**Quick Start (Testing):**
```
Menu → 13. Grid Bot: Initialize → Quick Start (5s intervals, ~70 seconds)
Menu → 14. Grid Bot: Start/Stop → Start
Menu → 15. Grid Bot: Status → View current status
```

**Production Mode (Live Trading):**
```
Menu → 13. Grid Bot: Initialize → Production Mode (60s intervals, ~20 minutes)
Menu → 14. Grid Bot: Start/Stop → Start
Menu → 15. Grid Bot: Status → Monitor performance
```

#### **Status Display:**

The Grid Bot Status (Menu Option 15) shows:
- **Bot State**: Active or Stopped
- **Total Trades**: Number of executed trades
- **Position**: Current BNB and USDT positions
- **Active Orders**: Current buy/sell orders
- **Market Conditions**: Current price, ATR, volatility level, grid interval

**Example Output:**
```
📊 GRID BOT STATUS
================================================================================
Status: 🟢 ACTIVE
Total Trades: 8
Position BNB: 0.042000
Position USDT: $-251.20
Active Orders: 2/10

📈 Market Conditions:
   Price: $602.50
   ATR: $12.30 (2.04%)
   Volatility: MEDIUM
   Grid Interval: $5.00

🎯 Active Orders:
   GridOrder(SELL, $607.50, 0.010000 BNB, OPEN)
   GridOrder(BUY, $597.50, 0.010000 BNB, OPEN)
================================================================================
```

#### **Configuration:**

The Grid Bot can be configured by modifying parameters in `manager_Version4.py`:

```python
grid_bot = VolatilityAdaptiveGridBot(
    atr_calculator,
    swap_manager,
    wallet_manager,
    MAIN_WALLET_ADDRESS,
    base_interval=5.0  # Adjust base interval in dollars
)
```

Additional parameters in `atr_calculator.py`:
- `atr_period`: Number of periods for ATR calculation (default: 14)

Additional parameters in `grid_bot.py`:
- `update_interval`: Order check frequency in seconds (default: 10)
- `atr_update_frequency`: Trades between ATR updates (default: 5)

#### **Safety Features:**

- **Initialization Validation**: Ensures sufficient price data before starting
- **Error Handling**: Graceful handling of network errors and price fetch failures
- **Automatic Cleanup**: Removes filled orders from active tracking
- **Status Monitoring**: Real-time visibility into bot performance
- **Telegram Notifications**: Alerts for start/stop events

### 9. **Complete Betting Workflow**

**Standard Manual Flow:**
```
1. Select wallet from list
2. Enter USDT amount to swap
3. Choose direction (up/down)
4. Preview transaction
5. Confirm
6. Bot swaps USDT → BNB
7. Bot places bet automatically
8. Telegram notification sent
```

**Instant Telegram Flow:**
```
1. Send: /bet 1/50/up
2. Bot handles everything automatically
3. Get status updates via Telegram
```

### 10. **Main Menu Options**

| Option | Function |
|--------|----------|
| 1 | Check main wallet balance |
| 2 | Swap BNB → USDT (main wallet) |
| 3 | Swap USDT → BNB (main wallet) |
| 4 | List all created wallets |
| 5 | Create new wallet |
| 6 | Start betting process (manual) |
| 7 | Claim rewards |
| 8 | Empty specific wallet |
| 9 | Drain ALL wallets |
| 10 | Distribute wealth to all wallets |
| 11 | Delete wallet |
| 12 | Show total BNB across sub-wallets |
| 13 | 🔷 Grid Bot: Initialize |
| 14 | 🔷 Grid Bot: Start/Stop |
| 15 | 🔷 Grid Bot: Status |
| 16 | Exit |

### 11. **Smart Contract Interactions**

**Prediction Contract:**
- `currentEpoch()` - Get current round number
- `rounds()` - Get round data (timestamps, prices, amounts)
- `betBull()` - Place UP bet
- `betBear()` - Place DOWN bet
- `ledger()` - Get user's bet info
- `claimable()` - Check if rewards can be claimed
- `claim()` - Claim winning rewards

**USDT Contract:**
- `balanceOf()` - Check USDT balance
- `approve()` - Allow router to spend USDT
- `allowance()` - Check current approval amount
- `transfer()` - Send USDT (not used in this bot)

**PancakeSwap Router:**
- `getAmountsOut()` - Preview swap rates
- `swapExactTokensForETH()` - USDT → BNB
- `swapExactETHForTokens()` - BNB → USDT

### 12. **Safety & Error Handling**

**Pre-Transaction Checks:**
- Balance verification before swaps
- Round lock status before betting
- Gas fee reservations
- Approval status checks
- Grid bot initialization validation

**Confirmation Prompts:**
- Swap confirmations
- Bet confirmations
- Wallet deletion warnings
- Distribution confirmations
- Grid bot start/stop confirmations

**Error Recovery:**
- Failed transaction reporting
- Automatic retry mechanisms (where applicable)
- Telegram error notifications
- Grid bot graceful error handling

### 13. **Data Persistence**

**Stored Data:**
- `created_wallets.json` - All wallet info (addresses, keys, names, timestamps)
- `.env` - Main wallet credentials and Telegram tokens

**Security Note:** 
Private keys are stored in plaintext JSON - should only be used for small amounts or testnet!

## Use Cases

### **Multi-Wallet Strategy**
1. Create 10 wallets
2. Distribute 95% of main wallet equally
3. Each wallet bets on different rounds/directions
4. Drain all back to main when done
5. Claim all rewards centrally

### **Instant Telegram Betting**
```
You: /bet 3/100/down
Bot: ⚡ INSTANT TELEGRAM BET!
Bot: 💱 100 USDT → ~0.15 BNB
Bot: ✅ Swap completed!
Bot: 🎯 BET PLACED! DOWN with 0.142 BNB
```

### **Reward Harvesting**
1. Select wallet
2. Check claimable rewards (shows all winnings)
3. Claim all in one transaction
4. Funds returned to wallet
5. Empty wallet to consolidate

## Example Session

```
📋 MAIN MENU: 5 (Create wallet)
✅ New wallet created: Wallet_1_143022

📋 MAIN MENU: 10 (Distribute wealth)
💰 Sending 0.05 BNB to each of 10 wallets...
✅ Distribution complete!

[On Telegram]
/bet 1/50/up

[Bot executes instantly]
🎯 Bet placed! Round 12345, UP, 0.047 BNB

[5 minutes later - round ends]
📋 MAIN MENU: 7 (Claim rewards)
🎁 Claimed! +0.087 BNB

📋 MAIN MENU: 9 (Drain all)
💀 All wallets drained back to main!
```

This bot essentially creates a **distributed betting operation** where you can deploy capital across multiple wallets, bet via Telegram instantly, and manage everything from one interface!
