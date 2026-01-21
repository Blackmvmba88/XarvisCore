interface ScoreBoardProps {
  score: number;
  totalQuestions: number;
  timeSpent: number;
  level: string;
  badgeEarned?: {
    name: string;
    description: string;
  };
}

/**
 * ScoreBoard Component
 * 
 * Displays the final score and results after completing a quiz
 * Shows badge earned if applicable
 */
export function ScoreBoard({ 
  score, 
  totalQuestions, 
  timeSpent, 
  level,
  badgeEarned 
}: ScoreBoardProps) {
  const percentage = (score / totalQuestions) * 100;
  const minutes = Math.floor(timeSpent / 60);
  const seconds = timeSpent % 60;

  const getScoreColor = (pct: number) => {
    if (pct >= 90) return 'text-green-600';
    if (pct >= 80) return 'text-blue-600';
    if (pct >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceMessage = (pct: number) => {
    if (pct >= 95) return '¡Perfecto! Eres un verdadero maestro 🏆';
    if (pct >= 90) return '¡Excelente trabajo! 🌟';
    if (pct >= 80) return '¡Muy bien! Sigue así 👏';
    if (pct >= 70) return 'Buen intento, sigue practicando 📚';
    return 'No te rindas, inténtalo de nuevo 💪';
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-gray-900 mb-2">
          ¡Quiz Completado!
        </h2>
        <p className="text-gray-600">Nivel: {level}</p>
      </div>

      {/* Score Circle */}
      <div className="flex justify-center mb-8">
        <div className="relative w-48 h-48">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="#e5e7eb"
              strokeWidth="12"
              fill="none"
            />
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="url(#gradient)"
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${(percentage / 100) * 553} 553`}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-5xl font-bold ${getScoreColor(percentage)}`}>
              {Math.round(percentage)}%
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {score}/{totalQuestions}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Message */}
      <div className="text-center mb-8">
        <p className="text-xl font-semibold text-gray-800">
          {getPerformanceMessage(percentage)}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-blue-600">{score}</div>
          <div className="text-sm text-blue-700 font-medium">Respuestas Correctas</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-purple-600">
            {minutes}:{seconds.toString().padStart(2, '0')}
          </div>
          <div className="text-sm text-purple-700 font-medium">Tiempo Total</div>
        </div>
      </div>

      {/* Badge Section */}
      {badgeEarned && percentage >= 80 && (
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-300 rounded-xl p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="text-6xl">{badgeEarned.name.split(' ')[0]}</div>
            <div className="flex-1">
              <div className="text-lg font-bold text-yellow-900">
                {badgeEarned.name}
              </div>
              <div className="text-sm text-yellow-700">
                {badgeEarned.description}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all duration-200 transform hover:scale-105">
          Intentar de Nuevo
        </button>
        <button className="flex-1 bg-white border-2 border-gray-300 text-gray-700 font-bold py-3 px-6 rounded-xl hover:border-gray-400 hover:shadow-md transition-all duration-200">
          Siguiente Nivel
        </button>
      </div>

      {/* Share Section */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500 mb-2">Comparte tu logro</p>
        <div className="flex justify-center space-x-3">
          <button className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 transition-colors">
            📱
          </button>
          <button className="w-10 h-10 rounded-full bg-green-600 text-white flex items-center justify-center hover:bg-green-700 transition-colors">
            📧
          </button>
          <button className="w-10 h-10 rounded-full bg-purple-600 text-white flex items-center justify-center hover:bg-purple-700 transition-colors">
            🔗
          </button>
        </div>
      </div>
    </div>
  );
}
