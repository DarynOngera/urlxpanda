use reqwest::Client;
use std::time::Duration;

pub async fn expand_url(url: &str) -> Result<String, Box<dyn std::error::Error>> {
    let client = Client::builder()
        .timeout(Duration::from_secs(10))
        .redirect(reqwest::redirect::Policy::none())
        .build()?;
    let mut current = url.to_string();

    for _ in 0..10 {
        let response = client.get(&current).send().await?;

        let status = response.status();

        if status.is_redirection() {
            if let Some(location) = response.headers().get(reqwest::header::LOCATION) {
                let next = location.to_str()?.to_string();
                current = next;
                continue;
            }
        }

        return Ok(current);
    }

    Ok(current)
}
