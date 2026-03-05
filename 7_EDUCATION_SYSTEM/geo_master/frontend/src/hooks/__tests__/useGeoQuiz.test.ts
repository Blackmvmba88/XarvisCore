import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { Quiz, useGeoQuiz } from '../useGeoQuiz';

const buildQuiz = (questions: Quiz['questions']): Quiz => ({
  quiz_id: 'quiz_test',
  level: 'americas',
  questions,
  total_questions: questions.length,
  time_limit_minutes: 10,
  passing_score: 80,
  badge: {
    name: 'Explorador',
    description: 'Badge de prueba',
  },
});

const responseOk = <T,>(data: T): Response => ({
  ok: true,
  json: async () => data,
} as Response);

const responseFail = (): Response => ({
  ok: false,
} as Response);

describe('useGeoQuiz', () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it('loads quiz and exposes first question', async () => {
    const quiz = buildQuiz([
      {
        id: 'q1',
        type: 'match_capital',
        question: 'Capital de Mexico',
        options: ['Ciudad de Mexico', 'Lima'],
        correct_answer: 'Ciudad de Mexico',
        country_code: 'mexico',
      },
    ]);
    fetchMock.mockResolvedValueOnce(responseOk(quiz));

    const { result } = renderHook(() => useGeoQuiz('americas'));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBeNull();
    expect(result.current.totalQuestions).toBe(1);
    expect(result.current.currentQuestion?.id).toBe('q1');
  });

  it('surfaces load errors from API', async () => {
    fetchMock.mockResolvedValueOnce(responseFail());

    const { result } = renderHook(() => useGeoQuiz('americas'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe('Failed to load quiz');
    expect(result.current.quiz).toBeNull();
  });

  it('transitions from one question to the next and updates score', async () => {
    const quiz = buildQuiz([
      {
        id: 'q1',
        type: 'match_capital',
        question: 'Capital de Mexico',
        options: ['Ciudad de Mexico', 'Lima'],
        correct_answer: 'Ciudad de Mexico',
        country_code: 'mexico',
      },
      {
        id: 'q2',
        type: 'match_capital',
        question: 'Capital de Peru',
        options: ['Lima', 'Quito'],
        correct_answer: 'Lima',
        country_code: 'peru',
      },
    ]);
    fetchMock.mockResolvedValueOnce(responseOk(quiz));

    const { result } = renderHook(() => useGeoQuiz('americas'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.handleAnswer('Ciudad de Mexico');
    });

    expect(result.current.score).toBe(1);
    expect(result.current.answers).toHaveLength(1);
    expect(result.current.currentQuestionIndex).toBe(1);
    expect(result.current.currentQuestion?.id).toBe('q2');
    expect(result.current.isComplete).toBe(false);
  });

  it('completes quiz and persists results when final answer is submitted', async () => {
    const setItemSpy = vi.spyOn(globalThis.localStorage, 'setItem');
    const quiz = buildQuiz([
      {
        id: 'q1',
        type: 'match_capital',
        question: 'Capital de Mexico',
        options: ['Ciudad de Mexico', 'Lima'],
        correct_answer: 'Ciudad de Mexico',
        country_code: 'mexico',
      },
    ]);

    fetchMock.mockResolvedValueOnce(responseOk(quiz));
    fetchMock.mockResolvedValueOnce(responseOk({ ok: true }));

    const { result } = renderHook(() => useGeoQuiz('americas'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.handleAnswer('Ciudad de Mexico');
    });

    await waitFor(() => expect(result.current.isComplete).toBe(true));

    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/geo-master/submit-quiz',
      expect.objectContaining({
        method: 'POST',
      })
    );
    expect(setItemSpy).toHaveBeenCalledWith('last_quiz_results', expect.any(String));
  });

  it('restarts quiz state without reloading questions', async () => {
    const quiz = buildQuiz([
      {
        id: 'q1',
        type: 'match_capital',
        question: 'Capital de Mexico',
        options: ['Ciudad de Mexico', 'Lima'],
        correct_answer: 'Ciudad de Mexico',
        country_code: 'mexico',
      },
      {
        id: 'q2',
        type: 'match_capital',
        question: 'Capital de Peru',
        options: ['Lima', 'Quito'],
        correct_answer: 'Lima',
        country_code: 'peru',
      },
    ]);
    fetchMock.mockResolvedValueOnce(responseOk(quiz));

    const { result } = renderHook(() => useGeoQuiz('americas'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.handleAnswer('Ciudad de Mexico');
    });

    act(() => {
      result.current.restartQuiz();
    });

    expect(result.current.score).toBe(0);
    expect(result.current.currentQuestionIndex).toBe(0);
    expect(result.current.answers).toHaveLength(0);
    expect(result.current.isComplete).toBe(false);
    expect(result.current.currentQuestion?.id).toBe('q1');
  });
});
