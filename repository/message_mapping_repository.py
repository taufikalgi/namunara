from models import MessageMappingModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def add_translated_message(
    session: AsyncSession, new_mapping: MessageMappingModel
):
    session.add(new_mapping)
    await session.commit()


async def get_translated_message_by_original_message_id(
    session: AsyncSession, original_message_id: int
):
    try:
        result = await session.execute(
            select(MessageMappingModel).where(
                MessageMappingModel.original_message_id == original_message_id
            )
        )
        return result.scalars().all()

    except Exception as e:
        print(
            f"Error fetching translated message for original_message_id {original_message_id}: {e}"
        )
        return None


async def delete_translated_message_by_original_message_id(
    session: AsyncSession, original_message_id: int
):
    try:
        result = await session.execute(
            select(MessageMappingModel).where(
                MessageMappingModel.original_message_id == original_message_id
            )
        )
        translated_message = result.scalars().first()
        if translated_message:
            await session.delete(translated_message)
            await session.commit()

    except Exception as e:
        print(
            f"Error deleting translated message with original_message_id {original_message_id}: {e}"
        )


async def get_translated_message_by_original_message_id_and_translation_channel_id(
    session: AsyncSession, original_message_id: int, translation_channel_id: int
):
    try:
        result = await session.execute(
            select(MessageMappingModel).where(
                MessageMappingModel.original_message_id == original_message_id,
                MessageMappingModel.translation_channel_id == translation_channel_id,
            )
        )
        return result.scalars().first()

    except Exception as e:
        print(
            f"Error fetching translated message for original_message_id {original_message_id} and translation_channel_id {translation_channel_id}: {e}"
        )
        return None
