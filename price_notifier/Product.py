class Product:
    def __init__(self, product):
        self.description = product["description"]
        self.name = product["name"]
        self.baseline_price = product["baseline_price"]
        # Allowed number representation in 'K' format (e.g. 3K, 10K etc) in json
        # Here while parsing, convert the prices with K notation to numeric value
        has_k_notation = str(self.baseline_price).lower().__contains__("k")
        price = self.baseline_price[:-1]
        self.baseline_price = str(int(price) * 1000) if has_k_notation else self.baseline_price
