
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from bot.services.database import AsyncSessionLocal

from bot.models.user_model import User
from bot.models.intent_chat_model import Intent
from bot.handlers.base import BaseHandler
from bot.handlers.wallet import WalletHandler
from bot.handlers.cashflow import CashflowHandler
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage
from bot.services.image import ImageManager
from bot.helpers.text_util import markdown_to_html, parse_json
from bot.constants import (
    BOT_RESPONSE_TO_REGISTER,
    BOT_RESPONSE_ERROR_SERVER,
    BOT_RESPONSE_INTENT_NOT_FOUND
)

logger = logging.getLogger(__name__)

class BaseIntent(BaseHandler):
    def __init__(self, llm_model: LLMModel, cache: CacheMessage, image_manager: ImageManager):
        self.llm_model = llm_model
        self.cache = cache
        self.image_manager = image_manager
        self.cashflow_handler = CashflowHandler(self.llm_model, self.cache)
        self.wallet_handler = WalletHandler(self.llm_model, self.cache)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        message = update.message.text

        user = await self._get_user(telegram_user.id)

        if not user:
            await update.message.reply_text(BOT_RESPONSE_TO_REGISTER)
            return

        try:
            chat = self.llm_model.create_base_chat_model()

            response = chat.send_message(message)
            response = self._build_response(response)

            response['user'] = self._format_user_data(user)

            logger.info(f'{response["intent"]} | {telegram_user.id} | {message}')

            self.cache.save_state(telegram_user.id, response)
            await self._save_intent(message, response)
            await self._route_intent(response, update, context)

        except ValueError:
            await update.message.reply_text(BOT_RESPONSE_ERROR_SERVER)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user

        if not update.message.photo:
            await update.message.reply_text('Foto tidak masuk, tolong ulangi foto lagi')
            return

        user = await self._get_user(telegram_user.id)

        if not user:
            await update.message.reply_text(BOT_RESPONSE_TO_REGISTER)
            return

        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        file_bytes = await file.download_as_bytearray()

        response = self.llm_model.parse_context_image(file_bytes)
        response = self._build_response(response)

        logger.info(f' {response["intent"]} | {telegram_user.id} | By photo input')

        response['user'] = self._format_user_data(user)

        self.cache.save_state(telegram_user.id, response)
        await self._save_intent('photo', response)
        await self._route_intent(response, update, context)

    def _build_response(self, response):
        input_token = response.usage_metadata.prompt_token_count
        output_token = response.usage_metadata.candidates_token_count
        response = parse_json(response.text)
        response['inputToken'] = input_token
        response['outputToken'] = output_token
        return response

    async def _save_intent(self, message: str, response: dict):
        async with AsyncSessionLocal() as session:
            new_intent = Intent(
                userId=response['user']['id'],
                chat=message,
                intent=response['intent'],
                response=str(response['content']),
                inputToken=response['inputToken'],
                outputToken=response['outputToken']
                
            )
            session.add(new_intent)
            await session.commit()

    async def _get_user(self, telegram_id: int) -> User:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.wallets))
                .where(User.telegramId == telegram_id)
            )
            return result.scalar_one_or_none()

    def _format_user_data(self, user: User) -> dict:
        return {
            'id': user.id,
            'username': user.username,
            'telegramId': user.telegramId,
            'wallets': [
                {'id': wallet.id, 'name': wallet.name, 'balance': float(wallet.balance)}
                for wallet in user.wallets if wallet.isActive
            ]
        }

    async def _route_intent(self, response, update: Update, context: ContextTypes.DEFAULT_TYPE):
        intent = response['intent']
        
        if intent == 'TANYA_WALLET':
            await self.wallet_handler.wallet_balance(update, context)
        elif intent == 'CATAT_TRANSAKSI':
            await self.cashflow_handler.input_cashflow_by_text(update, context)
        elif intent == 'TAMBAH_WALLET':
            await self.wallet_handler.add_wallet_from_intent(update, context)
        elif intent == 'MINTA_LAPORAN':
            await update.message.reply_text(str(response['content']))
        elif intent == 'LAINNYA':
            await update.message.reply_text(
                markdown_to_html(response['content']), 
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(BOT_RESPONSE_INTENT_NOT_FOUND)
