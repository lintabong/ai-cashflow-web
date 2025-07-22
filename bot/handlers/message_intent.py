
import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from bot.services.database import AsyncSessionLocal

from bot.models.user_model import User
from bot.handlers.base import BaseHandler
from bot.handlers.wallet import WalletHandler
from bot.handlers.cashflow import CashflowHandler
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage

from bot.helpers.text_util import parse_json

logger = logging.getLogger(__name__)

class MessageIntent(BaseHandler):
    def __init__(self, llm_model: LLMModel, cache: CacheMessage):
        self.llm_model = llm_model
        self.cache = cache
        self.cashflow_handler = CashflowHandler(self.llm_model, self.cache)
        self.wallet_handler = WalletHandler(self.llm_model, self.cache)

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        message = update.message.text

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.wallets))
                .where(User.telegramId == telegram_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await update.message.reply_text('Kamu belum daftar, daftar dulu dengan mengetik \"/register\"')
                return

            try:
                chat = self.llm_model.create_base_chat_model()

                response = chat.send_message(message)
                response = parse_json(response.text)
                
                response['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'telegramId': user.telegramId,
                    'wallets': [
                        {'id':wallet.id, 'name': wallet.name, 'balance': float(wallet.balance)}
                        for wallet in user.wallets if wallet.isActive
                    ]
                }

                self.cache.save_state(telegram_user.id, response['user'])

                if response['intent'] == 'TANYA_WALLET':
                    await self.wallet_handler.wallet_balance(update, context)
                elif response['intent'] == 'CATAT_TRANSAKSI':
                    await self.cashflow_handler.input_cashflow_by_text(update, context)
                else:
                    await update.message.reply_text('Perintah tidak dikenali.')
            
            except ValueError:
                await update.message.reply_text('Ada kesalahan di server, ulangi lagi')
