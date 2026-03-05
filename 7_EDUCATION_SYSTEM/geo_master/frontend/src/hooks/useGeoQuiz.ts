import { useEffect, useReducer, useState } from 'react';

export interface Question {
  id: string;
  type: string;
  question: string;
  options: string[];
  correct_answer: string;
  country_code: string;
}

export interface Quiz {
  quiz_id: string;
  level: string;
  questions: Question[];
  total_questions: number;
  time_limit_minutes: number | null;
  passing_score: number;
  badge: {
    name: string;
    description: string;
  };
}

export interface Answer {
  question_id: string;
  user_answer: string;
  is_correct: boolean;
  timestamp: string;
}

interface QuizState {
  quiz: Quiz | null;
  currentQuestionIndex: number;
  answers: Answer[];
  score: number;
  isLoading: boolean;
  error: string | null;
  startTime: number;
  isComplete: boolean;
}

type QuizAction =
  | { type: 'load_start'; startedAt: number }
  | { type: 'load_success'; quiz: Quiz; startedAt: number }
  | { type: 'load_error'; message: string }
  | { type: 'answer_submitted'; answer: Answer }
  | { type: 'restart'; startedAt: number };

interface CountryData {
  name: string;
  capital: string;
  continent: string;
  population: number;
  area_km2: number;
  coordinates: { lat: number; lng: number };
  capital_coordinates: { lat: number; lng: number };
  languages: string[];
  currency: string;
  flag_emoji: string;
  fun_facts: string[];
  major_cities?: Array<{
    name: string;
    coordinates: { lat: number; lng: number };
  }>;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  score: number;
  level: string;
  completed_at: string;
}

const createInitialQuizState = (): QuizState => ({
  quiz: null,
  currentQuestionIndex: 0,
  answers: [],
  score: 0,
  isLoading: true,
  error: null,
  startTime: Date.now(),
  isComplete: false,
});

export function quizReducer(state: QuizState, action: QuizAction): QuizState {
  switch (action.type) {
    case 'load_start':
      return {
        quiz: null,
        currentQuestionIndex: 0,
        answers: [],
        score: 0,
        isLoading: true,
        error: null,
        startTime: action.startedAt,
        isComplete: false,
      };
    case 'load_success':
      return {
        quiz: action.quiz,
        currentQuestionIndex: 0,
        answers: [],
        score: 0,
        isLoading: false,
        error: null,
        startTime: action.startedAt,
        isComplete: false,
      };
    case 'load_error':
      return {
        ...state,
        isLoading: false,
        error: action.message,
      };
    case 'answer_submitted': {
      if (!state.quiz || state.isComplete) {
        return state;
      }

      const answers = [...state.answers, action.answer];
      const score = action.answer.is_correct ? state.score + 1 : state.score;
      const isLastQuestion = state.currentQuestionIndex + 1 >= state.quiz.questions.length;

      return {
        ...state,
        answers,
        score,
        currentQuestionIndex: isLastQuestion ? state.currentQuestionIndex : state.currentQuestionIndex + 1,
        isComplete: isLastQuestion,
      };
    }
    case 'restart':
      return {
        ...state,
        currentQuestionIndex: 0,
        answers: [],
        score: 0,
        startTime: action.startedAt,
        isComplete: false,
        error: null,
      };
    default:
      return state;
  }
}

/**
 * useGeoQuiz Hook
 *
 * Custom hook for managing quiz state and API interactions.
 * State transitions are handled by a reducer so the quiz flow
 * remains explicit and deterministic.
 *
 * @param level - Quiz level (americas, world, expert)
 */
