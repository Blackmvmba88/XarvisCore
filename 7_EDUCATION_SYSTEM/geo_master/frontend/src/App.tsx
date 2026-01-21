import { useState } from 'react';
import { GeoGlobe } from './components/GeoGlobe';
import { QuizPanel } from './components/QuizPanel';
import { ScoreBoard } from './components/ScoreBoard';
import { CountryInfo } from './components/CountryInfo';
import { useGeoQuiz } from './hooks/useGeoQuiz';

type AppMode = 'menu' | 'quiz' | 'explore' | 'results';

function App() {
  const [mode, setMode] = useState<AppMode>('menu');
  const [selectedLevel, setSelectedLevel] = useState<string>('americas');
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);

  const {
    quiz,
    currentQuestion,
    currentQuestionIndex,
    totalQuestions,
    score,
    timeElapsed,
    isLoading,
    isComplete,
    handleAnswer,
    restartQuiz,
  } = useGeoQuiz(selectedLevel);

  const handleStartQuiz = (level: string) => {
    setSelectedLevel(level);
    setMode('quiz');
  };

  const handleQuizComplete = () => {
    setMode('results');
  };

  if (mode === 'menu') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          <div className="text-center mb-12">
            <h1 className="text-6xl font-bold text-white mb-4">
              🌍 GeoMaster
            </h1>
            <p className="text-xl text-blue-200">
              Sistema Educativo de Geografía Interactiva
            </p>
            <p className="text-sm text-blue-300 mt-2">
              BlackMamba University - Educación Soberana
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Level 1 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 transform transition-all hover:scale-105 cursor-pointer"
                 onClick={() => handleStartQuiz('americas')}>
              <div className="text-center">
                <div className="text-6xl mb-4">🌎</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Nivel 1: Américas
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Maestro de América Latina
                </p>
                <div className="space-y-2 text-xs text-left">
                  <div className="flex items-center space-x-2">
                    <span>📍</span>
                    <span>22 países</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>⏱️</span>
                    <span>10 minutos</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>🎯</span>
                    <span>80% para pasar</span>
                  </div>
                </div>
                <button className="mt-6 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all">
                  Comenzar
                </button>
              </div>
            </div>

            {/* Level 2 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 transform transition-all hover:scale-105 cursor-pointer"
                 onClick={() => handleStartQuiz('world')}>
              <div className="text-center">
                <div className="text-6xl mb-4">🌍</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Nivel 2: Mundial
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Viajero Mundial
                </p>
                <div className="space-y-2 text-xs text-left">
                  <div className="flex items-center space-x-2">
                    <span>📍</span>
                    <span>34+ países</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>⏱️</span>
                    <span>20 minutos</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>🎯</span>
                    <span>85% para pasar</span>
                  </div>
                </div>
                <button className="mt-6 w-full bg-gradient-to-r from-green-500 to-blue-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all">
                  Comenzar
                </button>
              </div>
            </div>

            {/* Level 3 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 transform transition-all hover:scale-105 cursor-pointer"
                 onClick={() => handleStartQuiz('expert')}>
              <div className="text-center">
                <div className="text-6xl mb-4">🗺️</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Nivel 3: Experto
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Cartógrafo Soberano
                </p>
                <div className="space-y-2 text-xs text-left">
                  <div className="flex items-center space-x-2">
                    <span>📍</span>
                    <span>195 países</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>⏱️</span>
                    <span>Sin límite</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>🎯</span>
                    <span>90% para pasar</span>
                  </div>
                </div>
                <button className="mt-6 w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all">
                  Comenzar
                </button>
              </div>
            </div>
          </div>

          <div className="mt-12 text-center">
            <button
              onClick={() => setMode('explore')}
              className="bg-white/20 backdrop-blur-sm text-white font-semibold py-3 px-8 rounded-xl hover:bg-white/30 transition-all"
            >
              🔍 Modo Exploración
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'quiz') {
    if (isLoading) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
          <div className="text-white text-2xl">Cargando quiz...</div>
        </div>
      );
    }

    if (isComplete) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
          <div className="max-w-3xl w-full">
            <ScoreBoard
              score={score}
              totalQuestions={totalQuestions}
              timeSpent={timeElapsed}
              level={selectedLevel}
              badgeEarned={quiz?.badge}
            />
            <div className="mt-6 flex gap-4">
              <button
                onClick={restartQuiz}
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all"
              >
                Intentar de Nuevo
              </button>
              <button
                onClick={() => setMode('menu')}
                className="flex-1 bg-white text-gray-800 font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all"
              >
                Menú Principal
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8 text-white">
            <div>
              <h2 className="text-2xl font-bold">GeoMaster Quiz</h2>
              <p className="text-sm opacity-70">Nivel: {selectedLevel}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{score}</div>
              <div className="text-sm opacity-70">Puntos</div>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Globe */}
            <div className="h-96 lg:h-auto">
              <GeoGlobe
                mode="quiz"
                highlightCountry={currentQuestion?.country_code}
              />
            </div>

            {/* Quiz Panel */}
            <div className="flex items-center">
              {currentQuestion && (
                <QuizPanel
                  question={currentQuestion}
                  questionNumber={currentQuestionIndex + 1}
                  totalQuestions={totalQuestions}
                  onAnswer={handleAnswer}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'explore') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center text-white mb-8">
            <h2 className="text-3xl font-bold mb-4">Modo Exploración 🔍</h2>
            <p>Haz clic en un país para ver su información</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            <div className="h-96 lg:h-auto">
              <GeoGlobe
                mode="explore"
                onCountryClick={(country) => setSelectedCountry(country)}
              />
            </div>

            <div>
              {selectedCountry ? (
                <CountryInfo
                  country={{
                    name: selectedCountry,
                    capital: 'Capital',
                    continent: 'Continent',
                    population: 0,
                    area_km2: 0,
                    languages: ['Language'],
                    currency: 'Currency',
                    flag_emoji: '🏳️',
                    fun_facts: ['Fun fact 1', 'Fun fact 2'],
                  }}
                  onClose={() => setSelectedCountry(null)}
                />
              ) : (
                <div className="bg-white rounded-2xl shadow-2xl p-12 text-center text-gray-500">
                  <div className="text-6xl mb-4">🌍</div>
                  <p>Selecciona un país para ver su información</p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-8 text-center">
            <button
              onClick={() => setMode('menu')}
              className="bg-white/20 backdrop-blur-sm text-white font-semibold py-3 px-8 rounded-xl hover:bg-white/30 transition-all"
            >
              ← Volver al Menú
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
