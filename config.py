from typing import Any
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    UBIC_URL: str = Field("http://0.0.0.0:8888", env="UBIC_URL")
    MONGO_HOST: str = Field("localhost", env="MONGO_HOST")
    MONGO_PORT: int = Field(27017, env="MONGO_PORT")
    ENDPOINTS_CACHE_TTL: int = Field(3600, env="ENDPOINTS_CACHE_TTL")
    BANK_UUID: str = Field("111aaaaa-1af0-489e-b761-d40344c12e70", env="BANK_UUID")
    MODULO: int = Field(4294967296, env="MODULO")
    SEMI_MODULO: int = 0
    COMPUTE_TIMEOUT: int = Field(1, env="COMPUTE_TIMEOUT")
    REQUEST_TIMEOUT: int = Field(1, env="REQUEST_TIMEOUT")
    MIN_PARTNERS_NUM: int = Field(1, env="MIN_PARTNERS_NUM")
    OWNER_UUID_HEADER: int = Field(1, env="OWNER_UUID_HEADER")
    PREFIX_URL: str = Field("/v1", env="PREFIX_URL")
    SHARES_ROUTE: str = ""
    QUOTA_ROUTE: str = ""
    ENDPOINTS_ROUTE: str = ""
    RECONSTRUCT_ROUTE: str = ""
    RESULT_ROUTE: str = ""

    def __init__(self, **data: Any):
        super(Config, self).__init__(**data)
        self.SHARES_ROUTE: str = self.PREFIX_URL + "/share"
        self.QUOTA_ROUTE: str = self.UBIC_URL + self.PREFIX_URL + "/quota"
        self.ENDPOINTS_ROUTE: str = self.UBIC_URL + self.PREFIX_URL + "/endpoints"
        self.RECONSTRUCT_ROUTE: str = self.UBIC_URL + self.PREFIX_URL + "/reconstruct"
        self.RESULT_ROUTE: str = self.UBIC_URL + self.PREFIX_URL + "/result"
        self.SEMI_MODULO = int(self.MODULO / 2)


config = Config()
