## MoonGlow Price Matcher

This project is designed to scrape prices from the MoonGlow online cosmetics shop and compare them with prices from competitors.

### Project Structure

- `config.py`: Configuration file containing database parameters and user agent details.
- `parsers/`: Directory containing parser modules.
  - `mg_parser.py`: Parser for Moonglow website.
  - `ms_parser.py`: Parser for MySkin website (competitor).
- `db/`: Directory to store the SQLite database file.
- `run_parsing.py`: Main script to run the parsing and matching process.

### 1. Clone the repository:
```python
git clone https://github.com/dvoykov/moonglow-price-matcher.git
```

### 2. Install dependencies:
```python
pip install -r requirements.txt
```

### 3.Usage
To run the parser, execute the `run_parsing.py` script with the desired parser type as an argument. For example:
```python
python run_parsing.py moonglow
```

Supported parser types:
- `moonglow`: Moonglow website parser.
- `myskin`: MySkin website parser.

The parser will scrape the product catalog, parse individual product pages, generate embeddings, and save the products to the SQLite database.

### 4. Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

### 5. License
This project is licensed under the MIT License - see the LICENSE file for details.
