#!/usr/bin/env python3
"""
Whale Portfolio Tracker v1.0
Tracks whale holdings, recent buys/sells, position changes, and alpha discovery
Part of the Professional Solana Memecoin Analysis Suite
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WhaleHolding:
    """Represents a whale's token holding"""
    contract_address: str
    token_symbol: str
    token_name: str
    balance_tokens: float
    balance_usd: float
    percentage_of_portfolio: float
    market_cap: float
    age_days: int
    last_transaction_hours: int
    entry_price_estimate: Optional[float] = None
    current_price: float = 0.0
    unrealized_pnl_percent: Optional[float] = None

@dataclass
class WhaleTransaction:
    """Represents a whale transaction"""
    wallet_address: str
    contract_address: str
    token_symbol: str
    action: str  # buy, sell, transfer
    amount_tokens: float
    amount_usd: float
    timestamp: datetime
    price_per_token: float
    significance: str  # small, medium, large, massive
    confidence: float

@dataclass
class WhalePortfolio:
    """Complete whale portfolio analysis"""
    wallet_address: str
    whale_tier: str
    total_portfolio_value: float
    num_holdings: int
    top_holdings: List[WhaleHolding]
    recent_transactions: List[WhaleTransaction]
    portfolio_diversity_score: int  # 0-100
    risk_profile: str  # conservative, balanced, aggressive, degen
    alpha_signals: List[Dict[str, Any]]
    performance_score: int  # 0-100 based on recent performance
    activity_level: str  # very_high, high, medium, low
    last_active_hours: int

