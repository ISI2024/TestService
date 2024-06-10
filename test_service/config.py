import yaml
from pydantic import BaseModel


class QRCodeEncryption(BaseModel):
    key: str
    algorithm: str
    token_life_time: int


class Config:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config = {}
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

            with open("config.yaml", "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)

                self.db_link = config['database']['link']
                self.qr_code = QRCodeEncryption(key=config['qr_code']['encrypt_key'],
                                                algorithm=config['qr_code']['algorithm'],
                                                token_life_time=config['qr_code']['token_life_time'])

                self.kafka_host = config['kafka']['host']
                self.test_cost = float(config['test_cost'])

                self.kafka_base = {
                    'bootstrap.servers': config['kafka']['host'],
                    'security.protocol': 'SASL_PLAINTEXT',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': config['kafka']['user'],
                    'sasl.password': config['kafka']['password']
                }

                self.kafka_consumer = self.kafka_base.copy()
                self.kafka_producer = self.kafka_base.copy()

                self.kafka_consumer['group.id'] = 'tests'
                self.kafka_consumer['auto.offset.reset'] = 'earliest'
                self.kafka_consumer['enable.auto.commit'] = False

                self.kafka_producer['client.id'] = 'tests-producer'