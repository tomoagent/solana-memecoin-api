"""
DexScreener API Integration
Phase 2 implementation - Tonight's second hour  
Real-time market data from DexScreener
"""

import requests
import asyncio
import time
import json
from typing import Dict, Any, Optional, List

class DexScreenerAPI:
    """
    DexScreener API client for real-time Solana token data
    """
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Solana-Memecoin-Analyzer/3.0',
            'Accept': 'application/json'
        })
    
    async def get_token_data(self, contract_address: str) -> Dict[str, Any]:
        """
        Get comprehensive token data from DexScreener
        Returns market cap, volume, price changes, liquidity info
        """
        
        print(f"📈 Fetching DexScreener data for {contract_address}")
        start_time = time.time()
        
        try:
            # DexScreener endpoint for Solana tokens
            url = f"{self.base_url}/tokens/{contract_address}"
            
            print(f"🌐 API Request: {url}")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ DexScreener API error: {response.status_code}")
                return self._create_error_response("api_error", response.status_code)
            
            data = response.json()
            
            if not data.get('pairs'):
                print(f"⚠️ No trading pairs found for {contract_address}")
                return self._create_error_response("no_pairs", "Token not found on DexScreener")
            
            # Process the response data
            processed_data = self._process_dexscreener_response(data, contract_address)
            
            elapsed_time = round(time.time() - start_time, 2)
            processed_data['fetch_time'] = elapsed_time
            
            print(f"✅ DexScreener data fetched in {elapsed_time}s")
            return processed_data
            
        except requests.exceptions.Timeout:
            print("⏰ DexScreener API timeout")
            return self._create_error_response("timeout", "API request timed out")
            
        except requests.exceptions.RequestException as e:
            print(f"🌐 DexScreener network error: {e}")
            return self._create_error_response("network_error", str(e))
            
        except json.JSONDecodeError as e:
            print(f"📄 DexScreener JSON parse error: {e}")
            return self._create_error_response("parse_error", str(e))
            
        except Exception as e:
            print(f"💥 Unexpected DexScreener error: {e}")
            return self._create_error_response("unknown_error", str(e))
    
    def _process_dexscreener_response(self, data: Dict[str, Any], contract_address: str) -> Dict[str, Any]:
        """
        Process raw DexScreener API response into our standardized format
        """
        
        pairs = data.get('pairs', [])
        
        if not pairs:
            return self._create_error_response("no_data", "No pairs available")
        
        # Find the best pair (highest liquidity or volume)
        best_pair = self._find_best_pair(pairs)
        
        if not best_pair:
            return self._create_error_response("no_valid_pair", "No valid trading pair found")
        
        # Extract market data
        market_data = self._extract_market_data(best_pair)
        
        # Extract liquidity information  
        liquidity_data = self._extract_liquidity_data(best_pair)
        
        # Extract price performance
        price_data = self._extract_price_data(best_pair)
        
        # Calculate derived metrics
        derived_metrics = self._calculate_derived_metrics(best_pair)
        
        return {
            "success": True,
            "source": "dexscreener.com",
            "contract_address": contract_address,
            "pair_address": best_pair.get('pairAddress'),
            "dex": best_pair.get('dexId', 'unknown'),
            "market_data": market_data,
            "liquidity_data": liquidity_data,
            "price_data": price_data,
            "derived_metrics": derived_metrics,
            "raw_pair_data": best_pair,  # Keep raw data for debugging
            "timestamp": time.time()
        }
    
    def _find_best_pair(self, pairs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the best trading pair based on liquidity and volume
        """
        
        valid_pairs = []
        
        for pair in pairs:
            # Filter for Solana pairs and exclude very small pairs
            if (pair.get('chainId') == 'solana' and 
                pair.get('liquidity', {}).get('usd', 0) > 1000):
                valid_pairs.append(pair)
        
        if not valid_pairs:
            return pairs[0] if pairs else None
        
        # Sort by liquidity (descending), then by volume
        def pair_score(pair):
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            volume_24h = pair.get('volume', {}).get('h24', 0)
            return (liquidity, volume_24h)
        
        best_pair = max(valid_pairs, key=pair_score)
        return best_pair
    
    def _extract_market_data(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic market data from pair
        """
        
        return {
            "price_usd": pair.get('priceUsd'),
            "market_cap": pair.get('fdv'),  # Fully Diluted Valuation
            "volume_24h": pair.get('volume', {}).get('h24'),
            "volume_6h": pair.get('volume', {}).get('h6'),
            "volume_1h": pair.get('volume', {}).get('h1'),
            "transactions_24h": pair.get('txns', {}).get('h24', {}).get('buys', 0) + 
                              pair.get('txns', {}).get('h24', {}).get('sells', 0),
            "buys_24h": pair.get('txns', {}).get('h24', {}).get('buys', 0),
            "sells_24h": pair.get('txns', {}).get('h24', {}).get('sells', 0)
        }
    
    def _extract_liquidity_data(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract liquidity information from pair
        """
        
        liquidity = pair.get('liquidity', {})
        
        return {
            "liquidity_usd": liquidity.get('usd'),
            "liquidity_base": liquidity.get('base'),
            "liquidity_quote": liquidity.get('quote'),
            "pair_created_at": pair.get('pairCreatedAt'),
            "dex_id": pair.get('dexId'),
            "pair_address": pair.get('pairAddress')
        }
    
    def _extract_price_data(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract price performance data
        """
        
        price_change = pair.get('priceChange', {})
        
        return {
            "price_change_5m": price_change.get('m5'),
            "price_change_1h": price_change.get('h1'), 
            "price_change_6h": price_change.get('h6'),
            "price_change_24h": price_change.get('h24'),
            "current_price": pair.get('priceUsd'),
            "price_native": pair.get('priceNative')
        }
    
    def _calculate_derived_metrics(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived metrics for risk assessment
        """
        
        volume_24h = pair.get('volume', {}).get('h24', 0)
        market_cap = pair.get('fdv', 0)
        liquidity_usd = pair.get('liquidity', {}).get('usd', 0)
        
        # Volume-to-MarketCap ratio
        volume_mcap_ratio = (volume_24h / market_cap) if market_cap > 0 else 0
        
        # Liquidity-to-MarketCap ratio  
        liquidity_mcap_ratio = (liquidity_usd / market_cap) if market_cap > 0 else 0
        
        # Buy/Sell pressure
        buys_24h = pair.get('txns', {}).get('h24', {}).get('buys', 0)
        sells_24h = pair.get('txns', {}).get('h24', {}).get('sells', 0)
        total_txns = buys_24h + sells_24h
        
        buy_pressure = (buys_24h / total_txns) if total_txns > 0 else 0.5
        
        # Age calculation
        created_at = pair.get('pairCreatedAt')
        age_hours = None
        if created_at:
            try:
                age_ms = time.time() * 1000 - created_at
                age_hours = age_ms / (1000 * 60 * 60)
            except:
                age_hours = None
        
        return {
            "volume_mcap_ratio": round(volume_mcap_ratio, 4),
            "liquidity_mcap_ratio": round(liquidity_mcap_ratio, 4),
            "buy_pressure": round(buy_pressure, 3),
            "age_hours": round(age_hours, 1) if age_hours else None,
            "trading_activity": "High" if volume_24h > 10000 else "Medium" if volume_24h > 1000 else "Low"
        }
    
    def _create_error_response(self, error_type: str, error_details: Any) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        
        return {
            "success": False,
            "error_type": error_type,
            "error_details": error_details,
            "market_data": {"error": "Data unavailable"},
            "liquidity_data": {"error": "Data unavailable"}, 
            "price_data": {"error": "Data unavailable"},
            "derived_metrics": {"error": "Data unavailable"},
            "timestamp": time.time()
        }

# Standalone test function
async def test_dexscreener_api():
    """
    Test DexScreener API with known tokens
    """
    
    api = DexScreenerAPI()
    
    test_tokens = [
        ("BONK", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
        ("USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    ]
    
    for name, address in test_tokens:
        print(f"\n🧪 Testing {name} ({address[:8]}...)")
        
        result = await api.get_token_data(address)
        
        if result["success"]:
            print(f"✅ Success! Fetch time: {result.get('fetch_time')}s")
            print(f"💰 Market cap: ${result['market_data'].get('market_cap', 'N/A')}")
            print(f"📊 Volume 24h: ${result['market_data'].get('volume_24h', 'N/A')}")
            print(f"📈 Price change 24h: {result['price_data'].get('price_change_24h', 'N/A')}%")
            print(f"💧 Liquidity: ${result['liquidity_data'].get('liquidity_usd', 'N/A')}")
        else:
            print(f"❌ Failed: {result['error_type']} - {result['error_details']}")

# Main execution
if __name__ == "__main__":
    asyncio.run(test_dexscreener_api())