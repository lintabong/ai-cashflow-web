
import logging
from bson import ObjectId
from decimal import Decimal
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.handlers.base import BaseHandler

from sqlalchemy.future import select
from bot.services.database import AsyncSessionLocal
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage
from bot.models.cashflow_model import Cashflow
from bot.models.wallet_model import Wallet
from bot.helpers.output_messages import render_grouped_table
from bot.helpers.date_util import string_to_datetime

logger = logging.getLogger(__name__)


class CashflowHandler(BaseHandler):
    def __init__(self, llm_model: LLMModel, cache: CacheMessage):
        self.llm_model = llm_model
        self.cache = cache

    @staticmethod
    def calculate_total(row: dict) -> Decimal:
        return Decimal(row['price']) * Decimal(row['quantity'])

    async def input_cashflow_by_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user

        state = self.cache.get_context(telegram_user.id)

        keyboard = [
                [
                    InlineKeyboardButton('✅ Ya', callback_data='cashflow_yes'),
                    InlineKeyboardButton('❌ Tidak', callback_data='cashflow_no'),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(render_grouped_table(state['content']), parse_mode='Markdown')
        await update.message.reply_text('Apakah transaksi ini benar?', reply_markup=reply_markup)

    async def handle_confirmation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        telegram_user = update.effective_user

        state = self.cache.get_context(telegram_user.id)

        wallet_use, wallet_id = state['content'][0]['wallet'], None

        for row in state['user']['wallets']:
            if wallet_use.lower() == row['name'].lower():
                wallet_id = row['id']
                break

        if not wallet_id:
            await query.edit_message_text('❌ Sepertinya wallet yang kamu sebutkan salah.')
            return

        try:
            if query.data == 'cashflow_yes':
                total_amount = Decimal('0.00')

                async with AsyncSessionLocal() as session:
                    async with session.begin():
                        for row in state['content']:

                            row_total = Decimal(row['price']) * Decimal(row['quantity'])
                            
                            cashflow = Cashflow(
                                id=str(ObjectId()),
                                userId=state['user']['id'],
                                walletId=wallet_id,
                                transactionDate=string_to_datetime(row['date']),
                                activityName=row['activityName'],
                                description='',
                                categoryId=1,
                                quantity=row['quantity'],
                                unit=row['unit'],
                                flowType=row['flowType'],
                                price=row['price'],
                                total=row_total,
                            )

                            session.add(cashflow)

                            if row['flowType'] == 'income':
                                total_amount -= row_total
                            if row['flowType'] == 'expense':
                                total_amount += row_total

                        result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))
                        wallet = result.scalar_one_or_none()
                        if wallet:
                            wallet.balance = wallet.balance - total_amount
                            await session.flush()
                    await session.commit()

                await query.edit_message_text('✅ Transaksi telah disimpan')
            elif query.data == 'cashflow_no':
                await query.edit_message_text('🚫 Transaksi dibatalkan. Silakan prompt ulang')

        except Exception as e:
            logger.error(f'Error handling confirmation: {e}')
            await query.edit_message_text('❌ Terjadi kesalahan saat memproses konfirmasi.')
            self.cache.clear_context(telegram_user.id)
            return

        self.cache.clear_context(telegram_user.id)
        logger.info(f'Success, clear cache {telegram_user.id}')
