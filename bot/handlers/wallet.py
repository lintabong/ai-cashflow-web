
import logging
from bson import ObjectId
from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers.base import BaseHandler

from bot.services.database import AsyncSessionLocal
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage
from bot.models.wallet_model import Wallet
from bot.helpers.output_messages import render_wallet_summary

logger = logging.getLogger(__name__)


class WalletHandler(BaseHandler):
    def __init__(self, llm_model: LLMModel, cache: CacheMessage):
        self.llm_model = llm_model
        self.cache = cache

    async def wallet_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        state = self.cache.get_state(telegram_user.id)
        self.cache.clear_user_data(telegram_user.id)
        await update.message.reply_text(render_wallet_summary(state['user']['wallets']), parse_mode='Markdown')

    async def add_wallet_from_intent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        state = self.cache.get_state(telegram_user.id)

        wallet_name_to_add = state['content']['name']
        wallet_nominal_to_add = state['content']['initialBalance']

        for wallet in state['user']['wallets']:
            if wallet['name'].lower() == wallet_name_to_add.lower():
                await update.message.reply_text(f'Wallet {wallet_name_to_add} sudah ada')
                return

        if 'answer' not in state['content']:
            await update.message.reply_text(
                f'Kamu ingin menambahkan {wallet_name_to_add} dengan nominal {wallet_nominal_to_add}?')
            return

        if state['content']['answer']:
            try:
                async with AsyncSessionLocal() as session:
                    session.add(Wallet(
                        id=str(ObjectId()),
                        userId=state['user']['id'],
                        name=wallet_name_to_add,
                        balance=wallet_nominal_to_add
                    ))
                    await session.commit()
                    await update.message.reply_text(f'✅ Wallet {wallet_name_to_add} berhasil ditambahkan!')
            except Exception as error:
                logger.warning(f'Error adding wallet for {telegram_user.id}: {str(error)}')
                await update.message.reply_text(f'🙏🏻 Maaf, terjadi kesalahan, silakan ulangi prompt')
        else:
            await update.message.reply_text(f'Baiklah')
        
        self.cache.clear_user_data(telegram_user.id)
