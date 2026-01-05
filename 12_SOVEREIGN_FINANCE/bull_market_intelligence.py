#!/usr/bin/env python3
"""
🐂 BULL MARKET INTELLIGENCE SYSTEM
Sistema de Inversión Inteligente - El Toro de Wall Street
Arquitecto: Iyari Cancino Gomez
Puerto: 7777

Capacidades:
- Monitoreo en tiempo real de mercados
- Análisis técnico con indicadores avanzados
- Sistema de alertas inteligente
- Recomendaciones de inversión
- Gestión de portafolio
- Visualización avanzada de datos
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import sys
import logging
from pathlib import Path
from functools import lru_cache
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar librerías científicas
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas/numpy no instalado. Ejecutar: pip install pandas numpy")
    # Crear mocks básicos
    class pd:
        @staticmethod
        def Series(data):
            return data
    class np:
        @staticmethod
        def sqrt(x):
            return x ** 0.5
        @staticmethod
        def mean(arr):
            return sum(arr) / len(arr) if arr else 0

# Intentar importar librerías financieras
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance no instalado. Ejecutar: pip install yfinance")

app = Flask(__name__)
CORS(app)

# Configuración
BASE_DIR = Path(__file__).parent
PORTFOLIO_FILE = BASE_DIR / "portfolio.json"
HISTORY_FILE = BASE_DIR / "investment_history.json"
CACHE_DURATION = 30  # segundos

# Caché global para datos de mercado
market_cache = {}
cache_timestamps = {}

class NashEquilibriumAnalyzer:
    """
    🎮 NASH EQUILIBRIUM ANALYZER
    Aplicación de Teoría de Juegos de John Nash al mercado financiero
    
    Conceptos implementados:
    - Equilibrio de Nash: Estrategia óptima donde ningún jugador puede mejorar unilateralmente
    - Estrategias Dominantes: Acciones que siempre superan a otras sin importar lo que hagan otros
    - Payoff Matrix: Matriz de retornos esperados
    - Game Theory: Análisis de competencia entre activos
    """
    
    def __init__(self):
        self.risk_free_rate = 0.05  # Tasa libre de riesgo (5%)
    
    def calculate_nash_equilibrium(self, asset_data):
        """
        Calcular el Equilibrio de Nash en una estrategia de inversión
        
        En el contexto financiero:
        - Jugador A: Inversor (tú)
        - Jugador B: El Mercado
        - Estrategias: COMPRAR, MANTENER, VENDER
        - Payoffs: Retornos esperados
        """
        
        if not asset_data or len(asset_data) < 50:
            return None
        
        # Calcular métricas clave
        returns = pd.Series([d['Close'] for d in asset_data]).pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (returns.mean() * 252 - self.risk_free_rate) / (volatility + 0.0001)
        momentum = returns.tail(20).mean()
        
        # Construir matriz de payoffs
        # Estados del mercado: ALCISTA, LATERAL, BAJISTA
        market_probs = self.estimate_market_state_probabilities(asset_data)
        
        # Estrategias del inversor y sus payoffs esperados
        strategies = {
            'COMPRAR': {
                'payoff_alcista': 0.15,    # 15% ganancia esperada
                'payoff_lateral': 0.02,     # 2% ganancia
                'payoff_bajista': -0.10,    # -10% pérdida
                'expected_return': None
            },
            'MANTENER': {
                'payoff_alcista': 0.08,     # 8% ganancia
                'payoff_lateral': 0.01,     # 1% ganancia
                'payoff_bajista': -0.05,    # -5% pérdida
                'expected_return': None
            },
            'VENDER': {
                'payoff_alcista': 0.00,     # 0% (costo de oportunidad)
                'payoff_lateral': 0.00,     # 0%
                'payoff_bajista': 0.00,     # 0% (evita pérdida)
                'expected_return': None
            }
        }
        
        # Calcular retornos esperados para cada estrategia
        for strategy, data in strategies.items():
            expected = (
                data['payoff_alcista'] * market_probs['alcista'] +
                data['payoff_lateral'] * market_probs['lateral'] +
                data['payoff_bajista'] * market_probs['bajista']
            )
            data['expected_return'] = expected
        
        # Encontrar estrategia dominante (Equilibrio de Nash)
        best_strategy = max(strategies.items(), key=lambda x: x[1]['expected_return'])
        
        # Calcular utilidad esperada de Nash
        nash_utility = best_strategy[1]['expected_return']
        
        return {
            'equilibrium_strategy': best_strategy[0],
            'expected_return': round(best_strategy[1]['expected_return'] * 100, 2),
            'market_state': market_probs,
            'sharpe_ratio': round(sharpe_ratio, 2),
            'payoff_matrix': strategies,
            'confidence': self.calculate_confidence(market_probs, sharpe_ratio),
            'nash_insight': self.generate_nash_insight(best_strategy[0], market_probs, nash_utility)
        }
    
    def estimate_market_state_probabilities(self, asset_data):
        """
        Estimar probabilidades de estados del mercado usando análisis bayesiano
        """
        if len(asset_data) < 50:
            return {'alcista': 0.33, 'lateral': 0.34, 'bajista': 0.33}
        
        closes = pd.Series([d['Close'] for d in asset_data])
        returns = closes.pct_change().dropna()
        
        # Clasificar días recientes
        recent_returns = returns.tail(20)
        
        bullish_days = len(recent_returns[recent_returns > 0.01])
        neutral_days = len(recent_returns[(recent_returns >= -0.01) & (recent_returns <= 0.01)])
        bearish_days = len(recent_returns[recent_returns < -0.01])
        
        total = bullish_days + neutral_days + bearish_days
        
        return {
            'alcista': round(bullish_days / total, 2),
            'lateral': round(neutral_days / total, 2),
            'bajista': round(bearish_days / total, 2)
        }
    
    def calculate_confidence(self, market_probs, sharpe_ratio):
        """
        Calcular nivel de confianza en la estrategia de Nash
        """
        # Confianza alta si hay claridad en el estado del mercado
        max_prob = max(market_probs.values())
        
        # Ajustar por Sharpe ratio
        sharpe_factor = min(abs(sharpe_ratio) / 2.0, 1.0)
        
        confidence = (max_prob * 0.7 + sharpe_factor * 0.3) * 100
        
        return round(confidence, 1)
    
    def generate_nash_insight(self, strategy, market_probs, utility):
        """
        Generar insight estratégico basado en principios de Nash
        """
        insights = {
            'COMPRAR': f"📈 Equilibrio de Nash: COMPRAR es óptimo. Probabilidad alcista {market_probs['alcista']*100:.0f}% sugiere que ningún jugador racional cambiaría esta estrategia.",
            'MANTENER': f"⚖️ Equilibrio de Nash: MANTENER es la estrategia dominante. El mercado está en equilibrio, cambiar no mejoraría el payoff esperado.",
            'VENDER': f"📉 Equilibrio de Nash: VENDER minimiza riesgo. Probabilidad bajista {market_probs['bajista']*100:.0f}% hace que esta sea la única estrategia racional."
        }
        
        return insights.get(strategy, "Estrategia en análisis")
    
    def analyze_competitive_dynamics(self, multiple_assets):
        """
        Analizar dinámicas competitivas entre múltiples activos (Multi-player Nash)
        """
        if len(multiple_assets) < 2:
            return None
        
        # Calcular correlaciones entre activos
        correlations = {}
        
        for i, asset1 in enumerate(multiple_assets):
            for asset2 in multiple_assets[i+1:]:
                if asset1['history'] and asset2['history']:
                    prices1 = pd.Series([d['Close'] for d in asset1['history']])
                    prices2 = pd.Series([d['Close'] for d in asset2['history']])
                    
                    if len(prices1) > 20 and len(prices2) > 20:
                        corr = prices1.tail(20).corr(prices2.tail(20))
                        correlations[f"{asset1['symbol']}-{asset2['symbol']}"] = round(corr, 2)
        
        # Identificar estrategias de diversificación óptimas
        low_corr_pairs = [(k, v) for k, v in correlations.items() if abs(v) < 0.3]
        
        return {
            'correlations': correlations,
            'diversification_opportunities': low_corr_pairs,
            'nash_recommendation': self.generate_diversification_strategy(correlations)
        }
    
    def generate_diversification_strategy(self, correlations):
        """
        Generar estrategia de diversificación basada en Nash
        """
        if not correlations:
            return "Insuficientes datos para análisis multi-activo"
        
        avg_correlation = np.mean(list(correlations.values()))
        
        if avg_correlation < 0.3:
            return "🎯 Equilibrio Nash: Portfolio óptimo detectado. Correlación baja permite maximizar retornos sin aumentar riesgo proporcional."
        elif avg_correlation > 0.7:
            return "⚠️ Riesgo sistémico: Alta correlación. Diversificar hacia activos no correlacionados es la estrategia dominante."
        else:
            return "⚖️ Balance moderado: Diversificación parcial. Mantener mix actual es un equilibrio de Nash local."

class BullMarketIntelligence:
    def __init__(self, initial_capital=2000):
        self.capital_mxn = initial_capital
        self.portfolio = self.load_portfolio()
        self.history = self.load_history()
        
        # Acciones populares para monitoreo
        self.watchlist = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN",  # Tech Giants
            "NVDA", "META", "AMD",  # Tech/AI
            "JPM", "BAC", "GS",  # Bancos
            "SPY", "QQQ", "DIA",  # ETFs de mercado
            "BTC-USD", "ETH-USD",  # Crypto
            "GC=F", "SI=F", "CL=F"  # Commodities (Oro, Plata, Petróleo)
        ]
        
        # Nash Equilibrium Engine
        self.nash_analyzer = NashEquilibriumAnalyzer()
    
    def load_portfolio(self):
        """Cargar portafolio guardado"""
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_portfolio(self):
        """Guardar portafolio"""
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def load_history(self):
        """Cargar historial de inversiones"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Guardar historial"""
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_market_data(self, symbol, period="1mo"):
        """Obtener datos de mercado de un símbolo"""
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                return None
            
            # Calcular indicadores técnicos
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            hist['RSI'] = self.calculate_rsi(hist['Close'])
            hist['MACD'], hist['Signal'] = self.calculate_macd(hist['Close'])
            hist['BB_Upper'], hist['BB_Lower'] = self.calculate_bollinger_bands(hist['Close'])
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            
            # Análisis de patrones
            patterns = self.detect_patterns(hist)
            prediction = self.predict_movement(hist)
            support_resistance = self.find_support_resistance(hist)
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'high_52w': round(hist['High'].max(), 2),
                'low_52w': round(hist['Low'].min(), 2),
                'sma_20': round(hist['SMA_20'].iloc[-1], 2) if not pd.isna(hist['SMA_20'].iloc[-1]) else None,
                'sma_50': round(hist['SMA_50'].iloc[-1], 2) if not pd.isna(hist['SMA_50'].iloc[-1]) else None,
                'sma_200': round(hist['SMA_200'].iloc[-1], 2) if not pd.isna(hist['SMA_200'].iloc[-1]) else None,
                'rsi': round(hist['RSI'].iloc[-1], 2) if not pd.isna(hist['RSI'].iloc[-1]) else None,
                'macd': round(hist['MACD'].iloc[-1], 2) if not pd.isna(hist['MACD'].iloc[-1]) else None,
                'recommendation': self.get_recommendation(hist),
                'patterns': patterns,
                'prediction': prediction,
                'support': support_resistance['support'],
                'resistance': support_resistance['resistance'],
                'nash_analysis': self.nash_analyzer.calculate_nash_equilibrium(hist.tail(90).reset_index().to_dict('records')),
                'history': hist.tail(90).reset_index().to_dict('records')
            }
        except Exception as e:
            print(f"Error obteniendo datos de {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calcular RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices):
        """Calcular MACD (Moving Average Convergence Divergence)"""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal
    
    def calculate_bollinger_bands(self, prices, period=20):
        """Calcular Bandas de Bollinger"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, lower_band
    
    def find_support_resistance(self, hist):
        """Encontrar niveles de soporte y resistencia"""
        highs = hist['High'].values
        lows = hist['Low'].values
        
        # Encontrar picos locales (resistencias)
        resistance_levels = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
        
        # Encontrar valles locales (soportes)
        support_levels = []
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        
        # Tomar los niveles más relevantes
        resistance = round(np.mean(resistance_levels[-3:]), 2) if resistance_levels else None
        support = round(np.mean(support_levels[-3:]), 2) if support_levels else None
        
        return {'support': support, 'resistance': resistance}
    
    def detect_patterns(self, hist):
        """Detectar patrones técnicos en el historial"""
        patterns = []
        
        if len(hist) < 50:
            return patterns
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        sma_200 = hist['SMA_200'].iloc[-1] if not pd.isna(hist['SMA_200'].iloc[-1]) else None
        
        # Golden Cross
        if not pd.isna(sma_50) and sma_20 > sma_50:
            prev_sma_20 = hist['SMA_20'].iloc[-5]
            prev_sma_50 = hist['SMA_50'].iloc[-5]
            if prev_sma_20 < prev_sma_50:
                patterns.append({
                    'name': 'Golden Cross',
                    'signal': 'ALCISTA',
                    'confidence': 'ALTA'
                })
        
        # Death Cross
        if not pd.isna(sma_50) and sma_20 < sma_50:
            prev_sma_20 = hist['SMA_20'].iloc[-5]
            prev_sma_50 = hist['SMA_50'].iloc[-5]
            if prev_sma_20 > prev_sma_50:
                patterns.append({
                    'name': 'Death Cross',
                    'signal': 'BAJISTA',
                    'confidence': 'ALTA'
                })
        
        # Tendencia alcista
        if sma_200 and current_price > sma_20 > sma_50 > sma_200:
            patterns.append({
                'name': 'Tendencia Alcista Fuerte',
                'signal': 'ALCISTA',
                'confidence': 'MEDIA'
            })
        
        # Tendencia bajista
        if sma_200 and current_price < sma_20 < sma_50 < sma_200:
            patterns.append({
                'name': 'Tendencia Bajista Fuerte',
                'signal': 'BAJISTA',
                'confidence': 'MEDIA'
            })
        
        # RSI extremos
        rsi = hist['RSI'].iloc[-1]
        if not pd.isna(rsi):
            if rsi < 20:
                patterns.append({
                    'name': 'Sobreventa Extrema',
                    'signal': 'COMPRAR',
                    'confidence': 'ALTA'
                })
            elif rsi > 80:
                patterns.append({
                    'name': 'Sobrecompra Extrema',
                    'signal': 'VENDER',
                    'confidence': 'ALTA'
                })
        
        return patterns
    
    def predict_movement(self, hist):
        """Predecir movimiento futuro basado en patrones históricos"""
        if len(hist) < 50:
            return {
                'direction': 'NEUTRAL',
                'confidence': 0,
                'target_price': None,
                'timeframe': '1-5 días'
            }
        
        current_price = hist['Close'].iloc[-1]
        
        # Análisis de momentum
        returns_5d = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
        returns_10d = (hist['Close'].iloc[-1] - hist['Close'].iloc[-10]) / hist['Close'].iloc[-10]
        returns_20d = (hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]
        
        # Volatilidad
        volatility = hist['Close'].pct_change().std() * np.sqrt(252)
        
        # Ponderación de señales
        signals = 0

@app.route('/api/analyze/<symbol>', methods=['GET'])
def analyze_symbol(symbol):
    """Análisis profundo de un símbolo con historial completo"""
    try:
        # Obtener 2 años de datos para análisis completo
        ticker = yf.Ticker(symbol)
        hist_2y = ticker.history(period='2y')
        
        if hist_2y.empty:
            return jsonify({'success': False, 'message': 'No hay datos suficientes'}), 404
        
        # Calcular todos los indicadores
        hist_2y['SMA_20'] = hist_2y['Close'].rolling(window=20).mean()
        hist_2y['SMA_50'] = hist_2y['Close'].rolling(window=50).mean()
        hist_2y['SMA_200'] = hist_2y['Close'].rolling(window=200).mean()
        hist_2y['RSI'] = bull_market.calculate_rsi(hist_2y['Close'])
        hist_2y['MACD'], hist_2y['Signal'] = bull_market.calculate_macd(hist_2y['Close'])
        hist_2y['BB_Upper'], hist_2y['BB_Lower'] = bull_market.calculate_bollinger_bands(hist_2y['Close'])
        
        patterns = bull_market.detect_patterns(hist_2y)
        prediction = bull_market.predict_movement(hist_2y)
        support_resistance = bull_market.find_support_resistance(hist_2y)
        
        # Calcular estadísticas de rendimiento
        returns_1m = ((hist_2y['Close'].iloc[-1] - hist_2y['Close'].iloc[-22]) / hist_2y['Close'].iloc[-22]) * 100 if len(hist_2y) > 22 else 0
        returns_3m = ((hist_2y['Close'].iloc[-1] - hist_2y['Close'].iloc[-66]) / hist_2y['Close'].iloc[-66]) * 100 if len(hist_2y) > 66 else 0
        returns_6m = ((hist_2y['Close'].iloc[-1] - hist_2y['Close'].iloc[-132]) / hist_2y['Close'].iloc[-132]) * 100 if len(hist_2y) > 132 else 0
        returns_1y = ((hist_2y['Close'].iloc[-1] - hist_2y['Close'].iloc[-252]) / hist_2y['Close'].iloc[-252]) * 100 if len(hist_2y) > 252 else 0
        
        # Análisis de volatilidad
        volatility_30d = hist_2y['Close'].tail(30).pct_change().std() * np.sqrt(252) * 100
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'patterns': patterns,
            'prediction': prediction,
            'support_resistance': support_resistance,
            'performance': {
                '1_month': round(returns_1m, 2),
                '3_months': round(returns_3m, 2),
                '6_months': round(returns_6m, 2),
                '1_year': round(returns_1y, 2),
                'volatility_30d': round(volatility_30d, 2)
            },
            'historical_data': hist_2y.tail(365).reset_index().to_dict('records')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
        rsi = hist['RSI'].iloc[-1]
        if not pd.isna(rsi):
            if rsi < 30:
                signals += 2
            elif rsi > 70:
                signals -= 2
        
        # MACD
        macd = hist['MACD'].iloc[-1]
        signal = hist['Signal'].iloc[-1]
        if not pd.isna(macd) and not pd.isna(signal):
            if macd > signal:
                signals += 1
            else:
                signals -= 1
        
        # SMAs
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        if not pd.isna(sma_20) and not pd.isna(sma_50):
            if current_price > sma_20 > sma_50:
                signals += 2
            elif current_price < sma_20 < sma_50:
                signals -= 2
        
        # Momentum
        if returns_5d > 0 and returns_10d > 0:
            signals += 1
        elif returns_5d < 0 and returns_10d < 0:
            signals -= 1
        
        # Determinar dirección y confianza
        direction = 'ALCISTA' if signals > 2 else 'BAJISTA' if signals < -2 else 'NEUTRAL'
        confidence = min(abs(signals) * 10, 100)
        
        # Calcular precio objetivo (basado en volatilidad y momentum)
        if direction == 'ALCISTA':
            target_price = round(current_price * (1 + volatility * 0.5), 2)
        elif direction == 'BAJISTA':
            target_price = round(current_price * (1 - volatility * 0.5), 2)
        else:
            target_price = round(current_price, 2)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'target_price': target_price,
            'timeframe': '1-5 días',
            'volatility': round(volatility * 100, 2)
        }
    
    def get_recommendation(self, hist):
        """Generar recomendación basada en indicadores"""
        if len(hist) < 50:
            return "ESPERAR - Datos insuficientes"
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        rsi = hist['RSI'].iloc[-1]
        
        if pd.isna(sma_20) or pd.isna(sma_50) or pd.isna(rsi):
            return "ESPERAR - Calculando indicadores"
        
        signals = []
        
        # Señales de compra
        if current_price > sma_20 and sma_20 > sma_50:
            signals.append("COMPRAR - Tendencia alcista")
        if rsi < 30:
            signals.append("COMPRAR - Sobreventa (RSI bajo)")
        
        # Señales de venta
        if current_price < sma_20 and sma_20 < sma_50:
            signals.append("VENDER - Tendencia bajista")
        if rsi > 70:
            signals.append("VENDER - Sobrecompra (RSI alto)")
        
        # Señales neutras
        if 30 <= rsi <= 70 and abs(current_price - sma_20) < (sma_20 * 0.02):
            signals.append("MANTENER - Rango neutral")
        
        return signals[0] if signals else "ESPERAR - Sin señales claras"
    
    def add_to_portfolio(self, symbol, shares, purchase_price):
        """Agregar activo al portafolio"""
        if symbol not in self.portfolio:
            self.portfolio[symbol] = {
                'shares': 0,
                'avg_price': 0,
                'total_invested': 0
            }
        
        current = self.portfolio[symbol]
        total_shares = current['shares'] + shares
        total_invested = current['total_invested'] + (shares * purchase_price)
        
        self.portfolio[symbol] = {
            'shares': total_shares,
            'avg_price': total_invested / total_shares,
            'total_invested': total_invested
        }
        
        # Registrar en historial
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': purchase_price,
            'total': shares * purchase_price
        })
        
        self.save_portfolio()
        self.save_history()
        
        return {'success': True, 'portfolio': self.portfolio[symbol]}
    
    def get_portfolio_value(self):
        """Calcular valor actual del portafolio"""
        if not YFINANCE_AVAILABLE:
            return {'total_invested': 0, 'current_value': 0, 'gain_loss': 0}
        
        total_invested = sum(item['total_invested'] for item in self.portfolio.values())
        current_value = 0
        
        for symbol, data in self.portfolio.items():
            try:
                ticker = yf.Ticker(symbol)
                current_price = ticker.history(period='1d')['Close'].iloc[-1]
                current_value += data['shares'] * current_price
            except:
                current_value += data['total_invested']
        
        gain_loss = current_value - total_invested
        gain_loss_percent = (gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'current_value': round(current_value, 2),
            'gain_loss': round(gain_loss, 2),
            'gain_loss_percent': round(gain_loss_percent, 2)
        }
    
    def get_market_summary(self):
        """Resumen general del mercado"""
        indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'Bitcoin': 'BTC-USD'
        }
        
        summary = {}
        for name, symbol in indices.items():
            data = self.get_market_data(symbol, period='1d')
            if data:
                summary[name] = {
                    'price': data['current_price'],
                    'change_percent': data['change_percent']
                }
        
        return summary

# Instancia global
bull_market = BullMarketIntelligence()

# ============================================
# RUTAS DE LA API
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/market/<symbol>', methods=['GET'])
def get_symbol_data(symbol):
    """Obtener datos de un símbolo específico"""
    period = request.args.get('period', '1y')  # Cambiado a 1 año por defecto
    data = bull_market.get_market_data(symbol, period)
    
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'No se pudo obtener datos'}), 404

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Obtener datos de todos los símbolos en watchlist"""
    results = []
    
    for symbol in bull_market.watchlist:
        data = bull_market.get_market_data(symbol, period='5d')
        if data:
            results.append(data)
    
    return jsonify({'success': True, 'watchlist': results})

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Obtener portafolio actual"""
    portfolio_value = bull_market.get_portfolio_value()
    
    return jsonify({
        'success': True,
        'portfolio': bull_market.portfolio,
        'value': portfolio_value,
        'capital_mxn': bull_market.capital_mxn
    })

@app.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    """Agregar activo al portafolio"""
    data = request.json
    symbol = data.get('symbol')
    shares = float(data.get('shares', 0))
    price = float(data.get('price', 0))
    
    result = bull_market.add_to_portfolio(symbol, shares, price)
    
    return jsonify(result)

@app.route('/api/market/summary', methods=['GET'])
def market_summary():
    """Resumen del mercado"""
    summary = bull_market.get_market_summary()
    return jsonify({'success': True, 'summary': summary})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtener historial de inversiones"""
    return jsonify({'success': True, 'history': bull_market.history})

@app.route('/api/nash/portfolio', methods=['POST'])
def analyze_nash_portfolio():
    """Análisis de Nash para portfolio completo"""
    try:
        symbols = request.json.get('symbols', [])
        
        if not symbols:
            return jsonify({'success': False, 'message': 'Se requiere lista de símbolos'}), 400
        
        # Obtener datos de todos los activos
        assets_data = []
        for symbol in symbols:
            data = bull_market.get_market_data(symbol, period='3mo')
            if data:
                assets_data.append(data)
        
        if len(assets_data) < 2:
            return jsonify({'success': False, 'message': 'Se requieren al menos 2 activos'}), 400
        
        # Análisis de Nash multi-jugador
        competitive_analysis = bull_market.nash_analyzer.analyze_competitive_dynamics(assets_data)
        
        return jsonify({
            'success': True,
            'analysis': competitive_analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# HTML TEMPLATE
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐂 Bull Market Intelligence</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bull-green: #00ff88;
            --bear-red: #ff3366;
            --gold: #ffd700;
            --bg: #0a0a14;
            --glass: rgba(15, 15, 30, 0.85);
            --border: rgba(0, 255, 136, 0.3);
            --text: #e0e0e0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        .header {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border-bottom: 3px solid var(--bull-green);
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 30px rgba(0, 0, 0, 0.5);
        }
        
        .header h1 {
            color: var(--bull-green);
            text-shadow: 0 0 30px var(--bull-green);
            font-size: 3rem;
            margin-bottom: 10px;
            animation: pulse 3s ease-in-out infinite;
        }
        
        .header .tagline {
            color: var(--gold);
            font-size: 1.2rem;
            text-shadow: 0 0 10px var(--gold);
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 30px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--glass);
            backdrop-filter: blur(15px);
            border: 2px solid var(--border);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 255, 136, 0.3);
            border-color: var(--bull-green);
        }
        
        .stat-card .value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .stat-card .value.positive {
            color: var(--bull-green);
            text-shadow: 0 0 20px var(--bull-green);
        }
        
        .stat-card .value.negative {
            color: var(--bear-red);
            text-shadow: 0 0 20px var(--bear-red);
        }
        
        .stat-card .label {
            color: var(--text);
            opacity: 0.7;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .watchlist-container {
            background: var(--glass);
            backdrop-filter: blur(15px);
            border: 2px solid var(--border);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .watchlist-container h2 {
            color: var(--bull-green);
            text-shadow: 0 0 15px var(--bull-green);
            margin-bottom: 25px;
            font-size: 1.8rem;
        }
        
        .watchlist-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .stock-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .stock-card:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 25px rgba(0, 255, 136, 0.4);
        }
        
        .stock-card .symbol {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--gold);
            margin-bottom: 5px;
        }
        
        .stock-card .patterns {
            margin-top: 10px;
            font-size: 0.75rem;
        }
        
        .stock-card .pattern-tag {
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            border-radius: 4px;
            font-weight: bold;
            background: rgba(0, 255, 136, 0.2);
            border: 1px solid var(--bull-green);
        }
        
        .stock-card .prediction {
            margin-top: 8px;
            padding: 8px;
            border-radius: 5px;
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid var(--gold);
            font-size: 0.8rem;
        }
        
        .stock-card .prediction .direction {
            font-weight: bold;
            font-size: 1rem;
        }
        
        .stock-card .prediction.bullish {
            background: rgba(0, 255, 136, 0.15);
            border-color: var(--bull-green);
            color: var(--bull-green);
        }
        
        .stock-card .prediction.bearish {
            background: rgba(255, 51, 102, 0.15);
            border-color: var(--bear-red);
            color: var(--bear-red);
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: var(--bull-green);
            font-size: 1.5rem;
            animation: pulse 2s infinite;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            overflow-y: auto;
        }
        
        .modal.active {
            display: flex;
          
    
    <!-- Modal de Análisis Profundo -->
    <div class="modal" id="analysisModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">📊 ANÁLISIS PROFUNDO</h2>
                <button class="close-btn" onclick="closeModal()">✕ CERRAR</button>
            </div>
            
            <div class="analysis-section">
                <h3>🎯 PREDICCIÓN</h3>
                <div id="predictionContent"></div>
            </div>
            
            <div class="analysis-section">
                <h3>📈 PATRONES DETECTADOS</h3>
                <div class="pattern-list" id="patternsList"></div>
            </div>
            
            <div class="analysis-section">
                <h3>🎮 EQUILIBRIO DE NASH - TEORÍA DE JUEGOS</h3>
                <div id="nashContent"></div>
            </div>
            
            <div class="analysis-section">
                <h3>📊 RENDIMIENTO HISTÓRICO</h3>
                <div id="performanceContent"></div>
            </div>
            
            <div class="analysis-section">
                <h3>📉 GRÁFICO HISTÓRICO (1 AÑO)</h3>
                <div class="chart-container">
                    <canvas id="historicalChart"></canvas>
                </div>
            </div>
        </div>
    </div>  align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border: 2px solid var(--bull-green);
            border-radius: 15px;
            padding: 30px;
            max-width: 1200px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h2 {
            color: var(--bull-green);
            text-shadow: 0 0 15px var(--bull-green);
        }
        
        .close-btn {
            background: var(--bear-red);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .close-btn:hover {
            background: #ff0033;
        }
        
        .analysis
                
                // Generar HTML de Nash
                let nashHTML = '';
                if (stock.nash_analysis && stock.nash_analysis.equilibrium_strategy) {
                    nashHTML = `
                        <div style="margin-top: 8px; padding: 6px; background: rgba(255, 215, 0, 0.1); border: 1px solid var(--gold); border-radius: 5px; font-size: 0.75rem;">
                            <strong>🎮 Nash:</strong> ${stock.nash_analysis.equilibrium_strategy}
                        </div>
                    `;
                }-section {
            margin: 20px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            border-radius: 10px;
        }
        // Generar HTML de patrones
                let patternsHTML = '';
                if (stock.patterns && stock.patterns.length > 0) {
                    patternsHTML = '<div class="patterns">';
                    stock.patterns.slice(0, 2).forEach(pattern => {
                        patternsHTML += `<span class="pattern-tag">${pattern.name}</span>`;
                    });
                    patternsHTML += '</div>';
                }
                
                // Generar HTML de predicción
                let predictionHTML = '';
                if (stock.prediction) {
                    const predClass = stock.prediction.direction === 'ALCISTA' ? 'bullish' : 
                                     stock.prediction.direction === 'BAJISTA' ? 'bearish' : '';
                    predictionHTML = `
                        <div class="prediction ${predClass}">
                            <div class="direction">${stock.prediction.direction}</div>
                            <div>Confianza: ${stock.prediction.confidence}%</div>
                            <div>Objetivo: $${stock.prediction.target_price}</div>
                        </div>
                    `;
                }
                
                card.innerHTML = `
                    <div class="symbol">${stock.symbol}</div>
                    <div class="price ${changeClass}">$${stock.current_price}</div>
                    <div class="change ${changeClass}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%
                    </div>
                    <div class="recommendation ${recommendationClass}">
                        ${stock.recommendation}
                    </div>
                    ${patternsHTML}
                    ${predictionHTML}columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .pattern-item {
            padding: 15px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--bull-green);
            border-radius: 8px;
        }
        
        .pattern-item.bearish {
            background: rgba(255, 51, 102, 0.1);
            border-color: var(--bear-red);
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        .stock-card .change {
            font-size: 1rem;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
        }
        
        .stock-card .change.positive {
            background: rgba(0, 255, 136, 0.2);
            color: var(--bull-green);
        }
        
        .stock-card .change.negative {
            background: rgba(255, 51, 102, 0.2);
            color: var(--bear-red);
        }
        
        .stock-card .recommendation {
            margin-top: 10px;
            padding: 8px;
            border-radius: 5px;
            font-size: 0.85rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .recommendation.buy {
            background: rgba(0, 255, 136, 0.2);
            color: var(--bull-green);
            border: 1px solid var(--bull-green);
        }
        
        .recommendation.sell {
            background: rgba(255, 51, 102, 0.2);
            color: var(--bear-red);
            border: 1px solid var(--bear-red);
        }
        
        .recommendation.hold {
            background: rgba(255, 215, 0, 0.2);
            color: var(--gold);
            border: 1px solid var(--gold);
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: var(--bull-green);
            font-size: 1.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .btn {
            background: linear-gradient(135deg, var(--bull-green), var(--gold));
            border: none;
            color: var(--bg);
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 1rem;
        }
        
        .btn:hover {
            transform: scale(1.1);
            box-shadow: 0 5px 30px rgba(0, 255, 136, 0.6);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐂 BULL MARKET INTELLIGENCE</h1>
        <div class="tagline">Sistema de Inversión Inteligente • Creando Activos Reales</div>
    </div>
    
    <div class="container">
        <div class="dashboard-grid" id="dashboardGrid">
            <div class="stat-card">
                <div class="label">Capital Total</div>
                <div class="value positive" id="totalCapital">$0</div>
            </div>
            <div class="stat-card">
                <div class="label">Valor Portafolio</div>
                <div class="value" id="portfolioValue">$0</div>
            </div>
            <div class="stat-card">
                <div class="label">Ganancia/Pérdida</div>
                <div class="value" id="gainLoss">$0</div>
            </div>
            <div class="stat-card">
                <div class="label">% Retorno</div>
                <div class="value" id="returnPercent">0%</div>
            </div>
        </div>
        
        <div class="watchlist-container">
            <h2>📊 MERCADO EN TIEMPO REAL</h2>
            <div class="loading" id="loading">⚡ CARGANDO DATOS DEL MERCADO...</div>
            <div class="watchlist-grid" id="watchlistGrid" style="display:none;"></div>
        </div>
    </div>
    
    <script>
        async function loadMarketData() {
            try {
                const response = await fetch('/api/watchlist');
                const data = await response.json();
                
                if (data.success) {
                    renderWatchlist(data.watchlist);
                }
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('watchlistGrid').style.display = 'grid';
            } catch (error) {
                console.error('Error cargando datos:', error);
        let currentChart = null;
        
        async function showDetails(symbol) {
            try {
                const response = await fetch(`/api/analyze/${symbol}`);
                const data = await response.json();
                
                if (!data.success) {
                    alert('No se pudo cargar el análisis');
                    return;
                }
                
                document.getElementById('modalTitle').textContent = `📊 ANÁLISIS PROFUNDO: ${symbol}`;
                
                // Renderizar predicción
                const pred = data.prediction;
                const predClass = pred.direction === 'ALCISTA' ? 'bullish' : 
                                 pred.direction === 'BAJISTA' ? 'bearish' : '';
                document.getElementById('predictionContent').innerHTML = `
                    <div class="prediction ${predClass}" style="font-size: 1.2rem;">
                        <div class="direction" style="font-size: 2rem; margin-bottom: 10px;">
                            ${pred.direction === 'ALCISTA' ? '📈' : pred.direction === 'BAJISTA' ? '📉' : '➡️'} 
                            ${pred.direction}
                        </div>
                  
                
                // Renderizar análisis de Nash
                const nash = data.nash_analysis;
                if (nash) {
                    const nashClass = nash.equilibrium_strategy === 'COMPRAR' ? 'bullish' : 
                                     nash.equilibrium_strategy === 'VENDER' ? 'bearish' : '';
                    document.getElementById('nashContent').innerHTML = `
                        <div class="prediction ${nashClass}" style="font-size: 1.1rem;">
                            <div style="font-size: 1.8rem; margin-bottom: 15px;">
                                🎮 Estrategia de Equilibrio: <strong>${nash.equilibrium_strategy}</strong>
                            </div>
                            <div style="margin-bottom: 10px;">
                                Retorno Esperado: <strong>${nash.expected_return}%</strong>
                            </div>
                            <div style="margin-bottom: 10px;">
                                Confianza Nash: <strong>${nash.confidence}%</strong>
                            </div>
                            <div style="margin-bottom: 10px;">
                                Sharpe Ratio: <strong>${nash.sharpe_ratio}</strong>
                            </div>
                            <div style="margin: 15px 0; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <strong>Estado del Mercado (Probabilidades):</strong><br>
                                📈 Alcista: ${(nash.market_state.alcista * 100).toFixed(0)}%<br>
                                ➡️ Lateral: ${(nash.market_state.lateral * 100).toFixed(0)}%<br>
                                📉 Bajista: ${(nash.market_state.bajista * 100).toFixed(0)}%
                            </div>
                            <div style="font-style: italic; padding: 10px; background: rgba(255, 215, 0, 0.1); border-left: 3px solid var(--gold); border-radius: 5px;">
                                ${nash.nash_insight}
                            </div>
                        </div>
                    `;
                } else {
                    document.getElementById('nashContent').innerHTML = '<p>Análisis de Nash no disponible</p>';
                }      <div>Confianza: <strong>${pred.confidence}%</strong></div>
                        <div>Precio Objetivo: <strong>$${pred.target_price}</strong></div>
                        <div>Plazo: <strong>${pred.timeframe}</strong></div>
                        <div>Volatilidad: <strong>${pred.volatility}%</strong></div>
                    </div>
                `;
                
                // Renderizar patrones
                const patternsList = document.getElementById('patternsList');
                patternsList.innerHTML = '';
                if (data.patterns.length > 0) {
                    data.patterns.forEach(pattern => {
                        const patternClass = pattern.signal === 'BAJISTA' ? 'bearish' : '';
                        patternsList.innerHTML += `
                            <div class="pattern-item ${patternClass}">
                                <strong>${pattern.name}</strong><br>
                                Señal: ${pattern.signal}<br>
                                Confianza: ${pattern.confidence}
                            </div>
                        `;
                    });
                } else {
                    patternsList.innerHTML = '<p>No se detectaron patrones significativos</p>';
                }
                
                // Renderizar rendimiento
                const perf = data.performance;
                document.getElementById('performanceContent').innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; opacity: 0.7;">1 Mes</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${perf['1_month'] >= 0 ? 'var(--bull-green)' : 'var(--bear-red)'};">
                                ${perf['1_month'] >= 0 ? '+' : ''}${perf['1_month']}%
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; opacity: 0.7;">3 Meses</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${perf['3_months'] >= 0 ? 'var(--bull-green)' : 'var(--bear-red)'};">
                                ${perf['3_months'] >= 0 ? '+' : ''}${perf['3_months']}%
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; opacity: 0.7;">6 Meses</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${perf['6_months'] >= 0 ? 'var(--bull-green)' : 'var(--bear-red)'};">
                                ${perf['6_months'] >= 0 ? '+' : ''}${perf['6_months']}%
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; opacity: 0.7;">1 Año</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${perf['1_year'] >= 0 ? 'var(--bull-green)' : 'var(--bear-red)'};">
                                ${perf['1_year'] >= 0 ? '+' : ''}${perf['1_year']}%
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; opacity: 0.7;">Volatilidad 30d</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: var(--gold);">
                                ${perf.volatility_30d}%
                            </div>
                        </div>
                    </div>
                `;
                
                // Renderizar gráfico
                renderHistoricalChart(data.historical_data, symbol);
                
                // Mostrar modal
                document.getElementById('analysisModal').classList.add('active');
            } catch (error) {
                console.error('Error en análisis:', error);
                alert('Error al cargar el análisis completo');
            }
        }
        
        function renderHistoricalChart(historicalData, symbol) {
            const ctx = document.getElementById('historicalChart').getContext('2d');
            
            // Destruir gráfico anterior si existe
            if (currentChart) {
                currentChart.destroy();
            }
            
            const dates = historicalData.map(d => {
                const date = new Date(d.Date);
                return date.toLocaleDateString('es-MX', { month: 'short', day: 'numeric' });
            });
            const prices = historicalData.map(d => d.Close);
            
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: `${symbol} - Precio de Cierre`,
                        data: prices,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#e0e0e0',
                                font: { size: 14 }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { 
                                color: '#e0e0e0',
                                maxRotation: 45,
                                minRotation: 45
                            },
                            grid: { color: 'rgba(0, 255, 136, 0.1)' }
                        },
                        y: {
                            ticks: { color: '#e0e0e0' },
                            grid: { color: 'rgba(0, 255, 136, 0.1)' }
                        }
                    }
                }
            });
        }
        
        function closeModal() {
            document.getElementById('analysisModal').classList.remove('active'
        
        function renderWatchlist(stocks) {
            const grid = document.getElementById('watchlistGrid');
            grid.innerHTML = '';
            
            stocks.forEach(stock => {
                const card = document.createElement('div');
                card.className = 'stock-card';
                
                const changeClass = stock.change_percent >= 0 ? 'positive' : 'negative';
                const recommendationClass = stock.recommendation.includes('COMPRAR') ? 'buy' : 
                                           stock.recommendation.includes('VENDER') ? 'sell' : 'hold';
                
                card.innerHTML = `
                    <div class="symbol">${stock.symbol}</div>
                    <div class="price ${changeClass}">$${stock.current_price}</div>
                    <div class="change ${changeClass}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%
                    </div>
                    <div class="recommendation ${recommendationClass}">
                        ${stock.recommendation}
                    </div>
                `;
                
                card.onclick = () => showDetails(stock.symbol);
                
                grid.appendChild(card);
            });
        }
        
        async function loadPortfolio() {
            try {
                const response = await fetch('/api/portfolio');
                const data = await response.json();
                
                if (data.success) {
                    const value = data.value;
                    
                    document.getElementById('totalCapital').textContent = 
                        `$${data.capital_mxn.toLocaleString()} MXN`;
                    document.getElementById('portfolioValue').textContent = 
                        `$${value.current_value.toLocaleString()}`;
                    
                    const gainLossEl = document.getElementById('gainLoss');
                    gainLossEl.textContent = `$${value.gain_loss.toLocaleString()}`;
                    gainLossEl.className = `value ${value.gain_loss >= 0 ? 'positive' : 'negative'}`;
                    
                    const returnEl = document.getElementById('returnPercent');
                    returnEl.textContent = `${value.gain_loss_percent >= 0 ? '+' : ''}${value.gain_loss_percent.toFixed(2)}%`;
                    returnEl.className = `value ${value.gain_loss_percent >= 0 ? 'positive' : 'negative'}`;
                }
            } catch (error) {
                console.error('Error cargando portafolio:', error);
            }
        }
        
        function showDetails(symbol) {
            alert(`Detalles de ${symbol} - Funcionalidad en desarrollo`);
        }
        
        // Auto-refresh cada 30 segundos
        setInterval(loadMarketData, 30000);
        
        // Cargar datos iniciales
        window.addEventListener('load', () => {
            loadMarketData();
            loadPortfolio();
        });
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("🐂 BULL MARKET INTELLIGENCE SYSTEM")
    print("="*60)
    print(f"📊 Capital Inicial: ${bull_market.capital_mxn} MXN")
    print(f"🌐 WebUI: http://localhost:7777")
    print("="*60)
    
    if not YFINANCE_AVAILABLE:
        print("\n⚠️  IMPORTANTE: Instala yfinance para datos en tiempo real:")
        print("   pip install yfinance pandas numpy\n")
    
    app.run(host='0.0.0.0', port=7777, debug=True)
