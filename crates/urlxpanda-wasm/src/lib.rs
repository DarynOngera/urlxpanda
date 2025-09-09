use wasm_bindgen::prelude::*;
use js_sys::Promise;
use wasm_bindgen_futures::future_to_promise;
use serde::{Deserialize, Serialize};

// Console logging macro
macro_rules! console_log {
    ($($t:tt)*) => (web_sys::console::log_1(&format!($($t)*).into()))
}

#[derive(Serialize, Deserialize)]
pub struct RedirectHop {
    pub url: String,
    pub status_code: u16,
    pub is_final: bool,
}

#[derive(Serialize, Deserialize)]
pub struct ExpansionResult {
    pub original_url: String,
    pub final_url: String,
    pub redirect_chain: Vec<RedirectHop>,
    pub expansion_time_ms: u32,
}

#[wasm_bindgen]
pub struct UrlExpander {
    max_redirects: u32,
    timeout_ms: u32,
}

#[wasm_bindgen]
impl UrlExpander {
    #[wasm_bindgen(constructor)]
    pub fn new() -> UrlExpander {
        UrlExpander {
            max_redirects: 10,
            timeout_ms: 10000,
        }
    }

    #[wasm_bindgen]
    pub fn set_max_redirects(&mut self, max_redirects: u32) {
        self.max_redirects = max_redirects;
    }

    #[wasm_bindgen]
    pub fn set_timeout_ms(&mut self, timeout_ms: u32) {
        self.timeout_ms = timeout_ms;
    }

    #[wasm_bindgen]
    pub fn expand_url(&self, url: &str) -> js_sys::Promise {
        let url = url.to_string();

        wasm_bindgen_futures::future_to_promise(async move {
            match expand_url_simple(&url).await {
                Ok(result) => {
                    match serde_wasm_bindgen::to_value(&result) {
                        Ok(js_value) => Ok(js_value),
                        Err(e) => Err(JsValue::from_str(&format!("Serialization error: {}", e))),
                    }
                },
                Err(e) => Err(JsValue::from_str(&format!("Error expanding URL: {}", e))),
            }
        })
    }
}

async fn expand_url_simple(url: &str) -> Result<ExpansionResult, String> {
    use web_sys::{Request, RequestInit, Response};
    use wasm_bindgen::JsCast;
    use wasm_bindgen_futures::JsFuture;
    
    let start_time = js_sys::Date::now() as u32;
    
    // URL validation
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Err("Invalid URL format".to_string());
    }
    
    console_log!("Expanding URL via backend: {}", url);
    
    // Call our backend API
    let api_url = format!("/.netlify/functions/expand?url={}", js_sys::encode_uri_component(url));
    
    let mut opts = RequestInit::new();
    opts.set_method("GET");
    
    let request = Request::new_with_str_and_init(&api_url, &opts)
        .map_err(|e| format!("Failed to create request: {:?}", e))?;

    let window = web_sys::window().ok_or("No global window object")?;
    let resp_value = JsFuture::from(window.fetch_with_request(&request))
        .await
        .map_err(|e| format!("Backend request failed: {:?}", e))?;

    let resp: Response = resp_value.dyn_into()
        .map_err(|e| format!("Failed to cast response: {:?}", e))?;

    if !resp.ok() {
        return Err(format!("Backend returned error: {}", resp.status()));
    }

    let json_value = JsFuture::from(resp.json().map_err(|e| format!("Failed to get JSON: {:?}", e))?)
        .await
        .map_err(|e| format!("Failed to parse JSON: {:?}", e))?;

    let json_str = js_sys::JSON::stringify(&json_value)
        .map_err(|e| format!("Failed to stringify JSON: {:?}", e))?;

    let result: ExpansionResult = serde_json::from_str(&json_str.as_string().unwrap_or_default())
        .map_err(|e| format!("Failed to deserialize result: {}", e))?;

    console_log!("Expansion completed: {} -> {}", result.original_url, result.final_url);
    
    Ok(result)
}


// Initialize function called when WASM module loads
#[wasm_bindgen(start)]
pub fn main() {
    console_log!("URLXpanda WASM module loaded successfully!");
}
