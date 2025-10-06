import uuid
from typing import AsyncGenerator, Callable, Generic, Type, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .exceptions import ConstraintViolationError, DatabaseError, NotFoundError

T = TypeVar("T", bound=SQLModel)


class BaseService(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        session_factory: Callable[[], AsyncGenerator[AsyncSession, None]],
    ):
        self.model = model
        self.session_factory = session_factory

    async def get(self, id: int | str | uuid.UUID):
        try:
            async for session in self.session_factory():
                obj = await session.get(self.model, id)
                if not obj:
                    raise NotFoundError(
                        f"{self.model.__name__} with id: {id} not found"
                    )
                return obj
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while fetching {self.model.__name__}: {str(e)}"
            ) from e

    async def create(self, data: dict):
        try:
            async for session in self.session_factory():
                obj = self.model.model_validate(data)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
                return obj
        except IntegrityError as e:
            raise ConstraintViolationError(
                f"Failed to create {self.model.__name__}: constraint violation"
            ) from e
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while creating {self.model.__name__}: {str(e)}"
            ) from e

    async def update(self, id: int | str | uuid.UUID, data: dict):
        try:
            async for session in self.session_factory():
                obj = await session.get(self.model, id)
                if not obj:
                    raise NotFoundError(
                        f"{self.model.__name__} with id: {id} not found"
                    )

                obj = self.model.sqlmodel_update(obj, data)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
                return obj
        except IntegrityError as e:
            raise ConstraintViolationError(
                f"Failed to update {self.model.__name__}: constraint violation"
            ) from e
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while updating {self.model.__name__}: {str(e)}"
            ) from e

    async def delete(self, id: int | str | uuid.UUID):
        try:
            async for session in self.session_factory():
                obj = await session.get(self.model, id)
                if not obj:
                    raise NotFoundError(
                        f"{self.model.__name__} with id: {id} not found"
                    )

                await session.delete(obj)
                await session.commit()
                return obj
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while deleting {self.model.__name__}: {str(e)}"
            ) from e

    async def list(self):
        try:
            async for session in self.session_factory():
                statement = select(self.model)
                result = await session.exec(statement)
                return result.all()

        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while listing {self.model.__name__}: {str(e)}"
            ) from e

    async def filter(self, *where_clauses):
        """
        Filter records using SQLAlchemy where clauses.

        Example usage:
            await service.filter(Model.user_id == user_id)
            await service.filter(Model.status == "active", Model.count > 5)
        """
        try:
            async for session in self.session_factory():
                statement = select(self.model).where(*where_clauses)
                result = await session.exec(statement)
                return result.all()

        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while filtering {self.model.__name__}: {str(e)}"
            ) from e