export function useGeoQuiz(level: string) {
  const [state, dispatch] = useReducer(quizReducer, undefined, createInitialQuizState);

  // Load quiz from backend
  useEffect(() => {
    const loadQuiz = async () => {
      dispatch({ type: 'load_start', startedAt: Date.now() });

      try {
        const response = await fetch(`/api/geo-master/quiz/${level}`);

        if (!response.ok) {
          throw new Error('Failed to load quiz');
        }

        const data = (await response.json()) as Quiz;
        dispatch({ type: 'load_success', quiz: data, startedAt: Date.now() });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        dispatch({ type: 'load_error', message });
        // Keep the existing logging for runtime diagnostics.
        console.error('Error loading quiz:', err);
      }
    };

    loadQuiz();
  }, [level]);

  const saveQuizResults = async (
    quizData: Quiz,
    finalAnswers: Answer[],
    quizStartTime: number
  ) => {
    try {
      const timeSpent = Math.floor((Date.now() - quizStartTime) / 1000);

      const results = {
        quiz_id: quizData.quiz_id,
        level: quizData.level,
        answers: finalAnswers,
        score: finalAnswers.filter((answer) => answer.is_correct).length,
        total_questions: quizData.total_questions,
        time_spent: timeSpent,
      };

      const response = await fetch('/api/geo-master/submit-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(results),
      });

      if (!response.ok) {
        throw new Error('Failed to save quiz results');
      }

      localStorage.setItem('last_quiz_results', JSON.stringify(results));
    } catch (err) {
      console.error('Error saving quiz results:', err);
    }
  };

  // Handle answer submission
  const handleAnswer = async (userAnswer: string) => {
    const quiz = state.quiz;
    if (!quiz || state.currentQuestionIndex >= quiz.questions.length || state.isComplete) {
      return;
    }

    const currentQuestion = quiz.questions[state.currentQuestionIndex];
    if (!currentQuestion) {
      return;
    }

    const answer: Answer = {
      question_id: currentQuestion.id,
      user_answer: userAnswer,
      is_correct: userAnswer === currentQuestion.correct_answer,
      timestamp: new Date().toISOString(),
    };

    const finalAnswers = [...state.answers, answer];
    const completesQuiz = state.currentQuestionIndex + 1 >= quiz.questions.length;

    dispatch({ type: 'answer_submitted', answer });

    if (completesQuiz) {
      await saveQuizResults(quiz, finalAnswers, state.startTime);
    }
  };

  // Restart quiz
  const restartQuiz = () => {
    dispatch({ type: 'restart', startedAt: Date.now() });
  };

  const currentQuestion =
    state.quiz && state.currentQuestionIndex < state.quiz.questions.length
      ? state.quiz.questions[state.currentQuestionIndex]
      : null;

  const timeElapsed = Math.floor((Date.now() - state.startTime) / 1000);
  const percentage = state.quiz?.total_questions ? (state.score / state.quiz.total_questions) * 100 : 0;

  return {
    quiz: state.quiz,
    currentQuestion,
    currentQuestionIndex: state.currentQuestionIndex,
    totalQuestions: state.quiz?.total_questions || 0,
    answers: state.answers,
    score: state.score,
    percentage,
    timeElapsed,
    isLoading: state.isLoading,
    error: state.error,
    isComplete: state.isComplete,
    handleAnswer,
    restartQuiz,
  };
}

/**
 * useCountryData Hook
 *
 * Hook for fetching and managing country data
 *
 * @param countryCode - Country code to fetch
 */
export function useCountryData(countryCode: string | null) {
  const [country, setCountry] = useState<CountryData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!countryCode) {
      setCountry(null);
      return;
    }

    const loadCountry = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`/api/geo-master/country/${countryCode}`);

        if (!response.ok) {
          throw new Error('Failed to load country data');
        }

        const data = await response.json();
        setCountry(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error loading country:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCountry();
  }, [countryCode]);

  return { country, isLoading, error };
}

/**
 * useLeaderboard Hook
 *
 * Hook for fetching and managing leaderboard data
 *
 * @param level - Leaderboard level
 */
export function useLeaderboard(level: string = 'global') {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLeaderboard = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`/api/geo-master/leaderboard/${level}`);

        if (!response.ok) {
          throw new Error('Failed to load leaderboard');
        }

        const data = await response.json();
        setLeaderboard(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error loading leaderboard:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadLeaderboard();
  }, [level]);

  return { leaderboard, isLoading, error };
}
