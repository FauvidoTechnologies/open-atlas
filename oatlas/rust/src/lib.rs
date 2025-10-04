use pyo3::prelude::*;
use std::fs;
use binwalk::Binwalk;
use serde::Serialize;

#[derive(Serialize)]
struct SignatureResultJson {
    offset: usize,
    id: String,
    size: usize,
    name: String,
    confidence: u8,
    description: String,
}

#[pyfunction]
fn scan_firmware(path: String) -> PyResult<String> {
    let binwalker = Binwalk::new();

    // Read the firmware file
    let file_data = fs::read(&path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e))
    })?;

    // Collect results into a Vec
    let mut results: Vec<SignatureResultJson> = Vec::new();
    for result in binwalker.scan(&file_data) {
        results.push(SignatureResultJson {
            offset: result.offset,
            id: result.id.to_string(),
            size: result.size,
            name: result.name.clone(),
            confidence: result.confidence,
            description: result.description.clone(),
        });
    }

    // Serialize to JSON
    let json_output = serde_json::to_string_pretty(&results).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON serialization failed: {}", e))
    })?;

    Ok(json_output)
}

/// Python module
#[pymodule]
fn rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan_firmware, m)?)?;
    Ok(())
}
