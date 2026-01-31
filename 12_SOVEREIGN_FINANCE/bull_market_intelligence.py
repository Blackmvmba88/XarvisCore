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
# Mocks robustos para cuando no hay pandas/numpy (Soberanía Tecnológica)
if not PANDAS_AVAILABLE:
    class SeriesMock(list):
        def pct_change(self):
            changes = [0]
            for i in range(1, len(self)):
                changes.append((self[i] - self[i-1]) / self[i-1] if self[i-1] != 0 else 0)
            return SeriesMock(changes)
        
        def dropna(self):
            return SeriesMock([x for x in self if x is not None])
        
        def std(self):
            if len(self) < 2: return 0
            mu = sum(self) / len(self)
            return (sum((x - mu)**2 for x in self) / (len(self) - 1))**0.5
        
        def mean(self):
            return sum(self) / len(self) if self else 0
        
        def tail(self, n):
            return SeriesMock(self[-n:])
        
        def rolling(self, window):
            class RollingMock:
                def __init__(self, data, w):
                    self.data = data
                    self.w = w
                def mean(self):
                    res = []
                    for i in range(len(self.data)):
                        if i < self.w - 1: res.append(None)
                        else:
                            window_sum = sum(self.data[i-self.w+1 : i+1])
                            res.append(window_sum / self.w)
                    return SeriesMock(res)
                def std(self):
                    res = []
                    for i in range(len(self.data)):
                        if i < self.w - 1: res.append(None)
                        else:
                            window_data = self.data[i-self.w+1 : i+1]
                            mu = sum(window_data) / self.w
                            res.append((sum((x - mu)**2 for x in window_data) / (self.w - 1))**0.5)
                    return SeriesMock(res)
            return RollingMock(self, window)

        def diff(self):
            diffs = [0]
            for i in range(1, len(self)):
                diffs.append(self[i] - self[i-1])
            return SeriesMock(diffs)

        def where(self, cond, other):
            return SeriesMock([self[i] if cond[i] else other for i in range(len(self))])

        def __gt__(self, other):
            return SeriesMock([x > other if x is not None else False for x in self])
        
        def __lt__(self, other):
            return SeriesMock([x < other if x is not None else False for x in self])

        def __ge__(self, other):
            return SeriesMock([x >= other if x is not None else False for x in self])

        def __le__(self, other):
            return SeriesMock([x <= other if x is not None else False for x in self])

        def __and__(self, other):
            return SeriesMock([self[i] and other[i] for i in range(len(self))])

        def __or__(self, other):
            return SeriesMock([self[i] or other[i] for i in range(len(self))])
            
        def __getitem__(self, key):
            if isinstance(key, (list, SeriesMock)) and len(key) == len(self):
                # Filtrado por máscara booleana
                return SeriesMock([self[i] for i in range(len(self)) if key[i]])
            return super().__getitem__(key)

        def corr(self, other):
            if len(self) != len(other) or len(self) < 2: return 0
            # Asegurar que ambos son listas de números
            s1 = [x for x in self if x is not None]
            s2 = [x for x in other if x is not None]
            if not s1 or not s2: return 0
            mu1, mu2 = sum(s1)/len(s1), sum(s2)/len(s2)
            num = sum((self[i]-mu1)*(other[i]-mu2) for i in range(len(self)) if self[i] is not None and other[i] is not None)
            den = (sum((x-mu1)**2 for x in s1) * sum((y-mu2)**2 for y in s2))**0.5
            return num / den if den != 0 else 0

    class pd:
        @staticmethod
        def Series(data):
            return SeriesMock(data)
        @staticmethod
        def isna(x):
            return x is None

    class np:
        @staticmethod
        def sqrt(x):
            return x ** 0.5
        @staticmethod
        def mean(arr):
            arr = [x for x in arr if x is not None]
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
        
        # Estrategias del inversor y sus payoffs esperados (Optimizado para Micromovimientos)
        strategies = {
            'COMPRAR': {
                'payoff_alcista': 0.15,    # 15% ganancia
                'payoff_lateral': -0.02,    # Penalización por estancamiento (costo de oportunidad)
                'payoff_bajista': -0.15,    # Pérdida real
                'expected_return': None
            },
            'MANTENER': {
                'payoff_alcista': 0.05,     # Ganancia pasiva menor
                'payoff_lateral': 0.01,     # Ganancia mínima
                'payoff_bajista': -0.03,    # Pérdida protegida
                'expected_return': None
            },
            'VENDER': {
                'payoff_alcista': -0.05,    # Costo de oportunidad alto
                'payoff_lateral': 0.00,     # Neutral
                'payoff_bajista': 0.05,     # "Ganancia" por evitar caída
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
        
        # Clasificar días recientes con umbrales más sensibles (0.5%)
        recent_returns = returns.tail(20)
        
        bullish_days = len(recent_returns[recent_returns > 0.005])
        neutral_days = len(recent_returns[(recent_returns >= -0.005) & (recent_returns <= 0.005)])
        bearish_days = len(recent_returns[recent_returns < -0.005])
        
        total = max(bullish_days + neutral_days + bearish_days, 1)
        
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
    
    def deposit_capital(self, amount):
        """Depositar capital virtual en el sistema"""
        self.capital_mxn += amount
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'DEPOSIT',
            'amount': amount,
            'new_balance': self.capital_mxn
        })
        self.save_history() # Verificamos si existe un método para esto abajo
        return self.capital_mxn

    def withdraw_capital(self, amount):
        """Retirar capital virtual del sistema"""
        if amount > self.capital_mxn:
            return None
        self.capital_mxn -= amount
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'WITHDRAW',
            'amount': amount,
            'new_balance': self.capital_mxn
        })
        self.save_history()
        return self.capital_mxn
    
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
        """Ejecutar una COMPRA de activo"""
        total_cost = shares * purchase_price
        if total_cost > self.capital_mxn:
            return {'success': False, 'message': 'Saldo insuficiente para esta operación'}

        if symbol not in self.portfolio:
            self.portfolio[symbol] = {
                'shares': 0,
                'avg_price': 0,
                'total_invested': 0
            }
        
        current = self.portfolio[symbol]
        total_shares = current['shares'] + shares
        total_invested = current['total_invested'] + total_cost
        
        self.portfolio[symbol] = {
            'shares': total_shares,
            'avg_price': total_invested / total_shares,
            'total_invested': total_invested
        }
        
        # Descontar del capital
        self.capital_mxn -= total_cost
        
        # Registrar en historial
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': purchase_price,
            'total': total_cost,
            'remaining_balance': self.capital_mxn
        })
        
        self.save_portfolio()
        self.save_history()
        
        return {'success': True, 'portfolio': self.portfolio[symbol], 'balance': self.capital_mxn}

    def sell_from_portfolio(self, symbol, shares, sell_price):
        """Ejecutar una VENTA de activo"""
        if symbol not in self.portfolio or self.portfolio[symbol]['shares'] < shares:
            return {'success': False, 'message': 'No tienes suficientes acciones para vender'}

        current = self.portfolio[symbol]
        total_revenue = shares * sell_price
        
        # Actualizar portafolio
        current['shares'] -= shares
        # El precio promedio no cambia al vender, pero el total invertido se ajusta proporcionalmente
        current['total_invested'] = current['shares'] * current['avg_price']
        
        if current['shares'] == 0:
            del self.portfolio[symbol]
        else:
            self.portfolio[symbol] = current

        # Aumentar capital
        self.capital_mxn += total_revenue

        # Registrar en historial
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'SELL',
            'symbol': symbol,
            'shares': shares,
            'price': sell_price,
            'total': total_revenue,
            'remaining_balance': self.capital_mxn
        })

        self.save_portfolio()
        self.save_history()

        return {'success': True, 'balance': self.capital_mxn}
    
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
    """Agregar activo al portafolio (COMPRA)"""
    data = request.json
    symbol = data.get('symbol')
    shares = float(data.get('shares', 0))
    price = float(data.get('price', 0))
    
    result = bull_market.add_to_portfolio(symbol, shares, price)
    return jsonify(result)

