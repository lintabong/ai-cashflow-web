
import logging
from bson import ObjectId
from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers.base import BaseHandler

from sqlalchemy.future import select
from bot.services.database import AsyncSessionLocal
from bot.models.user_model import User

logger = logging.getLogger(__name__)

class IndexHandler(BaseHandler):
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user = update.effective_user
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.telegramId == tg_user.id)
            )
            user = result.scalar_one_or_none()

        if user:
            logger.info(f'User {user.username} hit /start')
            await update.message.reply_text(f'Halo {user.username}')
        else:
            logger.info(f'Not registered: {user.username}')
            await update.message.reply_text('Kamu belum daftar, daftar dulu dengan mengetik \"/register\"')

    async def register(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.telegramId == telegram_user.id)
            )
            existing_user = result.scalars().first()

            if existing_user:
                if existing_user.isActive:
                    await update.message.reply_text('Kamu sudah terdaftar dan aktif.')
                    return
                
            new_user = User(
                id=str(ObjectId()),
                name=telegram_user.full_name,
                username=telegram_user.username,
                telegramId=telegram_user.id
            )

            session.add(new_user)
            await session.commit()
            await update.message.reply_text('Registrasi berhasil! 🎉')
            
        await update.message.reply_text(f'Halo: {telegram_user.username}')
