from fastapi import FastAPI
from sqlalchemy import orm, event

from database import engine
from deps import get_db
import models
import endpoints
from fastapi_pagination import add_pagination

app = FastAPI()

@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        # ユーザーの作成
        db_user = db.query(models.User).filter(models.User.name == "test-user-1").first()
        if db_user is None:
            for username in ["test-user-1", "test-user-2"]:
                user = models.User(name=username)
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # TODOの作成
                todo1 = models.Todo(title=f"{username} Task 1", status=models.StatusEnum.TODO, user_id=user.id)
                todo2 = models.Todo(title=f"{username} Task 2", status=models.StatusEnum.TODO, user_id=user.id)
                db.add_all([todo1, todo2])
                db.commit()
        
    finally:
        db.close()

    engine.connect()

@app.on_event("shutdown")
def shutdown():
    engine.dispose()

@event.listens_for(orm.Session, "do_orm_execute")  # type: ignore
def _add_filtering_deleted_at(execute_state: orm.ORMExecuteState) -> None:  # type: ignore
    """
    論理削除用のfilterを自動的に適用する
    以下のようにすると、論理削除済のデータも含めて取得可能
    query(...).filter(...).execution_options(include_deleted=True)
    ref: https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.do_orm_execute
         https://zenn.dev/tk_resilie/books/bd5708c54a8a0a/viewer/10-soft_delete
    """
    if not execute_state.execution_options.get("suppress_info_log", False):
        print(f"##########")
        print(execute_state.statement)




app.include_router(endpoints.api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80, reload=True)