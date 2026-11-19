// BM25 retrieval over the bundled guideline chunks (port of app/services/retriever.py).
import { readFileSync } from 'node:fs'

const metadata = JSON.parse(
  readFileSync(new URL('./data/guidelines.json', import.meta.url), 'utf-8'),
)

const STOPWORDS = new Set(
  `what when where why how is are the a an for with without should can could would do does did first line
treatment question answer main point guide guidelines general medical information patient health about this
that there these those more most into from of on in to be it as or and not used provide provided signs symptoms
common related condition conditions`.split(/\s+/),
)

export function tokenize(text) {
  return (text.toLowerCase().match(/\w+/gu) || []).filter((t) => !STOPWORDS.has(t))
}

// BM25Okapi with the same defaults as rank_bm25 (k1=1.5, b=0.75, epsilon=0.25).
const K1 = 1.5
const B = 0.75
const EPSILON = 0.25

const docs = metadata.map((item) => {
  const tokens = tokenize(item.text)
  const freqs = new Map()
  for (const t of tokens) freqs.set(t, (freqs.get(t) || 0) + 1)
  return { tokens, freqs, len: tokens.length, tokenSet: new Set(tokens) }
})
const avgdl = docs.reduce((s, d) => s + d.len, 0) / docs.length

const idf = new Map()
{
  const df = new Map()
  for (const d of docs) for (const t of d.freqs.keys()) df.set(t, (df.get(t) || 0) + 1)
  let idfSum = 0
  const negative = []
  for (const [t, n] of df) {
    const value = Math.log(docs.length - n + 0.5) - Math.log(n + 0.5)
    idf.set(t, value)
    idfSum += value
    if (value < 0) negative.push(t)
  }
  const floor = EPSILON * (idfSum / idf.size)
  for (const t of negative) idf.set(t, floor)
}

function scores(queryTokens) {
  return docs.map((d) => {
    let score = 0
    for (const q of queryTokens) {
      const f = d.freqs.get(q) || 0
      score += (idf.get(q) || 0) * ((f * (K1 + 1)) / (f + K1 * (1 - B + (B * d.len) / avgdl)))
    }
    return score
  })
}

export function retrieveTopChunks(query, topK = 2) {
  const queryTokens = tokenize(query)
  const querySet = new Set(queryTokens)
  const s = scores(queryTokens)
  const ranked = s
    .map((score, idx) => ({ score, idx }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)

  return ranked.map(({ score, idx }, i) => {
    const item = metadata[idx]
    let overlap = 0
    for (const t of querySet) if (docs[idx].tokenSet.has(t)) overlap++
    return {
      rank: i + 1,
      chunk_id: item.chunk_id,
      text: item.text,
      keyword_score: score,
      exact_coverage: querySet.size ? overlap / querySet.size : 0,
      score,
    }
  })
}
