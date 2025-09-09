use urlxpanda_lib::expand_url;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let url = "https://bit.ly/3eQsUNw"; // Or get from command line arguments

    println!("Expanding {}", url);

    let final_url = expand_url(url).await?;

    println!("Final URL: {}", final_url);

    Ok(())
}