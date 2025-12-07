from sqlalchemy.orm import Session
from api.repository.db_models import ProcessLogTable
from api.repository.models import ProcessLog

class ProcessLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, log: ProcessLog) -> ProcessLogTable:
        db_log = ProcessLogTable(**log.dict(exclude={"id"}))
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log
