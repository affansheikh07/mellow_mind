from pydantic_settings import BaseSettings
from pydantic import EmailStr

class Settings(BaseSettings):
    email_user: EmailStr
    email_pass: str
    PROJECT_NAME: str = "Mellow Mind"
    
    # Database settings
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DATABASE: str = "mellow_mind"
    
    # JWT settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Set default expiry time for the token (in minutes)
    SECRET_KEY: str = "Hesoyam@123!"     # Replace this with a strong secret key (ideally from an environment variable)
    ALGORITHM: str = "HS256"                # JWT encoding algorithm
    
    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        # return "mysql+pymysql://root:gfBIRcenYNvpVCLxqZrMdDppRqMuWIIA@mysql.railway.internal:3306/railway"

# Initialize settings
settings = Settings()
