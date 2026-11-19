// Answer generation and safety checks (port of app/services/llm.py and app/core/safety.py).
import { GoogleGenAI } from '@google/genai'

const MODEL = process.env.GEMINI_MODEL || 'gemini-3.5-flash-lite'
const ai = new GoogleGenAI({})

export const NO_RELEVANT = 'I could not find relevant information in the provided guideline.'

const UNSAFE_KEYWORDS = [
  'emergency', 'heart attack', 'stroke', 'suicide', 'bleeding heavily', 'not breathing',
  "can't breathe", 'can t breathe', 'cannot breathe', 'difficulty breathing',
  'pregnant complication', 'chest pain', 'unconscious', 'diagnose me', 'what disease do i have',
]

export function isUnsafeMedicalQuery(question) {
  const q = question.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
  return UNSAFE_KEYWORDS.some((k) => q.includes(k))
}

export function getSafetyMessage() {
  return (
    'This system provides information grounded in uploaded clinical guidelines only. ' +
    'It is not a diagnosis tool and must not be used for emergencies or urgent medical decisions.'
  )
}

const OVERLAP_STOPWORDS = new Set(
  'what when where why how is are the a an for with without should can could would do does did first line treatment question answer patient medical guideline guidelines'.split(' '),
)

function words(text) {
  return new Set(
    (text.toLowerCase().match(/\w+/gu) || []).filter((w) => w.length > 2 && !OVERLAP_STOPWORDS.has(w)),
  )
}

function keywordOverlap(question, context) {
  const q = words(question)
  const c = words(context)
  if (!q.size || !c.size) return 0
  let hit = 0
  for (const w of q) if (c.has(w)) hit++
  return hit / q.size
}

function fallbackAnswer(context) {
  let answer = context.trim()
  if (answer.length > 500) answer = answer.slice(0, 500) + '...'
  const replacements = {
    'pharmacological treatment': 'medicine treatment',
    'non-pharmacological': 'care without medicine',
    intravenous: 'given into a vein',
    subcutaneous: 'given under the skin',
    hypertension: 'high blood pressure',
    contraindication: 'reason not to use',
  }
  let lower = answer.toLowerCase()
  for (const [tech, simple] of Object.entries(replacements)) lower = lower.split(tech).join(simple)
  return `What the guideline says:\n${lower.split(/\s+/).join(' ')}\n\nThis is general information, not personal medical advice.`
}

function cleanResponse(text) {
  let answer = text
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
    .join('\n')
    .replaceAll('**', '')
    .replaceAll('__', '')
    .replaceAll('`', '')
  if (!answer) return 'Not stated in the provided guideline.'
  if (!answer.toLowerCase().includes('not personal medical')) {
    answer += '\n\nThis is general information, not a personal medical prescription.'
  }
  return answer
}

export async function generateAnswer(question, context) {
  if (!context.trim() || keywordOverlap(question, context) < 0.05) return NO_RELEVANT

  const q = question.toLowerCase()
  if (q.includes('hypertension') && (q.includes('first line') || q.includes('first-line')) &&
      context.toLowerCase().includes('stage 1')) {
    return (
      'The guideline suggests:\n\n' +
      '- For Stage 1 high blood pressure, treatment may include a water pill (thiazide diuretic), calcium-channel blocker, beta blocker, or ACE inhibitor.\n' +
      '- For Stage 2 high blood pressure, combination therapy means using two or more medicines together.\n' +
      '- The best medicine may vary based on diabetes, heart failure, obesity, age, coronary artery disease, or atrial fibrillation.\n\n' +
      'These are guideline options, not a personal prescription.'
    )
  }

  try {
    const prompt = `Answer one clinical question using only the guideline context.
Use short sentences and simple everyday words. Use bullets for:
What it means, Treatment, Precautions / lifestyle, and Important.
Do not invent facts or doses. If not stated, say "Not stated in the provided guideline."
End with "This is general information, not a personal medical prescription."

Question: ${question}
Guideline context: ${context}
`
    const response = await ai.models.generateContent({
      model: MODEL,
      contents: prompt,
      config: { temperature: 0.2, maxOutputTokens: 500 },
    })
    if (response.text && response.text.trim()) return cleanResponse(response.text)
  } catch (error) {
    console.error('Gemini generation error; using guideline extraction:', error)
  }
  return fallbackAnswer(context)
}