class WhalePortfolioTracker:
    """Advanced whale portfolio tracking and analysis"""
    
    def __init__(self):
        self.session = None
        self.whale_database = self._load_whale_database()
        self.cache = {}  # Simple caching mechanism
        self.cache_ttl = 300  # 5 minutes
        
    def _load_whale_database(self) -> Dict[str, Dict[str, Any]]:
        """Load the whale database with enhanced portfolio tracking capabilities"""
        return {
            # Mega Whales (>$10M typical holdings)
            "8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj": {
                "tier": "mega_whale", "typical_position": 15000000, "activity_score": 95,
                "specialization": ["memecoins", "defi"], "risk_tolerance": "aggressive",
                "alpha_track_record": 0.89, "followers": "high"
            },
            "GVXRSBjFk6e6J3NbVPXohDJetcTjaeeuykUpbQF8UoMU": {
                "tier": "mega_whale", "typical_position": 12000000, "activity_score": 88,
                "specialization": ["new_launches", "narrative_plays"], "risk_tolerance": "degen",
                "alpha_track_record": 0.94, "followers": "very_high"
            },
            
            # Whales ($1M-$10M)
            "4iwvfv5aBk5b4mGG2eL9NrWxc3jEdqhVh7wH7KmN7Pvm": {
                "tier": "whale", "typical_position": 2500000, "activity_score": 82,
                "specialization": ["established_memes", "bluechips"], "risk_tolerance": "balanced",
                "alpha_track_record": 0.76, "followers": "medium"
            },
            "AzNk5p9vTWjvjBSs9vVLHU5kXjKxfDx1a3vqFh8a2Jxm": {
                "tier": "whale", "typical_position": 3200000, "activity_score": 77,
                "specialization": ["defi", "governance"], "risk_tolerance": "conservative",
                "alpha_track_record": 0.71, "followers": "medium"
            },
            
            # Sharks ($100K-$1M)
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": {
                "tier": "shark", "typical_position": 350000, "activity_score": 91,
                "specialization": ["early_memes", "rugpull_recovery"], "risk_tolerance": "aggressive",
                "alpha_track_record": 0.83, "followers": "low"
            },
            "7t6H5s8wkP4R9VqA1NzKpFe6m3L4Q8Ux2CjY9xNpbE5G": {
                "tier": "shark", "typical_position": 450000, "activity_score": 86,
                "specialization": ["technical_analysis", "swing_trading"], "risk_tolerance": "balanced",
                "alpha_track_record": 0.79, "followers": "low"
            },
            
            # Dolphins ($10K-$100K) - The Alpha Hunters
            "BrG44HdsEhzapvs8bEqzvkq4egwjHg4Kp2C1F8L7M9Zt": {
                "tier": "dolphin", "typical_position": 45000, "activity_score": 94,
                "specialization": ["micro_caps", "narrative_timing"], "risk_tolerance": "degen",
                "alpha_track_record": 0.91, "followers": "none"
            },
            "3vF9K8mB2jQ7xYzW1eRu6TpH5sA4CdLk9uM7nPqE8bGs": {
                "tier": "dolphin", "typical_position": 38000, "activity_score": 89,
                "specialization": ["community_plays", "social_sentiment"], "risk_tolerance": "aggressive",
                "alpha_track_record": 0.87, "followers": "none"
            }
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=10, ttl_dns_cache=300, use_dns_cache=True)
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        return time.time() - self.cache[cache_key]['timestamp'] < self.cache_ttl
    
    async def _fetch_dexscreener_data(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Fetch token data from DexScreener with caching"""
        cache_key = f"dex_{contract_address}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        session = await self.get_session()
        url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': data,
                        'timestamp': time.time()
                    }
                    return data
                else:
                    logger.warning(f"DexScreener API error for {contract_address}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching DexScreener data for {contract_address}: {e}")
            return None
    
    def _simulate_whale_holdings(self, wallet_address: str, whale_info: Dict) -> List[WhaleHolding]:
        """
        Simulate whale holdings based on whale profile and market conditions
        In production, this would query blockchain data
        """
        holdings = []
        portfolio_value = whale_info['typical_position']
        
        # Generate holdings based on whale specialization and tier
        if whale_info['specialization'] == ["memecoins", "defi"]:
            # DeFi + Memecoin mix
            holdings.extend([
                WhaleHolding(
                    contract_address="So11111111111111111111111111111111111111112",
                    token_symbol="SOL", token_name="Solana",
                    balance_tokens=portfolio_value * 0.3 / 140,  # 30% in SOL at ~$140
                    balance_usd=portfolio_value * 0.3,
                    percentage_of_portfolio=30.0,
                    market_cap=65000000000,  # $65B
                    age_days=1200, last_transaction_hours=2,
                    current_price=140.0
                ),
                WhaleHolding(
                    contract_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", 
                    token_symbol="BONK", token_name="Bonk",
                    balance_tokens=portfolio_value * 0.25 / 0.000034,  # 25% in BONK
                    balance_usd=portfolio_value * 0.25,
                    percentage_of_portfolio=25.0,
                    market_cap=2400000000,  # $2.4B
                    age_days=380, last_transaction_hours=6,
                    current_price=0.000034
                )
            ])
        
        elif whale_info['specialization'] == ["new_launches", "narrative_plays"]:
            # New launch specialist
            holdings.extend([
                WhaleHolding(
                    contract_address="7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
                    token_symbol="POPCAT", token_name="Popcat",
                    balance_tokens=portfolio_value * 0.4 / 0.65,  # 40% in trending memecoin
                    balance_usd=portfolio_value * 0.4,
                    percentage_of_portfolio=40.0,
                    market_cap=650000000,  # $650M
                    age_days=45, last_transaction_hours=1,
                    current_price=0.65
                )
            ])
        
        # Add smaller positions for diversity
        remaining_percentage = 100 - sum(h.percentage_of_portfolio for h in holdings)
        if remaining_percentage > 0:
            # Add some smaller positions
            small_holdings = [
                ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC", 15.0),
                ("mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So", "mSOL", 10.0),
            ]
            
            for i, (addr, symbol, pct) in enumerate(small_holdings):
                if remaining_percentage >= pct:
                    holdings.append(WhaleHolding(
                        contract_address=addr, token_symbol=symbol, token_name=symbol,
                        balance_tokens=portfolio_value * (pct/100) / 1.0,  # Simplified pricing
                        balance_usd=portfolio_value * (pct/100),
                        percentage_of_portfolio=pct,
                        market_cap=1000000000, age_days=300,
                        last_transaction_hours=24, current_price=1.0
                    ))
                    remaining_percentage -= pct
        
        return holdings[:8]  # Limit to top 8 holdings
    
    def _simulate_recent_transactions(self, wallet_address: str, whale_info: Dict) -> List[WhaleTransaction]:
        """Simulate recent whale transactions"""
        transactions = []
        
        # Generate transactions based on activity score and specialization
        activity_multiplier = whale_info['activity_score'] / 100
        num_transactions = int(5 * activity_multiplier)  # Base 5 transactions
        
        base_time = datetime.now()
        
        for i in range(num_transactions):
            # Random transaction in the last 24 hours
            hours_ago = (i + 1) * (24 / num_transactions)
            timestamp = base_time - timedelta(hours=hours_ago)
            
            # Transaction type based on risk tolerance
            if whale_info['risk_tolerance'] == 'degen':
                actions = ['buy'] * 7 + ['sell'] * 3  # More buying for degens
            elif whale_info['risk_tolerance'] == 'conservative':
                actions = ['buy'] * 3 + ['sell'] * 4 + ['transfer'] * 3
            else:  # balanced/aggressive
                actions = ['buy'] * 5 + ['sell'] * 4 + ['transfer'] * 1
            
            action = actions[i % len(actions)]
            amount_usd = whale_info['typical_position'] * 0.02 * (1 + i * 0.1)  # 2-5% of portfolio
            
            transactions.append(WhaleTransaction(
                wallet_address=wallet_address,
                contract_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK example
                token_symbol="BONK", action=action,
                amount_tokens=amount_usd / 0.000034,
                amount_usd=amount_usd, timestamp=timestamp,
                price_per_token=0.000034,
                significance="medium" if amount_usd > 50000 else "small",
                confidence=0.85
            ))
        
        return transactions[:10]  # Limit to 10 recent transactions
    
    def _calculate_portfolio_diversity(self, holdings: List[WhaleHolding]) -> int:
        """Calculate portfolio diversity score (0-100)"""
        if not holdings:
            return 0
        
        # Factors: number of holdings, concentration, sector diversity
        num_holdings = len(holdings)
        
        # Concentration risk (lower is better for diversity)
        top_holding_percentage = max(h.percentage_of_portfolio for h in holdings)
        concentration_penalty = min(top_holding_percentage, 50) / 50 * 30  # Max 30 point penalty
        
        # Base score from number of holdings
        base_score = min(num_holdings * 10, 70)  # Max 70 from holdings count
        
        # Sector diversity bonus (simplified)
        sectors = set()
        for holding in holdings:
            if holding.token_symbol in ['SOL', 'mSOL', 'stSOL']:
                sectors.add('solana_ecosystem')
            elif holding.token_symbol in ['USDC', 'USDT']:
                sectors.add('stablecoins')
            elif holding.market_cap > 1000000000:
                sectors.add('large_cap')
            else:
                sectors.add('small_cap')
        
        sector_bonus = min(len(sectors) * 5, 20)  # Max 20 bonus
        
        final_score = int(base_score - concentration_penalty + sector_bonus)
        return max(0, min(100, final_score))
    
    def _determine_risk_profile(self, holdings: List[WhaleHolding], whale_info: Dict) -> str:
        """Determine whale's risk profile based on holdings"""
        if not holdings:
            return whale_info.get('risk_tolerance', 'unknown')
        
        # Calculate risk indicators
        small_cap_percentage = sum(
            h.percentage_of_portfolio for h in holdings 
            if h.market_cap < 100000000  # < $100M
        )
        
        stable_percentage = sum(
            h.percentage_of_portfolio for h in holdings
            if h.token_symbol in ['USDC', 'USDT', 'DAI']
        )
        
        young_token_percentage = sum(
            h.percentage_of_portfolio for h in holdings
            if h.age_days < 30
        )
        
        # Risk scoring
        risk_score = 0
        risk_score += small_cap_percentage * 0.8  # Small caps are risky
        risk_score += young_token_percentage * 1.2  # New tokens very risky
        risk_score -= stable_percentage * 0.5  # Stables reduce risk
        
        if risk_score > 60:
            return "degen"
        elif risk_score > 35:
            return "aggressive"  
        elif risk_score > 15:
            return "balanced"
        else:
            return "conservative"
    
    def _detect_alpha_signals(self, holdings: List[WhaleHolding], transactions: List[WhaleTransaction], whale_info: Dict) -> List[Dict[str, Any]]:
        """Detect potential alpha signals from whale activity"""
        signals = []
        
        # Recent large buys of small caps
        recent_buys = [t for t in transactions if t.action == 'buy' and t.timestamp > datetime.now() - timedelta(hours=6)]
        
        for buy in recent_buys:
            # Find corresponding holding
            holding = next((h for h in holdings if h.contract_address == buy.contract_address), None)
            
            if holding and holding.market_cap < 500000000 and buy.amount_usd > whale_info['typical_position'] * 0.05:  # 5%+ position in small cap
                signals.append({
                    'signal_type': 'large_buy_small_cap',
                    'contract_address': buy.contract_address,
                    'token_symbol': buy.token_symbol,
                    'significance': 'high',
                    'whale_tier': whale_info['tier'],
                    'buy_amount_usd': buy.amount_usd,
                    'market_cap': holding.market_cap,
                    'hours_ago': (datetime.now() - buy.timestamp).total_seconds() / 3600,
                    'alpha_probability': whale_info['alpha_track_record'],
                    'description': f"{whale_info['tier']} bought ${buy.amount_usd:,.0f} of {buy.token_symbol} (MC: ${holding.market_cap:,.0f})"
                })
        
        # New position in very young tokens
        young_holdings = [h for h in holdings if h.age_days < 7 and h.percentage_of_portfolio > 5]
        for holding in young_holdings:
            signals.append({
                'signal_type': 'early_position',
                'contract_address': holding.contract_address,
                'token_symbol': holding.token_symbol,
                'significance': 'very_high',
                'whale_tier': whale_info['tier'],
                'position_size_usd': holding.balance_usd,
                'token_age_days': holding.age_days,
                'alpha_probability': whale_info['alpha_track_record'] * 1.2,  # Boost for very early
                'description': f"{whale_info['tier']} holds ${holding.balance_usd:,.0f} in {holding.token_symbol} ({holding.age_days}d old)"
            })
        
        return signals[:5]  # Limit to top 5 signals
    
    async def analyze_whale_portfolio(self, wallet_address: str) -> Optional[WhalePortfolio]:
        """Analyze a whale's complete portfolio"""
        start_time = time.time()
        
        if wallet_address not in self.whale_database:
            return None
        
        whale_info = self.whale_database[wallet_address]
        
        try:
            # Simulate portfolio analysis (in production, query blockchain)
            holdings = self._simulate_whale_holdings(wallet_address, whale_info)
            transactions = self._simulate_recent_transactions(wallet_address, whale_info)
            
            # Calculate metrics
            diversity_score = self._calculate_portfolio_diversity(holdings)
            risk_profile = self._determine_risk_profile(holdings, whale_info)
            alpha_signals = self._detect_alpha_signals(holdings, transactions, whale_info)
            
            # Performance and activity scoring
            performance_score = int(whale_info['alpha_track_record'] * 100)
            
            recent_activity = len([t for t in transactions if t.timestamp > datetime.now() - timedelta(hours=24)])
            if recent_activity >= 5:
                activity_level = "very_high"
            elif recent_activity >= 3:
                activity_level = "high"
            elif recent_activity >= 1:
                activity_level = "medium"
            else:
                activity_level = "low"
            
            last_transaction = max(transactions, key=lambda t: t.timestamp) if transactions else None
            last_active_hours = int((datetime.now() - last_transaction.timestamp).total_seconds() / 3600) if last_transaction else 999
            
            portfolio = WhalePortfolio(
                wallet_address=wallet_address,
                whale_tier=whale_info['tier'],
                total_portfolio_value=whale_info['typical_position'],
                num_holdings=len(holdings),
                top_holdings=holdings,
                recent_transactions=transactions,
                portfolio_diversity_score=diversity_score,
                risk_profile=risk_profile,
                alpha_signals=alpha_signals,
                performance_score=performance_score,
                activity_level=activity_level,
                last_active_hours=last_active_hours
            )
            
            analysis_time = time.time() - start_time
            logger.info(f"Whale portfolio analysis completed in {analysis_time:.3f}s")
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error analyzing whale portfolio {wallet_address}: {e}")
            return None
    
    async def get_alpha_discoveries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alpha discoveries from all tracked whales"""
        start_time = time.time()
        alpha_discoveries = []
        
        try:
            # Analyze all whales in parallel
            tasks = []
            for wallet_address in list(self.whale_database.keys())[:limit]:  # Limit for performance
                tasks.append(self.analyze_whale_portfolio(wallet_address))
            
            portfolios = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect alpha signals
            for portfolio in portfolios:
                if isinstance(portfolio, WhalePortfolio) and portfolio.alpha_signals:
                    for signal in portfolio.alpha_signals:
                        signal['whale_address'] = portfolio.wallet_address
                        alpha_discoveries.append(signal)
            
            # Sort by alpha probability and recency
            alpha_discoveries.sort(key=lambda x: (x['alpha_probability'], -x.get('hours_ago', 999)), reverse=True)
            
            analysis_time = time.time() - start_time
            logger.info(f"Alpha discovery analysis completed in {analysis_time:.3f}s")
            
            return alpha_discoveries[:limit]
            
        except Exception as e:
            logger.error(f"Error getting alpha discoveries: {e}")
            return []

# Initialize tracker instance
whale_portfolio_tracker = WhalePortfolioTracker()

async def analyze_whale_portfolio_api(wallet_address: str) -> Dict[str, Any]:
    """API wrapper for whale portfolio analysis"""
    try:
        portfolio = await whale_portfolio_tracker.analyze_whale_portfolio(wallet_address)
        
        if not portfolio:
            return {
                "error": "Wallet not found in whale database",
                "wallet_address": wallet_address,
                "available_whales": len(whale_portfolio_tracker.whale_database)
            }
        
        # Convert to API response format
        response = {
            "wallet_address": portfolio.wallet_address,
            "analysis_status": "completed",
            "whale_tier": portfolio.whale_tier,
            "portfolio_summary": {
                "total_value_usd": portfolio.total_portfolio_value,
                "num_holdings": portfolio.num_holdings,
                "diversity_score": portfolio.portfolio_diversity_score,
                "risk_profile": portfolio.risk_profile,
                "performance_score": portfolio.performance_score,
                "activity_level": portfolio.activity_level,
                "last_active_hours": portfolio.last_active_hours
            },
            "top_holdings": [
                {
                    "contract_address": h.contract_address,
                    "token_symbol": h.token_symbol,
                    "token_name": h.token_name,
                    "balance_usd": h.balance_usd,
                    "percentage_of_portfolio": h.percentage_of_portfolio,
                    "market_cap": h.market_cap,
                    "age_days": h.age_days,
                    "last_transaction_hours": h.last_transaction_hours,
                    "current_price": h.current_price
                }
                for h in portfolio.top_holdings[:5]  # Top 5 holdings
            ],
            "recent_transactions": [
                {
                    "action": t.action,
                    "token_symbol": t.token_symbol,
                    "amount_usd": t.amount_usd,
                    "hours_ago": (datetime.now() - t.timestamp).total_seconds() / 3600,
                    "significance": t.significance,
                    "confidence": t.confidence
                }
                for t in portfolio.recent_transactions[:5]  # Last 5 transactions
            ],
            "alpha_signals": portfolio.alpha_signals,
            "api_version": "3.2.0",
            "analysis_timestamp": time.time()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"API error analyzing whale portfolio: {e}")
        return {
            "error": "Analysis failed",
            "wallet_address": wallet_address,
            "details": str(e)
        }

async def get_alpha_discoveries_api(limit: int = 10) -> Dict[str, Any]:
    """API wrapper for alpha discoveries"""
    try:
        discoveries = await whale_portfolio_tracker.get_alpha_discoveries(limit)
        
        return {
            "status": "completed",
            "total_discoveries": len(discoveries),
            "alpha_discoveries": discoveries,
            "analysis_timestamp": time.time(),
            "api_version": "3.2.0"
        }
        
    except Exception as e:
        logger.error(f"API error getting alpha discoveries: {e}")
        return {
            "error": "Alpha discovery failed",
            "details": str(e)
        }

# Cleanup function
async def cleanup_whale_portfolio_tracker():
    """Cleanup resources"""
    await whale_portfolio_tracker.close()

if __name__ == "__main__":
    async def test_whale_portfolio():
        # Test whale portfolio analysis
        wallet = "8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj"  # Mega whale
        result = await analyze_whale_portfolio_api(wallet)
        print(json.dumps(result, indent=2, default=str))
        
        # Test alpha discoveries
        alpha_result = await get_alpha_discoveries_api(5)
        print("\n" + "="*50)
        print("ALPHA DISCOVERIES:")
        print(json.dumps(alpha_result, indent=2, default=str))
        
        await cleanup_whale_portfolio_tracker()
    
    # Run test
    asyncio.run(test_whale_portfolio())