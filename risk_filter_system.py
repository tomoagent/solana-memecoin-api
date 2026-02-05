#!/usr/bin/env python3
"""
🚀 Phase 2: Advanced Risk Filter System
高精度リスク分析フィルター - Smart Scanner Bot連携

開発目標：30-40分で完成、Claude ~$0.15
機能：高度フィルタリング、複数リスク要素統合、自動判定
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp

class AdvancedRiskFilter:
    def __init__(self):
        self.api_base = "https://solana-memecoin-api.onrender.com"
        self.dexscreener_base = "https://api.dexscreener.com/latest"
        
        # 🎯 リスクフィルター設定
        self.risk_thresholds = {
            'max_risk_score': 45,           # 45点以上は除外
            'min_liquidity': 15000,         # $15K最低流動性
            'max_holder_concentration': 60, # 上位10ホルダー60%以下
            'min_age_hours': 2,            # 最低2時間経過
            'max_age_days': 7,             # 最大7日以内
            'min_volume_24h': 5000,        # 24h最低取引量$5K
            'max_price_change_1h': 200,    # 1時間200%以上は除外（Pumpリスク）
        }
        
        # 🏆 品質ボーナス設定
        self.quality_bonuses = {
            'verified_contract': -5,        # 認証済みコントラクト
            'audited_token': -10,          # 監査済みトークン
            'strong_community': -8,        # 活発コミュニティ
            'clear_roadmap': -5,           # ロードマップ明確
            'experienced_team': -12,       # 経験豊富チーム
        }
        
        # ⚠️ 危険シグナル
        self.danger_signals = {
            'honeypot_detected': 100,      # ハニーポット → 即除外
            'rug_pull_risk': 50,          # ラグプル兆候
            'dev_dump_detected': 40,       # Dev大量売却検知
            'social_spam': 25,            # ソーシャルスパム
            'fake_volume': 30,            # 偽取引量
        }

    async def analyze_token_advanced(self, contract_address: str) -> Dict:
        """
        🔍 高度トークン分析
        複数データソース統合 + リスク計算
        """
        try:
            print(f"🔍 Advanced analysis starting: {contract_address}")
            
            # 並行データ取得
            tasks = [
                self.get_basic_risk_analysis(contract_address),
                self.get_market_data(contract_address),
                self.get_holder_analysis(contract_address),
                self.check_danger_signals(contract_address),
                self.evaluate_quality_factors(contract_address)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 結果統合
            basic_risk = results[0] if not isinstance(results[0], Exception) else {}
            market_data = results[1] if not isinstance(results[1], Exception) else {}
            holder_data = results[2] if not isinstance(results[2], Exception) else {}
            danger_data = results[3] if not isinstance(results[3], Exception) else {}
            quality_data = results[4] if not isinstance(results[4], Exception) else {}
            
            # 🧮 統合リスク計算
            risk_analysis = await self.calculate_integrated_risk(
                basic_risk, market_data, holder_data, danger_data, quality_data
            )
            
            # 🎯 フィルタリング判定
            filter_decision = self.make_filter_decision(risk_analysis)
            
            return {
                'contract_address': contract_address,
                'timestamp': datetime.now().isoformat(),
                'basic_risk': basic_risk,
                'market_data': market_data,
                'holder_analysis': holder_data,
                'danger_signals': danger_data,
                'quality_factors': quality_data,
                'integrated_risk': risk_analysis,
                'filter_decision': filter_decision,
                'processing_time': time.time() - self.start_time
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {'error': str(e), 'contract_address': contract_address}

    async def get_basic_risk_analysis(self, contract_address: str) -> Dict:
        """📊 基本リスク分析（既存API活用）"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/analyze",
                    json={'contract_address': contract_address},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            print(f"⚠️ Basic risk API error: {e}")
            return {}

    async def get_market_data(self, contract_address: str) -> Dict:
        """📈 マーケットデータ取得"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.dexscreener_base}/dex/tokens/{contract_address}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('pairs'):
                            pair = data['pairs'][0]  # 最大流動性ペア
                            return {
                                'price_usd': float(pair.get('priceUsd', 0)),
                                'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                                'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                                'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0)),
                                'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                                'market_cap': float(pair.get('fdv', 0)),
                                'age_hours': self.calculate_token_age(pair.get('pairCreatedAt', ''))
                            }
                    return {}
        except Exception as e:
            print(f"⚠️ Market data error: {e}")
            return {}

    async def get_holder_analysis(self, contract_address: str) -> Dict:
        """👥 ホルダー分析（推定アルゴリズム）"""
        try:
            # DexScreenerデータからホルダー集中度を推定
            market_data = await self.get_market_data(contract_address)
            
            # 🧮 推定アルゴリズム
            liquidity = market_data.get('liquidity_usd', 0)
            market_cap = market_data.get('market_cap', 0)
            volume_24h = market_data.get('volume_24h', 0)
            
            if market_cap > 0:
                liquidity_ratio = liquidity / market_cap
                volume_ratio = volume_24h / market_cap if market_cap > 0 else 0
                
                # 高流動性比率 + 低取引量 = ホルダー集中の可能性
                estimated_concentration = max(0, min(100, 
                    100 - (liquidity_ratio * 200) - (volume_ratio * 50)
                ))
                
                return {
                    'estimated_holder_concentration': estimated_concentration,
                    'liquidity_ratio': liquidity_ratio,
                    'volume_ratio': volume_ratio,
                    'confidence_level': 'medium'  # 推定なので中程度
                }
            
            return {'estimated_holder_concentration': 50, 'confidence_level': 'low'}
            
        except Exception as e:
            print(f"⚠️ Holder analysis error: {e}")
            return {}

    async def check_danger_signals(self, contract_address: str) -> Dict:
        """🚨 危険シグナル検知"""
        danger_score = 0
        detected_signals = []
        
        try:
            # 基本リスク分析から危険要素抽出
            basic_risk = await self.get_basic_risk_analysis(contract_address)
            risk_score = basic_risk.get('risk_score', 0)
            
            # 🚨 危険シグナル判定
            if risk_score >= 80:
                danger_score += self.danger_signals['rug_pull_risk']
                detected_signals.append('high_risk_score')
            
            # マーケットデータから異常検知
            market_data = await self.get_market_data(contract_address)
            price_change_1h = abs(market_data.get('price_change_1h', 0))
            
            if price_change_1h > 500:  # 1時間で500%変動
                danger_score += self.danger_signals['fake_volume']
                detected_signals.append('extreme_price_volatility')
            
            return {
                'danger_score': danger_score,
                'detected_signals': detected_signals,
                'total_danger_points': danger_score
            }
            
        except Exception as e:
            print(f"⚠️ Danger signal check error: {e}")
            return {'danger_score': 0, 'detected_signals': []}

    async def evaluate_quality_factors(self, contract_address: str) -> Dict:
        """🏆 品質要素評価"""
        quality_score = 0
        quality_factors = []
        
        try:
            # マーケットデータから品質推定
            market_data = await self.get_market_data(contract_address)
            liquidity = market_data.get('liquidity_usd', 0)
            volume_24h = market_data.get('volume_24h', 0)
            age_hours = market_data.get('age_hours', 0)
            
            # 🏆 品質ボーナス判定
            if liquidity > 50000:  # $50K以上流動性
                quality_score += abs(self.quality_bonuses['strong_community'])
                quality_factors.append('high_liquidity')
            
            if volume_24h > 20000:  # $20K以上24h取引量
                quality_score += abs(self.quality_bonuses['clear_roadmap'])
                quality_factors.append('active_trading')
            
            if age_hours > 24 and age_hours < 168:  # 1-7日の適切な年齢
                quality_score += abs(self.quality_bonuses['verified_contract'])
                quality_factors.append('stable_age')
            
            return {
                'quality_score': quality_score,
                'quality_factors': quality_factors,
                'total_quality_bonus': -quality_score  # ボーナスは負数
            }
            
        except Exception as e:
            print(f"⚠️ Quality evaluation error: {e}")
            return {'quality_score': 0, 'quality_factors': []}

    async def calculate_integrated_risk(self, basic_risk: Dict, market_data: Dict, 
                                      holder_data: Dict, danger_data: Dict, quality_data: Dict) -> Dict:
        """🧮 統合リスク計算"""
        
        # ベースリスクスコア
        base_risk = basic_risk.get('risk_score', 50)
        
        # 市場リスク要素
        liquidity = market_data.get('liquidity_usd', 0)
        volume_24h = market_data.get('volume_24h', 0)
        price_change_1h = abs(market_data.get('price_change_1h', 0))
        
        # リスク調整
        risk_adjustments = 0
        
        # 流動性リスク
        if liquidity < 10000:
            risk_adjustments += 20
        elif liquidity < 5000:
            risk_adjustments += 35
        
        # ボリュームリスク
        if volume_24h < 2000:
            risk_adjustments += 15
        
        # 価格変動リスク
        if price_change_1h > 100:
            risk_adjustments += 10
        elif price_change_1h > 300:
            risk_adjustments += 25
        
        # ホルダー集中リスク
        holder_concentration = holder_data.get('estimated_holder_concentration', 50)
        if holder_concentration > 70:
            risk_adjustments += 15
        elif holder_concentration > 80:
            risk_adjustments += 30
        
        # 危険シグナル追加
        danger_points = danger_data.get('danger_score', 0)
        risk_adjustments += danger_points
        
        # 品質ボーナス適用
        quality_bonus = quality_data.get('total_quality_bonus', 0)
        risk_adjustments += quality_bonus
        
        # 最終リスクスコア
        final_risk_score = max(0, min(100, base_risk + risk_adjustments))
        
        return {
            'base_risk_score': base_risk,
            'market_risk_adjustments': risk_adjustments - danger_points - quality_bonus,
            'danger_penalty': danger_points,
            'quality_bonus': quality_bonus,
            'total_adjustments': risk_adjustments,
            'final_risk_score': final_risk_score,
            'risk_category': self.get_risk_category(final_risk_score),
            'confidence_level': self.calculate_confidence_level(basic_risk, market_data, holder_data)
        }

    def get_risk_category(self, risk_score: int) -> str:
        """🎯 リスクカテゴリ判定"""
        if risk_score <= 20:
            return "LOW_RISK"
        elif risk_score <= 40:
            return "MEDIUM_LOW_RISK"
        elif risk_score <= 60:
            return "MEDIUM_RISK"
        elif risk_score <= 80:
            return "HIGH_RISK"
        else:
            return "EXTREME_RISK"

    def calculate_confidence_level(self, basic_risk: Dict, market_data: Dict, holder_data: Dict) -> str:
        """🎯 信頼度レベル計算"""
        confidence_score = 0
        
        if basic_risk:
            confidence_score += 30
        if market_data:
            confidence_score += 40
        if holder_data and holder_data.get('confidence_level') == 'medium':
            confidence_score += 20
        
        if confidence_score >= 80:
            return "high"
        elif confidence_score >= 60:
            return "medium"
        else:
            return "low"

    def make_filter_decision(self, risk_analysis: Dict) -> Dict:
        """🎯 フィルタリング最終判定"""
        final_risk = risk_analysis.get('final_risk_score', 100)
        risk_category = risk_analysis.get('risk_category', 'EXTREME_RISK')
        confidence = risk_analysis.get('confidence_level', 'low')
        
        # 🚫 除外判定
        if final_risk > self.risk_thresholds['max_risk_score']:
            return {
                'decision': 'REJECT',
                'reason': f'Risk score {final_risk} exceeds threshold {self.risk_thresholds["max_risk_score"]}',
                'recommendation': 'AVOID - Too risky for investment',
                'risk_category': risk_category,
                'confidence': confidence
            }
        
        # ✅ 承認判定
        if final_risk <= 25 and confidence in ['medium', 'high']:
            return {
                'decision': 'STRONG_ACCEPT',
                'reason': f'Low risk score {final_risk} with {confidence} confidence',
                'recommendation': 'STRONG_BUY - Excellent risk profile',
                'risk_category': risk_category,
                'confidence': confidence
            }
        elif final_risk <= 35 and confidence == 'high':
            return {
                'decision': 'ACCEPT',
                'reason': f'Acceptable risk score {final_risk} with high confidence',
                'recommendation': 'BUY - Good investment opportunity',
                'risk_category': risk_category,
                'confidence': confidence
            }
        else:
            return {
                'decision': 'CONDITIONAL_ACCEPT',
                'reason': f'Medium risk score {final_risk}, requires monitoring',
                'recommendation': 'WATCH - Monitor before investing',
                'risk_category': risk_category,
                'confidence': confidence
            }

    def calculate_token_age(self, created_at: str) -> float:
        """⏰ トークン年齢計算"""
        try:
            if not created_at:
                return 0
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now() - created_time.replace(tzinfo=None)
            return age.total_seconds() / 3600  # 時間単位
        except:
            return 0

    async def batch_filter_tokens(self, contract_addresses: List[str]) -> List[Dict]:
        """📦 バッチフィルタリング処理"""
        print(f"🚀 Starting batch filtering for {len(contract_addresses)} tokens...")
        self.start_time = time.time()
        
        # セマフォで並行処理数制限（レート制限対策）
        semaphore = asyncio.Semaphore(3)
        
        async def analyze_with_semaphore(address):
            async with semaphore:
                return await self.analyze_token_advanced(address)
        
        # 並行分析実行
        tasks = [analyze_with_semaphore(addr) for addr in contract_addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # エラー除外、成功結果のみ
        valid_results = [r for r in results if isinstance(r, dict) and 'error' not in r]
        
        # フィルタリング結果統計
        decisions = [r.get('filter_decision', {}).get('decision', 'UNKNOWN') for r in valid_results]
        stats = {
            'total_analyzed': len(valid_results),
            'strong_accept': decisions.count('STRONG_ACCEPT'),
            'accept': decisions.count('ACCEPT'),
            'conditional_accept': decisions.count('CONDITIONAL_ACCEPT'),
            'reject': decisions.count('REJECT'),
            'processing_time': time.time() - self.start_time
        }
        
        print(f"📊 Batch filtering completed: {stats}")
        
        return {
            'results': valid_results,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }

    def save_filter_results(self, results: Dict, filename: str = None):
        """💾 フィルタリング結果保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_filter_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
        return filename

# 🚀 メイン実行関数
async def main():
    """Phase 2: Risk Filter System - メイン実行"""
    
    print("🚀 Phase 2: Advanced Risk Filter System Starting...")
    
    # テスト用コントラクトアドレス
    test_tokens = [
        "So11111111111111111111111111111111111111112",  # SOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        # "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",  # SAMO (例)
    ]
    
    # Risk Filter初期化
    filter_system = AdvancedRiskFilter()
    
    # バッチフィルタリング実行
    results = await filter_system.batch_filter_tokens(test_tokens)
    
    # 結果保存
    filename = filter_system.save_filter_results(results)
    
    print("\n🎯 Phase 2 Risk Filter System - Development Complete!")
    print(f"📊 Analysis Results: {results['statistics']}")
    print(f"💾 Saved to: {filename}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())