@app.route('/api/portfolio/sell', methods=['POST'])
def sell_from_portfolio():
    """Vender activo del portafolio (VENTA)"""
    data = request.json
    symbol = data.get('symbol')
    shares = float(data.get('shares', 0))
    price = float(data.get('price', 0))
    
    result = bull_market.sell_from_portfolio(symbol, shares, price)
    return jsonify(result)

@app.route('/api/balance/deposit', methods=['POST'])
def deposit_balance():
    """Depositar capital virtual"""
    amount = float(request.json.get('amount', 0))
    new_balance = bull_market.deposit_capital(amount)
    return jsonify({'success': True, 'balance': new_balance})

@app.route('/api/balance/withdraw', methods=['POST'])
def withdraw_balance():
    """Retirar capital virtual"""
    amount = float(request.json.get('amount', 0))
    new_balance = bull_market.withdraw_capital(amount)
    if new_balance is not None:
        return jsonify({'success': True, 'balance': new_balance})
    return jsonify({'success': False, 'message': 'Saldo insuficiente'}), 400

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
    <title>🐂 Xarvis Finance | Bull Market Intelligence</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bull-green: #00ff88;
            --bear-red: #ff3366;
            --gold: #ffd700;
            --bg: #05050a;
            --glass: rgba(15, 15, 30, 0.75);
            --glass-bright: rgba(30, 30, 50, 0.9);
            --border: rgba(0, 255, 136, 0.2);
            --text: #ffffff;
            --text-dim: #b0b0b0;
            --font-main: 'Outfit', 'Inter', -apple-system, sans-serif;
            --accent-gradient: linear-gradient(135deg, #00ff88 0%, #00bcff 100%);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: var(--font-main);
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 20% 20%, rgba(0, 255, 136, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(0, 188, 255, 0.05) 0%, transparent 40%);
        }

        /* --- UI COMPONENTS --- */
        .glass-panel {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }

        /* --- HEADER & NAVIGATION --- */
        header {
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.4);
        }

        .logo-area h1 {
            font-size: 1.5rem;
            letter-spacing: 2px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        .balance-pill {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--bull-green);
            padding: 8px 20px;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            transition: 0.3s;
        }

        .balance-pill:hover { background: rgba(0, 255, 136, 0.2); scale: 1.05; }

        /* --- LAYOUT --- */
        .main-grid {
            display: grid;
            grid-template-columns: 350px 1fr 350px;
            gap: 20px;
            padding: 20px;
            height: calc(100vh - 80px);
        }

        /* --- LISTS --- */
        .scrollable { overflow-y: auto; height: 100%; padding-right: 5px; }
        .scrollable::-webkit-scrollbar { width: 5px; }
        .scrollable::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

        .instrument-item {
            padding: 15px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.03);
            margin-bottom: 10px;
            cursor: pointer;
            transition: 0.2s;
            border: 1px solid transparent;
        }

        .instrument-item:hover {
            background: rgba(0, 255, 136, 0.05);
            border-color: var(--border);
        }

        .status-up { color: var(--bull-green); }
        .status-down { color: var(--bear-red); }

        /* --- TRADING TERMINAL --- */
        .terminal-viewport {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .chart-box { height: 60%; position: relative; }

        .trade-controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: auto;
        }

        .btn-trade {
            padding: 15px;
            border: none;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.1rem;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
        }

        .btn-buy { background: var(--bull-green); color: #000; box-shadow: 0 0 20px rgba(0, 255, 136, 0.3); }
        .btn-sell { background: var(--bear-red); color: #fff; box-shadow: 0 0 20px rgba(255, 51, 102, 0.3); }

        /* --- MODALS --- */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.85);
            display: none;
            place-items: center;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }

        .modal-content {
            width: 500px;
            background: var(--glass-bright);
            border: 1px solid var(--bull-green);
            padding: 40px;
            border-radius: 30px;
            text-align: center;
        }

        input {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            padding: 15px;
            border-radius: 10px;
            color: #fff;
            font-size: 1.2rem;
            margin: 20px 0;
            text-align: center;
        }

        .nash-tip {
            background: rgba(255, 215, 0, 0.1);
            color: var(--gold);
            padding: 15px;
            border-radius: 10px;
            font-size: 0.9rem;
            margin-bottom: 20px;
            border: 1px dashed var(--gold);
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-dim);
            padding: 10px 20px;
            cursor: pointer;
            font-weight: 600;
            border-bottom: 2px solid transparent;
        }

        .tab-btn.active {
            color: var(--bull-green);
            border-bottom-color: var(--bull-green);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <h1>🐂 XARVIS <span style="font-weight: 200;">FINANCE</span></h1>
        </div>
        
        <div style="display: flex; gap: 20px;">
            <div class="balance-pill" onclick="openBalanceModal()">
                <div style="font-size: 0.8rem; color: var(--text-dim);">EFECTIVO DISPONIBLE</div>
                <div id="topBalance" style="font-weight: 800; font-size: 1.1rem;">$0.00</div>
                <div style="background: var(--bull-green); color: #000; padding: 2px 8px; border-radius: 4px; font-weight: 800;">+</div>
            </div>
        </div>
    </header>

    <div class="main-grid">
        <!-- Explorador de Mercado -->
        <aside class="glass-panel viewport">
            <h3 style="margin-bottom: 20px; opacity: 0.6; font-size: 0.8rem; letter-spacing: 1px;">MERCADO EN VIVO</h3>
            <div class="scrollable" id="watchlistArea">
                <div style="text-align: center; opacity: 0.5; margin-top: 50px;">Sincronizando con Wall Street...</div>
            </div>
        </aside>

        <!-- Terminal Principal -->
        <main class="terminal-viewport">
            <div class="glass-panel chart-box">
                <div id="chartHeader" style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <h2 id="currentSymbol">SELECCIONA ACTIVO</h2>
                    <div id="currentPrice" style="font-size: 1.5rem; font-weight: 800;">$0.00</div>
                </div>
                <div style="height: calc(100% - 60px);">
                    <canvas id="mainChart"></canvas>
                </div>
            </div>

            <div class="glass-panel" style="flex: 1; display: flex; flex-direction: column;">
                <div style="margin-bottom: 15px; border-bottom: 1px solid var(--border); display: flex; gap: 20px;">
                    <button class="tab-btn active">ANÁLISIS DE NASH</button>
                    <button class="tab-btn">INDICADORES</button>
                    <button class="tab-btn">NOTICIAS</button>
                </div>
                
                <div id="nashAdvisor" style="flex: 1;">
                    <div style="text-align: center; margin-top: 30px; opacity: 0.3;">Selecciona un activo para recibir asesoría soberana</div>
                </div>

                <div class="trade-controls">
                    <button class="btn-trade btn-buy" onclick="openTradeModal('BUY')">EJECUTAR COMPRA</button>
                    <button class="btn-trade btn-sell" onclick="openTradeModal('SELL')">EJECUTAR VENTA</button>
                </div>
            </div>
        </main>

        <!-- Portafolio y Actividad -->
        <aside class="glass-panel viewport">
            <h3 style="margin-bottom: 20px; opacity: 0.6; font-size: 0.8rem; letter-spacing: 1px;">MI PORTAFOLIO</h3>
            <div id="portfolioSummary" style="margin-bottom: 20px; padding: 15px; border-radius: 12px; background: rgba(0,0,0,0.3);">
                <div style="font-size: 0.8rem; opacity: 0.6;">VALOR TOTAL</div>
                <div id="portfolioTotalValue" style="font-size: 1.8rem; font-weight: 800;">$0.00</div>
                <div id="portfolioPNL" style="font-size: 0.9rem; font-weight: 600;">$0.00 (0.00%)</div>
            </div>
            <div class="scrollable" id="portfolioList">
                <!-- Se llena dinámicamente -->
            </div>
        </aside>
    </div>

    <!-- MODALES -->
    <div class="modal-overlay" id="tradeModal">
        <div class="modal-content">
            <h2 id="tradeActionTitle">COMPRAR TSLA</h2>
            <div id="tradeNashAdvice" class="nash-tip">Cargando Inteligencia Competitiva...</div>
            <div style="font-size: 0.9rem; opacity: 0.6;">CANTIDAD DE ACCIONES</div>
            <input type="number" id="tradeQuantity" value="1" min="1" oninput="updateTradeTotal()">
            <div style="display: flex; justify-content: space-between; margin-bottom: 30px;">
                <span>TOTAL A PAGAR:</span>
                <span id="tradeTotalVal" style="font-weight: 800; color: var(--bull-green);">$0.00</span>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-trade" style="background: #333; color: #fff; flex: 1;" onclick="closeTradeModal()">CANCELAR</button>
                <button id="confirmTradeBtn" class="btn-trade" style="flex: 2; background: var(--accent-gradient); color: #000;">CONFIRMAR ORDEN</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="balanceModal">
        <div class="modal-content" style="border-color: var(--gold);">
            <h2 style="color: var(--gold);">GESTIÓN DE CAPITAL SOBERANO</h2>
            <p style="margin: 15px 0; opacity: 0.7;">Agrega fondos virtuales para experimentar operaciones en tiempo real.</p>
            <div style="font-size: 0.9rem; opacity: 0.6;">MONTO A DEPOSITAR (MXN)</div>
            <input type="number" id="depositAmount" value="10000" step="1000">
            <button class="btn-trade" style="width: 100%; background: var(--gold); color: #000;" onclick="executeDeposit()">RECARGAR SALDO VIRTUAL</button>
            <button style="background: none; border: none; color: #666; margin-top: 20px; cursor: pointer;" onclick="closeBalanceModal()">VOLVER</button>
        </div>
    </div>

    <script>
        let currentSymbol = null;
        let currentPrice = 0;
        let currentChart = null;
        let marketData = {};
        let portfolio = {};
        let userBalance = 0;

        // Initialize
        window.onload = async () => {
            await refreshData();
            setInterval(refreshData, 30000); // 30s auto-refresh
        };

        async function refreshData() {
            await loadMarket();
            await loadPortfolio();
        }

        async function loadMarket() {
            try {
                const res = await fetch('/api/watchlist');
                const data = await res.json();
                if (data.success) {
                    renderWatchlist(data.watchlist);
                }
            } catch (e) { console.error(e); }
        }

        function renderWatchlist(stocks) {
            const area = document.getElementById('watchlistArea');
            area.innerHTML = '';
            stocks.forEach(s => {
                marketData[s.symbol] = s;
                const div = document.createElement('div');
                div.className = 'instrument-item';
                div.onclick = () => selectSymbol(s.symbol);
                const color = s.change >= 0 ? 'var(--bull-green)' : 'var(--bear-red)';
                div.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-weight:800;">${s.symbol}</span>
                        <span style="font-weight:800;">$${s.current_price.toLocaleString()}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; opacity:0.7;">
                        <span>Vol: ${(s.volume/1000000).toFixed(1)}M</span>
                        <span style="color:${color}">${s.change_percent.toFixed(2)}%</span>
                    </div>
                `;
                area.appendChild(div);
            });
            if (!currentSymbol && stocks.length > 0) selectSymbol(stocks[0].symbol);
        }

        async function selectSymbol(symbol) {
            currentSymbol = symbol;
            const stock = marketData[symbol];
            currentPrice = stock.current_price;
            
            document.getElementById('currentSymbol').innerText = symbol;
            document.getElementById('currentPrice').innerText = `$${currentPrice.toLocaleString()}`;
            document.getElementById('currentPrice').className = stock.change >= 0 ? 'status-up' : 'status-down';

            // Load analysis
            try {
                const res = await fetch(`/api/analyze/${symbol}`);
                const data = await res.json();
                renderAnalysis(data);
                renderMainChart(data.historical_data, symbol);
            } catch (e) { console.log(e); }
        }

        function renderAnalysis(data) {
            const nash = data.nash_analysis;
            const advisor = document.getElementById('nashAdvisor');
            if (nash) {
                const strategyColor = nash.equilibrium_strategy === 'COMPRAR' ? 'var(--bull-green)' : 
                                     nash.equilibrium_strategy === 'VENDER' ? 'var(--bear-red)' : 'var(--gold)';
                advisor.innerHTML = `
                    <div style="padding: 20px;">
                        <div style="font-size: 3rem; font-weight: 900; color: ${strategyColor}; margin-bottom: 15px;">
                            ${nash.equilibrium_strategy}
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;">
                            <div class="glass-panel" style="padding:10px; text-align:center;">
                                <div style="font-size:0.7rem; opacity:0.6;">CONFIANZA</div>
                                <div style="font-weight:800;">${nash.confidence}%</div>
                            </div>
                            <div class="glass-panel" style="padding:10px; text-align:center;">
                                <div style="font-size:0.7rem; opacity:0.6;">RETORNO ESP.</div>
                                <div style="font-weight:800; color:var(--bull-green);">${nash.expected_return}%</div>
                            </div>
                            <div class="glass-panel" style="padding:10px; text-align:center;">
                                <div style="font-size:0.7rem; opacity:0.6;">SHARPE</div>
                                <div style="font-weight:800;">${nash.sharpe_ratio}</div>
                            </div>
                        </div>
                        <p style="opacity:0.8; line-height:1.6; font-style:italic;">"${nash.nash_insight}"</p>
                    </div>
                `;
                document.getElementById('tradeNashAdvice').innerText = `💡 NASH RECOMIENDA: ${nash.equilibrium_strategy} (${nash.confidence}% confianza)`;
            }
        }

        function renderMainChart(histData, symbol) {
            const ctx = document.getElementById('mainChart').getContext('2d');
            if (currentChart) currentChart.destroy();
            
            const labels = histData.map(d => new Date(d.Date).toLocaleDateString('es-MX', {month:'short', day:'numeric'}));
            const prices = histData.map(d => d.Close);

            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: symbol,
                        data: prices,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.05)',
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { 
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: 'rgba(255,255,255,0.3)' }
                        }
                    }
                }
            });
        }

        async function loadPortfolio() {
            try {
                const res = await fetch('/api/portfolio');
                const data = await res.json();
                if (data.success) {
                    userBalance = data.capital_mxn;
                    portfolio = data.portfolio;
                    
                    document.getElementById('topBalance').innerText = `$${userBalance.toLocaleString(undefined, {minimumFractionDigits:2})}`;
                    
                    const val = data.value;
                    document.getElementById('portfolioTotalValue').innerText = `$${val.current_value.toLocaleString()}`;
                    const pnlColor = val.gain_loss >= 0 ? 'var(--bull-green)' : 'var(--bear-red)';
                    document.getElementById('portfolioPNL').innerText = `${val.gain_loss >= 0 ? '+' : ''}$${val.gain_loss.toLocaleString()} (${val.gain_loss_percent.toFixed(2)}%)`;
                    document.getElementById('portfolioPNL').style.color = pnlColor;

                    renderPortfolio(data.portfolio);
                }
            } catch (e) { console.error(e); }
        }

        function renderPortfolio(assets) {
            const list = document.getElementById('portfolioList');
            list.innerHTML = '';
            
            Object.entries(assets).forEach(([sym, data]) => {
                const mData = marketData[sym] || { current_price: data.avg_price };
                const currentVal = data.shares * mData.current_price;
                const pnl = currentVal - data.total_invested;
                const pnlPct = (pnl / data.total_invested) * 100;

                const div = document.createElement('div');
                div.className = 'instrument-item';
                div.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-weight:800;">${sym}</span>
                        <span style="font-weight:800;">$${currentVal.toLocaleString()}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.7;">
                        <span>${data.shares} acciones @ $${data.avg_price.toFixed(2)}</span>
                        <span style="color:${pnl >= 0 ? 'var(--bull-green)' : 'var(--bear-red)'}">${pnl >= 0 ? '+' : ''}${pnlPct.toFixed(2)}%</span>
                    </div>
                `;
                list.appendChild(div);
            });
        }

        // --- TRADING LOGIC ---
        function openTradeModal(action) {
            if (!currentSymbol) return;
            const modal = document.getElementById('tradeModal');
            document.getElementById('tradeActionTitle').innerText = `${action === 'BUY' ? '⚡ COMPRAR' : '🔥 VENDER'} ${currentSymbol}`;
            document.getElementById('tradeActionTitle').style.color = action === 'BUY' ? 'var(--bull-green)' : 'var(--bear-red)';
            
            const btn = document.getElementById('confirmTradeBtn');
            btn.style.background = action === 'BUY' ? 'var(--accent-gradient)' : 'var(--bear-red)';
            btn.onclick = () => executeTrade(action);
            
            modal.style.display = 'grid';
            updateTradeTotal();
        }

        function closeTradeModal() {
            document.getElementById('tradeModal').style.display = 'none';
        }

        function updateTradeTotal() {
            const qty = document.getElementById('tradeQuantity').value;
            const total = qty * currentPrice;
            document.getElementById('tradeTotalVal').innerText = `$${total.toLocaleString(undefined, {minimumFractionDigits:2})}`;
        }

        async function executeTrade(action) {
            const qty = parseFloat(document.getElementById('tradeQuantity').value);
            const endpoint = action === 'BUY' ? '/api/portfolio/add' : '/api/portfolio/sell';
            
            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: currentSymbol,
                        shares: qty,
                        price: currentPrice
                    })
                });
                const data = await res.json();
                if (data.success) {
                    alert(`Operación Exitosa: ${action} ${qty} ${currentSymbol}`);
                    closeTradeModal();
                    await refreshData();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (e) { alert('Excepción en la red: ' + e); }
        }

        // --- BALANCE LOGIC ---
        function openBalanceModal() { document.getElementById('balanceModal').style.display = 'grid'; }
        function closeBalanceModal() { document.getElementById('balanceModal').style.display = 'none'; }

        async function executeDeposit() {
            const amount = parseFloat(document.getElementById('depositAmount').value);
            try {
                const res = await fetch('/api/balance/deposit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ amount: amount })
                });
                const data = await res.json();
                if (data.success) {
                    alert(`Capital Añadido: $${amount.toLocaleString()} MXN`);
                    closeBalanceModal();
                    await refreshData();
                }
            } catch (e) { console.error(e); }
        }
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
