import { css } from './core/stylesheet.js'
import { PopupController } from './core/popup.js'
import { WheelHandlerMixin } from './core/wheel-handler.js'
import { StatsData, StatsSpecs } from './core/stats.js'


export class LintIIVisualizer extends HTMLElement {
    static get observedAttributes() {
        return ['view']
    }

    constructor() {
        super()
        this.attachShadow({ mode: "open" })
        this._currentView = 'sentences'
    }

    connectedCallback() {
        if (this._data) {
            this.render()
            this.applyWheelHandling()
        }
    }

    disconnectedCallback() {
        this.removeWheelHandling()
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'view' && newValue) {
            this._currentView = newValue
            if (this.isConnected) {
                this.updateViewVisibility()
                this.updateToggleButton()
            }
        }
    }

    applyWheelHandling() {
        const contentArea = this.shadowRoot.querySelector('#content-area')
        if (contentArea) {
            Object.assign(contentArea, WheelHandlerMixin)
            contentArea.addWheelHandling()
        }
    }

    removeWheelHandling() {
        const contentArea = this.shadowRoot?.querySelector('#content-area')
        if (contentArea?.removeWheelHandling) {
            contentArea.removeWheelHandling()
        }
    }

    set data(value) {
        this._data = value
        if (this.isConnected) {
            this.render()
        }
    }

    async loadFromUrl(url) {
        const response = await fetch(url)
        this.data = await response.json()
    }

    switchView(view) {
        this._currentView = view
        this.updateViewVisibility()
        this.shadowRoot.querySelector('.popup').classList.remove('visible')

        const toggle = this.shadowRoot.querySelector('.view-toggle')
        const targetView = view === 'sentences' ? 'stats' : 'sentences'
        toggle.dataset.targetView = targetView
        toggle.textContent = view === 'sentences' ? 'Σ' : '¶'
    }

    updateViewVisibility() {
        this.shadowRoot.querySelectorAll('[data-view]').forEach(view => {
            view.hidden = view.dataset.view !== this._currentView
        })
    }

    setupEventListeners() {
        // View toggle buttons
        this.shadowRoot.querySelector('.view-toggle').addEventListener('click', (e) => {
            this.switchView(e.target.dataset.targetView)
        })

        // Popup interactions (delegated on content area)
        const contentArea = this.shadowRoot.querySelector('#content-area')
        const popupController = new PopupController(this.shadowRoot.querySelector('.popup'))

        contentArea.addEventListener('mouseover', (e) => popupController.show(e.target))
        contentArea.addEventListener('mouseout', (e) => popupController.hide(e.target))
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                ${css}
            </style>
            <header>
                <h1>
                    <span style="--index: 0">i</span><span style="--index: 1">N</span><span style="--index: 2">T</span>-<span style="--index: 0">I</span><span style="--index: 2">I</span>
                </h1>
                ${this.renderDocumentScores()}
                <button class="view-toggle" data-target-view="${this._currentView === 'sentences' ? 'stats' : 'sentences'}">
                    ${this._currentView === 'sentences' ? 'Σ' : '¶'}
                </button>
            </header>
            <div id="content-area">
                <div data-view="sentences">
                    ${this._data.sentences.map((s, idx) => this.renderSentence(s, idx)).join('')}
                </div>
                <div data-view="stats"></div>
            </div>
            <div class="popup"></div>
        `
        this.updateViewVisibility()
        this.setupEventListeners()
        this.renderStats()
    }

    renderContent() {
        const contentArea = this.shadowRoot.querySelector('#content-area')

        if (this._currentView === 'sentences') {
            contentArea.innerHTML = `
                <div class="sentences">
                    ${this._data.sentences.map((s, idx) => this.renderSentence(s, idx)).join('')}
                </div>
            `
            this.applyWheelHandling()
        } else {
            contentArea.innerHTML = '<div id="stats-container"></div>'
            this.renderStats()
        }
    }

    renderDocumentScores() {
        const totalWords = this._data.sentences.reduce((sum, s) => sum + s.word_features.length, 0)

        return `<dl class="document-scores">
            <div class="doc-stat">
                <dt>sentences</dt>
                <dd>${this._data.sentences.length}</dd>
            </div>
            <div class="doc-stat">
                <dt>lint score</dt>
                <dd>${this._data.document_lint_score.toFixed(1)}</dd>
            </div>
            ${this.renderDocumentLevel()}
        </dl>`
    }

    renderDocumentLevel() {
        return `<div data-level="${this._data.document_difficulty_level}"><span class="level-badge">${this._data.document_difficulty_level}</span></div>`
    }

    renderSentence(sentence, idx) {
        const tokens = sentence.word_features.filter(token => {
            if (token.pos !== 'PUNCT') return true
            return 'punctuation' in token
        })
        return `<span class="sentence" data-level="${sentence.difficulty_level}">
            <span class="sent-start-group">
                <span class="sent-idx">${idx + 1}</span>
                <span class="sent-start"></span>
            </span>
            ${tokens.map(item => this.renderWord(item)).join('')}
            <span class="sent-end-group">
                <span class="sent-end"></span>
                <span class="level-badge"
                    data-length="${tokens.length}"
                    data-score="${sentence.lint_score}"
                    data-max-sdl="${sentence.max_sdl}"
                    data-mean-freq="${sentence.mean_log_word_frequency}"
                    data-concrete-prop="${sentence.proportion_of_concrete_nouns}">
                    ${sentence.difficulty_level}
                </span>
            </span>
        </span>`
    }

    renderWord(wf) {
        const leading = wf.punctuation?.leading || ''
        const trailing = wf.punctuation?.trailing || ''
        const displayText = leading + wf.text + trailing

        const freqTier = wf.word_frequency ?
            wf.word_frequency < 3
            ? 'uncommon'
            : null
            : null

        const attrs = [
            `data-pos="${wf.pos}"`,
            `data-tag="${wf.tag}"`,
            wf.super_sem_type && `data-sem-type="${wf.super_sem_type}"`,
            wf.word_frequency && `data-freq="${wf.word_frequency}"`,
            freqTier && `data-freq-tier="${freqTier}"`,
            wf.dep_length > 0 && `data-dep-length="${wf.dep_length}"`
        ].filter(Boolean).join(' ')

        return `<span class="word" ${attrs}>${displayText}</span>`
    }

    async renderStats() {
        const styles = getComputedStyle(this)
        const colors = {
            concrete: styles.getPropertyValue('--color-concrete').trim(),
            abstract: styles.getPropertyValue('--color-abstract').trim(),
            undefined: styles.getPropertyValue('--color-undefined').trim(),
            unknown: styles.getPropertyValue('--color-unknown').trim(),
            currentColor: getComputedStyle(this).color,
        }
        const statsData = new StatsData(this._data)

        const spec = StatsSpecs.createStatsVisualization({
                wordFreqs: statsData.getWordFrequencies(),
                sentScores: statsData.getSentenceScores(),
                nounCounts: statsData.getNounCountsByType(),
                depLengths: statsData.getDependencyLengths(),
                contentWordsPerClause: statsData.getContentWordsPerClause(),
            }, colors
        )

        const container = this.shadowRoot.querySelector('[data-view="stats"]')
        await vegaEmbed(container, spec, { actions: false })
    }
}

window.customElements.define('lint-ii-visualizer', LintIIVisualizer)
