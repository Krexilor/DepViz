// LIBRARIES ---------------------------------------------------------------------------------------------------------------------------------------|
import { useState, useRef } from 'react'

// STYLES ------------------------------------------------------------------------------------------------------------------------------------------|
import styles from './DropZone.module.css'

// SUPPORTED FILES ---------------------------------------------------------------------------------------------------------------------------------|
const SUPPORTED = ['requirements.txt', 'pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod', 'Gemfile']

// COMPONENT ---------------------------------------------------------------------------------------------------------------------------------------|
export default function DropZone({ onUpload }) {

    const [dragging, setDragging] = useState(false)
    const [fileError, setFileError] = useState(null)
    const inputRef = useRef(null)

    function handleFile(file) {
        if (!SUPPORTED.includes(file.name)) {
            setFileError(`"${file.name}" is not supported. Use: ${SUPPORTED.join(', ')}`)
            return
        }
        setFileError(null)
        onUpload(file)
    }

    function onDragOver(e) {
        e.preventDefault()
        setDragging(true)
    }

    function onDragLeave() {
        setDragging(false)
    }

    function onDrop(e) {
        e.preventDefault()
        setDragging(false)
        const file = e.dataTransfer.files[0]
        if (file) handleFile(file)
    }

    function onInputChange(e) {
        const file = e.target.files[0]
        if (file) handleFile(file)
    }

    return (
        <div className = {styles.wrapper}>

            <div
                className = {`${styles.dropzone} ${dragging ? styles.dragging : ''}`}
                onDragOver = {onDragOver}
                onDragLeave = {onDragLeave}
                onDrop = {onDrop}
                onClick = {() => inputRef.current.click()}
            >
                <input
                    ref = {inputRef}
                    type = "file"
                    accept = ".txt,.toml,.json"
                    className = {styles.hiddenInput}
                    onChange = {onInputChange}
                />

                <div className = {styles.icon}>
                    <svg width = "28" height = "28" viewBox = "0 0 24 24" fill = "none" stroke = "currentColor" strokeWidth = "1.5" strokeLinecap = "round" strokeLinejoin = "round">
                        <path d = "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points = "17 8 12 3 7 8" />
                        <line x1 = "12" y1 = "3" x2 = "12" y2 = "15" />
                    </svg>
                </div>

                <p className = {styles.label}>
                    Drop your file here or <span>browse</span>
                </p>
                <p className = {styles.hint}>
                    requirements.txt · pyproject.toml · package.json
                </p>
            </div>

            <div className = {styles.badges}>
                {SUPPORTED.map(name => (
                    <span key = {name} className = {styles.badge}>{name}</span>
                ))}
            </div>

            {fileError && (
                <p className = {styles.error}>{fileError}</p>
            )}

        </div>
    )
}
