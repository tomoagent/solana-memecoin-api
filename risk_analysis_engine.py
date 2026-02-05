"""
Real Risk Analysis Engine
Phase 3 implementation - Tonight's third hour
Combines rugcheck.xyz + DexScreener data for intelligent risk scoring
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Tuple
from rugcheck_scraper_advanced import scrape_rugcheck_data
from dexscreener_api import DexScreenerAPI

class RiskAnalysisEngine:
    """
    Advanced risk analysis engine that combines multiple data sources
    to produce accurate investment risk scores and recommendations
    """
    
    def __init__(self):
        self.dexscreener = DexScreenerAPI()
        
        # Risk factor weights (total = 100)
        self.weights = {
            "liquidity_risk": 30,      # LP locks, burns
            "holder_concentration": 25, # Top holder %
            "age_risk": 20,            # Token age
            "market_activity": 15,     # Volume/trading
            "price_volatility": 10     # Price stability
        }
        
        # Risk thresholds
        self.thresholds = {
            "age_hours": {
                "high_risk": 24,       # < 24 hours = high risk
                "medium_risk": 168,    # < 1 week = medium risk  
            },
            "top_holder_percent": {
                "high_risk": 50,       # > 50% = high risk
                "medium_risk": 30,     # > 30% = medium risk
            },
            "liquidity_mcap_ratio": {
                "low_threshold": 0.05,  # < 5% = risk
                "medium_threshold": 0.15 # > 15% = good
            },
            "volume_mcap_ratio": {
                "low_threshold": 0.01,  # < 1% = low activity
                "high_threshold": 0.5   # > 50% = high activity
            }
        }
    
    async def analyze_token_risk(self, contract_address: str) -> Dict[str, Any]:
        """
        Comprehensive risk analysis combining all data sources
        Returns detailed risk assessment with explanations
        """
        
        print(f"🧠 Starting comprehensive risk analysis for {contract_address}")
        start_time = time.time()
        
        # Initialize results structure
        analysis_result = {
            "contract_address": contract_address,
            "analysis_status": "in_progress",
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "confidence_score": 0,
            "data_sources": [],
            "risk_factors": {},
            "recommendations": [],
            "warnings": [],
            "investment_guidance": {},
            "analysis_timestamp": time.time()
        }
        
        try:
            # Gather data from all sources
            data_sources = await self._gather_all_data(contract_address)
            analysis_result["data_sources"] = list(data_sources.keys())
            
            # Calculate individual risk factors
            risk_factors = self._calculate_risk_factors(data_sources)
            analysis_result["risk_factors"] = risk_factors
            
            # Calculate overall risk score
            overall_score, confidence = self._calculate_overall_score(risk_factors)
            analysis_result["risk_score"] = overall_score
            analysis_result["confidence_score"] = confidence
            
            # Determine risk level
            analysis_result["risk_level"] = self._determine_risk_level(overall_score)
            
            # Generate intelligent recommendations
            recommendations = self._generate_recommendations(risk_factors, overall_score, data_sources)
            analysis_result["recommendations"] = recommendations
            
            # Generate warnings for high-risk factors
            warnings = self._generate_warnings(risk_factors, data_sources)
            analysis_result["warnings"] = warnings
            
            # Generate investment guidance
            investment_guidance = self._generate_investment_guidance(overall_score, risk_factors, data_sources)
            analysis_result["investment_guidance"] = investment_guidance
            
            # Final status
            analysis_result["analysis_status"] = "completed"
            
            elapsed_time = round(time.time() - start_time, 2)
            analysis_result["analysis_duration"] = elapsed_time
            
            print(f"✅ Comprehensive analysis completed in {elapsed_time}s - Risk: {overall_score}/100")
            
            return analysis_result
            
        except Exception as e:
            print(f"💥 Risk analysis failed: {e}")
            analysis_result["analysis_status"] = "failed"
            analysis_result["error"] = str(e)
            return analysis_result
    
    async def _gather_all_data(self, contract_address: str) -> Dict[str, Any]:
        """
        Gather data from all sources concurrently for speed
        """
        
        print("📊 Gathering data from all sources...")
        
        # Run data gathering concurrently
        rugcheck_task = scrape_rugcheck_data(contract_address)
        dexscreener_task = self.dexscreener.get_token_data(contract_address)
        
        # Wait for both to complete
        rugcheck_data, dexscreener_data = await asyncio.gather(
            rugcheck_task,
            dexscreener_task,
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(rugcheck_data, Exception):
            print(f"⚠️ rugcheck error: {rugcheck_data}")
            rugcheck_data = {"success": False, "error": str(rugcheck_data)}
            
        if isinstance(dexscreener_data, Exception):
            print(f"⚠️ DexScreener error: {dexscreener_data}")
            dexscreener_data = {"success": False, "error": str(dexscreener_data)}
        
        return {
            "rugcheck": rugcheck_data,
            "dexscreener": dexscreener_data
        }
    
    def _calculate_risk_factors(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate individual risk factor scores
        """
        
        rugcheck = data_sources.get("rugcheck", {})
        dexscreener = data_sources.get("dexscreener", {})
        
        risk_factors = {}
        
        # 1. Liquidity Risk Analysis (30 points)
        liquidity_score = self._analyze_liquidity_risk(rugcheck, dexscreener)
        risk_factors["liquidity_risk"] = liquidity_score
        
        # 2. Holder Concentration Risk (25 points) 
        concentration_score = self._analyze_holder_concentration(rugcheck, dexscreener)
        risk_factors["holder_concentration"] = concentration_score
        
        # 3. Age Risk Analysis (20 points)
        age_score = self._analyze_age_risk(rugcheck, dexscreener)
        risk_factors["age_risk"] = age_score
        
        # 4. Market Activity Risk (15 points)
        activity_score = self._analyze_market_activity(dexscreener)
        risk_factors["market_activity"] = activity_score
        
        # 5. Price Volatility Risk (10 points)
        volatility_score = self._analyze_price_volatility(dexscreener)
        risk_factors["price_volatility"] = volatility_score
        
        return risk_factors
    
    def _analyze_liquidity_risk(self, rugcheck: Dict, dexscreener: Dict) -> Dict[str, Any]:
        """
        Analyze liquidity-related risks
        """
        
        risk_score = 0
        max_score = self.weights["liquidity_risk"]
        confidence = 0
        details = []
        
        # Check rugcheck liquidity data
        if rugcheck.get("success") and rugcheck.get("liquidity"):
            liquidity = rugcheck["liquidity"]
            confidence += 0.6
            
            if liquidity.get("locked") == True:
                details.append("✅ Liquidity appears locked")
                risk_score += 0  # No risk
            elif liquidity.get("locked") == False:
                details.append("🚨 No liquidity lock detected")
                risk_score += max_score  # Maximum risk
            else:
                details.append("⚠️ Liquidity lock status unclear")
                risk_score += max_score * 0.7  # High risk due to uncertainty
        
        # Check DexScreener liquidity ratio
        if dexscreener.get("success") and dexscreener.get("derived_metrics"):
            metrics = dexscreener["derived_metrics"]
            liquidity_ratio = metrics.get("liquidity_mcap_ratio", 0)
            confidence += 0.4
            
            if liquidity_ratio < self.thresholds["liquidity_mcap_ratio"]["low_threshold"]:
                details.append(f"⚠️ Low liquidity ratio: {liquidity_ratio:.1%}")
                risk_score += max_score * 0.3
            elif liquidity_ratio > self.thresholds["liquidity_mcap_ratio"]["medium_threshold"]:
                details.append(f"✅ Good liquidity ratio: {liquidity_ratio:.1%}")
            else:
                details.append(f"ℹ️ Moderate liquidity ratio: {liquidity_ratio:.1%}")
                risk_score += max_score * 0.1
        
        # Cap at maximum score
        risk_score = min(risk_score, max_score)
        
        return {
            "score": round(risk_score, 1),
            "max_score": max_score,
            "confidence": round(confidence, 2),
            "details": details,
            "category": "liquidity_safety"
        }
    
    def _analyze_holder_concentration(self, rugcheck: Dict, dexscreener: Dict) -> Dict[str, Any]:
        """
        Analyze holder concentration risks
        """
        
        risk_score = 0
        max_score = self.weights["holder_concentration"]
        confidence = 0
        details = []
        
        # Check rugcheck holder data
        if rugcheck.get("success") and rugcheck.get("holder_data"):
            holder_data = rugcheck["holder_data"]
            top_holder_percent = holder_data.get("top_holder_percent")
            
            if top_holder_percent is not None:
                confidence += 0.8
                
                if top_holder_percent > self.thresholds["top_holder_percent"]["high_risk"]:
                    details.append(f"🚨 Very high concentration: Top holder {top_holder_percent}%")
                    risk_score += max_score
                elif top_holder_percent > self.thresholds["top_holder_percent"]["medium_risk"]:
                    details.append(f"⚠️ High concentration: Top holder {top_holder_percent}%") 
                    risk_score += max_score * 0.6
                else:
                    details.append(f"✅ Good distribution: Top holder {top_holder_percent}%")
                    risk_score += max_score * 0.1
            else:
                details.append("ℹ️ Holder concentration data unavailable")
                risk_score += max_score * 0.5  # Assume moderate risk
        else:
            details.append("⚠️ No holder distribution data available")
            risk_score += max_score * 0.5  # Assume moderate risk when data unavailable
        
        # Cap at maximum score
        risk_score = min(risk_score, max_score)
        
        return {
            "score": round(risk_score, 1),
            "max_score": max_score,
            "confidence": round(confidence, 2),
            "details": details,
            "category": "holder_distribution"
        }
    
    def _analyze_age_risk(self, rugcheck: Dict, dexscreener: Dict) -> Dict[str, Any]:
        """
        Analyze age-related risks
        """
        
        risk_score = 0
        max_score = self.weights["age_risk"]
        confidence = 0
        details = []
        
        age_hours = None
        
        # Try to get age from DexScreener first (more reliable)
        if dexscreener.get("success") and dexscreener.get("derived_metrics"):
            age_hours = dexscreener["derived_metrics"].get("age_hours")
            if age_hours is not None:
                confidence += 0.9
        
        # Fallback to rugcheck age data
        if age_hours is None and rugcheck.get("success"):
            # Try to parse age from rugcheck market data
            market_data = rugcheck.get("market_data", {})
            age_info = market_data.get("age_info")
            if age_info:
                # Simple parsing - could be enhanced
                confidence += 0.5
                # This would need more sophisticated parsing
                details.append(f"ℹ️ Age info: {age_info}")
        
        if age_hours is not None:
            if age_hours < self.thresholds["age_hours"]["high_risk"]:
                details.append(f"🚨 Very new token: {age_hours:.1f} hours old")
                risk_score += max_score
            elif age_hours < self.thresholds["age_hours"]["medium_risk"]:
                details.append(f"⚠️ Recently created: {age_hours:.1f} hours old")
                risk_score += max_score * 0.6  
            else:
                details.append(f"✅ Established token: {age_hours:.1f} hours old")
                risk_score += max_score * 0.1
        else:
            details.append("ℹ️ Token age unavailable")
            risk_score += max_score * 0.4  # Moderate risk when age unknown
        
        return {
            "score": round(risk_score, 1),
            "max_score": max_score,
            "confidence": round(confidence, 2),
            "details": details,
            "category": "token_maturity"
        }
    
    def _analyze_market_activity(self, dexscreener: Dict) -> Dict[str, Any]:
        """
        Analyze market activity and trading patterns
        """
        
        risk_score = 0
        max_score = self.weights["market_activity"]
        confidence = 0
        details = []
        
        if dexscreener.get("success"):
            confidence += 0.9
            
            # Volume to market cap ratio
            derived_metrics = dexscreener.get("derived_metrics", {})
            volume_mcap = derived_metrics.get("volume_mcap_ratio", 0)
            
            if volume_mcap < self.thresholds["volume_mcap_ratio"]["low_threshold"]:
                details.append(f"⚠️ Low trading activity: {volume_mcap:.2%} volume/mcap")
                risk_score += max_score * 0.7
            elif volume_mcap > self.thresholds["volume_mcap_ratio"]["high_threshold"]:
                details.append(f"⚠️ Extremely high activity: {volume_mcap:.2%} volume/mcap")
                risk_score += max_score * 0.4  # High activity can also be risky
            else:
                details.append(f"✅ Normal trading activity: {volume_mcap:.2%} volume/mcap")
                risk_score += max_score * 0.1
            
            # Buy/sell pressure analysis
            buy_pressure = derived_metrics.get("buy_pressure", 0.5)
            if buy_pressure < 0.3:
                details.append(f"⚠️ Heavy selling pressure: {buy_pressure:.1%} buys")
                risk_score += max_score * 0.3
            elif buy_pressure > 0.7:
                details.append(f"✅ Strong buying pressure: {buy_pressure:.1%} buys")
            else:
                details.append(f"ℹ️ Balanced trading: {buy_pressure:.1%} buys")
                
        else:
            details.append("⚠️ Market activity data unavailable")
            risk_score += max_score * 0.5
        
        return {
            "score": round(risk_score, 1),
            "max_score": max_score,
            "confidence": round(confidence, 2),
            "details": details,
            "category": "trading_activity"
        }
    
    def _analyze_price_volatility(self, dexscreener: Dict) -> Dict[str, Any]:
        """
        Analyze price volatility patterns
        """
        
        risk_score = 0
        max_score = self.weights["price_volatility"]
        confidence = 0
        details = []
        
        if dexscreener.get("success") and dexscreener.get("price_data"):
            confidence += 0.8
            
            price_data = dexscreener["price_data"]
            
            # Analyze 24h price change
            price_change_24h = price_data.get("price_change_24h", 0)
            if price_change_24h is not None:
                abs_change = abs(price_change_24h)
                
                if abs_change > 50:
                    details.append(f"🚨 Extreme volatility: {price_change_24h:+.1f}% (24h)")
                    risk_score += max_score
                elif abs_change > 25:
                    details.append(f"⚠️ High volatility: {price_change_24h:+.1f}% (24h)")
                    risk_score += max_score * 0.6
                elif abs_change > 10:
                    details.append(f"ℹ️ Moderate volatility: {price_change_24h:+.1f}% (24h)")
                    risk_score += max_score * 0.3
                else:
                    details.append(f"✅ Low volatility: {price_change_24h:+.1f}% (24h)")
                    risk_score += max_score * 0.1
        else:
            details.append("ℹ️ Price volatility data unavailable")
            risk_score += max_score * 0.3
        
        return {
            "score": round(risk_score, 1),
            "max_score": max_score,
            "confidence": round(confidence, 2),
            "details": details,
            "category": "price_stability"
        }
    
    def _calculate_overall_score(self, risk_factors: Dict[str, Any]) -> Tuple[int, float]:
        """
        Calculate weighted overall risk score and confidence
        """
        
        total_weighted_score = 0
        total_confidence = 0
        factor_count = 0
        
        for factor_name, factor_data in risk_factors.items():
            if isinstance(factor_data, dict):
                score = factor_data.get("score", 0)
                confidence = factor_data.get("confidence", 0)
                
                total_weighted_score += score
                total_confidence += confidence
                factor_count += 1
        
        # Calculate average confidence
        avg_confidence = total_confidence / factor_count if factor_count > 0 else 0
        
        # Overall score is sum of weighted scores (already weighted in calculation)
        overall_score = min(100, max(0, round(total_weighted_score)))
        
        return overall_score, round(avg_confidence, 2)
    
    def _determine_risk_level(self, score: int) -> str:
        """
        Determine risk level based on score
        """
        
        if score <= 25:
            return "LOW"
        elif score <= 50:
            return "MEDIUM"  
        elif score <= 75:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _generate_recommendations(self, risk_factors: Dict, score: int, data_sources: Dict) -> List[str]:
        """
        Generate intelligent investment recommendations
        """
        
        recommendations = []
        
        if score <= 25:
            recommendations.append("💚 LOW RISK: Suitable for larger position sizes")
            recommendations.append("📊 Consider 3-5% of portfolio allocation")
        elif score <= 50:
            recommendations.append("💛 MEDIUM RISK: Suitable for moderate speculation")
            recommendations.append("⚖️ Consider 1-2% of portfolio allocation")
        elif score <= 75:
            recommendations.append("🟠 HIGH RISK: Only for experienced traders") 
            recommendations.append("⚠️ Maximum 0.5% of portfolio allocation")
        else:
            recommendations.append("🔴 EXTREME RISK: Avoid or micro-position only")
            recommendations.append("🚨 Maximum 0.1% of portfolio allocation")
        
        # Add specific recommendations based on risk factors
        for factor_name, factor_data in risk_factors.items():
            if isinstance(factor_data, dict) and factor_data.get("score", 0) > 15:
                # High risk factor - add specific advice
                if factor_name == "liquidity_risk":
                    recommendations.append("🔐 Monitor liquidity locks closely")
                elif factor_name == "holder_concentration":
                    recommendations.append("👥 Watch for large holder movements")  
                elif factor_name == "age_risk":
                    recommendations.append("⏰ Wait for token to mature before large positions")
                elif factor_name == "market_activity":
                    recommendations.append("📈 Monitor trading patterns for stability")
                elif factor_name == "price_volatility":
                    recommendations.append("📊 Use smaller position sizes due to volatility")
        
        return recommendations
    
    def _generate_warnings(self, risk_factors: Dict, data_sources: Dict) -> List[str]:
        """
        Generate specific warnings for high-risk factors
        """
        
        warnings = []
        
        # Check each risk factor for warnings
        for factor_name, factor_data in risk_factors.items():
            if isinstance(factor_data, dict):
                score = factor_data.get("score", 0)
                max_score = factor_data.get("max_score", 100)
                
                # Generate warning if factor score is high
                if score >= max_score * 0.7:  # 70% of max score
                    details = factor_data.get("details", [])
                    for detail in details:
                        if detail.startswith("🚨") or detail.startswith("⚠️"):
                            warnings.append(detail)
        
        return warnings
    
    def _generate_investment_guidance(self, score: int, risk_factors: Dict, data_sources: Dict) -> Dict[str, Any]:
        """
        Generate detailed investment guidance
        """
        
        guidance = {
            "position_sizing": self._get_position_sizing_advice(score),
            "entry_strategy": self._get_entry_strategy(score, risk_factors),
            "exit_strategy": self._get_exit_strategy(score, risk_factors),
            "monitoring": self._get_monitoring_advice(risk_factors),
            "time_horizon": self._get_time_horizon_advice(score, risk_factors)
        }
        
        return guidance
    
    def _get_position_sizing_advice(self, score: int) -> str:
        """Get position sizing advice based on risk score"""
        
        if score <= 25:
            return "3-5% of portfolio maximum"
        elif score <= 50:
            return "1-2% of portfolio maximum"
        elif score <= 75:
            return "0.5% of portfolio maximum"
        else:
            return "0.1% of portfolio maximum (micro-position only)"
    
    def _get_entry_strategy(self, score: int, risk_factors: Dict) -> str:
        """Get entry strategy advice"""
        
        if score <= 25:
            return "Standard entry acceptable"
        elif score <= 50:
            return "Consider dollar-cost averaging entry"
        else:
            return "Wait for confirmation of safety or enter very small test position"
    
    def _get_exit_strategy(self, score: int, risk_factors: Dict) -> str:
        """Get exit strategy advice"""
        
        if score <= 25:
            return "Standard exit rules apply"
        elif score <= 50:
            return "Take profits on significant gains, use trailing stops"
        else:
            return "Take profits quickly, use tight stop losses"
    
    def _get_monitoring_advice(self, risk_factors: Dict) -> str:
        """Get monitoring advice based on risk factors"""
        
        advice_parts = []
        
        for factor_name, factor_data in risk_factors.items():
            if isinstance(factor_data, dict) and factor_data.get("score", 0) > 15:
                if factor_name == "liquidity_risk":
                    advice_parts.append("liquidity events")
                elif factor_name == "holder_concentration":
                    advice_parts.append("large holder activity")
                elif factor_name == "age_risk":
                    advice_parts.append("early development signs")
                elif factor_name == "market_activity":
                    advice_parts.append("trading volume patterns")
                elif factor_name == "price_volatility":
                    advice_parts.append("price action closely")
        
        if advice_parts:
            return f"Monitor {', '.join(advice_parts)} closely"
        else:
            return "Standard monitoring protocols"
    
    def _get_time_horizon_advice(self, score: int, risk_factors: Dict) -> str:
        """Get time horizon advice"""
        
        if score <= 25:
            return "Medium to long-term holding acceptable"
        elif score <= 50:
            return "Short to medium-term positions recommended"  
        else:
            return "Very short-term positions only"

# Test function
async def test_risk_analysis():
    """
    Test the complete risk analysis engine
    """
    
    engine = RiskAnalysisEngine()
    
    # Test with BONK (medium risk memecoin)
    bonk_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    
    print("🧪 Testing complete risk analysis with BONK...")
    result = await engine.analyze_token_risk(bonk_address)
    
    print("\n📊 BONK Risk Analysis Results:")
    print(f"Risk Score: {result['risk_score']}/100 ({result['risk_level']})")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Analysis Duration: {result.get('analysis_duration', 0)}s")
    
    print("\n🔍 Risk Factors:")
    for factor_name, factor_data in result["risk_factors"].items():
        if isinstance(factor_data, dict):
            print(f"  {factor_name}: {factor_data['score']}/{factor_data['max_score']} points")
    
    print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
    for rec in result["recommendations"][:3]:  # Show first 3
        print(f"  {rec}")
    
    print(f"\n⚠️ Warnings ({len(result['warnings'])}):")
    for warning in result["warnings"][:3]:  # Show first 3
        print(f"  {warning}")

if __name__ == "__main__":
    asyncio.run(test_risk_analysis())