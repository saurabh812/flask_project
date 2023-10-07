# Integrated Flask Application with HTML Templates

from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Function to scrape product details by link
def scrape_amazon_product_details(amazon_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    page = requests.get(amazon_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    title_element = soup.find("span", {"id": "productTitle"})
    product_title = title_element.get_text(strip=True) if title_element else "No product title found."

    img_element = soup.find("img", {"id": "landingImage"})
    img_src = img_element.get("src") if img_element else "No image source found."

    price_element = soup.find("span", {"class": "a-price-whole"})
    product_price = price_element.get_text(strip=True) if price_element else "No product price found."

    return {'product_title': product_title, 'img_src': img_src, 'product_price': product_price}

# Function to scrape Amazon products by name
def scrape_amazon_products(product_name):
    search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    page = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    product_containers = soup.find_all('div', class_='s-result-item')

    products = []

    for container in product_containers:
        product_name_tag = container.find('span', class_='a-text-normal')
        product_name = product_name_tag.text.strip() if product_name_tag else 'N/A'

        product_image_tag = container.find('img', class_='s-image')
        product_image = product_image_tag['src'] if product_image_tag and 'src' in product_image_tag.attrs else 'N/A'

        product_title_tag = container.find('span', class_='a-size-medium')
        product_title = product_title_tag.text.strip() if product_title_tag else 'N/A'

        product_price_tag = container.find('span', class_='a-offscreen')
        product_price = product_price_tag.text.strip() if product_price_tag else 'N/A'

        product_link_tag = container.find('a', class_='a-link-normal')
        product_link = 'https://www.amazon.in' + product_link_tag['href'] if product_link_tag and 'href' in product_link_tag.attrs else 'N/A'

        products.append({
            'product_name': product_name,
            'product_image': product_image,
            'product_title': product_title,
            'product_price': product_price,
            'product_link': product_link
        })

    return products

# Route for the combined input page
@app.route('/')
def combined_input_page():
    return render_template('combined_input_page.html', products=[])

# Route to handle product details by link
@app.route('/product_details', methods=['POST'])
def product_details():
    amazon_url = request.form.get('amazon_url')
    product_details = scrape_amazon_product_details(amazon_url)
    return render_template('product_details_result.html', **product_details)

# Route to display products by name on form submission
@app.route('/display_product', methods=['POST'])
def display_product():
    product_name = request.form['product_name']

    # Scrape product information
    product_info = scrape_amazon_products(product_name)

    if product_info:
        # Render the display page with product information
        return render_template('product_search_result.html', products=product_info)
    else:
        return "Product not found."

if __name__ == '__main__':
    app.run(debug=True)
