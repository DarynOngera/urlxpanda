use wasm_bindgen::prelude::*;
use js_sys::Promise;
use wasm_bindgen_futures::future_to_promise;
use serde::{Deserialize, Serialize};
use url::Url;

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
    use web_sys::{Request, RequestInit, Response, Headers};
    use wasm_bindgen::JsCast;
    use wasm_bindgen_futures::JsFuture;
    
    let start_time = js_sys::Date::now() as u32;
    
    // URL validation
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Err("Invalid URL format".to_string());
    }
    
    let mut current_url = url.to_string();
    let mut redirect_chain: Vec<RedirectHop> = Vec::new();
    let max_redirects = 10;
    
    // Add initial URL
    redirect_chain.push(RedirectHop {
        url: url.to_string(),
        status_code: 0,
        is_final: false,
    });
    
    for i in 0..max_redirects {
        console_log!("Following redirect {}: {}", i + 1, current_url);
        
        let mut opts = RequestInit::new();
        opts.set_method("GET");
        opts.set_mode(web_sys::RequestMode::Cors); // Allow CORS for external URLs
        
        let request = Request::new_with_str_and_init(&current_url, &opts)
            .map_err(|e| format!("Failed to create request: {:?}", e))?;
        
        let window = web_sys::window().ok_or("No global window object")?;
        let resp_value = JsFuture::from(window.fetch_with_request(&request))
            .await
            .map_err(|e| format!("Fetch failed: {:?}", e))?;
        
        let resp: Response = resp_value.dyn_into()
            .map_err(|e| format!("Failed to cast response: {:?}", e))?;
        
        let status_code = resp.status();
        
        // Update the last hop with status
        if let Some(last) = redirect_chain.last_mut() {
            last.status_code = status_code as u16;
        }
        
        if status_code >= 300 && status_code < 400 {
            // Redirect
            let headers = resp.headers();
            let location = headers.get("location")
                .map_err(|_| "Failed to get location header".to_string())?;
            
            if location.is_none() {
                // No location, treat as final
                if let Some(last) = redirect_chain.last_mut() {
                    last.is_final = true;
                }
                break;
            }
            
            let location = location.unwrap();
            
            // Resolve relative URLs
            let next_url = Url::parse(&current_url)
                .map_err(|_| "Failed to parse current URL".to_string())?
                .join(&location)
                .map_err(|_| "Failed to join URLs".to_string())?
                .to_string();
            
            redirect_chain.push(RedirectHop {
                url: next_url.clone(),
                status_code: 0,
                is_final: false,
            });
            
            current_url = next_url;
            continue;
        } else {
            // Not a redirect, final
            if let Some(last) = redirect_chain.last_mut() {
                last.is_final = true;
            }
            break;
        }
    }
    
    // Ensure at least one is final
    if let Some(last) = redirect_chain.last_mut() {
        if !last.is_final {
            last.is_final = true;
        }
    }
    
    let expansion_time_ms = (js_sys::Date::now() as u32) - start_time;
    
    Ok(ExpansionResult {
        original_url: url.to_string(),
        final_url: current_url,
        redirect_chain,
        expansion_time_ms,
    })
}

// Initialize function called when WASM module loads
#[wasm_bindgen(start)]
pub fn main() {
    console_log!("URLXpanda WASM module loaded successfully!");
}
