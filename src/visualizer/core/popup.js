export class PopupController {
    constructor(popupElement) {
        this.popup = popupElement
    }

    show(target) {
        if (!target.matches('.word, .level-badge, .sent-start, .sent-end')) return

        let dataSource = target
        if (target.matches('.sent-start, .sent-end')) {
            const sentence = target.closest('.sentence')
            dataSource = sentence.querySelector('.level-badge')
        }

        if (Object.keys(dataSource.dataset).length === 0) return

        this.popup.innerHTML = this.renderContent(dataSource)
        this.popup.classList.add('visible')

        const rect = target.getBoundingClientRect()
        this.popup.style.top = `${rect.bottom}px`
        this.popup.style.left = `${rect.left}px`
    }

    hide(target) {
        if (!target.matches('.word, .level-badge')) return
        this.popup.classList.remove('visible')
    }

    renderContent(target) {
        const parts = [
            ...Object.entries(target.dataset).map(([key, value]) =>
                this.formatAttribute(key, value)
            )
        ]
        return parts.join('')
    }

    formatAttribute(key, value) {
        const label = key.replace(/([A-Z])/g, '-$1').toLowerCase()
        const formattedValue = this.formatValue(value)
        return `
            <div class="label">${label}</div>
            <div class="value">${formattedValue}</div>
        `
    }

    formatValue(value) {
        const num = parseFloat(value)
        if (isNaN(num)) return value
        return Number.isInteger(num) ? num.toString() : num.toFixed(1)
    }
}
