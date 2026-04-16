import { useState, useEffect } from 'react';

interface Question {
  id: string;
  type: string;
  question: string;
  options: string[];
  correct_answer: string;
  country_code: string;
}

interface Quiz {
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

interface Answer {
  question_id: string;
  user_answer: string;
  is_correct: boolean;
  timestamp: string;
}

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

/**
 * useGeoQuiz Hook
 * 
 * Custom hook for managing quiz state and API interactions
 * Handles quiz loading, answering, scoring, and persistence
 * 
 * @param level - Quiz level (americas, world, expert)
 */
export function useGeoQuiz(level: string) {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [score, setScore] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [isComplete, setIsComplete] = useState(false);

  // Load quiz from backend
  useEffect(() => {
    const loadQuiz = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // In production, this would fetch from the API
        // For now, we'll simulate with a timeout
        const response = await fetch(`/api/geo-master/quiz/${level}`);
        
        if (!response.ok) {
          throw new Error('Failed to load quiz');
        }

        const data = await response.json();
        setQuiz(data);
        setStartTime(Date.now());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error loading quiz:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadQuiz();
  }, [level]);

  // Handle answer submission
  const handleAnswer = async (userAnswer: string) => {
    if (!quiz || currentQuestionIndex >= quiz.questions.length) {
      return;
    }

    const currentQuestion = quiz.questions[currentQuestionIndex];
    const isCorrect = userAnswer === currentQuestion.correct_answer;

    const answer: Answer = {
      question_id: currentQuestion.id,
      user_answer: userAnswer,
      is_correct: isCorrect,
      timestamp: new Date().toISOString(),
    };

    // Update answers array
    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);

    // Update score
    if (isCorrect) {
      setScore(score + 1);
    }

    // Move to next question or complete quiz
    if (currentQuestionIndex + 1 >= quiz.questions.length) {
      setIsComplete(true);
      await saveQuizResults(newAnswers);
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  // Save quiz results to backend
  const saveQuizResults = async (finalAnswers: Answer[]) => {
    try {
      const timeSpent = Math.floor((Date.now() - startTime) / 1000);
      
      const results = {
        quiz_id: quiz?.quiz_id,
        level: quiz?.level,
        answers: finalAnswers,
        score: finalAnswers.filter(a => a.is_correct).length,
        total_questions: quiz?.total_questions,
        time_spent: timeSpent,
      };

      // In production, save to backend
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

      // Optionally save to local storage for persistence
      localStorage.setItem('last_quiz_results', JSON.stringify(results));
    } catch (err) {
      console.error('Error saving quiz results:', err);
    }
  };

  // Restart quiz
  const restartQuiz = () => {
    setCurrentQuestionIndex(0);
    setAnswers([]);
    setScore(0);
    setStartTime(Date.now());
    setIsComplete(false);
  };

  // Get current question
  const currentQuestion = quiz?.questions[currentQuestionIndex] || null;

  // Calculate time elapsed
  const timeElapsed = Math.floor((Date.now() - startTime) / 1000);

  // Calculate percentage
  const percentage = quiz?.total_questions 
    ? (score / quiz.total_questions) * 100 
    : 0;

  return {
    quiz,
    currentQuestion,
    currentQuestionIndex,
    totalQuestions: quiz?.total_questions || 0,
    answers,
    score,
    percentage,
    timeElapsed,
    isLoading,
    error,
    isComplete,
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
