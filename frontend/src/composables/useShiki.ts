// frontend/src/composables/useShiki.ts

import { ref, watch } from 'vue'
import {
  createHighlighter,
  type Highlighter,
  type LanguageInput,
} from 'shiki'

// Import themes
import githubDark from 'shiki/dist/themes/github-dark.mjs'
import githubLight from 'shiki/dist/themes/github-light.mjs'

/** Singleton highlighter promise — created once, reused everywhere. */
let highlighterPromise: Promise<Highlighter> | null = null

/** Loading state for UI feedback. */
const isReady = ref(false)
const loadError = ref<string | null>(null)

export function useShiki() {
  /**
   * Get or create the singleton Shiki highlighter.
   * Created once with both themes loaded.
   */
  function getHighlighter(): Promise<Highlighter> {
    if (!highlighterPromise) {
      highlighterPromise = createHighlighter({
        themes: [githubDark as any, githubLight as any],
        langs: [],  // Load dynamically via loadLanguage()
      })
        .then((hl) => {
          isReady.value = true
          return hl
        })
        .catch((err) => {
          loadError.value = err.message || 'Failed to initialize Shiki'
          highlighterPromise = null  // Allow retry
          throw err
        })
    }
    return highlighterPromise
  }

  /**
   * Load a language into the highlighter on demand.
   * Safe to call multiple times — Shiki skips already-loaded languages.
   */
  async function loadLanguage(lang: string): Promise<void> {
    const hl = await getHighlighter()

    // Skip if already loaded
    const loadedLangs = hl.getLoadedLanguages()
    if (loadedLangs.includes(lang)) return

    try {
      // Import the language grammar dynamically
      const grammar = await import(
        `shiki/langs/${lang}.mjs`
      ).then((m: any) => m.default || m)
      await hl.loadLanguage(grammar as LanguageInput)
    } catch {
      // Language not available — will fall back to 'text'
      console.warn(`Shiki: language '${lang}' not available, falling back to text`)
    }
  }

  /**
   * Get current theme based on data-theme attribute
   */
  function getCurrentTheme(): string {
    const theme = document.documentElement.getAttribute('data-theme')
    return theme === 'light' ? 'github-light' : 'github-dark'
  }

  /**
   * Highlight code with theme matching current mode.
   */
  async function highlight(
    code: string,
    lang: string,
  ): Promise<string> {
    const hl = await getHighlighter()

    // Ensure language is loaded
    await loadLanguage(lang)

    // Use theme matching current mode
    const theme = getCurrentTheme()
    return hl.codeToHtml(code, {
      lang: hl.getLoadedLanguages().includes(lang) ? lang : 'text',
      theme,
    })
  }

  return { getHighlighter, loadLanguage, highlight, isReady, loadError }
}
