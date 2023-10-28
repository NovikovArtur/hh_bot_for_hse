from unittest.mock import AsyncMock
import pytest
from Bot_for_money import send_help



@pytest.mark.asyncio
async def test_help_handler():
    message = AsyncMock()
    await send_help(message)
    message.answer.assert_called_with("Привет!\nЭтот бот поможет тебе найти работника в свой проект, или работу в "
                                      "увлекательном проекте.\nБыстрее создавай резюме и карточку проекта!")