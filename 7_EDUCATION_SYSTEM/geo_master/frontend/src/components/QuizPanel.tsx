import { useState } from 'react';

interface Question {
  id: string;
  type: 'capital' | 'country' | 'flag' | 'city';
  question: string;
  options: string[];
  correct_answer: string;
  country_code: string;
}

interface QuizPanelProps {
  question: Question;
  questionNumber: number;
  totalQuestions: number;
  onAnswer: (answer: string) => void;
  disabled?: boolean;
}

/**
 * QuizPanel Component
 * 
 * Displays quiz questions with multiple choice options
 * Handles user interaction and answer submission
 */
export function QuizPanel({ 
  question, 
  questionNumber, 
  totalQuestions, 
  onAnswer,
  disabled = false 
}: QuizPanelProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);

  const handleOptionClick = (option: string) => {
    if (disabled || isAnswered) return;

    setSelectedAnswer(option);
    setIsAnswered(true);
    
    // Call the parent callback after a brief delay for visual feedback
    setTimeout(() => {
      onAnswer(option);
      setSelectedAnswer(null);
      setIsAnswered(false);
    }, 500);
  };

  const getOptionClassName = (option: string) => {
    let baseClass = "w-full p-4 text-left rounded-lg border-2 transition-all duration-200 font-medium ";
    
    if (disabled) {
      return baseClass + "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-300";
    }

    if (selectedAnswer === option) {
      return baseClass + "bg-blue-500 text-white border-blue-600 shadow-lg transform scale-105";
    }

    return baseClass + "bg-white text-gray-800 border-gray-300 hover:border-blue-400 hover:bg-blue-50 cursor-pointer hover:shadow-md";
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 border-b-2 border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            {questionNumber}
          </div>
          <div className="text-sm text-gray-500">
            Pregunta {questionNumber} de {totalQuestions}
          </div>
        </div>
        <div className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-semibold">
          {question.type}
        </div>
      </div>

      {/* Question */}
      <div className="py-2">
        <h3 className="text-2xl font-bold text-gray-900 leading-relaxed">
          {question.question}
        </h3>
      </div>

      {/* Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {question.options.map((option, index) => (
          <button
            key={`${question.id}-${index}`}
            onClick={() => handleOptionClick(option)}
            disabled={disabled || isAnswered}
            className={getOptionClassName(option)}
          >
            <div className="flex items-center space-x-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-600">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="flex-1">{option}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Progress indicator */}
      <div className="pt-4">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
