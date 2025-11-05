export const css = `
    :host {
        color-scheme: light dark;
        --background: light-dark(hsl(60, 100%, 98%), hsl(60, 3%, 7%));

        --color-concrete: hsl(60, 80%, 50%);
        --color-abstract: hsl(195, 53%, 79%);
        --color-undefined: hsl(350, 90%, 83%);
        --color-unknown: hsl(0, 20%, 90%);

        --color-level-1: hsl(153, 53%, 53%);
        --color-level-2: hsl(198, 100%, 70%);
        --color-level-3: hsl(42, 100%, 53%);
        --color-level-4: hsl(348, 100%, 70%);

        display: grid;
        grid-template-rows: auto 1fr;
        max-height: 500px;
        border-top: 1px solid currentColor;
        border-bottom: 1px solid currentColor;
    }
    header {
        --gap: 3em;
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid currentColor;
        gap: var(--gap);

        h1 {
            user-select: none;
            line-height: 1.5em;
            padding-left: .35em;
            letter-spacing: 0.2em;
            white-space: nowrap;
            font-family: arial;
            :nth-child(4) {
                letter-spacing: 0.125em;
            }
            border-left: .225em solid currentColor;
            border-bottom: .2225em solid currentColor;

            span {
                font-size: calc(1em + var(--index) * 0.1em);
            }
            margin-block: .25em;
            margin-left: 1rem;
        }

        .document-scores {
            display: flex;
            align-items: center;
            gap: var(--gap);

            .doc-stat {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1.5em;

                dt {
                    display: inline;
                    font-size: .9em;
                    opacity: .7;
                }
                dd {
                    display: inline;
                    margin: 0;
                    font-family: monospace;
                    font-size: 1.25em;
                }
            }
        }
    }
    .view-toggle {
        position: absolute;
        font-family: monospace;
        top: 0;
        right: 0;
        width: 1.5em;
        height: 1.5em;
        color: currentColor;
        background: transparent;
        border: 1px solid currentColor;
        border-top: none;
        border-bottom-left-radius: .25em;
        cursor: pointer;
        transition: filter 0.2s ease;
        z-index: 9999;

        &:hover {
            background-color: color-mix(in oklch, currentColor 10%, transparent);
        }
    }

    #content-area {
        overflow-y: auto;
        overscroll-behavior: contain;
        }

    [data-view][hidden] {
        display: none;
    }
    [data-view="sentences"] {
        display: flex;
        flex-wrap: wrap;
        row-gap: 0.5em;
        align-items: center;
        padding-inline: .5em;
        padding-bottom: 1em;
        line-height: 1.5;
    }
    [data-view="stats"] {
        margin-block: .5em;
    }

    .level-badge {
        display: grid;
        place-items: center;
        width: 1.5em;
        height: 1.5em;
        border-radius: 50%;
        margin-right: 1em;
        font-family: monospace;
        line-height: 1em;
        color: white;
        user-select: none;
    }
    header .level-badge {
        font-size: 2em;
    }
    [data-level="1"] {
        .level-badge {
            background-color: var(--color-level-1);
        }
        .sent-idx,
        .sent-start::before,
        .sent-end::after {
            color: var(--color-level-1);
        }
    }
    [data-level="2"] {
        .level-badge {
            background-color: var(--color-level-2);
        }
        .sent-idx,
        .sent-start::before,
        .sent-end::after {
            color: var(--color-level-2);
        }
    }
    [data-level="3"] {
        .level-badge {
            background-color: var(--color-level-3);
        }
        .sent-idx,
        .sent-start::before,
        .sent-end::after {
            color: var(--color-level-3);
        }
    }
    [data-level="4"] {
        .level-badge {
            background-color: var(--color-level-4);
        }
        .sent-idx,
        .sent-start::before,
        .sent-end::after {
            color: var(--color-level-4);
        }
    }

    .sentence {
        --scale: 1.25;
        display: contents;

        .sent-start-group,
        .sent-end-group {
            position: relative;
            display: inline-flex;
            align-items: center;
            white-space: nowrap;
            transition: transform 0.2s ease;
        }

        &:has(.sent-start-group:hover, .sent-end-group:hover) .sent-start-group,
        &:has(.sent-start-group:hover, .sent-end-group:hover) .sent-end-group {
            transform: scale(var(--scale));
        }

        .sent-idx {
            font-size: .7em;
            position: absolute;
            top: 1em;
            right: 100%;
            margin-right: -.5em;
            text-align: right;
            font-family: monospace;
        }
        .sent-start::before,
        .sent-end::after {
            font-family: monospace;
            font-size: 3em;
            vertical-align: middle;
        }
        .sent-start::before {
            content: '[';
            padding-right: 0.2em;
        }
        .sent-end::after {
            content: ']';
            padding-left: 0.2em;
        }
    }
    .word {
        padding-inline: 1em;
        padding-block: .5em;
        margin-inline: .125em;
        border-radius: .25em;
        cursor: default;

        transition: filter 0.2s ease;

        &:hover {
            filter: brightness(0.85);
        }

        &:not([data-sem-type]):hover {
            background-color: color-mix(in oklch, currentColor 15%, transparent);
        }

        &[data-sem-type] {
            color: black;
        }
        &[data-sem-type="concrete"] {
            background-color: var(--color-concrete);
        }
        &[data-sem-type="abstract"] {
            background-color: var(--color-abstract);
        }
        &[data-sem-type="undefined"] {
            background-color: var(--color-undefined);
        }
        &[data-sem-type="unknown"] {
            background-color: var(--color-unknown);
        }

        &[data-freq-tier="uncommon"] {
            font-style: italic;
        }
    }
    .popup {
        display: none;
        pointer-events: none;
        position: fixed;
        padding: 0.5em 1em;
        border: 1px solid currentColor;
        border-radius: .25em;
        background: var(--vscode-notebook-editorBackground, var(--background));
        z-index: 1000;

        .label {
            font-size: .8125em;
        }
        .value {
            font-family: monospace;
            font-size: 1.25em;
        }
        &.visible {
            display: block;
        }
    }
`
