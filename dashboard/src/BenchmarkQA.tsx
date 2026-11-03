
import { useState } from 'react'

const API_URL = 'https://reliance-chronos-api.onrender.com'

interface QAResponse {
  question: string
  answer: string
  source: string
}

const suggestedQuestions = [
  'Which model performed best?',
  'Did news improve forecasting accuracy?',
  'Compare MAE of all models',
  'Compare RMSE of all models',
  'What is directional accuracy?',
  'Why did Naive perform better?',
]

export default function BenchmarkQA() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<QAResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async (selectedQuestion?: string) => {
    const currentQuestion = (
      selectedQuestion ?? question
    ).trim()

    if (!currentQuestion) {
      setError('Please enter a question.')
      return
    }

    setQuestion(currentQuestion)
    setLoading(true)
    setError('')
    setAnswer(null)

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to get an answer.'
        )
      }

      setAnswer(data as QAResponse)

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Something went wrong. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="qa-section">

      <div className="qa-header">
        <div>
          <span className="qa-label">
            PROJECT INSIGHTS
          </span>

          <h2>Benchmark Q&A Assistant</h2>

          <p>
            Ask questions about the Reliance stock forecasting
            experiment and understand the model results.
          </p>
        </div>
      </div>

      <div className="qa-input-area">

        <input
          type="text"
          value={question}
          onChange={(event) => {
            setQuestion(event.target.value)
            setError('')
          }}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !loading) {
              askQuestion()
            }
          }}
          placeholder="Ask about MAE, RMSE, models or news impact..."
          disabled={loading}
        />

        <button
          type="button"
          onClick={() => askQuestion()}
          disabled={loading || !question.trim()}
        >
          {loading ? 'Analyzing...' : 'Ask Question'}
        </button>

      </div>

      <div className="suggested-questions">

        <span>Suggested questions</span>

        <div className="question-list">
          {suggestedQuestions.map((item) => (
            <button
              type="button"
              key={item}
              onClick={() => askQuestion(item)}
              disabled={loading}
            >
              {item}
            </button>
          ))}
        </div>

      </div>

      {loading && (
        <div className="qa-loading">
          Analyzing your benchmark results...
        </div>
      )}

      {error && (
        <div className="qa-error">
          {error}
        </div>
      )}

      {answer && (
        <div className="qa-answer">

          <div className="qa-answer-heading">
            <span>ANSWER</span>
            <span className="qa-source-badge">
              Benchmark data
            </span>
          </div>

          <div className="qa-question">
            <strong>Your question</strong>
            <p>{answer.question}</p>
          </div>

          <div className="qa-response">
            <strong>Analysis</strong>
            <p>{answer.answer}</p>
          </div>

          <div className="qa-source">
            Source: {answer.source}
          </div>

        </div>
      )}

    </section>
  )
}
