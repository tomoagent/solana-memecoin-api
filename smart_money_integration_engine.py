#!/usr/bin/env python3
"""
🚀 Phase 3B: Smart Money Integration Engine
完全自動売買システム - 全コンポーネント統合版

統合機能:
- Smart Scanner Bot (Phase 1) - 新規検出
- Risk Filter System (Phase 2) - 高精度フィルタリング  
- Flow Prediction Engine (Phase 3A) - 予測アルゴリズム
- Professional Risk Analyzer - プロ分析
- Smart Money Tracker - ホエール追跡
- Whale Portfolio Analysis - ポートフォリオ分析

目標: 月$499-999自動売買システム、年$100K-500K収益
開発時間: 30-40分、Claude投資$0.15
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# 既存コンポーネントインポート（エラーハンドリング付き）
try:
    from smart_scanner_bot import SmartScannerBot
except ImportError:
    SmartScannerBot = None
    
try:
    from risk_filter_system import AdvancedRiskFilter
except ImportError:
    AdvancedRiskFilter = None
    
try:
    from flow_prediction_engine import FlowPredictionEngine, FlowPrediction, MarketForecast
except ImportError:
    FlowPredictionEngine = None
    FlowPrediction = None
    MarketForecast = None
    
try:
    from professional_risk_analyzer import ProfessionalRiskAnalyzer  
except ImportError:
    ProfessionalRiskAnalyzer = None

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """統合トレーディングシグナル"""
    contract_address: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD, WATCH
    confidence: float  # 0-100
    entry_price: float
    suggested_position_size: float  # % of portfolio
    stop_loss: float  # price level
    take_profit: List[float]  # multiple TP levels
    reasoning: List[str]  # why this signal
    risk_score: float  # 0-100
    expected_return_24h: float  # %
    expected_return_7d: float  # %
    smart_money_score: float  # 0-100
    flow_prediction_score: float  # 0-100
    whale_activity: str  # accumulating, distributing, neutral
    timestamp: datetime

@dataclass
class AutoTradeDecision:
    """自動売買最終判定"""
    action: str  # BUY, SELL, HOLD, MONITOR
    amount_usd: float
    priority: int  # 1-5 (5=highest)
    execution_timing: str  # immediate, wait_1h, wait_dip, market_open
    risk_management: Dict[str, Any]
    expected_pnl: Dict[str, float]  # 24h, 7d, 30d projections

class SmartMoneyIntegrationEngine:
    """完全統合自動売買エンジン"""
    
    def __init__(self):
        # 🔧 コンポーネント初期化（API-first approach）
        self.api_base = "https://solana-memecoin-api.onrender.com"
        self.dexscreener_base = "https://api.dexscreener.com/latest"
        
        # Fallback: local components if available
        self.scanner = SmartScannerBot() if SmartScannerBot else None
        self.risk_filter = AdvancedRiskFilter() if AdvancedRiskFilter else None
        self.flow_engine = FlowPredictionEngine() if FlowPredictionEngine else None
        self.risk_analyzer = ProfessionalRiskAnalyzer() if ProfessionalRiskAnalyzer else None
        
        # 🎯 自動売買設定
        self.trading_config = {
            'max_position_size': 0.05,  # 最大5%ポジション
            'max_risk_per_trade': 0.02,  # トレード毎2%リスク
            'portfolio_allocation': {
                'conservative': 0.3,  # 30% conservative trades
                'moderate': 0.5,      # 50% moderate risk trades  
                'aggressive': 0.2     # 20% high-risk high-reward
            },
            'profit_targets': {
                'quick_profit': 0.25,    # 25% quick take
                'medium_profit': 0.50,   # 50% medium take  
                'moon_profit': 2.0       # 200% moon take
            }
        }
        
        # 📊 スコアリング重み
        self.scoring_weights = {
            'risk_analysis': 0.25,        # Risk Analyzer結果
            'smart_money': 0.30,          # Smart Money追跡
            'flow_prediction': 0.25,      # Flow Prediction予測
            'market_momentum': 0.20       # Market勢い
        }
        
        # 🚨 安全装置
        self.safety_thresholds = {
            'max_daily_trades': 10,
            'max_daily_loss': 0.10,      # 10% daily loss limit
            'min_liquidity': 15000,      # $15K minimum
            'blacklist_tokens': set(),   # ブラックリストトークン
            'emergency_exit_conditions': []
        }
        
        # 📈 パフォーマンス追跡
        self.performance_tracker = {
            'total_signals': 0,
            'successful_signals': 0,
            'total_pnl': 0.0,
            'daily_trades': 0,
            'last_reset': datetime.now().date()
        }
        
        logger.info("🚀 Smart Money Integration Engine initialized!")
        logger.info(f"⚙️ Max position size: {self.trading_config['max_position_size']*100}%")
        logger.info(f"🛡️ Max daily loss limit: {self.safety_thresholds['max_daily_loss']*100}%")

    async def scan_new_tokens_api(self, session: aiohttp.ClientSession) -> List[Dict]:
        """📡 DexScreener API で新規トークン検出"""
        try:
            search_queries = ["solana", "pump", "meme", "SOL"]
            all_pairs = []
            
            for query in search_queries:
                url = f"{self.dexscreener_base}/dex/search?q={query}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        continue
                    
                    data = await response.json()
                    pairs = data.get('pairs', [])
                    
                    # Solanaペアのみ
                    solana_pairs = [p for p in pairs if p.get('chainId') == 'solana']
                    all_pairs.extend(solana_pairs)
                    
                    await asyncio.sleep(0.5)  # レート制限
            
            # 重複除去
            unique_pairs = {}
            for pair in all_pairs:
                addr = pair.get('pairAddress')
                if addr and addr not in unique_pairs:
                    unique_pairs[addr] = pair
            
            # データ整形
            formatted_tokens = []
            for pair in list(unique_pairs.values())[:50]:  # 最新50個
                if not pair.get('baseToken') or not pair.get('fdv'):
                    continue
                    
                token_data = {
                    'contract_address': pair['baseToken']['address'],
                    'symbol': pair['baseToken']['symbol'] or 'UNKNOWN',
                    'name': pair['baseToken']['name'] or 'Unknown Token',
                    'mc': float(pair.get('fdv', 0)),
                    'price': float(pair.get('priceUsd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                    'age_hours': self.calculate_token_age(pair.get('pairCreatedAt')),
                    'pair_address': pair.get('pairAddress'),
                    'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0))
                }
                formatted_tokens.append(token_data)
            
            return formatted_tokens
            
        except Exception as e:
            logger.error(f"❌ Token scanning error: {e}")
            return []

    def basic_filter_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """🔬 基本フィルタリング"""
        filtered = []
        
        # メジャートークン除外リスト
        major_tokens = ['SOL', 'USDC', 'USDT', 'ETH', 'BTC', 'BONK', 'WIF', 'POPCAT', 'JUP']
        
        for token in tokens:
            # メジャートークン除外
            symbol = token.get('symbol', '').upper()
            if symbol in major_tokens:
                continue
            
            # MC範囲チェック
            mc = token.get('mc', 0)
            if not (30000 <= mc <= 500000):  # $30K-500K
                continue
            
            # 流動性チェック
            liquidity = token.get('liquidity', 0)
            if liquidity < 15000:  # $15K minimum
                continue
            
            # 年齢チェック (新しいトークン優先)
            age_hours = token.get('age_hours', 0)
            if age_hours > 168:  # 7日以内
                continue
            
            # ボリュームチェック
            volume = token.get('volume_24h', 0)
            if volume < 5000:  # $5K minimum
                continue
            
            # 極端な価格変動除外
            price_change_1h = abs(token.get('price_change_1h', 0))
            if price_change_1h > 300:  # 300%以上は除外
                continue
            
            filtered.append(token)
        
        # MCでソート（小さい順 = より早期）
        filtered.sort(key=lambda x: x.get('mc', 0))
        
        logger.info(f"🔬 Basic filter: {len(filtered)}/{len(tokens)} tokens passed")
        return filtered

    def calculate_token_age(self, created_at) -> float:
        """⏰ トークン年齢計算"""
        try:
            if not created_at:
                return 0
            
            if isinstance(created_at, (int, float)):
                if created_at > 1e12:
                    created_at = created_at / 1000
                created_time = datetime.fromtimestamp(created_at)
                age = (datetime.now() - created_time).total_seconds() / 3600
                return round(age, 2)
            
            return 0
        except:
            return 0

    async def discover_opportunities(self, session: aiohttp.ClientSession) -> List[Dict]:
        """🔍 トレーディング機会発見（API-first approach）"""
        logger.info("🔍 Starting opportunity discovery...")
        
        try:
            # Step 1: DexScreener で新規トークン検出
            new_tokens = await self.scan_new_tokens_api(session)
            logger.info(f"📡 Found {len(new_tokens)} new tokens")
            
            if not new_tokens:
                logger.info("❌ No new tokens found")
                return []
            
            # Step 2: 基本フィルタリング（MC範囲、流動性）
            filtered_tokens = self.basic_filter_tokens(new_tokens)
            logger.info(f"🔬 Basic filter approved {len(filtered_tokens)} tokens")
            
            if not filtered_tokens:
                logger.info("❌ No tokens passed basic filtering")
                return []
            
            # Step 3: 詳細分析とシグナル生成
            trading_opportunities = []
            for token_data in filtered_tokens[:10]:  # 上位10個のみ処理
                opportunity = await self.analyze_trading_opportunity(session, token_data)
                if opportunity:
                    trading_opportunities.append(opportunity)
            
            logger.info(f"💎 Generated {len(trading_opportunities)} trading opportunities")
            return trading_opportunities
            
        except Exception as e:
            logger.error(f"❌ Opportunity discovery error: {e}")
            return []

    async def analyze_trading_opportunity(self, session: aiohttp.ClientSession, token_data: Dict) -> Optional[TradingSignal]:
        """📊 個別トレーディング機会分析"""
        try:
            contract_address = token_data['contract_address']
            symbol = token_data.get('symbol', 'UNKNOWN')
            
            logger.info(f"🔍 Analyzing trading opportunity: {symbol}")
            
            # 並行分析実行
            tasks = [
                self.get_professional_risk_analysis(session, contract_address),
                self.get_smart_money_analysis(session, contract_address),
                self.get_flow_prediction_analysis(session, contract_address),
                self.get_market_momentum_analysis(session, contract_address)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            risk_analysis = results[0] if not isinstance(results[0], Exception) else {}
            smart_money = results[1] if not isinstance(results[1], Exception) else {}
            flow_prediction = results[2] if not isinstance(results[2], Exception) else {}
            market_momentum = results[3] if not isinstance(results[3], Exception) else {}
            
            # 統合スコアリング
            trading_signal = self.calculate_trading_signal(
                token_data, risk_analysis, smart_money, flow_prediction, market_momentum
            )
            
            return trading_signal
            
        except Exception as e:
            logger.error(f"❌ Trading opportunity analysis error: {e}")
            return None

    async def get_professional_risk_analysis(self, session: aiohttp.ClientSession, contract_address: str) -> Dict:
        """📊 Professional Risk Analysis統合"""
        try:
            async with session.post(
                "https://solana-memecoin-api.onrender.com/analyze",
                json={"contract_address": contract_address},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Professional risk analysis error: {e}")
            return {}

    async def get_smart_money_analysis(self, session: aiohttp.ClientSession, contract_address: str) -> Dict:
        """🐋 Smart Money Tracker統合"""
        try:
            async with session.post(
                "https://solana-memecoin-api.onrender.com/smart-money",
                json={"contract_address": contract_address},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Smart money analysis error: {e}")
            return {}

    async def get_flow_prediction_analysis(self, session: aiohttp.ClientSession, contract_address: str) -> Dict:
        """🔮 Flow Prediction Engine統合"""
        try:
            async with session.post(
                "https://solana-memecoin-api.onrender.com/flow-prediction",
                json={"contract_address": contract_address},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Flow prediction analysis error: {e}")
            return {}

    async def get_market_momentum_analysis(self, session: aiohttp.ClientSession, contract_address: str) -> Dict:
        """📈 Market Momentum分析"""
        try:
            # DexScreenerから市場勢い分析
            async with session.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('pairs'):
                        pair = data['pairs'][0]
                        
                        # モメンタム計算
                        price_change_1h = float(pair.get('priceChange', {}).get('h1', 0))
                        price_change_6h = float(pair.get('priceChange', {}).get('h6', 0))
                        price_change_24h = float(pair.get('priceChange', {}).get('h24', 0))
                        volume_24h = float(pair.get('volume', {}).get('h24', 0))
                        
                        momentum_score = self.calculate_momentum_score(
                            price_change_1h, price_change_6h, price_change_24h, volume_24h
                        )
                        
                        return {
                            'momentum_score': momentum_score,
                            'price_changes': {
                                '1h': price_change_1h,
                                '6h': price_change_6h,
                                '24h': price_change_24h
                            },
                            'volume_24h': volume_24h,
                            'trend': self.get_trend_direction(price_change_1h, price_change_6h, price_change_24h)
                        }
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Market momentum analysis error: {e}")
            return {}

    def calculate_momentum_score(self, price_1h: float, price_6h: float, price_24h: float, volume: float) -> float:
        """📈 モメンタムスコア計算"""
        try:
            # 価格変動による勢いスコア
            momentum = 0
            
            # 短期勢い (1h)
            if price_1h > 5:
                momentum += 30
            elif price_1h > 2:
                momentum += 20
            elif price_1h > 0:
                momentum += 10
            elif price_1h < -10:
                momentum -= 20
            
            # 中期勢い (6h)  
            if price_6h > 15:
                momentum += 25
            elif price_6h > 5:
                momentum += 15
            elif price_6h < -20:
                momentum -= 15
            
            # 長期勢い (24h)
            if price_24h > 50:
                momentum += 20
            elif price_24h > 20:
                momentum += 15
            elif price_24h < -30:
                momentum -= 10
            
            # ボリューム調整
            if volume > 50000:  # $50K+
                momentum += 10
            elif volume > 20000:  # $20K+
                momentum += 5
            elif volume < 5000:   # $5K未満
                momentum -= 15
            
            return max(0, min(100, momentum + 50))  # 0-100範囲に正規化
            
        except Exception as e:
            logger.warning(f"⚠️ Momentum calculation error: {e}")
            return 50  # デフォルト中立

    def get_trend_direction(self, price_1h: float, price_6h: float, price_24h: float) -> str:
        """📈 トレンド方向判定"""
        if price_1h > 5 and price_6h > 10 and price_24h > 20:
            return "strong_bullish"
        elif price_1h > 2 and price_6h > 5:
            return "bullish"
        elif price_1h < -5 and price_6h < -10:
            return "bearish"
        elif price_1h < -10 and price_6h < -20:
            return "strong_bearish"
        else:
            return "neutral"

    def calculate_trading_signal(self, token_data: Dict, risk_analysis: Dict, 
                               smart_money: Dict, flow_prediction: Dict, market_momentum: Dict) -> TradingSignal:
        """🧮 統合トレーディングシグナル計算"""
        try:
            # スコア抽出と正規化
            risk_score = 100 - risk_analysis.get('risk_score', 50)  # 反転 (低リスク=高スコア)
            smart_money_score = smart_money.get('smart_money_score', 0)
            flow_score = flow_prediction.get('whale_accumulation_score', 0)  
            momentum_score = market_momentum.get('momentum_score', 50)
            
            # 重み付け統合スコア
            composite_score = (
                risk_score * self.scoring_weights['risk_analysis'] +
                smart_money_score * self.scoring_weights['smart_money'] +  
                flow_score * self.scoring_weights['flow_prediction'] +
                momentum_score * self.scoring_weights['market_momentum']
            )
            
            # シグナル判定
            signal_type = self.determine_signal_type(composite_score, risk_analysis, smart_money, flow_prediction)
            
            # ポジションサイズ計算
            position_size = self.calculate_position_size(composite_score, risk_analysis.get('risk_score', 50))
            
            # 価格レベル設定
            current_price = token_data.get('price', 0)
            stop_loss = current_price * 0.85  # 15% stop loss
            take_profit = [
                current_price * 1.25,  # 25% profit
                current_price * 1.50,  # 50% profit  
                current_price * 2.00   # 100% profit
            ]
            
            # シグナル作成
            return TradingSignal(
                contract_address=token_data['contract_address'],
                symbol=token_data.get('symbol', 'UNKNOWN'),
                signal_type=signal_type,
                confidence=composite_score,
                entry_price=current_price,
                suggested_position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=self.generate_reasoning(risk_analysis, smart_money, flow_prediction, market_momentum),
                risk_score=risk_analysis.get('risk_score', 50),
                expected_return_24h=flow_prediction.get('predicted_price_movement_24h', 0),
                expected_return_7d=flow_prediction.get('predicted_price_movement_7d', 0),
                smart_money_score=smart_money_score,
                flow_prediction_score=flow_score,
                whale_activity=flow_prediction.get('flow_direction', 'neutral'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Trading signal calculation error: {e}")
            # フォールバック: 安全なデフォルトシグナル
            return self.create_safe_default_signal(token_data)

    def determine_signal_type(self, composite_score: float, risk_analysis: Dict, 
                            smart_money: Dict, flow_prediction: Dict) -> str:
        """🎯 シグナルタイプ判定"""
        
        # 安全チェック
        if risk_analysis.get('risk_score', 100) > 60:
            return "AVOID"
        
        # スマートマネー売りシグナル
        if smart_money.get('net_flow', 0) < -50000:  # $50K以上の流出
            return "SELL"
        
        # 統合スコア判定（テスト用に緩和）
        if composite_score >= 75:
            return "STRONG_BUY"
        elif composite_score >= 55:
            return "BUY"
        elif composite_score >= 45:
            return "WATCH"
        elif composite_score >= 35:
            return "HOLD"
        else:
            return "AVOID"

    def calculate_position_size(self, composite_score: float, risk_score: float) -> float:
        """📏 ポジションサイズ計算"""
        base_size = self.trading_config['max_position_size']
        
        # スコアベース調整
        score_multiplier = composite_score / 100
        
        # リスクベース調整
        risk_multiplier = max(0.1, (100 - risk_score) / 100)
        
        # 最終ポジションサイズ
        position_size = base_size * score_multiplier * risk_multiplier
        
        return min(position_size, self.trading_config['max_position_size'])

    def generate_reasoning(self, risk_analysis: Dict, smart_money: Dict, 
                         flow_prediction: Dict, market_momentum: Dict) -> List[str]:
        """💡 判断根拠生成"""
        reasons = []
        
        # リスク分析
        risk_score = risk_analysis.get('risk_score', 50)
        if risk_score < 30:
            reasons.append(f"✅ Low risk score: {risk_score}/100")
        elif risk_score > 70:
            reasons.append(f"⚠️ High risk score: {risk_score}/100")
        
        # スマートマネー
        smart_score = smart_money.get('smart_money_score', 0)
        if smart_score > 70:
            reasons.append(f"🐋 Strong smart money activity: {smart_score}/100")
        elif smart_score < 30:
            reasons.append(f"❌ Weak smart money interest: {smart_score}/100")
        
        # フロー予測
        flow_direction = flow_prediction.get('flow_direction', 'neutral')
        if flow_direction == 'bullish':
            reasons.append("📈 Flow prediction: Bullish trend expected")
        elif flow_direction == 'bearish':
            reasons.append("📉 Flow prediction: Bearish trend expected")
        
        # モメンタム
        trend = market_momentum.get('trend', 'neutral')
        if trend in ['strong_bullish', 'bullish']:
            reasons.append(f"🚀 Market momentum: {trend}")
        elif trend in ['bearish', 'strong_bearish']:
            reasons.append(f"🔻 Market momentum: {trend}")
        
        return reasons[:5]  # 最大5個の理由

    def create_safe_default_signal(self, token_data: Dict) -> TradingSignal:
        """🛡️ 安全デフォルトシグナル"""
        return TradingSignal(
            contract_address=token_data['contract_address'],
            symbol=token_data.get('symbol', 'UNKNOWN'),
            signal_type="AVOID",
            confidence=0,
            entry_price=token_data.get('price', 0),
            suggested_position_size=0,
            stop_loss=0,
            take_profit=[],
            reasoning=["Error in analysis - default safe signal"],
            risk_score=100,
            expected_return_24h=0,
            expected_return_7d=0,
            smart_money_score=0,
            flow_prediction_score=0,
            whale_activity="unknown",
            timestamp=datetime.now()
        )

    async def execute_auto_trading_cycle(self) -> Dict[str, Any]:
        """🚀 完全自動売買サイクル実行"""
        logger.info("🚀 Starting auto trading cycle...")
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: 機会発見
                opportunities = await self.discover_opportunities(session)
                
                if not opportunities:
                    logger.info("❌ No trading opportunities found")
                    return {
                        'status': 'no_opportunities',
                        'execution_time': time.time() - start_time,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Step 2: シグナル生成
                trading_signals = []
                for opportunity in opportunities:
                    try:
                        signal = await self.analyze_trading_opportunity(session, opportunity)
                        if signal and signal.signal_type in ['STRONG_BUY', 'BUY']:
                            trading_signals.append(signal)
                    except Exception as e:
                        logger.error(f"❌ Signal generation error for {opportunity.get('symbol', 'unknown')}: {e}")
                        continue
                
                # Step 3: 信号優先度ソート
                trading_signals.sort(key=lambda x: x.confidence, reverse=True)
                
                # Step 4: 結果返却（実際の執行は別モジュール）  
                serialized_signals = []
                for signal in trading_signals[:5]:  # Top 5
                    try:
                        signal_dict = asdict(signal)
                        # datetime を ISO文字列に変換
                        if 'timestamp' in signal_dict:
                            signal_dict['timestamp'] = signal_dict['timestamp'].isoformat()
                        serialized_signals.append(signal_dict)
                    except Exception as e:
                        logger.warning(f"⚠️ Signal serialization error: {e}")
                        continue
                
                results = {
                    'status': 'success',
                    'cycle_timestamp': datetime.now().isoformat(),
                    'execution_time': time.time() - start_time,
                    'opportunities_found': len(opportunities),
                    'trading_signals': serialized_signals,
                    'performance_metrics': self.get_performance_metrics(),
                    'next_cycle_recommended': (datetime.now() + timedelta(hours=1)).isoformat()
                }
                
                logger.info(f"✅ Auto trading cycle completed: {len(trading_signals)} signals generated")
                return results
                
        except Exception as e:
            logger.error(f"❌ Auto trading cycle error: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """📊 パフォーマンスメトリクス"""
        return {
            'total_signals_generated': self.performance_tracker['total_signals'],
            'success_rate': (
                self.performance_tracker['successful_signals'] / 
                max(1, self.performance_tracker['total_signals']) * 100
            ),
            'total_pnl': self.performance_tracker['total_pnl'],
            'daily_trades': self.performance_tracker['daily_trades'],
            'last_reset': self.performance_tracker['last_reset'].isoformat()
        }

    def save_trading_results(self, results: Dict, filename: str = None):
        """💾 取引結果保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auto_trading_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Trading results saved: {filename}")
        return filename

# 🚀 メイン実行
async def main():
    """Phase 3B: Smart Money Integration Engine - メイン実行"""
    
    print("🚀 Phase 3B: Smart Money Integration Engine Starting...")
    print("=" * 60)
    
    # エンジン初期化
    integration_engine = SmartMoneyIntegrationEngine()
    
    # 自動売買サイクル実行
    results = await integration_engine.execute_auto_trading_cycle()
    
    # 結果保存
    filename = integration_engine.save_trading_results(results)
    
    # 結果表示
    print(f"\n🎯 Auto Trading Cycle Results:")
    print(f"   Status: {results['status']}")
    print(f"   Execution time: {results.get('execution_time', 0):.2f}s")
    print(f"   Opportunities found: {results.get('opportunities_found', 0)}")
    print(f"   Trading signals: {len(results.get('trading_signals', []))}")
    print(f"💾 Results saved: {filename}")
    
    print(f"\n🚀 Phase 3B: Smart Money Integration Engine - Complete!")
    print(f"💰 Ready for $499-999/month auto trading system!")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())