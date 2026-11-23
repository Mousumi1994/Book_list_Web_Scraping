import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Start at Page 1
current_url = "https://books.toscrape.com/"
scraped_data = []
page_number = 1

# Keep looping as long as there is a page URL to scrape
while current_url:
    print(f"Scraping Page {page_number}: {current_url}")
    
    # 1. Fetch and parse the current page
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 2. Extract all books on this page
    books = soup.find_all("article", class_="product_pod")
    
    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]
        
        scraped_data.append({
            "Title": title,
            "Price_Raw": price,
            "Rating_Word": rating
        })
    
    # 3. Look for the "Next" button at the bottom of the page
    next_button = soup.find("li", class_="next")
    
    if next_button:
        # Grab the relative link (e.g., "catalogue/page-2.html" or "page-3.html")
        next_href = next_button.a["href"]
        # Safely combine it with the current URL to get the full next link
        current_url = urljoin(current_url, next_href)
        page_number += 1
        
        # Be polite to the server: pause 0.2 seconds before the next request
        time.sleep(0.2)
    else:
        # No "Next" button found -> We reached the last page!
        print("Reached the last page! Scraping complete.")
        current_url = None  # This stops the while loop

# 4. Load ALL scraped books into Pandas
df = pd.DataFrame(scraped_data)
print(f"\nTotal books scraped: {len(df)}")

# --- DATA CLEANING & ANALYSIS ---
df["Price"] = df["Price_Raw"].str.replace("£", "").astype(float)

rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
df["Rating"] = df["Rating_Word"].map(rating_map)

print("\n--- Full Catalog Business Insights ---")
print(f"Average Book Price: £{df['Price'].mean():.2f}")
print("\nAverage Price by Star Rating:")
print(df.groupby("Rating")["Price"].mean().round(2))

# Save all 1,000 books to CSV
df.to_csv("all_books_dataset.csv", index=False)
print("\nSaved all data to 'all_books_dataset.csv'!")