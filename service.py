from sqlalchemy.exc import SQLAlchemyError

from core.schemas.vendor import VendorActivate
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from crud.users import update_user_vendor_state, get_user_by_id, update_user_keyMS
from uuid import UUID
from fastapi.exceptions import HTTPException
import httpx
from utils.crypto import TokenEncryptor

class VendorService:
    vendor_api_url = 'https://apps-api.moysklad.ru/api/vendor/1.0'

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_context(self):
        pass

    async def update_state(self, account_id: str, data: VendorActivate) -> str:
        account_id = UUID(account_id)

        user = await get_user_by_id(self.session, account_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            encryptor = TokenEncryptor(settings.keys.fernet_secret_key)

            if data.cause == "Install":
                state = "SettingsRequired"

            elif data.cause == "Resume":
                state = "Activated" if user.settings else "SettingsRequired"

            elif data.cause in ("TariffChanged", "Autoprolongation"):
                if not user.keyMS:
                    print("Ошибка, у пользователя нет апи ключа")
                    raise HTTPException(status_code=400, detail="User have not Key MS!")
                state = "Activated"
            else:
                raise HTTPException(status_code=400, detail="Unknown case")


            await update_user_vendor_state(self.session, user, state)

            if data.cause in ("Install", "Resume") and data.access:
                access = encryptor.encrypt(data.access[0]["access_token"])
                await update_user_keyMS(self.session, user, access)

            return state

        except SQLAlchemyError as e:
            print("HELLO", e)
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    async def delete(self):
        pass

    async def get(self):
        pass
