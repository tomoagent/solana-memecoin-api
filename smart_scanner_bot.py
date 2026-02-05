#!/usr/bin/env python3
"""
Smart Scanner Bot - Phase 1
自動memecoin検出 + スマートマネー売り検知 + 利確システム

Features:
- 新規memecoin自動検出（DexScreener API）
- MC範囲フィルタリング ($30K-500K)
- スマートマネー売り検知 (利確トリガー)
- 危険度自動判定
- 自動保存システム

Author: tomo (とも)
Date: 2026-02-06
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartScannerBot:
    """Smart Scanner Bot - 完全自動memecoin検出・分析・売り検知システム"""
    
    def __init__(self):
        self.dexscreener_base = "https://api.dexscreener.com/latest"
        self.risk_analyzer_url = "https://solana-memecoin-api.onrender.com"
        
        # 設定
        self.mc_min = 30000      # $30K minimum
        self.mc_max = 500000     # $500K maximum  
        self.risk_threshold = 60  # リスク60以下のみ
        self.smart_money_threshold = 50  # Smart Money Score 50以上
        
        # データ保存
        self.detected_tokens = []
        self.monitored_positions = {}  # 監視中ポジション
        self.scan_history = []
        
        # Smart Money売り検知設定
        self.sell_trigger_threshold = 0.15  # 15%以上の売り圧で利確
        self.whale_sell_alert_threshold = 50000  # $50K以上の売りで警告
        
        logger.info("🤖 Smart Scanner Bot initialized!")
        logger.info(f"MC Range: ${self.mc_min:,} - ${self.mc_max:,}")
        logger.info(f"Risk Threshold: {self.risk_threshold}/100")
        logger.info(f"Smart Money売り検知: {self.sell_trigger_threshold*100}%で利確")

    async def scan_new_tokens(self, session: aiohttp.ClientSession) -> List[Dict]:
        """新規トークン検出（Search APIを使用）"""
        logger.info("🔍 新規トークン検出開始...")
        
        try:
            # 複数キーワードで検索して新しいペアを見つける
            search_queries = ["solana", "SOL", "meme", "pump", "moon"]
            all_pairs = []
            
            for query in search_queries:
                url = f"{self.dexscreener_base}/dex/search?q={query}"
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"DexScreener search error for '{query}': {response.status}")
                        continue
                    
                    data = await response.json()
                    pairs = data.get('pairs', [])
                    
                    # Solanaペアのみフィルター
                    solana_pairs = [p for p in pairs if p.get('chainId') == 'solana']
                    all_pairs.extend(solana_pairs)
                    logger.info(f"🔍 '{query}' search: {len(solana_pairs)} Solanaペア見つかりました")
                    
                    # レート制限対策（300 req/min）
                    await asyncio.sleep(0.5)
            
            # 重複除去（pairAddressベース）
            unique_pairs = {}
            for pair in all_pairs:
                pair_addr = pair.get('pairAddress')
                if pair_addr and pair_addr not in unique_pairs:
                    unique_pairs[pair_addr] = pair
            
            pairs = list(unique_pairs.values())
            logger.info(f"🔍 重複除去後: {len(pairs)}個のユニークペア")
                
            # MC範囲フィルタリング＋年齢フィルター（新しいトークン優先）
            filtered_tokens = []
            for pair in pairs[:100]:  # 最新100ペアをチェック
                if not pair.get('fdv') or not pair.get('baseToken'):
                    continue
                    
                mc = float(pair.get('fdv', 0))
                if not (self.mc_min <= mc <= self.mc_max):
                    continue
                
                # 新しいトークンのみ（7日以内）
                age_hours = self._calculate_token_age(pair)
                if age_hours > 168:  # 7日 = 168時間
                    continue
                
                token_data = {
                    'contract_address': pair['baseToken']['address'],
                    'symbol': pair['baseToken']['symbol'] or 'UNKNOWN',
                    'name': pair['baseToken']['name'] or 'Unknown Token',
                    'mc': mc,
                    'price': float(pair.get('priceUsd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                    'age_hours': age_hours,
                    'pair_address': pair.get('pairAddress'),
                    'dex_name': pair.get('dexId', ''),
                    'detected_at': datetime.now().isoformat()
                }
                filtered_tokens.append(token_data)
                
                logger.info(f"✅ 新規トークン検出: {len(filtered_tokens)}個 (MC範囲内)")
                return filtered_tokens
                
        except Exception as e:
            logger.error(f"❌ 新規トークン検出エラー: {e}")
            return []

    async def analyze_token_risk(self, session: aiohttp.ClientSession, token_data: Dict) -> Dict:
        """トークンリスク分析（既存APIを活用）"""
        try:
            url = f"{self.risk_analyzer_url}/analyze"
            payload = {"contract_address": token_data['contract_address']}
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Risk API error for {token_data['symbol']}: {response.status}")
                    return {"risk_score": 100, "analysis_success": False}
                
                risk_data = await response.json()
                logger.info(f"🔍 {token_data['symbol']}: リスクスコア {risk_data.get('risk_score', 'N/A')}/100")
                
                return {
                    **risk_data,
                    "analysis_success": True
                }
                
        except Exception as e:
            logger.error(f"❌ リスク分析エラー {token_data['symbol']}: {e}")
            return {"risk_score": 100, "analysis_success": False}

    async def check_smart_money_activity(self, session: aiohttp.ClientSession, token_data: Dict) -> Dict:
        """Smart Money活動チェック + 売り検知"""
        try:
            url = f"{self.risk_analyzer_url}/smart-money"
            payload = {"contract_address": token_data['contract_address']}
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Smart Money API error for {token_data['symbol']}: {response.status}")
                    return {"smart_money_score": 0, "whale_activity": "unknown", "sell_signal": False}
                
                smart_data = await response.json()
                
                # 売り検知ロジック
                sell_signal = self._detect_sell_pressure(smart_data)
                
                if sell_signal:
                    logger.warning(f"🚨 {token_data['symbol']}: Smart Money売り検知！利確推奨")
                
                logger.info(f"🐋 {token_data['symbol']}: Smart Money Score {smart_data.get('smart_money_score', 0)}/100")
                
                return {
                    **smart_data,
                    "sell_signal": sell_signal,
                    "analysis_success": True
                }
                
        except Exception as e:
            logger.error(f"❌ Smart Money分析エラー {token_data['symbol']}: {e}")
            return {"smart_money_score": 0, "whale_activity": "unknown", "sell_signal": False}

    def _detect_sell_pressure(self, smart_data: Dict) -> bool:
        """スマートマネー売り圧検知"""
        try:
            # Net flow分析
            net_flow = smart_data.get('whale_flows', {}).get('net_flow', 0)
            if net_flow < -self.sell_trigger_threshold:
                return True
            
            # 大口売り検知
            recent_sells = smart_data.get('recent_whale_activity', [])
            for activity in recent_sells:
                if activity.get('type') == 'sell' and activity.get('usd_value', 0) > self.whale_sell_alert_threshold:
                    return True
            
            # Smart Money confidence急落
            confidence = smart_data.get('confidence_score', 50)
            if confidence < 30:  # 30以下で危険信号
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 売り圧検知エラー: {e}")
            return False

    def _calculate_token_age(self, pair_data: Dict) -> float:
        """トークン年齢計算（時間）"""
        try:
            # DexScreener Search APIの場合
            created_at = pair_data.get('pairCreatedAt')
            if created_at:
                # UNIXタイムスタンプ（ミリ秒）を秒に変換
                if isinstance(created_at, (int, float)):
                    if created_at > 1e12:  # ミリ秒の場合
                        created_at = created_at / 1000
                    created_time = datetime.fromtimestamp(created_at)
                    age_hours = (datetime.now() - created_time).total_seconds() / 3600
                    return round(age_hours, 2)
            
            # フォールバック：ペア作成時間が無い場合は0（最新として扱う）
            return 0
        except Exception as e:
            logger.warning(f"年齢計算エラー: {e}")
            return 0

    async def process_token(self, session: aiohttp.ClientSession, token_data: Dict) -> Optional[Dict]:
        """トークン完全分析処理"""
        logger.info(f"🔄 分析中: {token_data['symbol']} ({token_data['name'][:30]}...)")
        
        # 並行分析実行
        risk_task = self.analyze_token_risk(session, token_data)
        smart_task = self.check_smart_money_activity(session, token_data)
        
        risk_result, smart_result = await asyncio.gather(risk_task, smart_task)
        
        # 総合判定
        risk_score = risk_result.get('risk_score', 100)
        smart_score = smart_result.get('smart_money_score', 0)
        sell_signal = smart_result.get('sell_signal', False)
        
        # フィルタリング
        if risk_score > self.risk_threshold:
            logger.info(f"❌ {token_data['symbol']}: リスク高 ({risk_score}/100) - スキップ")
            return None
        
        if smart_score < self.smart_money_threshold:
            logger.info(f"❌ {token_data['symbol']}: Smart Money Score低 ({smart_score}/100) - スキップ")
            return None
        
        # 合格トークン
        processed_token = {
            **token_data,
            **risk_result,
            **smart_result,
            'overall_score': self._calculate_overall_score(risk_score, smart_score),
            'recommendation': self._get_recommendation(risk_score, smart_score, sell_signal),
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {token_data['symbol']}: 合格! Overall Score: {processed_token['overall_score']}/100")
        if sell_signal:
            logger.warning(f"🚨 {token_data['symbol']}: 売りシグナル検出 - 利確推奨!")
        
        return processed_token

    def _calculate_overall_score(self, risk_score: float, smart_score: float) -> float:
        """総合スコア計算 (0-100, 高いほど良い)"""
        # リスクスコアは反転（低い方が良い）
        adjusted_risk = 100 - risk_score
        # 重み付け: Smart Money 60%, Risk 40%
        overall = (smart_score * 0.6) + (adjusted_risk * 0.4)
        return round(overall, 1)

    def _get_recommendation(self, risk_score: float, smart_score: float, sell_signal: bool) -> str:
        """推奨アクション"""
        if sell_signal:
            return "SELL_NOW - Smart Money売り検知"
        
        overall = self._calculate_overall_score(risk_score, smart_score)
        
        if overall >= 80:
            return "STRONG_BUY - 高確率案件"
        elif overall >= 70:
            return "BUY - 良好案件"  
        elif overall >= 60:
            return "WATCH - 監視継続"
        else:
            return "AVOID - 避ける"

    def save_results(self, tokens: List[Dict]):
        """結果保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 詳細結果
        filename = f"scan_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                'scan_timestamp': datetime.now().isoformat(),
                'total_detected': len(tokens),
                'mc_range': f"${self.mc_min:,} - ${self.mc_max:,}",
                'tokens': tokens
            }, f, indent=2)
        
        # サマリー
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tokens': len(tokens),
            'strong_buy': len([t for t in tokens if t['recommendation'] == 'STRONG_BUY']),
            'buy': len([t for t in tokens if t['recommendation'] == 'BUY']),
            'sell_signals': len([t for t in tokens if t.get('sell_signal', False)]),
            'avg_overall_score': round(sum(t['overall_score'] for t in tokens) / len(tokens), 1) if tokens else 0
        }
        
        logger.info(f"📊 スキャン完了サマリー:")
        logger.info(f"   総検出: {summary['total_tokens']}個")
        logger.info(f"   STRONG_BUY: {summary['strong_buy']}個")
        logger.info(f"   BUY: {summary['buy']}個") 
        logger.info(f"   売りシグナル: {summary['sell_signals']}個")
        logger.info(f"   平均スコア: {summary['avg_overall_score']}/100")
        logger.info(f"📁 結果保存: {filename}")

    async def run_scan(self):
        """メインスキャン実行"""
        logger.info("🚀 Smart Scanner Bot 開始!")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Step 1: 新規トークン検出
            new_tokens = await self.scan_new_tokens(session)
            if not new_tokens:
                logger.info("❌ 新規トークンが見つかりませんでした")
                return
            
            # Step 2: 並行分析処理
            logger.info(f"🔄 {len(new_tokens)}個のトークンを分析中...")
            tasks = [self.process_token(session, token) for token in new_tokens]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Step 3: 成功結果のみフィルタリング  
            qualified_tokens = [r for r in results if r and not isinstance(r, Exception)]
            
            if qualified_tokens:
                # Step 4: 結果保存
                self.save_results(qualified_tokens)
                
                # Step 5: 売りシグナル緊急通知
                sell_tokens = [t for t in qualified_tokens if t.get('sell_signal', False)]
                if sell_tokens:
                    logger.warning("🚨 緊急: 売りシグナル検出トークン:")
                    for token in sell_tokens:
                        logger.warning(f"   💰 {token['symbol']}: {token['recommendation']}")
            else:
                logger.info("❌ 条件を満たすトークンはありませんでした")
        
        elapsed = time.time() - start_time
        logger.info(f"✅ スキャン完了! 実行時間: {elapsed:.1f}秒")

# メイン実行
async def main():
    """メイン関数"""
    scanner = SmartScannerBot()
    await scanner.run_scan()

if __name__ == "__main__":
    print("🤖 Smart Scanner Bot - Phase 1")
    print("=" * 50)
    asyncio.run(main())