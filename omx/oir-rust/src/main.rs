use std::io::{self, Read, Write};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Serialize)]
struct ErrorResponse {
    oir_version: String,
    message_type: String,
    metadata: ErrorMetadata,
    error: ErrorDetail,
}

#[derive(Serialize)]
struct ErrorMetadata {
    origin: String,
    timestamp: u64,
    message_id: String,
    correlation_id: String,
    schema: String,
}

#[derive(Serialize)]
struct ErrorDetail {
    code: String,
    reason: String,
}

fn get_timestamp() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs()
}

fn respond_error(reason: &str, original_msg_id: &str) {
    let response = ErrorResponse {
        oir_version: "1.0".to_string(),
        message_type: "error".to_string(),
        metadata: ErrorMetadata {
            origin: "O-RUST-ENGINE".to_string(),
            timestamp: get_timestamp(),
            message_id: format!("err-{}", get_timestamp()),
            correlation_id: original_msg_id.to_string(),
            schema: "oir-1.0".to_string(),
        },
        error: ErrorDetail {
            code: "REJECTED".to_string(),
            reason: reason.to_string(),
        },
    };
    
    let json_str = serde_json::to_string(&response).unwrap();
    println!("{}", json_str);
}

fn main() {
    let mut input_data = String::new();
    if io::stdin().read_to_string(&mut input_data).is_err() {
        return;
    }
    
    let input_data = input_data.trim();
    if input_data.is_empty() {
        return;
    }
    
    let message: Value = match serde_json::from_str(input_data) {
        Ok(v) => v,
        Err(_) => {
            respond_error("malformed JSON", "");
            return;
        }
    };
    
    let oir_version = message["oir_version"].as_str().unwrap_or("");
    if oir_version != "1.0" {
        respond_error(&format!("UNKNOWN version: {}", oir_version), "");
        return;
    }
    
    let msg_type = message["message_type"].as_str().unwrap_or("");
    if msg_type != "instruction" {
        respond_error(&format!("UNKNOWN message_type: {}", msg_type), "");
        return;
    }
    
    let message_id = message["metadata"]["message_id"].as_str().unwrap_or("");
    
    if message.get("instruction").is_none() {
        respond_error("missing instruction field", message_id);
        return;
    }
    
    if message.get("payload").is_none() {
        respond_error("missing payload", message_id);
        return;
    }
    
    let operation = message["instruction"]["operation"].as_str().unwrap_or("");
    
    // O-RUST protège l'intégrité du protocole (il valide la structure JSON)
    if operation == "ANALYZE_MEMORY" || operation == "EXPLORE_SCENARIO" {
        let payload = &message["payload"];
        let espace_data = payload.get("espace");
        
        if espace_data.is_none() || espace_data.unwrap().is_null() {
            respond_error("missing espace in payload", message_id);
            return;
        }
        
        // Strict Validation de base
        let espace = espace_data.unwrap();
        if !espace.is_object() || espace.get("blocs_libres").is_none() {
            respond_error("invalid espace schema", message_id);
            return;
        }
        
        let response_payload = json!({
            "status": "VALIDATED",
            "message": "OIR Envelope and payload schema are valid",
            "engine_version": "0.2.0-rust"
        });
        
        let response_message = json!({
            "oir_version": "1.0",
            "message_type": "result",
            "metadata": {
                "origin": "O-RUST-ENGINE",
                "timestamp": get_timestamp(),
                "message_id": format!("res-{}", get_timestamp()),
                "correlation_id": message_id,
                "schema": "oir-1.0"
            },
            "payload": response_payload
        });
        
        println!("{}", response_message.to_string());
    } else {
        respond_error(&format!("UNKNOWN type: {}", operation), message_id);
    }
}
