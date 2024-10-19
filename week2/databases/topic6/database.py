from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# postgres_url = "postgresql://jc-user:secret@localhost:5432/jc-db"
postgres_url = "postgresql://<user>:<password>@<host>:<port>/<db-name>"
engine = create_engine(postgres_url, echo=False)

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
