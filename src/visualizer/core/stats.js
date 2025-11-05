export class StatsData {
    constructor(data) {
        this._data = data
    }

    getSentenceScores() {
        return this._data.sentences.map(s => s.lint_score)
    }

    getWordFrequencies() {
        return this._data.sentences
            .flatMap(s => s.word_features)
            .map(wf => wf.word_frequency)
            .filter(freq => freq !== null)
    }

    getContentWordsPerClause() {
        return this._data.sentences.map(s => s.content_words_per_clause)
    }

    getNounCountsByType() {
        const counts = { concrete: 0, abstract: 0, undefined: 0, unknown: 0 }

        this._data.sentences.forEach(s => {
            s.word_features.forEach(wf => {
                if (wf.super_sem_type) {
                    counts[wf.super_sem_type]++
                }
            })
        })

        return counts
    }

    getDependencyLengths() {
        return this._data.sentences
            .flatMap(s => s.word_features)
            .map(wf => wf.dep_length)
            .filter(dl => dl !== undefined && dl > 0)
    }
}

export class StatsSpecs {
    static createScoreBoxPlot(sentScores) {
        return {
            title: "Sentence Score",
            data: { values: sentScores.map(value => ({ value })) },
            mark: { type: "boxplot", extent: "min-max" },
            encoding: {
                y: {
                    field: "value",
                    type: "quantitative",
                    title: "Readability Score",
                    scale: { domain: [0, 100] }
                }
            },
            width: 80
        }
    }

    static createFrequencyBoxPlot(wordFreqs) {
        return {
            title: "Word Frequency",
            data: { values: wordFreqs.map(value => ({ value })) },
            mark: { type: "boxplot", extent: "min-max" },
            encoding: {
                y: {
                    field: "value",
                    type: "quantitative",
                    title: "Zipf Frequency",
                    scale: { zero: false }
                }
            },
            width: 80
        }
    }

    static createContentWordsPerClauseBoxPlot(values) {
        return {
            title: "Content Words per Clause",
            data: { values: values.map(value => ({ value })) },
            mark: { type: "boxplot", extent: "min-max" },
            encoding: {
                y: {
                    field: "value",
                    type: "quantitative",
                    title: "Words/Clause",
                    scale: { zero: false }
                }
            },
            width: 80
        }
    }

    static createNounTypesBarChart(nounCounts, colors) {
        const data = Object.entries(nounCounts).map(([type, count]) => ({
            type,
            count
        }))

        return {
            title: "Noun Types",
            data: { values: data },
            mark: "bar",
            encoding: {
                x: {
                    field: "type",
                    type: "nominal",
                    title: null,
                    axis: { labelAngle: 0 }
                },
                y: {
                    field: "count",
                    type: "quantitative",
                    title: "Count"
                },
                color: {
                    field: "type",
                    type: "nominal",
                    scale: {
                        domain: ["concrete", "abstract", "undefined", "unknown"],
                        range: [
                            colors.concrete,
                            colors.abstract,
                            colors.undefined,
                            colors.unknown
                        ]
                    },
                    legend: null
                },
                tooltip: [
                    { field: "type", type: "nominal", title: "Type" },
                    { field: "count", type: "quantitative", title: "Count" }
                ]
            },
            width: 250
        }
    }

    static createDependencyLengthHistogram(depLengths) {
        // Count frequency of each dependency length
        const counts = depLengths.reduce((acc, dl) => {
            acc[dl] = (acc[dl] || 0) + 1
            return acc
        }, {})

        const data = Object.entries(counts).map(([length, count]) => ({
            length: parseInt(length),
            count
        }))

        return {
            title: "Dependency Length",
            data: { values: data },
            mark: "bar",
            encoding: {
                x: {
                    field: "length",
                    type: "ordinal",
                    title: "SDL"
                },
                y: {
                    field: "count",
                    type: "quantitative",
                    title: "Count"
                },
                tooltip: [
                    { field: "count", type: "quantitative", title: "Count" }
                ]
            },
            width: 200
        }
    }

    static createStatsVisualization({wordFreqs, sentScores, nounCounts, depLengths, contentWordsPerClause}, colors) {
        return {
            $schema: "https://vega.github.io/schema/vega-lite/v5.json",
            hconcat: [
                this.createScoreBoxPlot(sentScores),
                this.createFrequencyBoxPlot(wordFreqs),
                this.createContentWordsPerClauseBoxPlot(contentWordsPerClause),
                this.createNounTypesBarChart(nounCounts, colors),
                this.createDependencyLengthHistogram(depLengths)
            ],
            config: {
                view: { stroke: null },
                background: null,  // transparent background
                axis: {
                    domainColor: colors.currentColor,
                    tickColor: colors.currentColor,
                    gridColor: null,
                    labelColor: colors.currentColor,
                    titleColor: colors.currentColor
                },
                title: {
                    color: colors.currentColor
                },
                rule: {
                    color: colors.currentColor
                }
            }
        }
    }
}
