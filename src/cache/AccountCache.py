

class AccountCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = {}
        return cls._instance

    def get_data(self, key):
        # print(f"Returning cached data for key: {key in self.cache}")
        if str(key) in self.cache:
            # print(f"Returning cached data for key: {key}")
            return self.cache[str(key)]
        else:
           return None

    def set_data(self, key, value):
        # Simulate fetching data from a database or other data source
        # print(1111111111)
        # print(value)
        self.cache[str(key)] = value

    
    def get_all_data(self):
        return self.cache